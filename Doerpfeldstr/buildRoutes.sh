#!/bin/bash
pushd $(dirname $0)
# public transport
python $SUMO_HOME/tools/import/gtfs/gtfs2pt.py -c Doerpfeldstr.gtfscfg
# cars
python $SUMO_HOME/tools/randomTrips.py -n Doerpfeldstr_edit.net.xml.gz --seed 42 --fringe-factor 8 -p 3  -r cars.rou.xml -b 50400 -e 54000 --vehicle-class passenger --vclass passenger --prefix veh --allow-fringe.min-length 1000 --lanes  -L -l --min-distance 300 --remove-loops
python ./telraam2meandata.py -c Doerpfeldstr.t2mdcfg -o telraam_car_data.xml
python $SUMO_HOME/tools/routeSampler.py -r cars.rou.xml -d telraam_car_data.xml -o cars_sampled.rou.xml --prefix car_ --mismatch-output mismatch_car.xml --timeline TGw2_PKW --merge-strategy ignore
python $SUMO_HOME/tools/route/addStops2Routes.py -c Doerpfeldstr.as2rcfg --route-files cars_sampled.rou.xml -o cars_with_stops.rou.xml
# bikes
python $SUMO_HOME/tools/randomTrips.py -n Doerpfeldstr_edit.net.xml.gz --seed 42 --fringe-factor 10 -p 5  -r bikes.rou.xml -b 50400 -e 54000 --vehicle-class bicycle --vclass bicycle --prefix  bike --prefix "b" --allow-fringe.min-length 1000 --lanes  -L -l
python ./telraam2meandata.py -c Doerpfeldstr.t2mdcfg -o telraam_bike_data.xml --vtype bike
python $SUMO_HOME/tools/routeSampler.py -r bikes.rou.xml -d telraam_bike_data.xml -o bikes_sampled.rou.xml --prefix bike_ --mismatch-output mismatch_bike.xml --attributes "type=\"bicycle\""
# delivery
python $SUMO_HOME/tools/randomTrips.py -n Doerpfeldstr_edit.net.xml.gz --seed 42 --fringe-factor 8 -p 8  -r delivery.rou.xml -b 50400 -e 54000 --vehicle-class delivery --vclass delivery --prefix deliv --allow-fringe.min-length 1000 --lanes  -L -l --min-distance 300 --remove-loops
python ./telraam2meandata.py -c Doerpfeldstr.t2mdcfg -o telraam_heavy_data.xml --vtype heavy
python $SUMO_HOME/tools/routeSampler.py -r delivery.rou.xml -d telraam_heavy_data.xml -o delivery_sampled.rou.xml --prefix delivery_ --mismatch-output mismatch_delivery.xml --attributes "type=\"delivery\"" --timeline TGw_LKW --merge-strategy ignore
python $SUMO_HOME/tools/route/addStops2Routes.py -c Doerpfeldstr.as2rcfg --route-files delivery_sampled.rou.xml -o delivery_with_stops.rou.xml -t vtypes.xml
# pedestrians
python $SUMO_HOME/tools/randomTrips.py -n Doerpfeldstr_edit.net.xml.gz --seed 42 --fringe-factor 1 --insertion-density 10 -r peds.rou.xml -b 50400 -e 54000 --vehicle-class pedestrian --prefix ped --pedestrians --max-distance 2000 --persontrip.walk-opposite-factor 0.8
python ./telraam2meandata.py -c Doerpfeldstr.t2mdcfg -o telraam_ped_data.xml --vtype ped
python $SUMO_HOME/tools/routeSampler.py -r peds.rou.xml -d telraam_ped_data.xml -o ped_sampled.rou.xml --prefix ped_ --mismatch-output mismatch_ped.xml --pedestrians --attributes "type=\"pedestrian\""

popd
