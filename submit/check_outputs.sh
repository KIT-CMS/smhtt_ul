#!/bin/bash

ERA=$1
TAG=$2
CHANNELS=${@:3}

source utils/setup_root.sh
source utils/setup_susy_samples.sh $ERA

python submit/check_outputs.py -e $ERA -c $CHANNELS --tag $TAG
