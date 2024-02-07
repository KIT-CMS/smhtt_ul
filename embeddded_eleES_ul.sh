#used with CMSSW_11_3_4

export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5

VARIABLES="m_vis"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

output_shapes="elees_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_rootfile=${shapes_output}.root
shapes_rootfile_synced=${shapes_output_synced}_synced.root

# Datacard Setup
datacard_output="datacards/${NTUPLETAG}-${TAG}/${ERA}_elees"

# print the paths to be used
echo "KINGMAKER_BASEDIR_XROOTD: $KINGMAKER_BASEDIR_XROOTD"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "FRIENDS: ${FRIENDS}"

categories=("barrel" "endcap" "Inclusive")
printf -v categories_string '%s,' "${categories[@]}"
echo "Using Cateogires ${categories_string%,}"

if [[ $MODE == "XSEC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#       xsec friends                                                                         #"
    echo "##############################################################################################"
    echo "running xsec friends script"
    python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsxrootd-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
fi
echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
echo "##############################################################################################"

# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
fi

if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS \
        --era $ERA --num-processes 4 --num-threads 3 \
        --optimization-level 1 --skip-systematic-variations \
        --special-analysis "EleES" \
        --control-plot-set ${VARIABLES} \
        --output-file $shapes_output
fi

if [[ $MODE == "LOCAL" ]]; then

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output" ]; then
        mkdir -p $shapes_output
    fi

    source utils/setup_root.sh
    echo "start"
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 4 --num-threads 4 \
        --optimization-level 1 \
        --special-analysis "EleES" \
        --control-plot-set ${VARIABLES} \
        --skip-systematic-variations \
        --output-file $shapes_output \
        --xrootd --validation-tag $TAG
fi

if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_ul.sh $ERA $CHANNEL \
        "singlegraph" $TAG 0 $NTUPLETAG $CONDOR_OUTPUT "EleES"
    echo "[INFO] Jobs submitted"
fi
if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ $MODE == "PLOT-CONTROL" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"
    for CATEGORY in "${categories[@]}"; do
        python3 plotting/plot_shapes_control_ee_channel.py -l --era Run${ERA} --input ${shapes_rootfile} --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category $CATEGORY
        python3 plotting/plot_shapes_control_ee_channel.py -l --era Run${ERA} --input ${shapes_rootfile} --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category $CATEGORYpython3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_rootfile} --variables ${VARIABLES} --channels ${CHANNEL} --category $CATEGORY
    done

fi


if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"

    echo "##############################################################################################"

    python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-qcd --special "EleES"


    echo "##############################################################################################"
    echo "#     synced shapes                                      #"
    echo "##############################################################################################"

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python shapes/convert_to_synced_shapes.py -e $ERA \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        --variable-selection ${VARIABLES} \
        --special "EleES" \
        -n 1
    POSTFIX="-ML"
    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"

    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}*.root

    exit 0
fi

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw.sh
    ulimit -s unlimited
    # inputfile
    POSTFIX="-ML"
    TAG=
    inputfile="htt_${CHANNEL}.inputs-sm-${ERA}${POSTFIX}.root"
    $CMSSW_BASE/bin/slc7_amd64_gcc900/MorphingEleES_UL \
        --base_path=$PWD \
        --input_folder_ee=$shapes_output_synced \
        --real_data=true \
        --classic_bbb=false \
        --verbose=true \
        --postfix=$POSTFIX \
        --auto_rebin=false \
        --rebin_categories=false \
        --era=$ERA \
        --output="output/$datacard_output"
    
    combineTool.py -M T2W -i output/$datacard_output/htt_ee_*/ -o workspace.root --parallel 4
    exit 0
fi

