#!/bin/bash
ERA=$1
CHANNEL="cmb"
[[ ! -z $2 ]] && CHANNEL=$2

source utils/setup_cmssw.sh

pushd $FITDIR

for p in gg bb
do
        combineTool.py -M CollectLimits \
                       output_mssm/${ERA}/${CHANNEL}/higgsCombine.${p}H*.root \
                       --use-dirs \
                       -o output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}.json
done

if [[ "$ERA" =~ "2016" ]]
then
    TITLE="35.9 fb^{-1} (2016, 13 TeV)"
elif [[ "$ERA" =~ "2017" ]]
then
    TITLE="41.5 fb^{-1} (2017, 13 TeV)"
elif [[ "$ERA" =~ "2018" ]]
then
    TITLE="59.7 fb^{-1} (2018, 13 TeV)"
elif [[ "$ERA" =~ "combined" ]]
then
    TITLE="137 fb^{-1} (13 TeV)"
else
    echo "[ERROR] Given era $ERA is not defined. Aborting..."
    exit 1
fi

for p in gg bb
do
        plotMSSMLimits.py output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}_${CHANNEL}.json \
                          --cms-sub "Own Work" --title-right "$TITLE" \
                          --process "${p}#phi" \
                          --y-axis-min 0.0001 --y-axis-max 1000.0 \
                          --show exp,obs \
                          --output mssm_model-independent_${ERA}_${p}H_${CHANNEL} \
                          --logx --logy
done
