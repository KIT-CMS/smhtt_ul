export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNELS_str=${1}
IFS=',' read -r -a CHANNELS <<< "${CHANNELS_str}"
ERA=${2}
NTUPLETAG=${3}
TAG=${4}
MODE=${5}
WP=${6}
WP_VSe=${7}
WP_VSmu=${8}
ES_up=${9}
ES_down=${10}
EXTENDED_TAG_UP=${11:-"M_pre_20to20_ext_up"}
EXTENDED_TAG_DOWN=${12:-"M_pre_20to20_ext_down"}
BIN_TAG=${13}


echo ${NTUPLETAG}
echo ${WP}

VARIABLES="m_vis"
POSTFIX="-TauID_ES"
ulimit -s unlimited
source utils/setup_ul_samples.sh ${NTUPLETAG} ${ERA}

# Debuggung breakpoint()with ipdb:
# pip3 install ipdb
export PYTHONBREAKPOINT="ipdb.set_trace"

# [INFO] tau_id_es_measurement/tau_id_es_sim_fit_conf.sh contains all fit parameters.

# Datacard Setup

datacard_output_pt="datacards_pt_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_dm="datacards_dm_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_incl="datacards_incl_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

# datacard_output_dm_pt="datacards_dm_pt_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"
datacard_output_dm_pt="datacards_dm_pt_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}_VSe${WP_VSe}"

poi_path="poi_corr_${TAG}"

impact_path="impacts_${TAG}"


echo "MY WP,WP_VSe,WP_VSmu is: " ${WP} ${WP_VSe} ${WP_VSmu}
echo "My out path is: ${shapes_output}"
echo "My synchpath is ${shapes_output_synced}"

# print the paths to be used
echo "KINGMAKER_BASEDIR: ${KINGMAKER_BASEDIR}"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "FRIENDS: ${FRIENDS}"
echo "XSEC: ${XSEC_FRIENDS}"


all_categories=("DM0" "DM1" "DM1011" \
"DM0_PT20_40" "DM1_PT20_40" "DM1011_PT20_40" \
"DM0_PT40_200" "DM1_PT40_200" "DM1011_PT40_200")
# Generates es_shifts from {ES_down} to ${ES_up} in 0.1 steps:
es_shifts=()
ES_up_int=$(printf "%.0f" "$(echo "${ES_up}*10" | bc -l)")
ES_down_int=$(printf "%.0f" "$(echo "${ES_down}*10" | bc -l)")
for i in $(seq ${ES_down_int} ${ES_up_int}); do
    shift_val=$(printf "%.1f" "$(echo "${i} / 10" | bc -l)")
    if [[ $shift_val == "0.0" ]]; then
        es_shifts+=("EMB")  # Replace emb0p0 with EMB
    elif [[ $shift_val == -* ]]; then
        # Remove minus and replace the dot with "p"
        formatted=${shift_val#-}
        formatted=${formatted/./p}
        es_shifts+=("embminus${formatted}")
    else
        formatted=${shift_val/./p}
        es_shifts+=("emb${formatted}")
    fi
done
echo "${es_shifts[@]}"

echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNELS_str} -${ERA}-${NTUPLETAG}                             #"
echo "##############################################################################################"


if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    CHANNELS=('mt')
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}

        python shapes/produce_shapes_tauid_es_extensions.py --channels ${CHANNEL} \
            --directory ${NTUPLES} \
            --${CHANNEL}-friend-directory ${XSEC_FRIENDS} \
            --era ${ERA} --num-processes 4 --num-threads 8 \
            --vs-jet-wp ${WP} \
            --vs-ele-wp ${WP_VSe} \
            --vs-mu-wp ${WP_VSmu} \
            --optimization-level 1 --skip-systematic-variations \
            --special-analysis "TauID_ES" \
            --control-plot-set ${VARIABLES} \
            --output-file ${shapes_output}  --xrootd  --validation-tag ${TAG} --binning-tag ${BIN_TAG} \
            --es-up ${ES_up} --es-down ${ES_down}
    done
fi


if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    CHANNELS=('mt')
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        
        echo "[INFO] Running on Condor"
        echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
        bash submit/submit_shape_production_tauid_es_extensions.sh ${ERA} ${CHANNEL} \
        "singlegraph" ${TAG} 0 ${NTUPLETAG} ${CONDOR_OUTPUT} "TauID_ES" ${WP} ${WP_VSe} ${WP_VSmu} ${ES_up} ${ES_down} ${BIN_TAG}
        echo "[INFO] Jobs submitted"
    done
fi