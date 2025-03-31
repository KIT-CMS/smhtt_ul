#!/bin/bash

FF_FRIENDS_TAG=""
SELECTION_OPTION="CR"
SELECTION_OPTION_ESTIMATION="CR"
PLOTVERSION="all"
FF_TYPE="fake_factor"

# Parse arguments using getopt.
OPTS=$(getopt -o c:e:n:t:m:fff:so:soe:fft:p: --long channel:,era:,ntupletag:,tag:,mode:,ff_friends_tag:,selection_option:,selection_option_estimation:,ff_type:,plotversion: -n 'control_plots_ul.sh' -- "${@}")
if [ ${?} != 0 ]; then
  echo "Failed parsing options." >&2
  exit 1
fi
eval set -- "${OPTS}"

while true; do
  case "${1}" in
  -c | --channel)
    CHANNEL="${2}"
    shift 2
    ;;
  -e | --era)
    ERA="${2}"
    shift 2
    ;;
  -n | --ntupletag)
    NTUPLETAG="${2}"
    shift 2
    ;;
  -t | --tag)
    TAG="${2}"
    shift 2
    ;;
  -m | --mode)
    MODE="${2}"
    shift 2
    ;;
  -fff | --ff_friends_tag)
    FF_FRIENDS_TAG="${2}"
    shift 2
    ;;
  -so | --selection_option)
    SELECTION_OPTION="${2}"
    shift 2
    ;;
  -soe | --selection_option_estimation)
    SELECTION_OPTION_ESTIMATION="${2}"
    shift 2
    ;;
  -fft | --ff_type)
    FF_TYPE="${2}"
    shift 2
    ;;
  -p | --plotversion)
    PLOTVERSION="${2}"
    shift 2
    ;;
  --)
    shift
    break
    ;;
  *)
    break
    ;;
  esac
done

# Crash if any required parameters are missing.
if [ -z "${CHANNEL}" ] || [ -z "${ERA}" ] || [ -z "${NTUPLETAG}" ] || [ -z "${TAG}" ] || [ -z "${MODE}" ]; then
  echo "Missing required parameters. You must supply --channel, --era, --ntupletag, --tag, and --mode." >&2
  exit 1
fi

export COLUMNS=$(tput cols)
export PYTHONPATH=${PYTHONPATH}:${PWD}/Dumbledraw
source utils/setup_root.sh
ulimit -s unlimited
source utils/setup_root.sh
source utils/setup_ul_samples.sh ${NTUPLETAG} ${ERA}

# VARIABLES="phi_2,phi_1,q_1,mjj,iso_2,iso_1,mjj,pt_dijet,pt_tt,pt_vis,mt_2,mt_1,tau_decaymode_1,tau_decaymode_2,nbtag,njets,jphi_2,jphi_1,jeta_2,jeta_1,jpt_2,jpt_1,eta_1,eta_2,pt_2,pt_1,mt_tot,met,metphi,m_vis,deltaR_ditaupair,pzetamissvis"
variable_list=(
  phi_2
  phi_1
  q_1
  mjj
  iso_2
  iso_1
  mjj
  pt_dijet
  pt_tt
  pt_vis
  mt_2
  mt_1
  tau_decaymode_1
  tau_decaymode_2
  nbtag
  njets
  jphi_2
  jphi_1
  jeta_2
  jeta_1
  jpt_2
  jpt_1
  eta_1
  eta_2
  pt_2
  pt_1
  mt_tot
  met
  metphi
  m_vis
  deltaR_ditaupair
  pzetamissvis
  mass_2
  bpt_1
  bpt_2
  mTdileptonMET
  pt_tt
  pt_ttjj
)
VARIABLES=$(IFS=, ; echo "${variable_list[*]}")

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
  nice -n 19 python3 friends/build_friend_tree.py --basepath ${KINGMAKER_BASEDIR_XROOTD} --outputpath root://cmsdcache-kit-disk.gridka.de/${XSEC_FRIENDS} --nthreads 20
fi

if [[ ${MODE} == "SHAPES" ]]; then
  echo "##############################################################################################"
  echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
  echo "##############################################################################################"

  # if the output folder does not exist, create it
  if [ ! -d "${shapes_output}" ]; then
    mkdir -p ${shapes_output}
  fi

  if [[ -n "${FF_FRIENDS_TAG}" ]]; then
    FF_FRIENDS="/store/user/${USER}/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/${FF_FRIENDS_TAG}/"
  fi

  nice -n 19 python shapes/produce_shapes.py --channels ${CHANNEL} \
    --directory ${NTUPLES} \
    --${CHANNEL}-friend-directory ${XSEC_FRIENDS} ${FF_FRIENDS} \
    --era ${ERA} --num-processes 30 --num-threads 60 \
    --optimization-level 1 --control-plots \
    --control-plot-set ${VARIABLES} --skip-systematic-variations \
    --output-file ${shapes_output} \
    --xrootd --validation-tag ${TAG} \
    --vs-jet-wp "Tight" --vs-ele-wp "VVLoose" --apply-tauid \
    --selection-option ${SELECTION_OPTION} --ff-type ${FF_TYPE}

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

  BASE_COMMAND="python3 plotting/plot_shapes_control.py \
                    -l \
                    --era Run${ERA} \
                    --input ${shapes_output}.root \
                    --variables ${VARIABLES} \
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
