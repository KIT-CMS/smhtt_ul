#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3

source utils/setup_cmssw.sh

PostFitShapesFromWorkspace -m 125 -w output/workspaces/${ERA}-${CHANNEL}-${VARIABLE}-control-workspace.root -d output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-control/_${VARIABLE}/${ERA}/htt_${CHANNEL}_300_${ERA}/combined.txt.cmb -o output/shapes/${ERA}-${CHANNEL}-${VARIABLE}-control-datacard-shapes-prefit.root
