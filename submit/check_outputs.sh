#!/bin/bash

ERA=$1
IFS="," read -r -a CHANNELS <<< $2
TAG=$3
CONTROL=$4

[[ ! -z $4 ]] || CONTROL=0
CONTROL_ARG=""
if [[ $CONTROL == 1 ]]
then
    CONTROL_ARG="--control"
fi

source utils/setup_root.sh
source utils/setup_susy_samples.sh $ERA

python submit/check_outputs.py -e $ERA -c ${CHANNELS[@]} --tag $TAG $CONTROL_ARG
