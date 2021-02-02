#!/bin/bash

ERA=$1
CHANNEL=$2

source utils/setup_cmssw.sh

pushd $FITDIR

combineTool.py -M Impacts -d output_mssm/${ERA}/${CHANNEL}/ws.root -m 125 \
               --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
               --doInitialFit --robustFit 1 \
               -t -1 --expectSignal=1 \
               --parallel 16

combineTool.py -M Impacts -d output_mssm/${ERA}/${CHANNEL}/ws.root -m 125 \
               --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
               --robustFit 1 --doFits \
               -t -1 --expectSignal=1 \
               --parallel 16

combineTool.py -M Impacts -d output_mssm/${ERA}/${CHANNEL}/ws.root -m 125 -o ${ERA}_${CHANNEL}_impacts.json

plotImpacts.py -i ${ERA}_${CHANNEL}_impacts.json -o ${ERA}_${CHANNEL}_impacts