if [[ $MODE == "FIT" ]]; then
    source utils/setup_cmssw.sh
    for INPUT in output/$datacard_output/htt_ee_barrel; do
        echo "[INFO] Fit barrel workspace from path ${INPUT}"
        WORKSPACE=${INPUT}/workspace.root
        combine \
            -M MultiDimFit \
            -n _initialFit_Test \
            --algo singles \
            --redefineSignalPOIs elees,r \
            --setParameterRanges elees=-0.48,-0.47:r=0.8,1.2 \
            --robustFit 1 \
            -m 0 -d ${WORKSPACE} \
            --setParameters elees=-0.47,r=1.0 \
            --setRobustFitAlgo=Minuit2 \
            --setRobustFitStrategy=0 \
            --setRobustFitTolerance=0.2 \
            --X-rtd FITTER_NEW_CROSSING_ALGO \
            --X-rtd FITTER_NEVER_GIVE_UP \
            --X-rtd FITTER_BOUND \
            --cminFallbackAlgo "Minuit2,0:0.1" \
            --cminFallbackAlgo "Minuit,0:0.1"

        combineTool.py -M MultiDimFit -d ${WORKSPACE} \
            --algo grid \
            --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
            -P elees -m 0 \
            --redefineSignalPOIs elees,r \
            --setParameters elees=-0.47,r=1.0 \
            --setParameterRanges elees=-0.48,-0.46:r=0.8,1.2 \
            --floatOtherPOIs 1 \
            --points 200 \
            --robustFit 1 \
            --setRobustFitAlgo=Minuit2 \
            --setRobustFitStrategy=0 \
            --setRobustFitTolerance=0.2 \
            --X-rtd FITTER_NEW_CROSSING_ALGO \
            --X-rtd FITTER_NEVER_GIVE_UP \
            --X-rtd FITTER_BOUND \
            --cminFallbackAlgo "Minuit2,0:0.1" \
            --cminFallbackAlgo "Minuit,0:0.1" \
            -n ${ERA}_elees
        cp higgsCombine${ERA}_elees.MultiDimFit.mH0.root ${INPUT}
    done
    for INPUT in output/$datacard_output/htt_ee_endcap; do
        echo "[INFO] Fit barrel workspace from path ${INPUT}"
        WORKSPACE=${INPUT}/workspace.root
        combine \
            -M MultiDimFit \
            -n _initialFit_Test \
            --algo singles \
            --redefineSignalPOIs elees,r \
            --setParameterRanges elees=-0.73,-0.68:r=0.8,1.2 \
            --robustFit 1 \
            -m 0 -d ${WORKSPACE} \
            --setParameters elees=-0.715,r=1.00 \
            --setRobustFitAlgo=Minuit2 \
            --setRobustFitStrategy=0 \
            --setRobustFitTolerance=0.2 \
            --X-rtd FITTER_NEW_CROSSING_ALGO \
            --X-rtd FITTER_NEVER_GIVE_UP \
            --X-rtd FITTER_BOUND \
            --cminFallbackAlgo "Minuit2,0:0.1" \
            --cminFallbackAlgo "Minuit,0:0.1"

        combineTool.py -M MultiDimFit -d ${WORKSPACE} \
            --algo grid \
            --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
            -P elees -m 0 \
            --redefineSignalPOIs elees,r \
            --setParameters elees=-0.715,r=1.00 \
            --setParameterRanges elees=-0.73,-0.68:r=0.8,1.2  \
            --floatOtherPOIs 1 \
            --points 200 \
            --robustFit 1 \
            --setRobustFitAlgo=Minuit2 \
            --setRobustFitStrategy=0 \
            --setRobustFitTolerance=0.2 \
            --X-rtd FITTER_NEW_CROSSING_ALGO \
            --X-rtd FITTER_NEVER_GIVE_UP \
            --X-rtd FITTER_BOUND \
            --cminFallbackAlgo "Minuit2,0:0.1" \
            --cminFallbackAlgo "Minuit,0:0.1" \
            -n ${ERA}_elees
        cp higgsCombine${ERA}_elees.MultiDimFit.mH0.root ${INPUT}
    done
    exit 0
fi

