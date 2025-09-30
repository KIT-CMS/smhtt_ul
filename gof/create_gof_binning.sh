export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
VARIABLES=$4
ADDITIONAL_FRIENDS=$5
TAG=$6

ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA
source utils/setup_root.sh


FRIENDS=""
if [ -n "${ADDITIONAL_FRIENDS}" ]; then
  echo "INFO: Constructing friend directory paths for: ${ADDITIONAL_FRIENDS}"
  for tag in ${ADDITIONAL_FRIENDS}; do
    path="/store/user/${USER}/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/${tag}/"
    FRIENDS+="${path} "
  done
  FRIENDS="${FRIENDS% }"
fi


python3 gof/build_binning.py --channel $CHANNEL \
    --directory $NTUPLES \
    --era $ERA --variables ${VARIABLES} --${CHANNEL}-friend-directory ${XSEC_FRIENDS} ${FRIENDS} \
    --output-folder "config/gof_binning"
