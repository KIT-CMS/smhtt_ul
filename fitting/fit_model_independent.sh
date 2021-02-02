#!/bin/bash

ERA=$1
CHANNEL="cmb"
[[ ! -z $2 ]] && CHANNEL=$2

source utils/setup_cmssw.sh

pushd $FITDIR

combineTool.py -M AsymptoticLimits \
               -m "110,120,130,140,160,180,200,250,300,350,400,450,500,600,700,800,900,1000,1200,1400,1600,1800,2000,2300,2600,2900,3200" \
               --rAbsAcc 0 --rRelAcc 0.0005 \
               --boundlist ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/input/mssm_boundaries.json \
               --setParameters r_ggH=0,r_bbH=0 \
               --redefineSignalPOIs r_bbH \
               -d output_mssm/${ERA}/${CHANNEL}/ws.root \
               --there -n ".bbH" --job-mode condor \
               --dry-run \
               --task-name bbH_full_${ERA} \
               --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01 \
               -v 1

# After adaption of condor_bbH_full_combined.sub, submit to batch system:
condor_submit condor_bbH_full_${ERA}.sub

combineTool.py -M AsymptoticLimits \
               -m "110,120,130,140,160,180,200,250,300,350,400,450,500,600,700,800,900,1000,1200,1400,1600,1800,2000,2300,2600,2900,3200" \
               --rAbsAcc 0 --rRelAcc 0.0005 \
               --boundlist ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/input/mssm_boundaries.json \
               --setParameters r_ggH=0,r_bbH=0 \
               --redefineSignalPOIs r_ggH \
               -d output_mssm/${ERA}/${CHANNEL}/ws.root \
               --there -n ".ggH" --job-mode condor \
               --dry-run \
               --task-name ggH_full_${ERA} \
               --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01 \
               -v 1

# After adaption of condor_ggH_full_combined.sub, submit to batch system:
condor_submit condor_ggH_full_${ERA}.sub
