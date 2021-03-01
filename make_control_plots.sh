#!/bin/bash

ERA=$1
CHANNEL=$2
TAG=$3

if [[ ! -z $4 ]]
then
    IFS="," read -a VARIABLES <<< $4
else
    VARIABLES=(pt_1 pt_2 eta_1 eta_2 m_sv_puppi m_vis jpt_1 jpt_2 jeta_1 jeta_2 dijetpt jdeta mjj njets_red nbtag_red bpt_1 bpt_2 mTdileptonMET_puppi mt_1_puppi mt_2_puppi pZetaPuppiMissVis ptvis pt_tt_puppi puppimet)
fi

# Merge the shapes.
# bash submit/merge_outputs.sh $ERA $CHANNEL $TAG 1

# Produce the different estimations.
bash shapes/do_estimations.sh $ERA output/shapes/${ERA}-${CHANNEL}-control-shapes-${TAG}/shapes-control-${ERA}-${CHANNEL}.root 1

# Convert them to synced shapes,
bash shapes/convert_to_synced_shapes.sh $ERA $CHANNEL dummy $TAG 1

for VAR in ${VARIABLES[@]}
do
    # Produce the datacards.
    bash datacards/produce_gof_datacard.sh $ERA $CHANNEL $VAR $TAG
    # Produce the workspaces.
    bash datacards/produce_gof_workspace.sh $ERA $CHANNEL $VAR
    # Produce the prefit shapes.
    bash shapes/extract_postfit_shapes.sh $ERA $CHANNEL $VAR
    # Produce the plots.
    bash plotting/plot_shapes_control_systematics.sh $ERA $CHANNEL $VAR 1 1
done
