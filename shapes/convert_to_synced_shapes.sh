#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
TAG=$4

source utils/setup_root.sh

python shapes/convert_to_synced_shapes.py -e $ERA \
                                          -i output/shapes/${ERA}-${CHANNEL}-analysis-shapes-${TAG}/shapes-analysis-${ERA}-${CHANNEL}.root \
                                          -o output/shapes/${ERA}-${CHANNEL}-${TAG}-synced_shapes_${VARIABLE} \
                                          --variable-selection ${VARIABLE} \
                                          -n 12

OUTFILE=output/shapes/${ERA}-${CHANNEL}-${TAG}-synced_shapes_${VARIABLE}.root
echo "[INFO] Adding written files to single output file $OUTFILE..."
hadd $OUTFILE output/shapes/${ERA}-${CHANNEL}-${TAG}-synced_shapes_${VARIABLE}/*.root
