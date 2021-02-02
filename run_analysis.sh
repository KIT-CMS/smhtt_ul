#!/bin/bash

ERA=$1
CHANNEL=$2
[[ -z $2 ]] && CHANNEL="cmb"

export FITDIR=fits

bash datacards/produce_datacards.sh 2017 mssm 5 | tee -a produce_datacards_${ERA}_${CHANNEL}.log

bash datacards/produce_workspace.sh 2017 mssm 5 | tee -a produce_workspace_${ERA}_${CHANNEL}.log
