#!/bin/bash
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
YDECAY=$5

for MASSX in 240 450 800 1200 2000 4000; do
    python plot_mY_dependent_limits.py -d limit_jsons/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG} -p $YDECAY -x $MASSX -c $CHANNEL
done

for MASSY in 70 125 250 500 1000 1600 2800; do
    python plot_mX_dependent_limits.py -d limit_jsons/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG} -p $YDECAY -y $MASSY -c $CHANNEL
done

python plot_2D_limits.py -d limit_jsons/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG} -p $YDECAY