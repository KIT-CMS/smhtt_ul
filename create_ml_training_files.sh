export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3

ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA
source utils/setup_root.sh
python trainings/produce_training_configs.py --channels et,mt \
    --directory $NTUPLES \
    --et-friend-directory $XSEC_FRIENDS $FF_FRIENDS \
    --mt-friend-directory $XSEC_FRIENDS $FF_FRIENDS \
    --eras $ERA --trainings-config trainings/default_training_sm.yaml \
    --output-folder /work/sbrommer/smhtt_ul/training_configs/v6
