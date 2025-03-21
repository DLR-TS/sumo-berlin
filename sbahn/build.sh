#!/bin/bash
$SUMO_HOME/tools/net/generateStationEdges.py -n berlin-sbahn.net.xml.gz -s berlin-stops.add.xml.gz -o ped_access
netconvert -c stations.netccfg
$SUMO_HOME/tools/randomTrips.py -c persontrips.rtcfg
