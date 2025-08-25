#!/bin/bash

ADDITIONAL_FRIENDS="xsec"
SELECTION_OPTION="CR"
SELECTION_OPTION_ESTIMATION="CR"
PLOTVERSION="all"
FF_TYPE="none"
VARIABLES=""
DEFAULT_VARIABLES_LIST=(
  pt_1 eta_1 phi_1 tau_decaymode_1 mt_1 iso_1 mass_1
  pt_2 eta_2 phi_2 tau_decaymode_2 mt_2 iso_2 mass_2
  jpt_1 jeta_1 jphi_1
  jpt_2 jeta_2 jphi_2
  bpt_1 beta_1 bphi_1 btag_value_1
  bpt_2 beta_2 bphi_2 btag_value_2
  pt_tt pt_tt pt_vis pt_dijet pt_ttjj
  mjj mt_tot m_vis
  met metphi mTdileptonMET metSumEt
  nbtag njets
  q_1 pzetamissvis jet_hemisphere
  deltaR_ditaupair deltaEta_ditaupair deltaPhi_ditaupair
)

options=(
  "c:channel:"
  "e:era:"
  "n:ntupletag:"
  "t:tag:"
  "m:mode:"
  "f:additional_friends:"
  "s:selection_option:"
  "S:selection_option_estimation:"
  "F:ff_type:"
  "p:plotversion:"
  "v:variables:"
)

short_opts=""
long_opts=""
for opt_pair in "${options[@]}"; do
  IFS=':' read -r short long <<< "$opt_pair"
  if [[ "${opt_pair}" == *: ]]; then
      short_opts+="${short}:"
      long_opts+="${long}:,"
  else
      short_opts+="${short}"
      long_opts+="${long},"
  fi
done
long_opts=${long_opts%,}

OPTS=$(getopt -o "${short_opts}" --long "${long_opts}" -n 'control_plots_ul.sh' -- "${@}")
if [ ${?} != 0 ]; then
  echo "Failed parsing options." >&2
  exit 1
fi
eval set -- "${OPTS}"

while true; do
  case "${1}" in
  -c | --channel)
    CHANNEL="${2}"; shift 2; ;;
  -e | --era)
    ERA="${2}"; shift 2; ;;
  -n | --ntupletag)
    NTUPLETAG="${2}"; shift 2; ;;
  -t | --tag)
    TAG="${2}"; shift 2; ;;
  -m | --mode)
    MODE="${2}"; shift 2; ;;
  -f | --additional_friends)
    ADDITIONAL_FRIENDS="${2}"; shift 2; ;;
  -s | --selection_option)
    SELECTION_OPTION="${2}"; shift 2; ;;
  -S | --selection_option_estimation)
    SELECTION_OPTION_ESTIMATION="${2}"; shift 2; ;;
  -F | --ff_type)
    FF_TYPE="${2}"; shift 2; ;;
  -p | --plotversion)
    PLOTVERSION="${2}"; shift 2; ;;
  -v | --variables)
    VARIABLES="${2}"; shift 2; ;;
  --)
    shift
    break
    ;;
  *)
    break
    ;;
  esac
done

if [ -z "${CHANNEL}" ] || [ -z "${ERA}" ] || [ -z "${NTUPLETAG}" ] || [ -z "${TAG}" ] || [ -z "${MODE}" ]; then
  echo "Missing required parameters. You must supply --channel, --era, --ntupletag, --tag, and --mode." >&2
  exit 1
fi

USED_VARIABLES=""
if [ -z "${VARIABLES}" ] || [ "${VARIABLES}" == "default" ]; then
  echo "INFO: Using the default variable list defined in the script."
  USED_VARIABLES=$(IFS=, ; echo "${DEFAULT_VARIABLES_LIST[*]}")
else
  echo "INFO: Using custom variable list provided via --variables."
  USED_VARIABLES="${VARIABLES}"
fi

# A safety check to ensure the final list is not empty
if [ -z "${USED_VARIABLES}" ]; then
    echo "ERROR: The final variable list to be plotted is empty. Exiting." >&2
    exit 1
fi

FRIENDS=""
if [ -n "${ADDITIONAL_FRIENDS}" ]; then
  echo "INFO: Constructing friend directory paths for: ${ADDITIONAL_FRIENDS}"
  for tag in ${ADDITIONAL_FRIENDS}; do
    path="/store/user/${USER}/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/${tag}/"
    FRIENDS+="${path} "
  done
  FRIENDS="${FRIENDS% }"
fi

# ---

export PYTHONPATH=${PYTHONPATH}:${PWD}/Dumbledraw
ulimit -s unlimited
export COLUMNS=$(tput cols)
source utils/setup_root.sh
source utils/setup_ul_samples.sh ${NTUPLETAG} ${ERA}

output_shapes="control_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shape_rootfile=${shapes_output}.root
# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"

if [[ $MODE == "XSEC" ]]; then

echo "##############################################################################################"
echo "#      Checking xsec friends directory                                                       #"
echo "##############################################################################################"

  echo "running xsec friends script"
  echo "XSEC_FRIENDS: ${XSEC_FRIENDS}"
  nice -n 19 python3 friends/build_friend_tree.py \
    --basepath ${KINGMAKER_BASEDIR_XROOTD} \
    --outputpath root://cmsdcache-kit-disk.gridka.de/${XSEC_FRIENDS} \
    --dataset-config "datasets/nanoAOD_v9/datasets.json" \
    --nthreads 20
fi

if [[ $MODE == "SHAPES" ]]; then
    echo "##############################################################################################"
    echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
    echo "##############################################################################################"

  # if the output folder does not exist, create it
  if [ ! -d "${shapes_output}" ]; then
    mkdir -p ${shapes_output}
  fi

  nice -n 19 python shapes/produce_shapes.py --channels ${CHANNEL} \
    --directory ${NTUPLES} \
    --${CHANNEL}-friend-directory ${XSEC_FRIENDS} ${FRIENDS} \
    --era ${ERA} --num-processes 30 --num-threads 60 \
    --optimization-level 1 --control-plots \
    --control-plot-set ${USED_VARIABLES} --skip-systematic-variations \
    --output-file ${shapes_output} \
    --xrootd --validation-tag ${TAG} \
    --vs-jet-wp "Tight" --vs-ele-wp "VVLoose" --apply-tauid \
    --selection-option ${SELECTION_OPTION} --ff-type ${FF_TYPE}

    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"
    if [[ $CHANNEL == "mm" ]]; then
        python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-qcd
    else
        python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-qcd
    fi
fi

if [[ $MODE == "PLOT" ]]; then
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"

  BASE_COMMAND="python3 plotting/plot_shapes_control.py \
                    -l \
                    --era Run${ERA} \
                    --input ${shapes_output}.root \
                    --variables ${USED_VARIABLES} \
                    --channels ${CHANNEL} \
                    --tag ${TAG} \
                    --selection-option ${SELECTION_OPTION}"

  if [[ ${PLOTVERSION} == "all" || ${PLOTVERSION} == "emb+ff" ]]; then
    ${BASE_COMMAND} --embedding --fake-factor
  elif [[ ${PLOTVERSION} == "all" || ${PLOTVERSION} == "emb+classic" ]]; then
    ${BASE_COMMAND} --embedding
  elif [[ ${PLOTVERSION} == "all" || ${PLOTVERSION} == "classic+ff" ]]; then
    ${BASE_COMMAND} --fake-factor
  elif [[ ${PLOTVERSION} == "all" || ${PLOTVERSION} == "classic+classic" ]]; then
    ${BASE_COMMAND}
  fi
fi
