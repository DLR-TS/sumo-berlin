#!/bin/bash
pushd $(dirname $0)
python $SUMO_HOME/tools/net/cut_net.py -n ../tk/tk.net.xml.gz -j Doerpfeldstr.geojson -o Doerpfeldstr_raw.net.xml.gz
netconvert -s Doerpfeldstr_raw.net.xml.gz --remove-edges.input-file remove_edges.txt -o Doerpfeldstr_removed.net.xml.gz
netconvert -s ../../Doerpfeldstr/net.net.xml.gz --keep-edges.input-file keep_edges.txt -o Doerpfeldstr_keep.net.xml.gz
netconvert -s Doerpfeldstr_keep.net.xml.gz,Doerpfeldstr_removed.net.xml.gz -n joined.nod.xml --junctions.join-reset --crossings.guess -o Doerpfeldstr_merged.net.xml.gz
popd
