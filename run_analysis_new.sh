export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL="mt"
ERA="2018"
NTUPLETAG="ff_and_cr_2018UL_mt__2026-03-27__v2"
# TAG="nn_output_groupedDNN__FF_adjusted__2026-04-30__v1"
# TAG="nn_output_groupedDNN__2026-04-30__v1"
# TAG="nn_output_groupedDNN__FF_adjusted__2026-05-07__1sigmatest__v1"
# TAG="test_new_nominal_1sigma_ff__v1"
# TAG="test_old_nominal_1sigma__ff__v1"

# TAG="test_old_nominal_1sigma__ff__half_fix__v1"
# TAG="nn_output_CENNT_ml_ff_fixed_ff_unct__adjusted_syst_test"
# TAG="nn_output_CENNT__2026-05-25__ml_ff_fixed_ff_unct__adjusted_syst_test"

# TAG="nn_output_SANNT__2026-05-29__ml_ff_fixed_ff_unct__adjusted_syst_test"

# ---

# TAG="nn_output_SANNT__2026-05-31__N2pmp100___ml_ff_fixed_ff_unct__adjusted_syst_test"

FORCE_REPROCESSING=1

MODE=$1
TAG=$2

POSTFIX="-ML"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Datacard Setup
datacard_output="datacards/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}"

output_shapes="analysis_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}

shapes_output_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_rootfile=${shapes_output}.root
shapes_rootfile_synced=${shapes_output_synced}_synced.root




# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
fi

echo "###################################"
echo "#           Mode ${MODE}          #"
echo "###################################"

if [[ $MODE == "SYNC" ]]; then
    # source utils/setup_root.sh
    # python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-ff --do-qcd

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python shapes/convert_to_synced_shapes_without_emb_es_id.py -e $ERA \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        -n 1

    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}*.root

    exit 0
fi

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw.sh
    # inputfile
    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"

    ${CMSSW_BASE}/bin/el9_amd64_gcc12/MorphingSMRun2Legacy \
        --base_path=$PWD \
        --input_folder_mt=$shapes_output_synced \
        --real_data=false \
        --classic_bbb=false \
        --binomial_bbb=false \
        --jetfakes=1 \
        --embedding=1 \
        --postfix="-ML" \
        --channel=${CHANNEL} \
        --auto_rebin=true \
        --stxs_signals="stxs_stage0_syst" \
        --categories="stxs_stage0_syst" \
        --era=${ERA} \
        --output=output/$datacard_output \
        --use_automc=true \
        --train_ff=1 \
        --train_stage0=1\
        --train_emb=1
    THIS_PWD=${PWD}
    echo $THIS_PWD
    cd output/$datacard_output/$CHANNEL
    for FILE in */*.txt; do
        sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
    done
    cd $THIS_PWD

    echo "[INFO] Create Workspace for datacard"
    # combineTool.py -M T2W -i output/$datacard_output/htt_$channel_*/ -o workspace.root --parallel 4 -m 125
    combineTool.py -M T2W -o workspace.root -i output/$datacard_output/$CHANNEL/125 --parallel 4 -m 125 \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH_htt.?$:r_ggH[1,-5,5]"' \
        --PO '"map=^.*/qqH_htt.?$:r_qqH[1,-5,5]"'
        # --PO '"map=^.*/WH_htt.?$:r_VH[1,-5,7]"' \
       	# --PO '"map=^.*/ZH_htt.?$:r_VH[1,-5,7]"'
        # --PO '"map=^.*/ggZH_had_htt.?$:r_ggH[1,-5,5]"' \
        # --PO '"map=^.*/WH_had_htt.?$:r_qqH[1,-5,5]"' \
        # --PO '"map=^.*/ZH_had_htt.?$:r_qqH[1,-5,5]"' \
        # --PO '"map=^.*/ggZH_lep_htt.?$:r_VH[1,-5,7]"'
    exit 0
fi

if [[ $MODE == "FIT" ]]; then
    source utils/setup_cmssw.sh
        combineTool.py \
        -M MultiDimFit \
        -m 125 \
        -d output/$datacard_output/$CHANNEL/125/workspace.root \
        --algo singles \
        --robustFit 1 \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0 \
        -n $ERA -v1 \
        --parallel 1 --there
    for RESDIR in output/$datacard_output/$CHANNEL/125; do
        echo "[INFO] Printing fit result for category $(basename $RESDIR)"
        FITFILE=${RESDIR}/higgsCombine${ERA}.MultiDimFit.mH125.root
        python datacards/print_fitresult.py ${FITFILE}
    done
    exit 0
