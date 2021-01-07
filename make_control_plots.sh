#!/bin/bash

ERA=$1
CHANNEL=$2
TAG=$3

if [[ ! -z $4 ]]
then
    IFS="," read -a VARIABLES <<< $4
else
    VARIABLES=(pt_1 pt_2 eta_1 eta_2 m_sv_puppi m_vis jpt_1 jpt_2 jeta_1 jeta_2 dijetpt jdeta mjj bpt_1 bpt_2 mTdileptonMET_puppi mt_1_puppi mt_2_puppi pZetaPuppiMissVis ptvis pt_tt_puppi puppimet)
fi

for VAR in ${VARIABLES[@]}
do
    bash datacards/produce_gof_datacard.sh $ERA $CHANNEL $VAR $TAG
    bash datacards/produce_gof_workspace.sh $ERA $CHANNEL $VAR
    bash shapes/extract_postfit_shapes.sh $ERA $CHANNEL $VAR
    bash plotting/plot_shapes_gof.sh $ERA $CHANNEL $VAR 1 1
done
