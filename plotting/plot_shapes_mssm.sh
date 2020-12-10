#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
DIR=$2
JETFAKES=$3
EMBEDDING=$4
CHANNELS=${@:5}

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

for FILE in ${DIR}/${ERA}/cmb/prefit_shapes.root
do
    for OPTION in "" "--png"
    do
        ./plotting/plot_shapes_mssm.py -i $FILE -c $CHANNELS -e $ERA $OPTION $JETFAKES_ARG $EMBEDDING_ARG  --normalize-by-bin-width -o ${DIR}/${ERA}/cmb # --linear
    done
done
