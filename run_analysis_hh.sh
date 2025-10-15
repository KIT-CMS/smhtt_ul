set -euo pipefail

TAG=$1
NNSCORE_FRIENDS=$2
USE_SYSTEMATICS=${3:-no}

export USE_SYSTEMATICS

echo "[INFO] Using tag: $TAG"
echo "[INFO] Using NN score friends: $NNSCORE_FRIENDS"
echo "[INFO] Using systematic uncertainties (yes, no): $USE_SYSTEMATICS"

ERA=2018
NTUPLETAG=all-v4

# analysis shapes
bash run_analysis.sh et $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS LOCAL
bash run_analysis.sh mt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS LOCAL
bash run_analysis.sh tt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS LOCAL

# sync shapes
bash run_analysis.sh et $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS SYNC
bash run_analysis.sh mt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS SYNC
bash run_analysis.sh tt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS SYNC

# plot sync shapes
bash run_analysis.sh et $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS PLOT_ANALYSIS_SHAPES
bash run_analysis.sh mt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS PLOT_ANALYSIS_SHAPES
bash run_analysis.sh tt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS PLOT_ANALYSIS_SHAPES

# produce datacards (channel is ignored -> run with tt will produce for all channels)
bash run_analysis.sh tt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS DATACARD-PY-SYST

# fit (channel is ignored -> run with tt will produce for all channels)
bash run_analysis.sh tt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS FIT-HH