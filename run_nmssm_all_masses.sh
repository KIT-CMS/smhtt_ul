#!/bin/bash
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5

ulimit -s unlimited

for MASSX in 240 450 800; do
    for MASSY in 70 125 250 500 1000 1600 2800; do
        SUM=$((MASSY+125))
        if [ "$SUM" -gt "$MASSX" ]; then
            continue
        fi
        source run_nmssm_analysis.sh $CHANNEL $ERA $NTUPLETAG $TAG $MASSX $MASSY $MODE
    done
done