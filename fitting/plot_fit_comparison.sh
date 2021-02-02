#!/bin/bash

ERA=$1
CHANNEL="cmb"
[[ ! -z $2 ]] && CHANNEL=$2

source utils/setup_cmssw.sh

pushd $FITDIR

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

echo $PWD

for p in gg bb
do
     plotMSSMLimits.py --process "${p}#phi" \
                       --show exp0 "output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}_${CHANNEL}.json:exp0:LineColor=1,MarkerSize=0,LineStyle=2,LineWidth=2,Title=\"Expected w/ ggH uncerts\"" \
                                   "/work/mburkart/Run2Legacy/Run2Legacy_MSSM_FitResults/2021_01_29/output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}_${CHANNEL}.json:exp0:LineColor=2,MarkerSize=0,LineStyle=2,LineWidth=2,Title=\"Expected w/o ggH uncerts\"" \
                                   "output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}_${CHANNEL}.json:exp+2:LineColor=1,MarkerSize=0,LineStyle=7,LineWidth=2,Title=\"#pm 2 #sigma expected w/ ggH uncerts\"" \
                                   "output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}_${CHANNEL}.json:exp+1:LineColor=1,MarkerSize=0,LineStyle=4,LineWidth=2,Title=\"#pm 1 #sigma w/ ggH uncerts\"" \
                                   "output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}_${CHANNEL}.json:exp-1:LineColor=1,MarkerSize=0,LineStyle=4,LineWidth=2,Title=\"\"" \
                                   "output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}_${CHANNEL}.json:exp-2:LineColor=1,MarkerSize=0,LineStyle=7,LineWidth=2,Title=\"\"" \
                       --ratio-to "/work/mburkart/Run2Legacy/Run2Legacy_MSSM_FitResults/2021_01_29/output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}_${CHANNEL}.json:exp0" \
                       --output mssm_model-independent_${ERA}_${p}H_${CHANNEL}_ggH_reweighting_unc \
                       --title-right "$TITLE" \
                       --y-axis-min 0.0001 --y-axis-max 1000.0 \
                       --logx --logy \
                       --cms-sub "Own Work"
                       #       "fit_results_et_mt_tt_2020_09_23/mssm_${p}H_${ERA}_${CHANNEL}.json:exp0:LineColor=2,MarkerSize=0,LineStyle=2,LineWidth=2,Title=\"Previous Expected\"" \
     # plotMSSMLimits.py --process "${p}#phi" \
     #                   --show exp0 "output_mssm/${ERA}/${CHANNEL}/mssm_${p}H_${ERA}_${CHANNEL}.json:exp0:LineColor=1,MarkerSize=0,LineStyle=2,LineWidth=2,Title=\"Expected\"" \
     #                               "limits_artur/mssm_${p}H_${ERA}_${CHANNEL}.json:exp0:LineColor=2,MarkerSize=0,LineStyle=2,LineWidth=2,Title=\"Arturs limits\"" \
     #                   --ratio-to "limits_artur/mssm_${p}H_${ERA}_${CHANNEL}.json:exp0" \
     #                   --output mssm_model-independent_${ERA}_${p}H_${CHANNEL}_comparison_limits_artur \
     #                   --title-right "$TITLE" \
     #                   --y-axis-min 0.0001 --y-axis-max 1000.0 \
     #                   --logx --logy \
     #                   --cms-sub "Own Work"
     #                   #       "fit_results_et_mt_tt_2020_09_23/mssm_${p}H_${ERA}_${CHANNEL}.json:exp0:LineColor=2,MarkerSize=0,LineStyle=2,LineWidth=2,Title=\"Previous Expected\"" \
done
