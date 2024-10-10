export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MASSX=$5
MASSY=$6
MODE=$7

POSTFIX="-${MASSX}_${MASSY}"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Datacard Setup
datacard_output="datacards/${NTUPLETAG}-${TAG}/${ERA}"

output_shapes="nmssm_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
output_shapes_boosted="nmssm_boosted_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_boosted=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes_boosted}
shapes_output_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_output_boosted_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/boosted_synced
shapes_output_all_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/all_synced
shapes_rootfile=${shapes_output}${POSTFIX}.root
shapes_rootfile_boosted=${shapes_output_boosted}${POSTFIX}.root
shapes_rootfile_synced=${shapes_output_synced}${POSTFIX}_synced.root

# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
fi
if [ ! -d "$shapes_output_boosted" ]; then
    mkdir -p $shapes_output_boosted
fi

# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "output_shapes_boosted: ${output_shapes_boosted}"
echo "XSEC_FRIENDS: ${XSEC_FRIENDS}"
echo "FF_FRIENDS: ${FF_FRIENDS}"
echo "NN_RES_FRIENDS: ${NN_RES_FRIENDS}"
echo "NN_BOOST_FRIENDS: ${NN_BOOST_FRIENDS}"
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
fi

if [[ $MODE == "XSEC" ]]; then
    source utils/setup_root.sh
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
elif [[ $MODE == "XSEC_XROOTD" ]]; then
    source utils/setup_root.sh
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
        python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath $XSEC_FRIENDS --nthreads 20
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
        --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS $NN_FRIENDS \
        --era $ERA --num-processes 8 --num-threads 12 \
        --optimization-level 1 --skip-systematic-variations --xrootd \
        --output-file $shapes_output --boosted-b-analysis \
        --massX $MASSX --massY $MASSY --validation-tag $TAG
    
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS $NN_FRIENDS \
        --era $ERA --num-processes 8 --num-threads 12 \
        --optimization-level 1 --skip-systematic-variations --xrootd \
        --output-file $shapes_output_boosted --boosted-b-analysis --boosted-tau-analysis \
        --massX $MASSX --massY $MASSY --validation-tag $TAG
fi

if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_nmssm.sh $ERA $CHANNEL \
        "singlegraph" $TAG $NTUPLETAG $CONDOR_OUTPUT $MASSX $MASSY 0
    echo "[INFO] Jobs submitted"
