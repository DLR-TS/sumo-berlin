#!/usr/bin/env python
import os
import sys
import subprocess
import gzip
import urllib.request
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import sumolib  # noqa


def update():
    urllib.request.urlretrieve("https://download.geofabrik.de/europe/germany/brandenburg-latest.osm.pbf",
                               "osm/brandenburg-latest.osm.pbf")
    lon = []
    lat = []
    for poi in sumolib.xml.parse_fast("location_priorities.xml", "poi", ["lon", "lat"]):
        lon.append(float(poi.lon))
        lat.append(float(poi.lat))
    subprocess.check_call(["osmconvert", "osm/brandenburg-latest.osm.pbf", "-o=osm/bb.o5m",
                           "-b=%s,%s,%s,%s" % (min(lon) - 0.01, min(lat) - 0.01, max(lon) + 0.01, max(lat) + 0.01)])
    call = ["osmfilter", "osm/bb.o5m", "--keep-ways=highway= railway= cycleway= aeroway= waterway=",
            "--keep-nodes=", "--drop-relations=type=multipolygon route=hiking", "--drop-author",
            "--drop-tags=note= old_name= source= name:etymology:wikidata= wikipedia="]
    with gzip.open("osm/bb_filtered.osm.xml.gz", "wb") as filtered:
        filtered.write(subprocess.check_output(call))


def check_edge(net, edge_id, found):
    if "#" in edge_id:
        osm_id, idx = edge_id.split("#")
        idx = int(idx)
    else:
        osm_id, idx = edge_id, 1
    for i in (idx - 1, idx, idx + 1):
        new_id = "%s#%s" % (osm_id, i)
        if net.hasEdge(new_id):
            return True, new_id
    if not found and net.hasEdge(osm_id):
        return True, osm_id
    return False, edge_id


def check_landmarks():
    net = sumolib.net.readNet("netpatch/berlin.net.xml.gz")
    with open("landmarks") as landmarks:
        new_landmarks = []
        for line in landmarks:
            edge_id = line.strip()
            found = True
            if not net.hasEdge(edge_id):
                print("missing landmark edge", edge_id)
                found, edge_id = check_edge(net, edge_id, found)
                if not found:
                    if edge_id[0] == "-":
                        edge_id = edge_id[1:]
                    else:
                        edge_id = "-" + edge_id
                    found, edge_id = check_edge(net, edge_id, found)
            if found:
                new_landmarks.append(edge_id)
    with open("new_landmarks", "w") as landmarks:
        landmarks.write("\n".join(new_landmarks))


def main():
    argParser = sumolib.options.ArgumentParser()
    argParser.add_argument("-v", "--verbose", action="store_true", default=False,
                           help="tell me what you are doing")
    argParser.add_argument("-l", "--check-landmarks", action="store_true", default=False,
                           help="recheck landmark validity")
    argParser.add_argument("-u", "--update", action="store_true", default=False,
                           help="update OSM data from geofabrik")
    argParser.add_argument("--sbahn", action="store_true", default=False,
                           help="build only sbahn simulation")
    argParser.add_argument("--osmpt", action="store_true", default=False,
                           help="use public transport routes from OSM rather than GTFS")
    argParser.add_argument("--skip-net", dest="skipnet",  action="store_true", default=False,
                           help="do not rebuild the network")
    options = argParser.parse_args()
    if options.update:
        update()
    if not options.sbahn and not options.skipnet:
        subprocess.check_call([sumolib.checkBinary("netconvert"), "netpatch/berlin.netccfg"])
    if options.check_landmarks:
        check_landmarks()
    typemapPrefix = os.path.join(os.environ["SUMO_HOME"], "data", "typemap", "osmNetconvert")
    if not options.skipnet:
        subprocess.check_call([sumolib.checkBinary("netconvert"), "-c", "berlin.netccfg",
                               "--output-prefix", "../sbahn/berlin-", "-o", "sbahn.net.xml.gz",
                               "--keep-edges.by-type", "railway.light_rail|usage.main,railway.light_rail|service.siding,railway.light_rail|service.crossover,railway.rail|usage.main",
                               "--remove-edges.by-vclass", "rail,rail_electric,rail_fast",
                               "--type-files", typemapPrefix + ".typ.xml," + typemapPrefix + "RailUsage.typ.xml"], cwd='netpatch')
    if options.osmpt:
        subprocess.check_call([sys.executable, os.path.join(os.environ["SUMO_HOME"], "tools", "ptlines2flows.py"),
            "-c", "sbahn.ptlfcfg"], cwd="sbahn")
    else:
        if not os.path.exists("sbahn/BVG_VBB_bereichsscharf_20190603.zip"):
            urllib.request.urlretrieve("https://sumo.dlr.de/daily/GTFS_VBB_Juni-Dezember-2019.zip",
                                       "sbahn/BVG_VBB_bereichsscharf_20190603.zip")
        subprocess.check_call([sys.executable, os.path.join(os.environ["SUMO_HOME"], "tools", "import", "gtfs", "gtfs2pt.py"),
                               "-c", "sbahn.gtfscfg"], cwd="sbahn")
    if not options.sbahn and not options.skipnet:
        subprocess.check_call([sumolib.checkBinary("netconvert"), "tk/tk.netccfg"])


if __name__ == "__main__":
    main()
