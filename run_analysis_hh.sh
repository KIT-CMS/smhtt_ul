set -euo pipefail

TAG=Simon_ML_v12_04_05_26_ff_v2
# NNSCORE_FRIENDS=ML_Friends_FF_30_04_26
USE_SYSTEMATICS=${4:-no}

export USE_SYSTEMATICS

echo "[INFO] Using tag: $TAG"
# echo "[INFO] Using NN score friends: $NNSCORE_FRIENDS"
echo "[INFO] Using systematic uncertainties (yes, no): $USE_SYSTEMATICS"

ERA=2018
NTUPLETAG=sda_v12_16_04_26_v2

#XSEC
# bash run_analysis.sh tt $ERA $NTUPLETAG $TAG XSEC

for CH in mt tt et; do
    #CTRL
    # bash run_analysis.sh $CH $ERA $NTUPLETAG $TAG CTRL
    # bash run_analysis.sh $CH $ERA $NTUPLETAG $TAG CONTROL_SDA


    # # analysis shapes
    # bash run_analysis.sh $CH $ERA $NTUPLETAG $TAG LOCAL

    # # sync shapes
    # bash run_analysis.sh $CH $ERA $NTUPLETAG $TAG SYNC
    # plot sync shap
    bash run_analysis.sh $CH $ERA $NTUPLETAG $TAG PLOT_ANALYSIS_SHAPES
done


# produce datacards (channel is ignored -> run with tt will produce for all channels)
# bash run_analysis.sh tt $ERA $NTUPLETAG $TAG DATACARD-PY-SYST

# fit (channel is ignored -> run with tt will produce for all channels)
# bash run_analysis.sh tt $ERA $NTUPLETAG $TAG FIT-HH