if [[ $MODE == "POSTFIT" ]]; then
    source utils/setup_cmssw.sh
    for INPUT in output/$datacard_output/htt_ee_*; do
        CATEGORY=$(basename $INPUT)
        echo "#############################"
        echo $INPUT
        python fitting/plot1DScan.py \
            --main ${INPUT}/higgsCombine${ERA}_elees.MultiDimFit.mH0.root \
            --POI elees \
            --output ${ERA}_${CATEGORY}_elees_plot_nll \
            --translate fitting/translate.json \
            --y-max 10 --main-color 2 --chop 100
        done
    exit 0
fi

if [[ $MODE == "PLOT-POSTFIT" ]]; then
    source utils/setup_cmssw.sh
    for RESDIR in output/$datacard_output/htt_ee_barrel; do
        WORKSPACE=${RESDIR}/workspace.root
        echo "[INFO] Printing fit result for category $(basename $RESDIR)"
        FILE=${RESDIR}/postfitshape.root
        FITFILE=${RESDIR}/fitDiagnostics.${ERA}.root
        combine \
            -n .$ERA \
            -M FitDiagnostics \
            -d $WORKSPACE \
            --redefineSignalPOIs elees,r \
            --setParameters elees=-0.47,r=1.00 \
            --setParameterRanges elees=-0.49,-0.46:r=0.8,1.2 \
            --robustFit 1 -v1 \
            --robustHesse 1 \
            --X-rtd MINIMIZER_analytic \
            --cminDefaultMinimizerStrategy 0
        mv fitDiagnostics.${ERA}.root $FITFILE
        echo "[INFO] Building Prefit/Postfit shapes"
        PostFitShapesFromWorkspace -w ${WORKSPACE} \
            -m 125 -d ${RESDIR}/combined.txt.cmb \
            --output ${FILE} \
            -f ${FITFILE}:fit_s --postfit
    done
        for RESDIR in output/$datacard_output/htt_ee_endcap; do
        WORKSPACE=${RESDIR}/workspace.root
        echo "[INFO] Printing fit result for category $(basename $RESDIR)"
        FILE=${RESDIR}/postfitshape.root
        FITFILE=${RESDIR}/fitDiagnostics.${ERA}.root
        combine \
            -n .$ERA \
            -M FitDiagnostics \
            -d $WORKSPACE \
            --redefineSignalPOIs elees,r \
            --setParameters elees=-0.715,r=1.00 \
            --setParameterRanges elees=-0.8,-0.6:r=0.8,1.2  \
            --robustFit 1 -v1 \
            --robustHesse 1 \
            --X-rtd MINIMIZER_analytic \
            --cminDefaultMinimizerStrategy 0
        mv fitDiagnostics.${ERA}.root $FITFILE
        echo "[INFO] Building Prefit/Postfit shapes"
        PostFitShapesFromWorkspace -w ${WORKSPACE} \
            -m 125 -d ${RESDIR}/combined.txt.cmb \
            --output ${FILE} \
            -f ${FITFILE}:fit_s --postfit
    done

    source utils/setup_root.sh
    i=1
    for RESDIR in output/$datacard_output/htt_ee_*; do
        WORKSPACE=${RESDIR}/workspace.root

        CATEGORY=$(basename $RESDIR)
        FILE=${RESDIR}/postfitshape.root
        FITFILE=${RESDIR}/fitDiagnostics.${ERA}.root
        # create output folder if it does not exist
        if [ ! -d "output/postfitplots/" ]; then
            mkdir -p output/postfitplots/
        fi
        echo "[INFO] Postfits plots for category $CATEGORY"
        python3 plotting/plot_shapes_eleES_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --fake-factor --single-category $CATEGORY --categories "None" -o output/postfitplots/ --prefit
        python3 plotting/plot_shapes_eleES_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --fake-factor --single-category $CATEGORY --categories "None" -o output/postfitplots/
        i=$((i + 1))
    done
    exit 0
