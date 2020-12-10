#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
INPUT=$2
OUTPUT=$3  # Output directory the plots are written to.
JETFAKES=$4
EMBEDDING=$5
CHANNELS=${@:6}

EMBEDDING_ARG=""
if [ $EMBEDDING == 1 ]
then
    EMBEDDING_ARG="--embedding"
fi

JETFAKES_ARG=""
if [ $JETFAKES == 1 ]
then
    JETFAKES_ARG="--fake-factor"
fi

if [[ ! -d "$OUTPUT" ]]
then
    mkdir $OUTPUT
fi

for FILE in $INPUT
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_shapes_mssm.py -i $FILE -c $CHANNELS -e $ERA $OPTION $JETFAKES_ARG $EMBEDDING_ARG  --normalize-by-bin-width -o $OUTPUT --model-independent # --linear
        # ./plotting/plot_shapes_mssm.py -i $FILE -c $CHANNELS -e $ERA $OPTION $JETFAKES_ARG $EMBEDDING_ARG  --normalize-by-bin-width -o plots_from_naf_control # --linear
    done
done
