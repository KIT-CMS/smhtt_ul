export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5
WP=$6


echo $NTUPLETAG
echo $WP

VARIABLES="m_vis"
POSTFIX="-ML"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Datacard Setup

datacard_output="datacards_test_pt_v3/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_dm="datacards_dm_test_v3/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_incl="datacards_incl_test_v3/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

impact_path="impacts_test_v3"

output_shapes="tauid_shapes-${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_synced=output/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_rootfile=${shapes_output}.root
shapes_rootfile_mm=${shapes_output}_mm.root
shapes_rootfile_synced=${shapes_output_synced}_synced.root

echo "MY WP is: " ${WP}
echo "My out path is: ${shapes_output}"
echo "My synchpath is ${shapes_output_synced}"

# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "FRIENDS: ${FRIENDS}"
echo "XSEC: ${XSEC_FRIENDS}"

categories=("Pt20to25" "Pt25to30" "Pt30to35" "PtGt40" "DM0" "DM1" "DM10_11" "Inclusive")
dm_categories=("DM0" "DM1" "DM10_11")
# dm_categories=("DM0")
printf -v categories_string '%s,' "${categories[@]}"
echo "Using Cateogires ${categories_string%,}"

es_shifts=("embminus2p5" "embminus2p4" "embminus2p3" "embminus2p2" "embminus2p1" "embminus2p0" "embminus1p9" "embminus1p8" "embminus1p7" "embminus1p6" "embminus1p5" "embminus1p4" "embminus1p3"\
 "embminus1p2" "embminus1p1" "embminus1p0" "embminus0p9" "embminus0p8" "embminus0p7" "embminus0p6" "embminus0p5" "embminus0p4" "embminus0p3" "embminus0p2" "embminus0p1" "emb0p0" "emb0p1"\
  "emb0p2" "emb0p3" "emb0p4" "emb0p5" "emb0p6" "emb0p7" "emb0p8" "emb0p9" "emb1p0" "emb1p1" "emb1p2" "emb1p3" "emb1p4" "emb1p5" "emb1p6"\
   "emb1p7" "emb1p8" "emb1p9" "emb2p0" "emb2p1" "emb2p2" "emb2p3" "emb2p4" "emb2p5")

# es_shifts=("embminus2p5" "embminus2p4" "embminus2p3")

VS_ELE_WP="vvloose"


