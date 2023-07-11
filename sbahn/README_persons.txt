tools/ptlines2flows.py -c sbahn.ptlfcfg
tools/net/generateStationEdges.py -c berlin-sbahn-stations.gsecfg
netconvert -c berlin-sbahn-stations.netccfg
tools/randomTrips.py -c persontrips.rtcfg
sumo-gui -c sbahn_osmlines_persons.sumocfg

