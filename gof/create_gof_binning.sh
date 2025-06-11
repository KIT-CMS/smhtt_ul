export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=${1}
ERA=${2}
NTUPLETAG=${3}
VARIABLES=${4}
TAG=${5}
WP_VSjet=${6}
WP_VSe=${7}
WP_VSmu=${8}

ulimit -s unlimited
source utils/setup_ul_samples.sh ${NTUPLETAG} ${ERA}
source utils/setup_root.sh

python3 gof/build_binning.py --channel ${CHANNEL} \
    --directory ${NTUPLES} --tag ${TAG}\
    --wp-vsjet ${WP_VSjet} --wp-vse ${WP_VSe} --wp-vsmu ${WP_VSmu} \
    --era ${ERA} --variables ${VARIABLES} --${CHANNEL}-friend-directory ${FRIENDS} \
    --output-folder "config/gof_binning"