fi

if [[ $MODE == "FIT-SPLIT" ]]; then
    # source utils/setup_cmssw.sh
    ./fitting/fit_split_by_unc_cons.sh $datacard_output $ERA $CHANNEL 0 "inclusive"
    ./fitting/fit_split_by_unc_cons.sh $datacard_output $ERA $CHANNEL 0 "stage0"
    exit 0
fi

if [[ $MODE == "POSTFIT" ]]; then
    source utils/setup_cmssw.sh
    RESDIR=output/$datacard_output/$CHANNEL/125
    WORKSPACE=${RESDIR}/workspace.root
    echo "[INFO] Printing fit result for category $(basename $RESDIR)"
    FILE=${RESDIR}/postfitshape.root
    FITFILE=${RESDIR}/fitDiagnostics.${ERA}.root
    combine \
        -n .$ERA \
        -M FitDiagnostics \
        -m 125 -d $WORKSPACE \
        --robustFit 1 -v1 \
        --robustHesse 1 \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0
    mv fitDiagnostics.2018.root $FITFILE
    echo "[INFO] Building Prefit/Postfit shapes"
    PostFitShapesFromWorkspace -w ${WORKSPACE} \
        -m 125 -d ${RESDIR}/combined.txt.cmb \
        -o ${FILE} \
        -f ${FITFILE}:fit_s --postfit
    FILE=${RESDIR}/prefitshape.root
    PostFitShapesFromWorkspace -w ${WORKSPACE} \
        -m 125 -d ${RESDIR}/combined.txt.cmb \
        -o ${FILE}
    exit 0
fi

if [[ $MODE == "PLOT-POSTFIT" ]]; then
    source utils/setup_root.sh
    RESDIR=output/$datacard_output/$CHANNEL/125
    WORKSPACE=${RESDIR}/workspace.root
    CATEGORIES="stxs_stage0"
    PLOTDIR=output/plots/${ERA}-${TAG}-${CHANNEL}_shape-plots
    FILE=${RESDIR}/postfitshape.root
    [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
    echo "[INFO] Using postfitshapes from $FILE"
    # python3 plotting/plot_shapes.py -i $FILE -o $PLOTDIR \
    #         -c ${channel} -e $ERA --categories $CATEGORIES \
    #         --fake-factor --embedding --normalize-by-bin-width \
    #         -l --train-ff True --train-emb True
        # CATEGORIES="stxs_stage0"

    python3 plotting/plot_shapes_combined.py -i $FILE -o $PLOTDIR -c ${CHANNEL} -e $ERA  --categories $CATEGORIES --fake-factor --embedding -l --train-ff True --train-emb True --combine-signals
    FILE=${RESDIR}/prefitshape.root
    python3 plotting/plot_shapes_combined.py -i $FILE -o $PLOTDIR -c ${CHANNEL} -e $ERA  --categories $CATEGORIES --fake-factor --embedding -l --train-ff True --train-emb True --combine-signals
    exit 0
fi

if [[ $MODE == "IMPACTS" ]]; then
    source utils/setup_cmssw.sh
    combineTool.py -M T2W -o workspace.root -i output/$datacard_output/$CHANNEL/125 --parallel 4 -m 125 \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH_htt.?$:r[1,-5,5]"' \
        --PO '"map=^.*/qqH_htt.?$:r[1,-5,5]"'
    WORKSPACE=output/$datacard_output/$CHANNEL/125/workspace.root
    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --doInitialFit --robustFit 1 \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --robustFit 1 --doFits \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 -o sm_${ERA}_${CHANNEL}_impacts.json
    plotImpacts.py -i sm_${ERA}_${CHANNEL}_impacts.json -o sm_${ERA}_${CHANNEL}_impacts
    # cleanup the fit files
    rm higgsCombine*.root
    mv sm_${ERA}_${CHANNEL}_impacts.pdf output/$datacard_output/
    mv sm_${ERA}_${CHANNEL}_impacts.json output/$datacard_output/
    exit 0
fi