fi
if [[ $MODE == "CONDOR_BOOSTED" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_nmssm.sh $ERA $CHANNEL \
        "singlegraph" $TAG $NTUPLETAG $CONDOR_OUTPUT $MASSX $MASSY 1
    echo "[INFO] Jobs submitted"
fi

if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}-${MASSX}-${MASSY}/*.root
    hadd -j 5 -n 600 -f $shapes_rootfile_boosted ${CONDOR_OUTPUT}/../boosted_analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}-${MASSX}-${MASSY}/*.root
fi

if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile} --do-emb-tt --do-ff --do-qcd
    python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile_boosted} --do-emb-tt --do-ff --do-qcd

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi
    if [ ! -d "$shapes_output_boosted_synced" ]; then
        mkdir -p $shapes_output_boosted_synced
    fi
    if [ ! -d "$shapes_output_all_synced" ]; then
        mkdir -p $shapes_output_all_synced
    fi

    python shapes/convert_to_synced_shapes.py -e $ERA \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        -n 1
    
    python shapes/convert_to_synced_shapes.py -e $ERA \
        -i ${shapes_rootfile_boosted} \
        -o ${shapes_output_boosted_synced} \
        -n 1

    inputfile="nmssm_${CHANNEL}.inputs-nmssm-Run${ERA}${POSTFIX}.root"
    inputfile_boosted="nmssm_${CHANNEL}.inputs-nmssm_boosted-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_all_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}-synced*.root 
    hadd -f $shapes_output_all_synced/$inputfile_boosted $shapes_output_boosted_synced/${ERA}-${CHANNEL}-synced-boosted*.root
fi

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw14.sh
    # inputfile
    inputfile="nmssm_${CHANNEL}.inputs-nmssm-Run${ERA}${POSTFIX}.root"
    inputfile_boosted="nmssm_${CHANNEL}.inputs-nmssm_boosted-Run${ERA}${POSTFIX}.root"

    ${CMSSW_BASE}/bin/el9_amd64_gcc12/MorphingNMSSMRun2UL \
        --base_path=$PWD \
        --input_folder_mt="${shapes_output_all_synced}/${inputfile}" \
        --input_folder_tt="${shapes_output_all_synced}/${inputfile}" \
        --input_folder_et="${shapes_output_all_synced}/${inputfile}" \
        --boosted_tt=false \
        --heavy_mass=$MASSX \
        --light_mass=$MASSY \
        --real_data=true \
        --classic_bbb=false \
        --binomial_bbb=false \
        --jetfakes=1 \
        --embedding=0 \
        --postfix=${POSTFIX} \
        --chan=${CHANNEL} \
        --auto_rebin=true \
        --era=${ERA} \
        --output_folder=output/$datacard_output \
        --use_automc=true \
        --remove_empty_categories=true \
        --train_ff=1 \
        --train_emb=1 \
        --categories="nmssm" \
        --verbose=true

    ${CMSSW_BASE}/bin/el9_amd64_gcc12/MorphingNMSSMRun2UL \
        --base_path=$PWD \
        --input_folder_mt="${shapes_output_all_synced}/${inputfile_boosted}" \
        --input_folder_tt="${shapes_output_all_synced}/${inputfile_boosted}" \
        --input_folder_et="${shapes_output_all_synced}/${inputfile_boosted}" \
        --boosted_tt=true \
        --heavy_mass=$MASSX \
        --light_mass=$MASSY \
        --real_data=true \
        --classic_bbb=false \
        --binomial_bbb=false \
        --jetfakes=1 \
        --embedding=0 \
        --postfix=${POSTFIX} \
        --chan=${CHANNEL} \
        --auto_rebin=true \
        --era=${ERA} \
        --output_folder=output/$datacard_output \
        --use_automc=true \
        --remove_empty_categories=true \
        --train_ff=1 \
        --train_emb=1 \
        --categories="nmssm" \
        --verbose=true
    echo "[INFO] Created datacard"
fi

if [[ $MODE == "DATACARD_MERGE" ]]; then
    source utils/setup_cmssw14.sh
    THIS_PWD=${PWD}
    echo $THIS_PWD
    cd output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}
    merge_cmd="combineCards.py"
    for FILE in *.txt; do
        merge_cmd+=" ${FILE%.*}=${FILE}"
    done
    merge_cmd+=" > combined.txt.cmb"
    echo $merge_cmd
    eval "$merge_cmd"

    # sed -i '$s/$/\nBR_Hbb rateParam * NMSSM_Ytt 0.582 [0.582,0.582]/' "combined.txt.cmb"
    # sed -i '$s/$/\nBR_Htt rateParam * NMSSM_Ybb 0.0627 [0.0627,0.0627]/' "combined.txt.cmb"
    # sed -i '$s/$/\nalpha_Ybb rateParam * NMSSM_Ybb 0.9027 [-0.1,1.1]/' "combined.txt.cmb"
    # sed -i '$s/$/\nalpha_Ytt rateParam * NMSSM_Ytt (1-@0) alpha_Ybb/' "combined.txt.cmb"
    sed -i '$s/$/\n* autoMCStats 10 0 1/' "combined.txt.cmb"
    
    cd $THIS_PWD
    echo "[INFO] Merged datacards"
fi

if [[ $MODE == "WORKSPACE_LIMIT" ]]; then
    source utils/setup_cmssw14.sh
    combineTool.py -M T2W -o "workspace.root" \
        -i output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/combined.txt.cmb \
        -m $MASSY --parallel 1 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/NMSSM_Ytt:r_NMSSM_Ytt[0,0,200]"' \
        --PO '"map=^.*/NMSSM_Ybb:r_NMSSM_Ybb[0,0,200]"' \
        --channel-masks
    echo "[INFO] Created Workspace for datacard"
fi

if [[ $MODE == "WORKSPACE_LIMIT_COMB" ]]; then
    source utils/setup_cmssw14.sh
    combineTool.py -M T2W -o "workspace.root" \
        -i output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/combined.txt.cmb \
        -m $MASSY --parallel 1 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/NMSSM_Ytt:r_NMSSM[0,0,200]"' \
        --PO '"map=^.*/NMSSM_Ybb:r_NMSSM[0,0,200]"' \
        --channel-masks
    echo "[INFO] Created Workspace for datacard"
fi

if [[ $MODE == "WORKSPACE_FIT" ]]; then
    source utils/setup_cmssw14.sh
    # combineTool.py -M T2W -o workspace.root -i output/$datacard_output/cmb/* --parallel 16
    combineTool.py -M T2W -o "workspace_multidimfit.root" \
        -i output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/combined.txt.cmb \
        -m $MASSY --parallel 1 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/NMSSM_Ytt:r_NMSSM_Ytt[0,-10,10]"' \
        --PO '"map=^.*/NMSSM_Ybb:r_NMSSM_Ybb[0,-10,10]"' \
        --channel-masks
    echo "[INFO] Created Workspace for datacard"
fi

if [[ $MODE == "FIT_LIMITS_Ybb" ]]; then
    source utils/setup_cmssw14.sh
    combineTool.py \
        -M AsymptoticLimits \
        -m $MASSY \
        -d output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/workspace.root \
        -n $ERA \
        --parallel 1 --there --verbose 2 \
        --cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.01 \
        --run blind \
        --redefineSignalPOIs r_NMSSM_Ybb \
        --freezeParameters r_NMSSM_Ytt \
        --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0
    echo "[INFO] Fit is done"
fi

# mask_nmssm_et_0_2018=0,mask_nmssm_et_1_2018=1,mask_nmssm_et_2_2018=0,mask_nmssm_et_3_2018=1,mask_nmssm_et_4_2018=0,mask_nmssm_et_5_2018=0,mask_nmssm_et_6_2018=0,mask_nmssm_et_7_2018=0
# mask_boosted_nmssm_et_0_2018=1,mask_boosted_nmssm_et_1_2018=1,mask_boosted_nmssm_et_2_2018=1,mask_boosted_nmssm_et_3_2018=1,mask_boosted_nmssm_et_4_2018=1,mask_boosted_nmssm_et_5_2018=1,mask_boosted_nmssm_et_6_2018=1,mask_boosted_nmssm_et_7_2018=1

# mask_nmssm_mt_0_2018=0,mask_nmssm_mt_1_2018=1,mask_nmssm_mt_2_2018=0,mask_nmssm_mt_3_2018=1,mask_nmssm_mt_4_2018=0,mask_nmssm_mt_5_2018=0,mask_nmssm_mt_6_2018=0,mask_nmssm_mt_7_2018=0
# mask_boosted_nmssm_mt_0_2018=1,mask_boosted_nmssm_mt_1_2018=1,mask_boosted_nmssm_mt_2_2018=1,mask_boosted_nmssm_mt_3_2018=1,mask_boosted_nmssm_mt_4_2018=1,mask_boosted_nmssm_mt_5_2018=1,mask_boosted_nmssm_mt_6_2018=1,mask_boosted_nmssm_mt_7_2018=1

# mask_nmssm_tt_0_2018=0,mask_nmssm_tt_1_2018=1,mask_nmssm_tt_2_2018=0,mask_nmssm_tt_3_2018=1,mask_nmssm_tt_4_2018=0,mask_nmssm_tt_5_2018=0,mask_nmssm_tt_6_2018=0,mask_nmssm_tt_7_2018=0
# mask_boosted_nmssm_tt_0_2018=1,mask_boosted_nmssm_tt_1_2018=1,mask_boosted_nmssm_tt_2_2018=1,mask_boosted_nmssm_tt_3_2018=1,mask_boosted_nmssm_tt_4_2018=1,mask_boosted_nmssm_tt_5_2018=1,mask_boosted_nmssm_tt_6_2018=1,mask_boosted_nmssm_tt_7_2018=1

if [[ $MODE == "FIT_LIMITS_Ytt" ]]; then
    source utils/setup_cmssw14.sh
    combineTool.py \
        -M AsymptoticLimits \
        -m $MASSY \
        -d output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/workspace.root \
        -n $ERA \
        --parallel 1 --there --verbose 2 \
        --cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.01 \
        --run blind \
        --redefineSignalPOIs r_NMSSM_Ytt \
        --freezeParameters r_NMSSM_Ybb \
        --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0,mask_nmssm_et_1_2018=1,mask_nmssm_et_0_2018=1,mask_nmssm_et_3_2018=1,mask_nmssm_mt_1_2018=1,mask_nmssm_mt_0_2018=1,mask_nmssm_mt_3_2018=1,mask_nmssm_tt_1_2018=1,mask_nmssm_tt_0_2018=1,mask_nmssm_tt_3_2018=1,mask_boosted_nmssm_et_0_2018=1,mask_boosted_nmssm_et_1_2018=1,mask_boosted_nmssm_et_2_2018=1,mask_boosted_nmssm_et_3_2018=1,mask_boosted_nmssm_et_4_2018=1,mask_boosted_nmssm_et_5_2018=1,mask_boosted_nmssm_et_6_2018=1,mask_boosted_nmssm_et_7_2018=1,mask_boosted_nmssm_mt_0_2018=1,mask_boosted_nmssm_mt_1_2018=1,mask_boosted_nmssm_mt_2_2018=1,mask_boosted_nmssm_mt_3_2018=1,mask_boosted_nmssm_mt_4_2018=1,mask_boosted_nmssm_mt_5_2018=1,mask_boosted_nmssm_mt_6_2018=1,mask_boosted_nmssm_mt_7_2018=1,mask_boosted_nmssm_tt_0_2018=1,mask_boosted_nmssm_tt_1_2018=1,mask_boosted_nmssm_tt_2_2018=1,mask_boosted_nmssm_tt_3_2018=1,mask_boosted_nmssm_tt_4_2018=1,mask_boosted_nmssm_tt_5_2018=1,mask_boosted_nmssm_tt_6_2018=1,mask_boosted_nmssm_tt_7_2018=1
    echo "[INFO] Fit is done"
fi

if [[ $MODE == "FIT_LIMITS" ]]; then
    source utils/setup_cmssw14.sh
    combineTool.py \
        -M AsymptoticLimits \
        -m $MASSY \
        -d output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/workspace.root \
        -n $ERA \
        --parallel 1 --there --verbose 0 \
        --cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.01 \
        --run blind \
        --redefineSignalPOIs r_NMSSM --trackParameters r_NMSSM,alpha_Ybb,alpha_Ytt \
        --setParameterRanges r_NMSSM=0,200:alpha_Ybb=0,1 \
        --freezeParameters BR_Htt,BR_Hbb,alpha_Ybb \
        --setParameters r_NMSSM=0,alpha_Ybb=1
    echo "[INFO] Fit is done"
fi

# alpha_Ybb=0.9027 <- SM

if [[ $MODE == "TOY" ]]; then
    source utils/setup_cmssw14.sh
    combineTool.py \
        -M GenerateOnly --saveToys \
        -m $MASSY \
        -d output/$datacard_output/cmb/${MASSX}_${MASSY}/workspace.root \
        -n $ERA \
        -t -1 --there --verbose 2 \
        --freezeParameters BR_Htt,BR_Hbb \
        --setParameters r_NMSSM=0,alpha_Ybb=0.5,mask_nmssm_mt_0_2018=0,mask_nmssm_mt_1_2018=0,mask_nmssm_mt_2_2018=0,mask_nmssm_mt_3_2018=0,mask_nmssm_mt_4_2018=0,mask_nmssm_mt_5_2018=0,mask_nmssm_mt_6_2018=0,mask_nmssm_mt_7_2018=0,mask_boosted_nmssm_mt_0_2018=0,mask_boosted_nmssm_mt_1_2018=0,mask_boosted_nmssm_mt_2_2018=0,mask_boosted_nmssm_mt_3_2018=0,mask_boosted_nmssm_mt_4_2018=0,mask_boosted_nmssm_mt_5_2018=0,mask_boosted_nmssm_mt_6_2018=0,mask_boosted_nmssm_mt_7_2018=0
    echo "[INFO] Toy is done"
fi

if [[ $MODE == "FIT" ]]; then
    source utils/setup_cmssw14.sh
    combineTool.py \
        -M FitDiagnostics \
        -m $MASSY \
        -d output/$datacard_output/cmb/${MASSX}_${MASSY}/workspace.root \
        -n $ERA \
        --parallel 1 --there --verbose 2 \
        -t -1 --toysFile ${PWD}/output/$datacard_output/cmb/${MASSX}_${MASSY}/higgsCombine2018.GenerateOnly.mH500.123456.root \
        --cminDefaultMinimizerStrategy 1 --cminDefaultMinimizerTolerance 0.01 \
        --X-rtd MINIMIZER_analytic \
        --redefineSignalPOIs r_NMSSM,alpha_Ybb \
        --freezeParameters BR_Htt,BR_Hbb \
        --setParameters r_NMSSM=1,alpha_Ybb=0.9027,mask_nmssm_mt_0_2018=0,mask_nmssm_mt_1_2018=0,mask_nmssm_mt_2_2018=0,mask_nmssm_mt_3_2018=0,mask_nmssm_mt_4_2018=0,mask_nmssm_mt_5_2018=0,mask_nmssm_mt_6_2018=0,mask_nmssm_mt_7_2018=0,mask_boosted_nmssm_mt_0_2018=0,mask_boosted_nmssm_mt_1_2018=0,mask_boosted_nmssm_mt_2_2018=0,mask_boosted_nmssm_mt_3_2018=0,mask_boosted_nmssm_mt_4_2018=0,mask_boosted_nmssm_mt_5_2018=0,mask_boosted_nmssm_mt_6_2018=0,mask_boosted_nmssm_mt_7_2018=0
    echo "[INFO] Fit is done"
fi

if [[ $MODE == "PARAM_SCAN" ]]; then
    source utils/setup_cmssw14.sh
    combineTool.py \
        -M MultiDimFit \
        -m $MASSY \
        -d output/$datacard_output/cmb/${MASSX}_${MASSY}/workspace.root \
        -n $ERA --X-rtd MINIMIZER_no_analytic \
        --parallel 1 --there --verbose 0 \
        -t -1 --algo=grid --points 4000 --alignEdges 1 --toysFile ${PWD}/output/$datacard_output/cmb/${MASSX}_${MASSY}/higgsCombine2018.GenerateOnly.mH${MASSY}.123456.root \
        --redefineSignalPOIs alpha_Ybb,r_NMSSM \
        --freezeParameters BR_Htt,BR_Hbb \
        --setParameterRanges r_NMSSM=0,10:alpha_Ybb=0,1 \
        --setParameters r_NMSSM=1,alpha_Ybb=0.9027,mask_nmssm_mt_0_2018=1,mask_nmssm_mt_1_2018=1,mask_nmssm_mt_2_2018=0,mask_nmssm_mt_3_2018=0,mask_nmssm_mt_4_2018=0,mask_nmssm_mt_5_2018=0,mask_nmssm_mt_6_2018=0,mask_nmssm_mt_7_2018=0,mask_boosted_nmssm_mt_0_2018=1,mask_boosted_nmssm_mt_1_2018=1,mask_boosted_nmssm_mt_2_2018=0,mask_boosted_nmssm_mt_3_2018=0,mask_boosted_nmssm_mt_4_2018=0,mask_boosted_nmssm_mt_5_2018=0,mask_boosted_nmssm_mt_6_2018=0,mask_boosted_nmssm_mt_7_2018=0
    echo "[INFO] Scan is done"
fi

if [[ $MODE == "COLLECT_LIMITS" ]]; then
    source utils/setup_cmssw14.sh

    COLLECTION_FILE="limit_jsons/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/nmssm_${ERA}_${CHANNEL}_${MASSX}.json"
    COLLECTION_DIR=$(dirname "$COLLECTION_FILE")

    # Check if the directory exists
    if [ ! -d "$COLLECTION_DIR" ]; then
        mkdir -p "$COLLECTION_DIR"
    fi

    combineTool.py \
        -M CollectLimits output/${datacard_output}/${CHANNEL}/${MASSX}_*/higgsCombine*Asymptotic*.root \
        --use-dirs -o $COLLECTION_FILE

    echo "[INFO] Limits collected"
fi

if [[ $MODE == "IMPACTS" ]]; then
    source utils/setup_cmssw14.sh
    WORKSPACE=output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/workspace_multidimfit.root
    combineTool.py -M Impacts -d $WORKSPACE -m $MASSY \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 1 \
        --doInitialFit --robustFit 1 -t -1 \
        --parallel 1 --redefineSignalPOIs r_NMSSM_Ybb \
        --freezeParameters r_NMSSM_Ytt \
        --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=1

    combineTool.py -M Impacts -d $WORKSPACE -m $MASSY \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 1 \
        --robustFit 1 --doFits -t -1 \
        --parallel 1 --redefineSignalPOIs r_NMSSM_Ybb \
        --freezeParameters r_NMSSM_Ytt \
        --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=1

    combineTool.py -M Impacts -d $WORKSPACE -m $MASSY --redefineSignalPOIs r_NMSSM_Ybb -o output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/impacts.json
    plotImpacts.py -i output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/impacts.json -o output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/impacts
    # cleanup the fit files
    rm higgsCombine*.root
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

if [[ $MODE == "PREFIT" ]]; then
    source utils/setup_cmssw14.sh
    WORKSPACE=output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}/workspace.root
    
    PostFitShapesFromWorkspace -m ${MASSY} -w $WORKSPACE \
        -o output/${datacard_output}/${CHANNEL}/${MASSX}_${MASSY}/datacard-shapes-prefit.root \
        -d output/${datacard_output}/${CHANNEL}/${MASSX}_${MASSY}/combined.txt.cmb
fi

if [[ $MODE == "PLOT-PREFIT" ]]; then
    source utils/setup_root.sh
    SUMMARYFOLDER=output/gof/${NTUPLETAG}-${TAG}/plots
    [ -d $SUMMARYFOLDER ] || mkdir -p $SUMMARYFOLDER
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        gof_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        PLOTDIR=output/${datacard_output}/plots
        PREFITFILE=output/${datacard_output}/${ID}-datacard-shapes-prefit.root
        [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
       
        for OPTION in "" "--png"; do
            python3 plotting/plot_shapes_gof.py -l -i $PREFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor \
                --gof-variable $VARIABLE -o ${PLOTDIR}
        done
        cp ${PLOTDIR}/*.p{df,ng} $SUMMARYFOLDER
    done
fi
