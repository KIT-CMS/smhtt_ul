#!/bin/bash

IFS="," read -a ERA <<< $1
# IFS="," read -a CHANNEL <<< $2
ANALYSIS=$2

CORES=1
[[ ! -z $3 ]] && CORES=$3
echo "Using $CORES cores..."

source utils/setup_cmssw.sh

pushd $FITDIR

if [[ "$ANALYSIS" =~ "mssm_vs_sm_classic_h125" ]]
then
    morph_parallel.py --output output --analysis $ANALYSIS \
                      --eras $(IFS="," ; echo ${ERA[*]}) \
                      --category_list ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/input/mssm_classic_categories.txt \
                      --variable mt_tot_puppi \
                      --additional_arguments="--auto_rebin=1" \
                      --parallel $CORES
elif [[ "$ANALYSIS" =~ "mssm_vs_sm_heavy" ]]
then
    morph_parallel.py --output output --analysis $ANALYSIS \
                      --eras $(IFS="," ; echo ${ERA[*]}) \
                      --category_list ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/input/mssm_classic_categories.txt \
                      --variable mt_tot_puppi \
                      --parallel $CORES
elif [[ "$ANALYSIS" =~ "mssm_vs_sm_h125" ]]
then
    morph_parallel.py --output output --analysis $ANALYSIS \
                      --eras $(IFS="," ; echo ${ERA[*]}) \
                      --category_list ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/input/mssm_new_categories.txt \
                      --variable mt_tot_puppi \
                      --parallel $CORES
    morph_parallel.py --output output --analysis $ANALYSIS \
                      --eras $(IFS="," ; echo ${ERA[*]}) \
                      --category_list ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/input/sm_categories.txt \
                      --variable m_sv_puppi \
                      --parallel $CORES
elif [[ "$ANALYSIS" =~ "mssm" || "$ANALYSIS" =~ "mssm_vs_sm_CPV" ]]
then
    #TODO: Split treatment of higgs pt fractions for 2016.
    morph_parallel.py --output output --analysis $ANALYSIS \
                      --eras $(IFS="," ; echo ${ERA[*]}) \
                      --category_list ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/input/mssm_classic_categories.txt \
                      --variable mt_tot_puppi \
                      --additional_arguments="--auto_rebin=1" \
                      --sm_gg_fractions ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/data/higgs_pt_v0.root \
                      --parallel $CORES
    morph_parallel.py --output output --analysis $ANALYSIS \
                      --eras $(IFS="," ; echo ${ERA[*]}) \
                      --category_list ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/input/control_region_categories.txt \
                      --variable mt_tot_puppi \
                      --additional_arguments="--auto_rebin=1" \
                      --sm_gg_fractions ${CMSSW_BASE}/src/CombineHarvester/MSSMvsSMRun2Legacy/data/higgs_pt_v0.root \
                      --parallel $CORES
else
    echo "[ERROR] Given analysis $ANALYSIS not known."
    exit 1
fi

OUTPUT_FOLDER=output_${ANALYSIS}
for era in ${ERA[@]};
do
    for CH in et mt tt em
    do
        mkdir -p ${OUTPUT_FOLDER}/${era}/${CH}/; rsync -av --progress output_mssm/${era}/htt_${CH}_*/*  output_mssm/${era}/${CH}/
    done
    mkdir -p ${OUTPUT_FOLDER}/${era}/cmb/; rsync -av --progress output_mssm/${era}/htt_*/*  output_mssm/${era}/cmb/
done
mkdir -p output_mssm/combined/cmb/; rsync -av --progress output_mssm/201?/htt_*/*  output_mssm/combined/cmb/
