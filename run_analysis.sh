export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
NNSCORE_FRIENDS=$5
MODE=$6

POSTFIX="-ML"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Datacard Setup
datacard_output="datacards/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}"

output_shapes="tauid_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_rootfile=${shapes_output}.root
shapes_rootfile_synced=${shapes_output_synced}_synced.root

# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
fi

# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "FRIENDS: ${FRIENDS}"
echo "NNSCORE_FRIENDS: ${NNSCORE_FRIENDS}"
echo "###################################"
echo "#           Mode ${MODE}          #"
echo "###################################"

if [[ $MODE == "COPY" ]]; then
    source utils/setup_root.sh

    # if the xsec friends directory does not exist, create it
    if [ ! -d "$BASEDIR/$ERA" ]; then
        mkdir -p $BASEDIR/$ERA
    fi
    if [ "$(ls -A $BASEDIR/$ERA)" ]; then
        echo "Ntuples already copied to ceph"
    else
        echo "Copying ntuples to ceph"
        rsync -avhPl $KINGMAKER_BASEDIR$ERA/ $BASEDIR$ERA/
    fi
    exit 0
elif [[ $MODE == "COPY_XROOTD" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Copying ntuples to ceph via xrootd"
    echo "xrdcp -r $KINGMAKER_BASEDIR_XROOTD$ERA/ $BASEDIR$ERA/"
    if [ ! -d "$BASEDIR/$ERA" ]; then
        mkdir -p $BASEDIR/$ERA
    fi
    xrdcp -r $KINGMAKER_BASEDIR_XROOTD$ERA $BASEDIR
    exit 0
fi

if [[ $MODE == "XSEC" ]]; then
    source utils/setup_root.sh
    python3 friends/build_friend_tree.py --basepath $BASEDIR --outputpath $XSEC_FRIENDS --nthreads 20
    # if the xsec friends directory does not exist, create it
    if [ ! -d "$XSEC_FRIENDS" ]; then
        mkdir -p $XSEC_FRIENDS
    fi
    # if th xsec friends dir is empty, run the xsec friends script
    if [ "$(ls -A $XSEC_FRIENDS)" ]; then
        echo "xsec friends dir already exists"
    else
        echo "xsec friends dir is empty"
        echo "running xsec friends script"
        python3 friends/build_friend_tree.py --basepath $BASEDIR --outputpath $XSEC_FRIENDS --nthreads 20
    fi
    exit 0
fi

if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $FRIENDS $NNSCORE_FRIENDS  \
        --era $ERA --num-processes 4 --num-threads 6 \
        --optimization-level 1 --skip-systematic-variations \
        --output-file $shapes_output

    python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-ff --do-qcd

    # now plot the shapes by looping over the categories
    for category in "ggh" "qqh" "ztt" "tt" "ff" "misc" "xxh"; do
        python3 plotting/plot_ml_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --channel ${CHANNEL} --embedding --fake-factor --category ${category} --output-dir output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/controlplots --normalize-by-bin-width
    done
fi

if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $FRIENDS $NNSCORE_FRIENDS \
        --era $ERA --num-processes 4 --num-threads 12 \
        --optimization-level 1 \
        --output-file $shapes_output
fi

if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_ul.sh $ERA $CHANNEL \
        "singlegraph" $TAG 0 $NTUPLETAG $CONDOR_OUTPUT 0 $NNSCORE_FRIENDS
    echo "[INFO] Jobs submitted"
fi
if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-ff --do-qcd

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python shapes/convert_to_synced_shapes.py -e $ERA \
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

    ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
        --base_path=$PWD \
        --input_folder_mt=$shapes_output_synced \
        --input_folder_tt=$shapes_output_synced \
        --input_folder_et=$shapes_output_synced \
        --input_folder_em=$shapes_output_synced \
        --real_data=false \
        --classic_bbb=false \
        --binomial_bbb=false \
        --jetfakes=1 \
        --embedding=1 \
        --postfix="-ML" \
        --channel=${CHANNEL} \
        --auto_rebin=true \
        --stxs_signals="stxs_stage0" \
        --categories="stxs_stage0" \
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

if [[ $MODE == "DATACARD-MC" ]]; then
    source utils/setup_cmssw.sh
    # inputfile
    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"

    ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
        --base_path=$PWD \
        --input_folder_mt=$shapes_output_synced \
        --input_folder_tt=$shapes_output_synced \
        --input_folder_et=$shapes_output_synced \
        --input_folder_em=$shapes_output_synced \
        --real_data=false \
        --classic_bbb=false \
        --binomial_bbb=false \
        --jetfakes=1 \
        --embedding=0 \
        --postfix="-ML" \
        --channel=${CHANNEL} \
        --auto_rebin=true \
        --stxs_signals="stxs_stage0" \
        --categories="stxs_stage0" \
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
    # combineTool.py -M T2W -i output/$datacard_output/htt_$CHANNEL_*/ -o workspace.root --parallel 4 -m 125
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

if [[ $MODE == "FIT-SPLIT-MC" ]]; then
    # source utils/setup_cmssw.sh
    ./fitting/fit_split_by_unc_cons.sh $datacard_output $ERA $CHANNEL 1 "inclusive"
    ./fitting/fit_split_by_unc_cons.sh $datacard_output $ERA $CHANNEL 1 "stage0"
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

if [[ $MODE == "PLOT-POSTFIT-MC" ]]; then
    source utils/setup_root.sh
    RESDIR=output/$datacard_output/$CHANNEL/125
    WORKSPACE=${RESDIR}/workspace.root
    CATEGORIES="stxs_stage0"
    PLOTDIR=output/plots/${ERA}-${TAG}-${CHANNEL}_shape-plots
    FILE=${RESDIR}/postfitshape.root
    [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
    echo "[INFO] Using postfitshapes from $FILE"
    python3 plotting/plot_shapes_combined.py -i $FILE -o $PLOTDIR -c ${CHANNEL} -e $ERA  --categories $CATEGORIES --fake-factor -l --train-ff True --train-emb True --combine-signals
    FILE=${RESDIR}/prefitshape.root
    python3 plotting/plot_shapes_combined.py -i $FILE -o $PLOTDIR -c ${CHANNEL} -e $ERA  --categories $CATEGORIES --fake-factor -l --train-ff True --train-emb True --combine-signals
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

if [[ $MODE == "IMPACTS-MC" ]]; then
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

    combineTool.py -M Impacts -d $WORKSPACE -m 125 -o sm_mc_${ERA}_${CHANNEL}_impacts.json
    plotImpacts.py -i sm_mc_${ERA}_${CHANNEL}_impacts.json -o sm_mc_${ERA}_${CHANNEL}_impacts
    # cleanup the fit files
    rm higgsCombine*.root
    mv sm_mc_${ERA}_${CHANNEL}_impacts.pdf output/$datacard_output/
    mv sm_mc_${ERA}_${CHANNEL}_impacts.json output/$datacard_output/
    exit 0
fi

if [[ $MODE == "DATACARD-ZFIT" ]]; then
    source utils/setup_cmssw.sh
    # inputfile
    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"

    ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
        --base_path=$PWD \
        --input_folder_mt=$shapes_output_synced \
        --input_folder_tt=$shapes_output_synced \
        --input_folder_et=$shapes_output_synced \
        --input_folder_em=$shapes_output_synced \
        --real_data=true \
        --classic_bbb=false \
        --binomial_bbb=false \
        --jetfakes=1 \
        --embedding=1 \
        --postfix="-ML" \
        --channel=${CHANNEL} \
        --auto_rebin=true \
        --stxs_signals="stxs_stage0" \
        --categories="stxs_stage0" \
        --era=${ERA} \
        --output=output/${datacard_output} \
        --use_automc=true \
        --train_ff=1 \
        --train_stage0=1\
        --train_emb=1 \
        --fit_ztt=true
    THIS_PWD=${PWD}
    echo $THIS_PWD
    cd output/$datacard_output/$CHANNEL
    for FILE in */*.txt; do
        sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
    done
    cd $THIS_PWD

    echo "[INFO] Create Workspace for datacard"
    combineTool.py -M T2W -o workspace.root -i output/$datacard_output/$CHANNEL/125 --parallel 4 -m 125

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

    WORKSPACE=output/$datacard_output/$CHANNEL/125/workspace.root
    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --doInitialFit --robustFit 1 \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --robustFit 1 --doFits \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 -o zfit_${ERA}_${CHANNEL}.json
    plotImpacts.py -i zfit_${ERA}_${CHANNEL}.json -o zfit_${ERA}_${CHANNEL}_impacts
    # cleanup the fit files
    rm higgsCombine*.root
    mv zfit_${ERA}_${CHANNEL}_impacts.pdf output/$datacard_output/
    mv zfit_${ERA}_${CHANNEL}.json output/$datacard_output/
    exit 0
fi

if [[ $MODE == "DATACARD-ZFIT-MC" ]]; then
    source utils/setup_cmssw.sh
    # inputfile
    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"

    ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
        --base_path=$PWD \
        --input_folder_mt=$shapes_output_synced \
        --input_folder_tt=$shapes_output_synced \
        --input_folder_et=$shapes_output_synced \
        --input_folder_em=$shapes_output_synced \
        --real_data=true \
        --classic_bbb=false \
        --binomial_bbb=false \
        --jetfakes=1 \
        --embedding=0 \
        --postfix="-ML" \
        --channel=${CHANNEL} \
        --auto_rebin=true \
        --stxs_signals="stxs_stage0" \
        --categories="stxs_stage0" \
        --era=${ERA} \
        --output=output/${datacard_output} \
        --use_automc=true \
        --train_ff=1 \
        --train_stage0=1\
        --train_emb=1 \
        --fit_ztt=true
    THIS_PWD=${PWD}
    echo $THIS_PWD
    cd output/$datacard_output/$CHANNEL
    for FILE in */*.txt; do
        sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
    done
    cd $THIS_PWD

    echo "[INFO] Create Workspace for datacard"
    combineTool.py -M T2W -o workspace.root -i output/$datacard_output/$CHANNEL/125 --parallel 4 -m 125

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

        WORKSPACE=output/$datacard_output/$CHANNEL/125/workspace.root
    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --doInitialFit --robustFit 1 \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --robustFit 1 --doFits \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 -o zfit_mc_${ERA}_${CHANNEL}.json
    plotImpacts.py -i zfit_mc_${ERA}_${CHANNEL}.json -o zfit_mc_${ERA}_${CHANNEL}_impacts
    # cleanup the fit files
    rm higgsCombine*.root
    mv zfit_mc_${ERA}_${CHANNEL}_impacts.pdf output/$datacard_output/
    mv zfit_mc_${ERA}_${CHANNEL}.json output/$datacard_output/
    exit 0
fi