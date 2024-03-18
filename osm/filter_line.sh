#!/bin/bash
osmfilter bb.o5m --keep= --keep-relations="ref=$1" > $1.osm.xml
