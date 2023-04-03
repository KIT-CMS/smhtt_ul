export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5
WP=$6
VS_ELE_WP=$7
DEEP_TAU=$8


echo $NTUPLETAG
echo $WP

VARIABLES="m_vis"
POSTFIX="-ML"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Datacard Setup

datacard_output="datacards/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

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
printf -v categories_string '%s,' "${categories[@]}"
echo "Using Cateogires ${categories_string%,}"

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
        --${CHANNEL}-friend-directory $FRIENDS \
        --era $ERA --num-processes 3 --num-threads 8 \
         --wp $WP \
        --vs_ele_wp ${VS_ELE_WP} \
        --optimization-level 1 --skip-systematic-variations \
        --special-analysis "TauID" \
        --control-plot-set ${VARIABLES} \
        --output-file $shapes_output
fi

PROCESSES="emb"
number="_emb_1"
if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $FRIENDS \
        --era $ERA --num-processes 2 --num-threads 14 \
         --wp $WP \
        --vs_ele_wp ${VS_ELE_WP} \
        --optimization-level 1 \
        --special-analysis "TauID" \
         --process-selection $PROCESSES \
        --control-plot-set ${VARIABLES} \
        --optimization-level 1 \
        --output-file $shapes_output$number
fi

if [[ $MODE == "CONTROLREGION" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels mm \
        --directory $NTUPLES \
        --mm-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 3 --num-threads 9 \
         --wp $WP \
        --vs_ele_wp ${VS_ELE_WP} \
        --optimization-level 1 --skip-systematic-variations \
        --special-analysis "TauID" \
        --output-file "${shapes_output}_mm"
fi


if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_ul.sh $ERA $CHANNEL \
        "singlegraph" $TAG 0 $NTUPLETAG $CONDOR_OUTPUT "TauID" $WP $VS_ELE_WP
    echo "[INFO] Jobs submitted"
fi

if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"

    bash ./shapes/do_estimations.sh 2018 ${shapes_rootfile} 1

    bash ./shapes/do_estimations.sh 2018 ${shapes_rootfile_mm} 1

    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"

    # mkdir -p control_plots_tauid/${WP}/

    # python3 plotting/plot_shapes_tauID.py -l --era Run${ERA} --input ${shapes_rootfile} --variables ${VARIABLES} --channels ${CHANNEL} --embedding --categories ${categories_string%,} --output control_plots_tauid/${WP}/

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
        -n 1

    python shapes/convert_to_synced_shapes.py -e $ERA \
        -i "${shapes_rootfile_mm}" \
        -o "${shapes_output_synced}_mm" \
        --variable-selection ${VARIABLES} \
        -n 1

    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}*.root

    inputfile="htt_mm.inputs-sm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile ${shapes_output_synced}_mm/${ERA}-mm-*.root
    exit 0
fi


if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw.sh
    # inputfile
    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
    # for category in "pt_binned" "inclusive" "dm_binned"
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
        --categories="all" \
        --era=$ERA \
        --output=$datacard_output
    THIS_PWD=${PWD}
    echo $THIS_PWD
    cd output/$datacard_output/
    for FILE in htt_mt_*/*.txt; do
        sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
    done
    cd $THIS_PWD

    echo "[INFO] Create Workspace for datacard"
    combineTool.py -M T2W -i output/$datacard_output/htt_mt_*/ -o workspace.root --parallel 4 -m 125
    exit 0
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
            --era=$ERA \
            --output=$datacard_output
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd output/$datacard_output/
        for FILE in cmb/*.txt; do
            sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
        done
        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -i output/$datacard_output/htt_mt_${pt_cat}/ -o workspace.root --parallel 4 -m 125
    done

    exit 0
fi

if [[ $MODE == "FIT" ]]; then
    source utils/setup_cmssw.sh
    # --setParameterRanges CMS_htt_doublemutrg_Run${ERA}=$RANGE \
    combineTool.py -M MultiDimFit -m 125 -d output/$datacard_output/htt_mt_*/combined.txt.cmb \
        --algo singles --robustFit 1 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --floatOtherPOIs 1 \
        -n $ERA -v1 \
        --parallel 1 --there --robustHesse 1
    for RESDIR in output/$datacard_output/htt_mt_*; do
        echo "[INFO] Printing fit result for category $(basename $RESDIR)"
        FITFILE=${RESDIR}/higgsCombine${ERA}.MultiDimFit.mH125.root
        python datacards/print_fitresult.py ${FITFILE}
    done
    exit 0
fi

if [[ $MODE == "MULTIFIT" ]]; then
    source utils/setup_cmssw.sh

    # combineTool.py -M T2W -i /work/olavoryk/DT25_smhtt/smhtt_ul/output/datacards/2022_07_v6-try_no_qqh_shape_v1/2018_tauid_medium/cmb/ \
    #                -o out_multidim.root \
    #                --parallel 8 -m 125 \
    #                -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
    #                 --PO '"map=^.*/EMB_Pt20to25:r_EMB_Pt20to25[1,0,2]"' \
    #                 --PO '"map=^.*/EMB_Pt25to30:r_EMB_Pt25to30[1,0,2]"' \
    #                 --PO '"map=^.*/EMB_Pt30to35:r_EMB_Pt30to35[1,0,2]"' \
    #                 --PO '"map=^.*/EMB_Pt35to40:r_EMB_Pt35to40[1,0,2]"' \
    #                 --PO '"map=^.*/EMB_PtGt40:r_EMB_PtGt40[1,0,2]"' 


    combineTool.py -M T2W -i output/$datacard_output/cmb \
                -o out_multidim.root \
                --parallel 8 -m 125 \
                -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
                --PO '"map=^.*/EMB_Pt20to25:r_EMB_Pt20to25[1,0.8,1.3]"' \
                --PO '"map=^.*/EMB_Pt25to30:r_EMB_Pt25to30[1,0.8,1.3]"' \
                --PO '"map=^.*/EMB_Pt30to35:r_EMB_Pt30to35[1,0.8,1.3]"' \
                --PO '"map=^.*/EMB_Pt35to40:r_EMB_Pt35to40[1,0.8,1.3]"' \
                --PO '"map=^.*/EMB_PtGt40:r_EMB_PtGt40[1,0.8,1.2]"' 


    # combineTool.py \
    #     -n .multidim_pt_fit \
    #     -M MultiDimFit\
    #     -m 125 -d /work/olavoryk/DT25_smhtt/smhtt_ul/output/datacards/2022_07_v6-try_no_qqh_shape_v1/2018_tauid_medium/cmb/out_multidim.root \
    #     --algo singles \
    #     --robustFit 1 \
    #     --X-rtd MINIMIZER_analytic \
    #     --cminDefaultMinimizerStrategy 0 \
    #     --floatOtherPOIs 1 \
    #     --expectSignal 1 \
    #     -v1 

        combineTool.py \
        -n .multidim_pt_fit \
        -M MultiDimFit\
        -m 125 -d output/$datacard_output/cmb/out_multidim.root \
        --algo singles \
        --robustFit 1 \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0 \
        --floatOtherPOIs 1 \
        --expectSignal 1 \
        -v1 --robustHesse 1



        FITFILE=higgsCombine.multidim_pt_fit.MultiDimFit.mH125.root
        mv $FITFILE output/$datacard_output/cmb/
        python datacards/print_fitresult.py output/$datacard_output/cmb/${FITFILE}

        

    exit 0
fi

if [[ $MODE == "POSTFIT" ]]; then
    source utils/setup_cmssw.sh

    # WORKSPACE=/work/olavoryk/DT25_smhtt/smhtt_ul/output/datacards/2022_07_v6-try_no_qqh_shape_v1/2018_tauid_medium/cmb/out_multidim.root
    WORKSPACE=output/$datacard_output/cmb/out_multidim.root
    echo "[INFO] Printing fit result for category $(basename $RESDIR)"
    FILE=output/$datacard_output/cmb/postfitshape.root
    FITFILE=output/$datacard_output/cmb/fitDiagnostics.${ERA}.root
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
        -m 125 -d output/$datacard_output/cmb/combined.txt.cmb \
        -o ${FILE} \
        -f ${FITFILE}:fit_s --postfit

    exit 0
fi

if [[ $MODE == "PLOT-MULTIPOSTFIT" ]]; then
    source utils/setup_root.sh

    fit_categories=("Pt20to25" "Pt25to30" "Pt30to35" "Pt35to40" "PtGt40")



    for RESDIR in "${fit_categories[@]}" 
      do
        # WORKSPACE=/work/olavoryk/DT25_smhtt/smhtt_ul/output/datacards/2022_07_v6-try_no_qqh_shape_v1/2018_tauid_medium/cmb/out_multidim.root
        WORKSPACE=output/$datacard_output/cmb/out_multidim.root


        CATEGORY=$RESDIR
        # FILE=/work/olavoryk/DT25_smhtt/smhtt_ul/output/datacards/2022_07_v6-try_no_qqh_shape_v1/2018_tauid_medium/cmb/postfitshape.root
        FILE=output/$datacard_output/cmb/postfitshape.root
        # FITFILE=/work/olavoryk/DT25_smhtt/smhtt_ul/output/datacards/2022_07_v6-try_no_qqh_shape_v1/2018_tauid_medium/cmb/fitDiagnostics.${ERA}.root
        FITFILE=output/$datacard_output/cmb/fitDiagnostics.${ERA}.root

        # create output folder if it does not exist
        if [ ! -d "output/postfitplots_muemb_${TAG}_multifit/" ]; then
            mkdir -p output/postfitplots_muemb_${TAG}_multifit/${WP}
        fi
        echo "[INFO] Postfits plots for category $CATEGORY"
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category $CATEGORY --categories "None" -o output/postfitplots_muemb_${TAG}_multifit/${WP} --prefit
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category $CATEGORY --categories "None" -o output/postfitplots_muemb_${TAG}_multifit/${WP}
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category 100 --categories "None" -o output/postfitplots_muemb_${TAG}_multifit/${WP} --prefit
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category 100 --categories "None" -o output/postfitplots_muemb_${TAG}_multifit/${WP}
    done
    exit 0
fi

if [[ $MODE == "PLOT-SF" ]]; then
    # source utils/setup_root.sh
    source /work/olavoryk/source_files/setup-centOS7-gcc10.sh
    echo python3 plotting/plot_TauID_sf.py --input output/$datacard_output/ --output output/postfitplots_muemb_${TAG} --wp ${WP}
    python3 plotting/plot_TauID_sf.py --input output/$datacard_output/ --output output/postfitplots_muemb_${TAG} --wp ${WP}
    exit 0
fi

if [[ $MODE == "IMPACTS" ]]; then
    source utils/setup_cmssw.sh

    if [ ! -d "impacts_output/${ERA}/${CHANNEL}/${WP}/${TAG}" ]; then
        mkdir -p impacts_output/${ERA}/${CHANNEL}/${WP}/${TAG}
    fi

    WORKSPACE=output/$datacard_output/cmb/out_multidim.root

    fit_categories=("Pt20to25" "Pt25to30" "Pt30to35" "Pt35to40" "PtGt40")


    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
                --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
                --doInitialFit --robustFit 1 \
                --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
                --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
                --robustFit 1 --doFits \
                --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 -o tauid_${ERA}_${CHANNEL}_${WP}_${TAG}_impacts_multifit.json

    for pt_cat in "${fit_categories[@]}"
      do
    
        plotImpacts.py -i tauid_${ERA}_${CHANNEL}_${WP}_${TAG}_impacts_multifit.json -o tauid_${ERA}_${CHANNEL}_${WP}_${TAG}_impacts_multifit_EMB_$pt_cat --POI r_EMB_$pt_cat  
    
        mv tauid_${ERA}_${CHANNEL}_${WP}_${TAG}_impacts_multifit_EMB_$pt_cat.pdf impacts_output/${ERA}/${CHANNEL}/${WP}/${TAG}
    
    done
    #  --pullDef unconstPullAsym
    # cleanup the fit files
    rm higgsCombine*.root

    mv tauid_${ERA}_${CHANNEL}_${WP}_${TAG}_impacts_multifit.json impacts_output/${ERA}/${CHANNEL}/${WP}/${TAG}


    exit 0
fi

if [[ $MODE == "JSON" ]]; then
    source utils/setup_root.sh
    python3 friends/create_xpog_json.py  --wp $WP --user_out_tag $TAG --era $ERA --channel $CHANNEL --input output/$datacard_output/ 
    exit 0
fi


if [[ $MODE == "POI_CORRELATION" ]]; then
    source utils/setup_root.sh
    FITFILE=output/$datacard_output/cmb/fitDiagnostics.${ERA}.root
    
    # python corr_plot.py $ERA $FITFILE
    python corr_poi_multifit.py $ERA $FITFILE

fi

