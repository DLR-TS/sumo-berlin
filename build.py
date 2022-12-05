#!/usr/bin/env python
import os
import sys
import subprocess
import urllib.request
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import sumolib  # noqa

#urllib.request.urlretrieve("https://download.geofabrik.de/europe/germany/brandenburg-latest.osm.pbf", "osm/brandenburg-latest.osm.pbf")
lon = []
lat = []
for poi in sumolib.xml.parse_fast("location_priorities.xml", "poi", ["lon", "lat"]):
    lon.append(float(poi.lon))
    lat.append(float(poi.lat))
subprocess.check_call(["osmconvert", "osm/brandenburg-latest.osm.pbf", "-o=osm/bb.o5m", "-b=%s,%s,%s,%s" % (min(lon) - 0.01, min(lat) - 0.01, max(lon) + 0.01, max(lat) + 0.01)])
subprocess.check_call(["osmfilter", "osm/bb.o5m", '--keep-ways=highway= railway= cycleway= aeroway= waterway=', "--keep-nodes=", '--drop-relations=type=multipolygon route=hiking', "--out-o5m", "-o=osm/bb_filtered.o5m"])
subprocess.check_call(["osmconvert", "osm/bb_filtered.o5m", "-o=osm/bb_filtered.osm.xml"])
subprocess.check_call([sumolib.checkBinary("netconvert"), "berlin.netccfg"])
