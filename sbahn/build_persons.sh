#!/bin/bash
$SUMO_HOME/tools/net/generateStationEdges.py -c berlin-sbahn-stations.gsecfg
$SUMO_HOME/tools/randomTrips.py -c persontrips.rtcfg
