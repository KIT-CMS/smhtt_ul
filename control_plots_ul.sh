#!/bin/bash

ADDITIONAL_FRIENDS="xsec"
ADDITIONAL_MULTIFRIENDS=""
SELECTION_OPTION="CR"
SELECTION_OPTION_ESTIMATION="CR"
PLOTVERSION="all"
FF_TYPE="none"
VARIABLES=""
NANOAODVERSION="v9"
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
  deltaR_jj deltaR_1j1 deltaR_1j2 deltaR_2j1 deltaR_2j2 deltaR_12j1 deltaR_12j2 deltaR_12jj
  deltaEta_jj deltaEta_1j1 deltaEta_1j2 deltaEta_2j1 deltaEta_2j2 deltaEta_12j1 deltaEta_12j2 deltaEta_12jj
  deltaPhi_jj deltaPhi_1j1 deltaPhi_1j2 deltaPhi_2j1 deltaPhi_2j2 deltaPhi_12j1 deltaPhi_12j2 deltaPhi_12jj
  eta_fastmtt m_fastmtt phi_fastmtt pt_fastmtt
)

options=(
  "c:channel:"
  "e:era:"
  "n:ntupletag:"
  "t:tag:"
  "m:mode:"
  "f:additional_friends:"
  "M:additional_multifriends:"
  "s:selection_option:"
  "S:selection_option_estimation:"
  "F:ff_type:"
  "p:plotversion:"
  "v:variables:"
  "N:nanoaodversion:"
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
  -M | --additional_multifriends)
    ADDITIONAL_MULTIFRIENDS="${2}"; shift 2; ;;
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
  -N | --nanoaodversion)
    NANOAODVERSION="${2}"; shift 2; ;;
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

MULTIFRIENDS=""
if [ -n "${ADDITIONAL_MULTIFRIENDS}" ]; then
  echo "INFO: Constructing friend directory paths for: ${ADDITIONAL_MULTIFRIENDS}"
  for tag in ${ADDITIONAL_MULTIFRIENDS}; do
    path="/store/user/${USER}/CROWN/ntuples/${NTUPLETAG}/CROWNMultiFriends/${tag}/"
    MULTIFRIENDS+="${path} "
  done
  MULTIFRIENDS="${MULTIFRIENDS% }"
fi

# ---

elementIn() {
  local element
  for element in "${@:2}"; do [[ "$element" == "$1" ]] && return 0; done
  return 1
}

ask_for_confirmation() {
    local question="$1"
    local answer
    read -p "$question [y/N] " answer
    case "${answer,,}" in
        y|yes) return 0 ;;
        *) return 1 ;;
    esac
}

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
echo "KINGMAKER_BASEDIR: ${KINGMAKER_BASEDIR}"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"

if [[ ${MODE} == "XSEC" ]]; then

  echo "##############################################################################################"
  echo "#      Checking xsec friends directory                                                       #"
  echo "##############################################################################################"

  echo "running xsec friends script"
  echo "XSEC_FRIENDS: ${XSEC_FRIENDS}"
  nice -n 19 python3 friends/build_friend_tree.py \
    --basepath ${KINGMAKER_BASEDIR_XROOTD} \
    --outputpath root://cmsdcache-kit-disk.gridka.de/${XSEC_FRIENDS} \
    --dataset-config "datasets/nanoAOD_${NANOAODVERSION}/datasets.json" \
    --nthreads 20
fi

if [[ ${MODE} == "SHAPES" ]]; then
  echo "##############################################################################################"
  echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
  echo "##############################################################################################"

  # if the output folder does not exist, create it
  if [ ! -d "${shapes_output}" ]; then
    mkdir -p ${shapes_output}
  fi

  GRAPH_FILENAME=${CHANNEL}_${ERA}_${NTUPLETAG}_${TAG}.pkl

  BASE_COMMAND=(
    nice -n 19 python shapes/produce_shapes.py
    --channels ${CHANNEL}
    --directory ${NTUPLES}
    --${CHANNEL}-friend-directory ${XSEC_FRIENDS} ${FRIENDS} ${MULTIFRIENDS}
    --era ${ERA}
    --num-processes 30
    --num-threads 60
    --optimization-level 2
    --control-plots
    --control-plot-set ${USED_VARIABLES}
    --output-file ${shapes_output}
    --xrootd
    --validation-tag ${TAG}
    --vs-jet-wp "Tight"
    --vs-ele-wp "VVLoose"
    --apply-tauid
    --selection-option ${SELECTION_OPTION}
    --ff-type ${FF_TYPE}
    # --skip-systematic-variations
    # the following two options should be mutually exclusive
    # --- 1 ---
    --only-create-graphs
    --graph-filename ${GRAPH_FILENAME}
    # --- 2 ---
    # --collect-config-only
    # --config-output-file ${CHANNEL}_${ERA}_${NTUPLETAG}_${TAG}.yaml
  )

  "${BASE_COMMAND[@]}"

  if elementIn "--only-create-graphs" "${BASE_COMMAND[@]}"; then
    
    echo "Graph splitting enabled."
    bash split_graph_processing/run_split_graph_processing.sh ${GRAPH_FILENAME} ${shape_rootfile}
    if ask_for_confirmation "Graph processing finished. Clean up the temporary directories? ('tmp' and 'condor_jobs')?"; then
        rm -rfv split_graph_processing/tmp
        rm -rfv split_graph_processing/condor_jobs
    else
        echo "Cleanup skipped"
    fi
  fi

  echo "##############################################################################################"
  echo "#      Additional estimations                                      #"
  echo "##############################################################################################"
  if [[ ${CHANNEL} == "mm" ]]; then
    nice -n 19 python shapes/do_estimations.py -e ${ERA} -i ${shapes_output}.root \
      --do-qcd
  else
    nice -n 19 python shapes/do_estimations.py -e ${ERA} -i ${shapes_output}.root \
      --do-emb-tt --do-qcd --do-ff --selection-option ${SELECTION_OPTION_ESTIMATION}
  fi
fi

if [[ ${MODE} == "PLOT" ]]; then
  echo "##############################################################################################"
  echo "#     plotting                                      #"
  echo "##############################################################################################"

  BASE_COMMAND=(
    python3 plotting/plot_shapes_control.py
    -l
    --era Run${ERA}
    --input "${shapes_output}.root"
    --variables "${USED_VARIABLES}"
    --channels "${CHANNEL}"
    --tag "${TAG}"
    --selection-option "${SELECTION_OPTION}"
  )

  if [[ ${PLOTVERSION} == "all" || ${PLOTVERSION} == "emb+ff" ]]; then
    "${BASE_COMMAND[@]}" --embedding --fake-factor
  fi
  if [[ ${PLOTVERSION} == "all" || ${PLOTVERSION} == "emb+classic" ]]; then
    "${BASE_COMMAND[@]}" --embedding
  fi
  if [[ ${PLOTVERSION} == "all" || ${PLOTVERSION} == "classic+ff" ]]; then
    "${BASE_COMMAND[@]}" --fake-factor
  fi
  if [[ ${PLOTVERSION} == "all" || ${PLOTVERSION} == "classic+classic" ]]; then
    "${BASE_COMMAND[@]}"
  fi
fi
