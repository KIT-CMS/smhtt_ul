#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
TAG=$4

CONTROL=$5

[[ ! -z $5 ]] || CONTROL=0

source utils/bashFunctionCollection.sh
source utils/setup_root.sh

if [[ $CONTROL == 0 ]]
then
    logandrun python shapes/convert_to_synced_shapes.py -e $ERA \
                                                        -i output/shapes/${ERA}-${CHANNEL}-analysis-shapes-${TAG}/shapes-analysis-${ERA}-${CHANNEL}.root \
                                                        -o output/shapes/${ERA}-${CHANNEL}-${TAG}-synced_shapes_${VARIABLE} \
                                                        --variable-selection ${VARIABLE} \
                                                        -n 12
    OUTFILE=output/shapes/${ERA}-${CHANNEL}-${TAG}-synced_shapes_${VARIABLE}.root
    echo "[INFO] Adding written files to single output file $OUTFILE..."
    logandrun hadd -f $OUTFILE output/shapes/${ERA}-${CHANNEL}-${TAG}-synced_shapes_${VARIABLE}/*.root
else
    logandrun python shapes/convert_to_synced_shapes.py -e $ERA \
                                                        -i output/shapes/${ERA}-${CHANNEL}-control-shapes-${TAG}/shapes-control-${ERA}-${CHANNEL}.root \
                                                        -o output/shapes/${ERA}-${CHANNEL}-${TAG}-gof-synced_shapes \
                                                        --gof \
                                                        -n 12
fi
