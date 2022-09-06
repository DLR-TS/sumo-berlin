download https://download.geofabrik.de/europe/germany/brandenburg-latest.osm.bz2
osmconvert brandenburg-latest.osm.pbf -o=bb.o5m -b=12.754312,52.245548,13.890688,52.803157
osmfilter bb.o5m --keep-ways="highway= railway= cycleway= aeroway= waterway=" --keep-nodes= --drop-relations="type=multipolygon route=hiking" --out-o5m -o=bb_filtered.o5m
osmconvert bb_filtered.o5m -o=bb_filtered.osm.xml

... convert to osm.xml.gz