if [[ $MODE == "COPY" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Copy sample to ceph, it not there yet                                                     #"
    echo "##############################################################################################"
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
    echo "##############################################################################################"
    echo "#      Copy sample to ceph, it not there yet                                                     #"
    echo "##############################################################################################"
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
    echo "##############################################################################################"
    echo "#      Checking xsec friends directory                                                       #"
    echo "##############################################################################################"
    python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsxrootd-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
    exit 0
fi


echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
echo "##############################################################################################"
echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
echo "##############################################################################################"

# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
    mkdir -p "${shapes_output}_mm"
fi

echo "${shapes_output}_mm"

if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 3 --num-threads 9 \
        --vs-jet-wp $WP \
        --vs-ele-wp ${VS_ELE_WP} \
        --optimization-level 1 --skip-systematic-variations \
        --special-analysis "TauID" \
        --control-plot-set ${VARIABLES} \
        --output-file $shapes_output  --xrootd  --validation-tag $TAG 
fi

if [[ $MODE == "CONTROLREGION" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels mm \
        --directory $NTUPLES \
        --mm-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 3 --num-threads 9 \
        --vs-jet-wp $WP \
        --vs-ele-wp ${VS_ELE_WP} \
        --optimization-level 1 --skip-systematic-variations \
        --special-analysis "TauID" \
        --output-file "${shapes_output}_mm"  --xrootd --validation-tag $TAG
fi

PROCESSES="emb"
number="_emb_ssos"
if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 3 --num-threads 9 \
        --vs-jet-wp $WP \
        --vs-ele-wp ${VS_ELE_WP} \
        --optimization-level 1 \
        --special-analysis "TauID" \
        --process-selection $PROCESSES \
        --control-plot-set ${VARIABLES} \
        --optimization-level 1 \
        --output-file $shapes_output$number --xrootd --validation-tag $TAG 
fi

if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_ul.sh $ERA $CHANNEL \
        "singlegraph" $TAG 0 $NTUPLETAG $CONDOR_OUTPUT "TauID" 0 $WP $VS_ELE_WP
    echo "[INFO] Jobs submitted"
fi

if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ "${ERA}" == "2018"  ||  "${ERA}" == "2017" ]]; then 
    datacard_era=${ERA}
elif [[ "${ERA}" == "2016postVFP"  ||  "${ERA}" == "2016preVFP" ]]; then
   datacard_era="2016"
fi

if [[ $MODE == "PLOT-CONTROL-ES" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"
    python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile} --do-emb-tt --do-qcd

        for CATEGORY in "${dm_categories[@]}"
    do
        for es_sh in "${es_shifts[@]}"
        do 
            python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
            --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category $CATEGORY --energy_scale --es_shift $es_sh
        done
    done
fi

if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"

    python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile} --do-emb-tt --do-qcd

    python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile_mm} --do-qcd

    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"



    echo "##############################################################################################"
    echo "#     synced shapes                                      #"
    echo "##############################################################################################"

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python shapes/convert_to_synced_shapes.py -e ${datacard_era} \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        --variable-selection ${VARIABLES} \
        -n 1

    python shapes/convert_to_synced_shapes.py -e ${datacard_era} \
        -i "${shapes_rootfile_mm}" \
        -o "${shapes_output_synced}_mm" \
        --variable-selection ${VARIABLES} \
        -n 1

    inputfile="htt_${CHANNEL}.inputs-sm-Run${datacard_era}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${datacard_era}-${CHANNEL}*.root

    inputfile="htt_mm.inputs-sm-Run${datacard_era}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile ${shapes_output_synced}_mm/${datacard_era}-mm-*.root

    exit 0
fi

if [[ $MODE == "INST_COMB" ]]; then
    source utils/install_combine_tauid.sh
fi

pt_categories=("Pt20to25" "Pt25to30" "Pt30to35" "Pt35to40" "PtGt40")
if [[ $MODE == "DATACARD_COMB" ]]; then
    source utils/setup_cmssw.sh
    # # inputfile

    for pt_cat in "${pt_categories[@]}"
    do
        inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
        # # for category in "pt_binned" "inclusive" "dm_binned"
        $CMSSW_BASE/bin/slc7_amd64_gcc700/MorphingTauID2017 \
            --base_path=$PWD \
            --input_folder_mt=$shapes_output_synced \
            --input_folder_mm=$shapes_output_synced \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=0 \
            --embedding=1 \
            --verbose=true \
            --postfix=$POSTFIX \
            --use_control_region=true \
            --auto_rebin=true \
            --categories=${pt_cat} \
            --era=$datacard_era \
            --output=$datacard_output
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd output/$datacard_output/
        # for FILE in cmb/*.txt; do
        #     sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
        # done
        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -i output/$datacard_output/htt_mt_${pt_cat}/ -o workspace.root --parallel 4 -m 125
    done

    exit 0
fi


dm_categories=("DM0" "DM1" "DM10_11")
if [[ $MODE == "DATACARD_DM" ]]; then
    source utils/setup_cmssw_tauid.sh
    # # inputfile

    for dm_cat in "${dm_categories[@]}"
    do
        inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
        # # for category in "dm_binned"
        $CMSSW_BASE/bin/slc7_amd64_gcc10/MorphingTauID2017 \
            --base_path=$PWD \
            --input_folder_mt=$shapes_output_synced \
            --input_folder_mm=$shapes_output_synced \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=0 \
            --embedding=1 \
            --verbose=true \
            --postfix=$POSTFIX \
            --use_control_region=true \
            --auto_rebin=true \
            --categories=${dm_cat} \
            --era=$datacard_era \
            --output=$datacard_output_dm
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd output/$datacard_output_dm/
    
        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -i output/$datacard_output_dm/htt_mt_${dm_cat}/ -o workspace_dm.root --parallel 4 -m 125
    done

    exit 0
fi

if [[ $MODE == "MULTIFIT" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create Workspace for all the datacards"
    combineTool.py -M T2W -i output/$datacard_output_dm/cmb \
                -o out_multidim_dm.root \
                --parallel 8 -m 125 \
                -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
                --PO '"map=^.*/EMB_DM0:r_EMB_DM_0[1,0.8,1.1]"' \
                --PO '"map=^.*/EMB_DM1:r_EMB_DM_1[1,0.8,1.1]"' \
                --PO '"map=^.*/EMB_DM10_11:r_EMB_DM_10_11[1,0.8,1.1]"'  

    combineTool.py -M MultiDimFit -n .comb_id_0.8_1.1_es_-1.2_1.2_dm -d output/$datacard_output_dm/cmb/out_multidim_dm.root \
    --setParameters ES_DM0=0.0,ES_DM1=0.0,ES_DM10_11=0.0,r_EMB_DM_0=1.0,r_EMB_DM_1=1.0,r_EMB_DM_10_11=1.0 \
    --setParameterRanges r_EMB_DM_0=0.8,1.1:r_EMB_DM_1=0.8,1.1:r_EMB_DM_10_11=0.8,1.1:ES_DM0=-1.2,1.2:ES_DM1=-1.2,1.2:ES_DM10_11=-1.2,1.2 \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_DM0,ES_DM1,ES_DM10_11,r_EMB_DM_0,r_EMB_DM_1,r_EMB_DM_10_11 --floatOtherPOIs=1 \
    --points=400 --algo singles

fi



if [[ $MODE == "SCAN_2D" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create 2D scan"

        for dm_cat in "${dm_categories[@]}"
    do
    
        combineTool.py -M T2W -i output/$datacard_output_dm/htt_mt_${dm_cat}/ -o ws_scan_${dm_cat}.root

        combineTool.py -M MultiDimFit -n .nominal_${dm_cat} -d output/$datacard_output_dm/htt_mt_${dm_cat}/ws_scan_${dm_cat}.root \
        --setParameters ES_${dm_cat}=0.2,r=0.9 --setParameterRanges r=0.8,1.0:ES_${dm_cat}=-1.1,1.1 \
        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
        --redefineSignalPOIs ES_${dm_cat},r \
        --floatOtherPOIs=1 --points=400 --algo grid

        echo "[INFO] Plotting 2D scan ..."
        python3 plot_2D_scan.py --name nominal_${dm_cat} --tau-id-poi ${dm_cat} --tau-es-poi ES_${dm_cat} --outname tau_id_${dm_cat}
    done

fi


