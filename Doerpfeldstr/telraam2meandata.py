#!/usr/bin/env python3
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
# Copyright (C) 2025-2026 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# SPDX-License-Identifier: EPL-2.0

"""
Convert Telraam segment data (GeoJSON + hourly CSV) to SUMO meandata XML
for a chosen day.

Each GeoJSON feature (a road segment) is matched to the nearest SUMO edge
using the segment midpoint. Bidirectional segments are matched to both the
forward and reverse SUMO edges; left/right Telraam counts are assigned based
on the angular alignment between the segment direction and each edge direction.

Usage example:
  python tools/telraam2meandata.py \
      --net doe/Doerpfeldstr_edit.net.xml.gz \
      --geojson doe/bzm_telraam_segments.geojson \
      --csv doe/bzm_telraam_2025_03.csv.gz \
      --day 2025-03-05 \
      --output doe/telraam_2025-03-05.xml
"""

import csv
import json
import math
import os
import sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import sumolib


def parse_args():
    parser = sumolib.options.ArgumentParser(description=__doc__,
                                            formatter_class=sumolib.options.RawDescriptionHelpFormatter)
    parser.add_argument("-n", "--net", required=True, help="SUMO network file (.net.xml or .net.xml.gz)")
    parser.add_argument("--geojson", required=True, help="Telraam segments GeoJSON file")
    parser.add_argument("--csv", required=True, help="Telraam hourly CSV file (may be .gz)")
    parser.add_argument("--day", required=True, help="Day to export, format YYYY-MM-DD")
    parser.add_argument("-o", "--output", required=True, help="Output meandata XML file")
    parser.add_argument("--radius", type=float, default=50.0,
                        help="Search radius in metres for edge matching (default: 50)")
    parser.add_argument("--interval-id", default="telraam",
                        help="id attribute for the <interval> element")
    parser.add_argument("--vtype", default="car", choices=["car", "ped", "bike", "heavy"],
                        help="Telraam count column to use (default: car)")
    return parser.parse_args()


def segment_direction(coords):
    """Return a unit direction vector from first to last coordinate (XY)."""
    x0, y0 = coords[0]
    x1, y1 = coords[-1]
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length == 0:
        return (0.0, 0.0)
    return (dx / length, dy / length)


def edge_direction(edge):
    """Return a unit direction vector along a SUMO edge (XY)."""
    shape = edge.getShape()
    return segment_direction(shape)


def midpoint_xy(coords):
    """Return the XY midpoint of a list of (x, y) pairs."""
    mid_idx = len(coords) // 2
    x = (coords[mid_idx - 1][0] + coords[mid_idx][0]) / 2 if len(coords) > 1 else coords[0][0]
    y = (coords[mid_idx - 1][1] + coords[mid_idx][1]) / 2 if len(coords) > 1 else coords[0][1]
    return x, y


def reverse_edge_id(edge_id):
    """Return the ID of the edge in the opposite direction."""
    if edge_id.startswith("-"):
        return edge_id[1:]
    return "-" + edge_id


def match_segment(net, geo_coords_xy, seg_dir, radius):
    """
    Find the best matching SUMO edge for a segment and return a dict:
      { 'forward': edge_id_aligned_with_seg_dir,
        'backward': edge_id_opposite_to_seg_dir }
    Either value may be None if no edge is found or exists.
    """
    mx, my = midpoint_xy(geo_coords_xy)
    candidates = net.getNeighboringEdges(mx, my, r=radius)
    if not candidates:
        return None

    # pick the nearest edge
    nearest_edge, _ = sorted(candidates, key=lambda x: x[1])[0]
    e_dir = edge_direction(nearest_edge)
    alignment = seg_dir[0] * e_dir[0] + seg_dir[1] * e_dir[1]

    # alignment > 0  => nearest edge runs in the same direction as the segment
    if alignment >= 0:
        fwd_id = nearest_edge.getID()
        bwd_id = reverse_edge_id(fwd_id)
        if not net.hasEdge(bwd_id):
            bwd_id = None
    else:
        bwd_id = nearest_edge.getID()
        fwd_id = reverse_edge_id(bwd_id)
        if not net.hasEdge(fwd_id):
            fwd_id = None
    return fwd_id, bwd_id


