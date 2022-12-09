#!/usr/bin/env python
import os
import sys
import subprocess
import gzip
import urllib.request
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import sumolib  # noqa

#urllib.request.urlretrieve("https://download.geofabrik.de/europe/germany/brandenburg-latest.osm.pbf", "osm/brandenburg-latest.osm.pbf")
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
subprocess.check_call([sumolib.checkBinary("netconvert"), "berlin.netccfg"])
net = sumolib.net.readNet("netpatch/berlin.net.xml.gz")
with open("landmarks") as landmarks:
    new_landmarks = []
    for line in landmarks:
        edge_id = line.strip()
        if not net.hasEdge(edge_id):
            print("missing landmark edge", edge_id)
            if "#" in edge_id:
                osm_id, idx = edge_id.split("#")
                idx = int(idx)
            else:
                osm_id, idx = edge_id, 1
            for i in (idx - 1, idx, idx + 1):
                edge_id = "%s#%s" % (osm_id, i)
                if net.hasEdge(edge_id):
                    print("proposing", edge_id)
                    break
        new_landmarks.append(edge_id)
with open("new_landmarks", "w") as landmarks:
    landmarks.write("\n".join(new_landmarks))

subprocess.check_call([sumolib.checkBinary("netconvert"), "tk/tk.netccfg"])
