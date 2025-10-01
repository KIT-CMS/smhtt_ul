set -euo pipefail

TAG=$1
NNSCORE_FRIENDS=$2

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
bash run_analysis.sh tt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS DATACARD-PY

# fit (channel is ignored -> run with tt will produce for all channels)
bash run_analysis.sh tt $ERA $NTUPLETAG $TAG $NNSCORE_FRIENDS FIT-HH