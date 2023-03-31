#!/usr/bin/bash
export LCG_RELEASE=102
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
INPUT=$2
CHANNEL=$3

# v="pt_1,pt_2,eta_1,eta_2,m_vis,m_sv_puppi,pt_tt_puppi,ptvis,jpt_1,jpt_2,jeta_1,jeta_2,bpt_1,bpt_2,puppimet,DiTauDeltaR,pZetaPuppiMissVis,mt_1_puppi,mt_2_puppi,mTdileptonMET_puppi,njets,nbtag,jdeta,dijetpt,mjj"
v="pt_1,pt_2,m_vis,njets,mt_1,nbtag,met,eta_1,eta_2,pt_tt,pt_vis,mjj,jpt_1,jpt_2,jeta_1,jeta_2,bpt_1,bpt_2"
plotting/plot_shapes_control.py -l --era Run${ERA} --input $INPUT --variables ${v} --channels ${CHANNEL} --embedding
plotting/plot_shapes_control.py -l --era Run${ERA} --input $INPUT --variables ${v} --channels ${CHANNEL}
plotting/plot_shapes_control.py -l --era Run${ERA} --input $INPUT --variables ${v} --channels ${CHANNEL} --nlo
