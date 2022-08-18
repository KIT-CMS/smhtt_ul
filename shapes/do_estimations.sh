#!/bin/bash

ERA=$1
INPUT=$2
EMBTT=$3
SPECIAL=$4
[[ -z $EMBTT ]] && EMBTT=1
echo $EMBTT

if [[ $EMBTT == 1 ]]
then
    EMB_ARG="--emb-tt"
else
    EMB_ARG=""
fi

source utils/setup_root.sh

if [[ $SPECIAL != "" ]]
then
    SPECIAL_ARG="--special $SPECIAL"
else
    SPECIAL_ARG=""
fi

python shapes/do_estimations.py -e $ERA -i $INPUT $EMB_ARG $SPECIAL_ARG