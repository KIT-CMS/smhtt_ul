#!/bin/bash
ulimit -s unlimited

IFS="," read -a ERA <<< $1
ANALYSIS=$2
CORES=1
[[ ! -z $3 ]] && CORES=$3
echo "Use $CORES cores."

source utils/setup_cmssw.sh

pushd $FITDIR

if [[ "$ANALYSIS" =~ "output_mssm_vs_sm_classic_h125" ]]
then
combineTool.py -M T2W -o ws_mh125.root \
               -P CombineHarvester.MSSMvsSMRun2Legacy.MSSMvsSM:MSSMvsSM \
               --PO filePrefix=${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/data/ \
               --PO modelFile=13,Run2017,mh125_13.root \
               --PO MSSM-NLO-Workspace=${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/data/higgs_pt_v3_mssm_mode.root \
               -i output_${ANALYSIS}/combined/cmb/ 
               --PO minTemplateMass=110.0 
               --PO maxTemplateMass=3200.0
elif [[ "$ANALYSIS" =~ "mssm" ]]
then
    if [[ ${#ERA[@]} == 1 ]]
    then
        INPUT=output_${ANALYSIS}/${ERA}/cmb/
        # INPUT=output_${ANALYSIS}/${ERA}/{cmb,htt_*,et,mt,tt,em}/
    else
        INPUT=output_${ANALYSIS}/{$(IFS="," ; echo ${ERA[*]})}/{cmb,htt_*,et,mt,tt,em}
    fi
    combineTool.py -M T2W -o "ws.root" \
                   -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
                   --PO '"map=^.*/ggh_(i|t|b).?$:r_ggH[0,0,200]"' --PO '"map=^.*/bbh$:r_bbH[0,0,200]"' \
                   -i $INPUT \
                   -m 110 \
                   --parallel $CORES
else
    echo "[ERROR] Given analysis $ANALYSIS not known. Aborting..."
    exit 1
fi
