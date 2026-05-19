#!/bin/bash
pushd $(dirname $0)
# public transport
python $SUMO_HOME/tools/import/gtfs/gtfs2pt.py -c Doerpfeldstr.gtfscfg
python ./ptPersons.py gtfs_pt_vehicles.add.xml 
# parking
python $SUMO_HOME/tools/generateParkingAreas.py -n Doerpfeldstr_edit.net.xml.gz --edge-type.keep highway.residential -o parkingAreas.add.xml
python $SUMO_HOME/tools/route/addStops2Routes.py -n Doerpfeldstr_edit.net.xml.gz --parking-areas parkingAreas.add.xml -o parking.rou.xml -d 100000 --rel-occupancy 0.8 --color '#505050'
sed 's/depart="0"/depart="6:0:0"/' parking.rou.xml > parking6.rou.xml
# cars
python $SUMO_HOME/tools/randomTrips.py -n Doerpfeldstr_edit.net.xml.gz --seed 42 --fringe-factor 8 -p 1  -r cars.rou.xml --prefix veh --lanes -l --min-distance 300 --remove-loops -a preferences.xml
python ./telraam2meandata.py -c Doerpfeldstr.t2mdcfg -o telraam_car_data.xml
python $SUMO_HOME/tools/routeSampler.py -r cars.rou.xml -d telraam_car_data.xml,manual_car_data.xml -o cars_sampled.rou.xml --prefix car_ --mismatch-output mismatch_car.xml --timeline TGw2_PKW --merge-strategy ignore -T turn_probabilities.xml --attributes "color=\"random\""
# --turn-files main_relations.xml
python $SUMO_HOME/tools/countEdgeUsage.py cars_sampled.rou.xml -i
python $SUMO_HOME/tools/route/addStops2Routes.py -c Doerpfeldstr.as2rcfg --route-files cars_sampled.rou.xml -o cars_with_stops.rou.xml
# bikes
python $SUMO_HOME/tools/randomTrips.py -n Doerpfeldstr_edit.net.xml.gz --seed 42 --fringe-factor 10 -p 5  -r bikes.rou.xml --vehicle-class bicycle --vclass bicycle --prefix bike --lanes -l
python ./telraam2meandata.py -c Doerpfeldstr.t2mdcfg -o telraam_bike_data.xml --vtype bike
python $SUMO_HOME/tools/routeSampler.py -r bikes.rou.xml -d telraam_bike_data.xml -o bikes_sampled.rou.xml --prefix bike --mismatch-output mismatch_bike.xml --attributes "type=\"bicycle\" color=\"random\""
# delivery
python $SUMO_HOME/tools/randomTrips.py -n Doerpfeldstr_edit.net.xml.gz --seed 42 --fringe-factor 8 -p 8  -r delivery.rou.xml --vehicle-class delivery --vclass delivery --prefix deliv --lanes -l --min-distance 300 --remove-loops -a preferences.xml
python ./telraam2meandata.py -c Doerpfeldstr.t2mdcfg -o telraam_heavy_data.xml --vtype heavy
python $SUMO_HOME/tools/routeSampler.py -r delivery.rou.xml -d telraam_heavy_data.xml -o delivery_sampled.rou.xml --prefix delivery --mismatch-output mismatch_delivery.xml --attributes "type=\"delivery\"" --timeline TGw_LKW --merge-strategy ignore
python $SUMO_HOME/tools/route/addStops2Routes.py -c Doerpfeldstr.as2rcfg --route-files delivery_sampled.rou.xml -o delivery_with_stops.rou.xml -t vtypes.xml
# pedestrians
python $SUMO_HOME/tools/randomTrips.py -n Doerpfeldstr_edit.net.xml.gz -b 6:0:0 -e 7:0:0 --seed 42 --fringe-factor 1 --insertion-density 10 -r peds.rou.xml --vehicle-class pedestrian --prefix ped --pedestrians --max-distance 2000 --persontrip.walk-opposite-factor 0.8 --persontrip.modes public -a vtypes.xml,gtfs_pt_stops.add.xml,gtfs_pt_vehicles.add.xml
python ./telraam2meandata.py -c Doerpfeldstr.t2mdcfg -o telraam_ped_data.xml --vtype ped
python $SUMO_HOME/tools/routeSampler.py -r peds.rou.xml -d telraam_ped_data.xml -o ped_sampled.rou.xml --prefix ped --mismatch-output mismatch_ped.xml --pedestrians --attributes "type=\"pedestrian\" color=\"random\""

popd