def build_segment_map(net, geojson_path, radius):
    """
    Return a dict mapping segment_id (str) -> match dict from match_segment().
    Only segments with at least one matched edge are included.
    """
    with open(geojson_path) as f:
        collection = json.load(f)

    mapping = {}
    unmatched = 0
    for feature in collection["features"]:
        seg_id = str(feature["properties"]["segment_id"])
        lines = feature["geometry"]["coordinates"]  # MultiLineString

        # Flatten all lines into one polyline for direction/midpoint computation
        all_lonlat = [pt for line in lines for pt in line]
        try:
            all_xy = [net.convertLonLat2XY(pt[0], pt[1]) for pt in all_lonlat]
        except Exception:
            unmatched += 1
            continue

        seg_dir = segment_direction(all_xy)
        match = match_segment(net, all_xy, seg_dir, radius)
        if match is None:
            unmatched += 1
            continue
        mapping[seg_id] = match

    if unmatched:
        print(f"  {unmatched} segments had no nearby edge and were skipped.", file=sys.stderr)
    print(f"  Matched {len(mapping)} segments to SUMO edges.", file=sys.stderr)
    return mapping


def load_day_data(csv_path, day, vtype):
    """
    Return a dict: {segment_id: {hour_int: {'lft': n, 'rgt': n}}}
    hour_int (0..23) is the start-of-hour label parsed from 'YYYY-MM-DD HH:00'.
    vtype selects which Telraam columns to read: car, ped, bike, or heavy.
    """
    data = {}
    with sumolib.openz(csv_path) as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            date_str = row["date_local"]  # e.g. "2025-03-05 07:00"
            if not date_str.startswith(day):
                continue
            seg_id = row["segment_id"]
            hour = int(date_str[11:13])  # HH
            lft = float(row[vtype + "_lft"] or 0)
            rgt = float(row[vtype + "_rgt"] or 0)
            data.setdefault(seg_id, {})[hour] = {"lft": lft, "rgt": rgt}
    return data


def write_meandata(output_path, day_data, segment_map, interval_id):
    """Write a meandata XML file with one <interval> per hour."""
    # Collect all hours present in the data
    all_hours = sorted({h for seg in day_data.values() for h in seg})

    with open(output_path, "w", encoding="utf-8") as out:
        out.write("<meandata>\n")
        for hour in all_hours:
            begin_sec = hour * 3600
            end_sec = (hour + 1) * 3600
            out.write(f'    <interval begin="{begin_sec}" end="{end_sec}" id="{interval_id}">\n')

            # average counts per edge across all segments that map to it
            edge_totals = {}   # edge_id -> running sum
            edge_hits = {}     # edge_id -> number of contributing segments
            for seg_id, hours in day_data.items():
                if hour not in hours:
                    continue
                match = segment_map.get(seg_id)
                if match is None:
                    continue
                lft = hours[hour]["lft"]
                rgt = hours[hour]["rgt"]
                fwd, bwd = match
                if fwd:
                    edge_totals[fwd] = edge_totals.get(fwd, 0) + lft
                    edge_hits[fwd] = edge_hits.get(fwd, 0) + 1
                if bwd:
                    edge_totals[bwd] = edge_totals.get(bwd, 0) + rgt
                    edge_hits[bwd] = edge_hits.get(bwd, 0) + 1

            for eid in sorted(edge_totals):
                count = edge_totals[eid] / edge_hits[eid]
                if count > 0:
                    out.write(f'        <edge id="{eid}" entered="{int(count)}" />\n')

            out.write("    </interval>\n")
        out.write("</meandata>\n")


def main():
    args = parse_args()

    print(f"Reading network: {args.net}", file=sys.stderr)
    net = sumolib.net.readNet(args.net)

    print(f"Matching GeoJSON segments to network edges (radius={args.radius}m) ...", file=sys.stderr)
    segment_map = build_segment_map(net, args.geojson, args.radius)

    print(f"Loading CSV data for day {args.day} (vtype={args.vtype}) ...", file=sys.stderr)
    day_data = load_day_data(args.csv, args.day, args.vtype)
    print(f"  Found data for {len(day_data)} segments on {args.day}.", file=sys.stderr)

    print(f"Writing meandata to: {args.output}", file=sys.stderr)
    write_meandata(args.output, day_data, segment_map, args.interval_id)
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
