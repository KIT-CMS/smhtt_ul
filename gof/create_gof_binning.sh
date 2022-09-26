export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
VARIABLES=$4

ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA
source utils/setup_root.sh

python3 gof/build_binning.py --channel $CHANNEL \
    --directory $NTUPLES \
    --era $ERA --variables ${VARIABLES} --${CHANNEL}-friend-directory $FRIENDS \
    --output-folder "config/gof_binning"