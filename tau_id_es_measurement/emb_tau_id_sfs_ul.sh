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
POSTFIX="-TauID_ES"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# [INFO] tau_id_es_measurement/tau_id_es_sim_fit_conf.sh contains all fit parameters.

# Datacard Setup

datacard_output_pt="datacards_pt_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_dm="datacards_dm_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_incl="datacards_incl_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

impact_path="impacts_${TAG}"

output_shapes="tauid_shapes-${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_synced=output/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_rootfile=${shapes_output}.root
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

categories=("DM0" "DM1" "DM10_11")
all_categories=("Pt20to25" "Pt25to30" "Pt30to35" "Pt35to40" "PtGt40" "DM0" "DM1" "DM10_11")
dm_categories=("DM0" "DM1" "DM10_11")
pt_categories=("Pt20to25" "Pt25to30" "Pt30to35" "Pt35to40" "PtGt40")

es_shifts4_0=("embminus4p0" "embminus3p9" "embminus3p8" "embminus3p7" "embminus3p6" "embminus3p5" "embminus3p4" "embminus3p3"\
 "embminus3p2" "embminus3p1" "embminus3p0" "embminus2p9" "embminus2p8" "embminus2p7" "embminus2p6" "embminus2p5" "embminus2p4"\ 
 "embminus2p3" "embminus2p2" "embminus2p1" "embminus2p0" "embminus1p9" "embminus1p8" "embminus1p7" "embminus1p6" "embminus1p5"\
  "embminus1p4" "embminus1p3" "embminus1p2" "embminus1p1" "embminus1p0" "embminus0p9" "embminus0p8" "embminus0p7" "embminus0p6"\
   "embminus0p5" "embminus0p4" "embminus0p3" "embminus0p2" "embminus0p1" "emb0p0" "emb0p1" "emb0p2" "emb0p3" "emb0p4" "emb0p5" "emb0p6"\
    "emb0p7" "emb0p8" "emb0p9" "emb1p0" "emb1p1" "emb1p2" "emb1p3" "emb1p4" "emb1p5" "emb1p6" "emb1p7" "emb1p8" "emb1p9" "emb2p0" "emb2p1"\
     "emb2p2" "emb2p3" "emb2p4" "emb2p5" "emb2p6" "emb2p7" "emb2p8" "emb2p9" "emb3p0" "emb3p1" "emb3p2" "emb3p3" "emb3p4" "emb3p5" "emb3p6"\
      "emb3p7" "emb3p8" "emb3p9" "emb4p0")


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
fi


if [[ $MODE == "XSEC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Checking xsec friends directory                                                       #"
    echo "##############################################################################################"
    python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsdcache-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
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
    python shapes/produce_shapes_tauid_es.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 4 --num-threads 8 \
        --vs-jet-wp $WP \
        --optimization-level 1 --skip-systematic-variations \
        --special-analysis "TauID_ES" \
        --control-plot-set ${VARIABLES} \
        --output-file $shapes_output  --xrootd  --validation-tag $TAG 
fi


# TODO: check this LOCAL part
PROCESSES="emb"
number="_emb_ssos"
if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes_tauid_es.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 3 --num-threads 9 \
        --vs-jet-wp $WP \
        --optimization-level 1 \
        --special-analysis "TauID" \
        --process-selection $PROCESSES \
        --control-plot-set ${VARIABLES} \
        --optimization-level 1 \
        --output-file $shapes_output$number --xrootd --validation-tag $TAG --es
fi


if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_tauid_es.sh $ERA $CHANNEL \
        "singlegraph" $TAG 0 $NTUPLETAG $CONDOR_OUTPUT "TauID_ES" $WP
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

    if [[ $CHANNEL != "mm" ]]; then
        python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile} --do-qcd --do-emb-tt -s TauID_ES
    fi
    if [[ $CHANNEL == "mm" ]]; then
        python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile} --do-qcd -s TauID_ES
    fi

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

    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}*.root
fi


if [[ $MODE == "PLOT-CONTROL-ES" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"

        for CATEGORY in "${dm_categories[@]}"
    do
        for es_sh in "${es_shifts4_0[@]}"
        do 
            python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
            --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category $CATEGORY --energy_scale --es_shift $es_sh --tag $TAG --normalize-by-bin-width
        done
    done
fi

# For the next steps combine need to be installed (if not already done)
# via e.g. source utils/install_combine_tauid.sh

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw_tauid.sh
    
    for cat in "${dm_categories[@]}"
    do
        # for category in "dm_binned"
        if [[ " ${dm_categories[@]} " =~ " $cat " ]]; then
          datacard_output=$datacard_output_dm
        fi

        inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
        
        $CMSSW_BASE/bin/el9_amd64_gcc12/MorphingTauID2017 \
            --base_path=$PWD \
            --input_folder_mt=$shapes_output_synced \
            --input_folder_mm="output/${WP}-${ERA}-mm-${NTUPLETAG}-${TAG}/synced" \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=0 \
            --embedding=1 \
            --verbose=true \
            --postfix=$POSTFIX \
            --use_control_region=true \
            --auto_rebin=true \
            --categories=${cat} \
            --era=$ERA \
            --output=$datacard_output   
    done
fi


if  [[ $MODE == "WORKSPACE" ]]; then 
    source utils/setup_cmssw_tauid.sh
    
    for cat in "${dm_categories[@]}"
    do
        # for category in "dm_binned"
        if [[ " ${dm_categories[@]} " =~ " $cat " ]]; then
          datacard_output=$datacard_output_dm
        fi
        THIS_PWD=${PWD}
        echo $THIS_PWD
        if [ ! -d "output/${datacard_output}" ]; then
            mkdir -p  output/${datacard_output}
        fi

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -i output/$datacard_output/htt_mt_${cat}/ \
            -o workspace_${cat}.root --parallel 4 -m 125 \
            -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
            --PO "map=^.*/EMB_${cat}:r_EMB_${cat}[1,0.5,1.5]" \
            --PO "map=^.*/MUEMB:r_EMB_${cat}[1,0.5,1.5]"
    done
fi

#  2D likelihood scan for tau ID + ES, we vary ID from 0.5 to 1.5 abd ES from -4.0 % to +4.0%

# That's reflected in min/max_id and min/max_es parameters that have corresponding ranges


min_id=0
max_id=0
min_es=0
max_es=0

mH=120

scan_2D_plot_path="scan_2D_"${TAG}

if [[ $MODE == "SCAN_2D" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create 2D scan"

    for cat in "${categories[@]}"
    do
        if [[ " ${dm_categories[@]} " =~ " $cat " ]]; then
            datacard_output=$datacard_output_dm
            min_id=0.5
            max_id=1.5
            min_es=-4.0
            max_es=4.0
        fi
        if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
            datacard_output=$datacard_output_pt
            min_id=0.5
            max_id=1.5
            min_es=-4.0
            max_es=4.0
        fi

        combineTool.py -M T2W -i output/$datacard_output/htt_mt_${cat}/ -o ws_scan_${cat}.root
        

        combineTool.py -M MultiDimFit -n .scan_2D_${cat} -d output/$datacard_output/htt_mt_${cat}/ws_scan_${cat}.root \
            --setParameters ES_${cat}=0.2,r=0.9 --setParameterRanges r=${min_id},${max_id}:ES_${cat}=${min_es},${max_es} \
            --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
            --redefineSignalPOIs ES_${cat},r \
            --floatOtherPOIs=1 --points=400 --algo grid -m ${mH} --alignEdges=1

        echo "[INFO] Moving scan file to datacard folder ..."
        mv higgsCombine.scan_2D_${cat}.MultiDimFit.mH${mH}.root output/$datacard_output/htt_mt_${cat}/

        echo "[INFO] Plotting 2D scan ..."
        echo "[INFO] Input file: " output/$datacard_output/htt_mt_${cat}/higgsCombine.scan_2D_${cat}.MultiDimFit.mH${mH}.root
        echo "But before we create a folder for 2D scans"

        if [ ! -d "${scan_2D_plot_path}" ]; then
            mkdir -p  ${scan_2D_plot_path}
        fi

        python3 tau_id_es_measurement/plot_2D_scan.py --name scan_2D_${cat} --in-path output/$datacard_output/htt_mt_${cat}/ \
        --tau-id-poi ${cat} --tau-es-poi ES_${cat} --outname ${cat}
        mv scan_2D_${cat}* ${scan_2D_plot_path}
        mv 1D_projections_2Dscan_${cat}* ${scan_2D_plot_path}
    done

fi


fix_es=-1.4
fix_id=1.097

probl_nuisance="ES_DM1"

probl_categories=("DM1")

if [[ $MODE == "PROBL_NUIS_SCAN" ]]; then

    source utils/setup_cmssw_tauid.sh

   echo "[INFO] Create 1D scan for problematic nuisance parameter ${probl_nuisance}"

           for cat in "${probl_categories[@]}"
    do
    if [[ " ${dm_categories[@]} " =~ " $cat " ]]; then
        datacard_output=$datacard_output_dm
    fi
    if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
        datacard_output=$datacard_output_pt
    fi

    combineTool.py -M MultiDimFit -n .scan_2D${cat}_check_poi -d output/$datacard_output/htt_mt_${cat}/ws_scan_${cat}.root \
    --setParameters ES_${cat}=${fix_es},r=${fix_id} --setParameterRanges r=0.5,1.5:ES_${cat}=-4.0,4.0 \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ${probl_nuisance} \
    --floatOtherPOIs=1 --points=400 --algo grid -v 2

    echo "[INFO] Moving scan with problematic nuisance parameter file to datacard folder ..."

    mv higgsCombine.nominal_${cat}_check_poi.MultiDimFit.mH120.root output/$datacard_output/htt_mt_${cat}/

    echo "[INFO] Plotting 1D scan ..."

    python3 plot1DScan.py  output/$datacard_output/htt_mt_${cat}/higgsCombine.nominal_${cat}_check_poi.MultiDimFit.mH120.root \
     --POI $probl_nuisance --y-max 12 --output ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}_${probl_nuisance}_scan

    mv ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}_${probl_nuisance}_scan.* output/$datacard_output/htt_mt_${cat}/
    done
fi

# This script sets all necessary fit parameters. Check if they are correctly exported!
. tau_id_es_measurement/tau_id_es_sim_fit_conf.sh

if [[ $MODE == "MULTIFIT" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create Workspace for all the DM datacards"
    combineTool.py -M T2W -i output/$datacard_output_dm/cmb \
                -o out_multidim_dm.root \
                --parallel 3 -m 125 \
                -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
                --PO '"map=^.*/EMB_DM0:r_EMB_DM_0[1,${min_id_dm0},${max_id_dm0}]"' \
                --PO '"map=^.*/EMB_DM1:r_EMB_DM_1[1,${min_id_dm1},${max_id_dm1}]"' \
                --PO '"map=^.*/EMB_DM10_11:r_EMB_DM_10_11[1,${min_id_dm10_11},${max_id_dm10_11}]"'  

    combineTool.py -M MultiDimFit -n .comb_dm_fit -d output/$datacard_output_dm/cmb/out_multidim_dm.root \
    --setParameters ES_DM0=${es_dm0},ES_DM1=${es_dm1},ES_DM10_11=${es_dm10_11},r_EMB_DM_0=${id_dm0},r_EMB_DM_1=${id_dm1},r_EMB_DM_10_11=${id_dm10_11} \
    --setParameterRanges r_EMB_DM_0=${min_id_dm0},${max_id_dm0}:r_EMB_DM_1=${min_id_dm1},${max_id_dm1}:r_EMB_DM_10_11=${min_id_dm10_11},${max_id_dm10_11}:ES_DM0=${min_es_dm0},${max_es_dm0}:ES_DM1=${min_es_dm1},${max_es_dm1}:ES_DM10_11=${min_es_dm10_11},${max_es_dm10_11} \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_DM0,ES_DM1,ES_DM10_11,r_EMB_DM_0,r_EMB_DM_1,r_EMB_DM_10_11 --floatOtherPOIs=1 \
    --points=400 --algo singles

    mv higgsCombine.comb_dm_fit.MultiDimFit.mH120.root output/$datacard_output_dm/cmb/


    # echo "[INFO] Create Workspace for all the pT datacards"
    # combineTool.py -M T2W -i output/$datacard_output_pt/cmb \
    #             -o out_multidim_pt.root \
    #             --parallel 1 -m 125 \
    #             -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
    #             --PO '"map=^.*/EMB_Pt20to25:r_EMB_Pt_20to25[1,${min_id_pt20to25},${max_id_pt20to25}]"' \
    #             --PO '"map=^.*/EMB_Pt25to30:r_EMB_Pt_25to30[1,${min_id_pt25to30},${max_id_pt25to30}]"' \
    #             --PO '"map=^.*/EMB_Pt30to35:r_EMB_Pt_30to35[1,${min_id_pt30to35},${max_id_pt30to35}]"' \
    #             --PO '"map=^.*/EMB_Pt35to40:r_EMB_Pt_35to40[1,${min_id_pt35to40},${max_id_pt35to40}]"' \
    #             --PO '"map=^.*/EMB_PtGt40:r_EMB_Pt_Gt40[1,${min_id_ptgt40},${max_id_ptgt40}]"'

    # combineTool.py -M MultiDimFit -n .comb_pt_fit -d output/$datacard_output_pt/cmb/out_multidim_pt.root \
    # --setParameters ES_Pt20to25=${es_pt20to25},ES_Pt25to30=${es_pt25to30},ES_Pt30to35=${es_pt30to35},ES_Pt35to40=${es_pt35to40},ES_PtGt40=${es_ptgt40},r_EMB_Pt_20to25=${id_pt20to25},r_EMB_Pt_25to30=${id_pt25to30},r_EMB_Pt_30to35=${id_pt30to35},r_EMB_Pt_35to40=${id_pt35to40}, r_EMB_Pt_Gt40=${id_ptgt40} \
    # --setParameterRanges r_EMB_Pt_20to25=${min_id_pt20to25},${max_id_pt20to25}:r_EMB_Pt_25to30=${min_id_pt25to30},${max_id_pt25to30}:r_EMB_Pt_30to35=${min_id_pt30to35},${max_id_pt30to35}:r_EMB_Pt_35to40=${min_id_pt35to40},${max_id_pt35to40}:r_EMB_Pt_Gt40=${min_id_ptgt40},${max_id_ptgt40}:ES_Pt20to25=${min_es_pt20to25},${max_es_pt20to25}:ES_Pt25to30=${min_es_pt25to30},${max_es_pt25to30}:ES_Pt30to35=${min_es_pt30to35},${max_es_pt30to35}:ES_Pt35to40=${min_es_pt35to40},${max_es_pt35to40}:ES_PtGt40=${min_es_ptgt40},${max_es_ptgt40} \
    # --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    # --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    # --redefineSignalPOIs ES_Pt20to25,ES_Pt25to30,ES_Pt30to35,ES_Pt35to40,ES_PtGt40,r_EMB_Pt_20to25,r_EMB_Pt_25to30,r_EMB_Pt_30to35,r_EMB_Pt_35to40,r_EMB_Pt_Gt40 --floatOtherPOIs=1 \
    # --points=400 --algo singles

    # mv higgsCombine.comb_pt_fit.MultiDimFit.mH120.root output/$datacard_output_pt/cmb/

fi

min_id_sep=0
max_id_sep=0

min_es_sep=0
max_es_sep=0

cent_id_sep=0
cent_es_sep=0

id_fit_stri=""
map_str=''


if [[ $MODE == "MULTIFIT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create Workspace for all the datacards (fitting separately in every DM category)"    

        for cat in "${categories[@]}"
    do
        if [[ " ${dm_categories[@]} " =~ " $cat " ]]; then
            datacard_output=$datacard_output_dm
        fi
        if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
            datacard_output=$datacard_output_pt
        fi

    export cat
    . tau_id_es_measurement/tau_id_es_sim_fit_conf.sh

    echo "My values for ${cat}"
    echo ${id_fit_stri}
    echo ${min_id_sep}, ${max_id_sep}

    combineTool.py -M T2W -i output/$datacard_output/htt_mt_${cat} \
        -o out_multidim_${cat}_sep_cat.root \
        --parallel 1 -m ${mH} \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO ${map_str} \

    combineTool.py -M MultiDimFit -n .comb_sep_fit_${cat} -d output/$datacard_output/htt_mt_${cat}/out_multidim_${cat}_sep_cat.root \
    --setParameters ES_${cat}=${cent_es_sep},r_EMB_${id_fit_stri}=${cent_id_sep} \
    --setParameterRanges r_EMB_${id_fit_stri}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep} \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_${cat},r_EMB_${id_fit_stri} --floatOtherPOIs=1 \
    --points=400 --algo singles -m ${mH}

    mv higgsCombine.comb_sep_fit_${cat}.MultiDimFit.mH${mH}.root output/$datacard_output/htt_mt_${cat}/
 done
fi


if [[ $MODE == "POSTFIT_MULT" ]]; then
    source utils/setup_cmssw_tauid.sh

    WORKSPACE=output/$datacard_output_dm/cmb/out_multidim_dm.root
    echo "[INFO] Printing fit result for category $(basename $RESDIR)"
    FITFILE=output/$datacard_output_dm/cmb/fitDiagnostics_dm.${ERA}.root
   
    combineTool.py -M FitDiagnostics  -d ${WORKSPACE} -m ${mH} \
    --setParameters ES_DM0=${es_dm0},ES_DM1=${es_dm1},ES_DM10_11=${es_dm10_11},r_EMB_DM_0=${id_dm0},r_EMB_DM_1=${id_dm1},r_EMB_DM_10_11=${id_dm10_11} \
    --setParameterRanges r_EMB_DM_0=${min_id_dm0},${max_id_dm0}:r_EMB_DM_1=${min_id_dm1},${max_id_dm1}:r_EMB_DM_10_11=${min_id_dm10_11},${max_id_dm10_11}:ES_DM0=${min_es_dm0},${max_es_dm0}:ES_DM1=${min_es_dm1},${max_es_dm1}:ES_DM10_11=${min_es_dm10_11},${max_es_dm10_11} \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_DM0,ES_DM1,ES_DM10_11,r_EMB_DM_0,r_EMB_DM_1,r_EMB_DM_10_11  \
    --parallel 16   -v2 --robustHesse 1 --saveShapes --saveWithUncertainties
    mv fitDiagnostics.Test.root $FITFILE
    mv higgsCombine.Test.FitDiagnostics.mH${mH}.root output/$datacard_output_dm/cmb/
    echo "[INFO] Already built Prefit/Postfit shapes"

    python3 postfitter/postfitter.py -in ${FITFILE} -out output/${datacard_output_dm}/cmb/ --era ${ERA}

    # echo " DM finished, now pT"

    # WORKSPACE=output/$datacard_output_pt/cmb/out_multidim_pt.root
    # echo "[INFO] Printing fit result for category $(basename $RESDIR)"
    # FILE=output/$datacard_output_pt/cmb/postfitshape_pt.root
    # FITFILE=output/$datacard_output_pt/cmb/fitDiagnostics_pt.${ERA}.root

    # combineTool.py -M MultiDimFit -n .comb_pt_fit -d output/$datacard_output_pt/cmb/out_multidim_pt.root \
    # --setParameters ES_Pt20to25=${es_pt20to25},ES_Pt25to30=${es_pt25to30},ES_Pt30to35=${es_pt30to35},ES_Pt35to40=${es_pt35to40},ES_PtGt40=${es_ptgt40},r_EMB_Pt_20to25=${id_pt20to25},r_EMB_Pt_25to30=${id_pt25to30},r_EMB_Pt_30to35=${id_pt30to35},r_EMB_Pt_35to40=${id_pt35to40},r_EMB_Pt_Gt40=${id_ptgt40} \
    # --setParameterRanges r_EMB_Pt_20to25=${min_id_pt20to25},${max_id_pt20to25}:r_EMB_Pt_25to30=${min_id_pt25to30},${max_id_pt25to30}:r_EMB_Pt_30to35=${min_id_pt30to35},${max_id_pt30to35}:r_EMB_Pt_35to40=${min_id_pt35to40},${max_id_pt35to40}:r_EMB_Pt_Gt40=${min_id_ptgt40},${max_id_ptgt40}:ES_Pt20to25=${min_es_pt20to25},${max_es_pt20to25}:ES_Pt25to30=${min_es_pt25to30},${max_es_pt25to30}:ES_Pt30to35=${min_es_pt30to35},${max_es_pt30to35}:ES_Pt35to40=${min_es_pt35to40},${max_es_pt35to40}:ES_PtGt40=${min_es_ptgt40},${max_es_ptgt40} \
    # --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    # --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    # --redefineSignalPOIs ES_Pt20to25,ES_Pt25to30,ES_Pt30to35,ES_Pt35to40,ES_PtGt40,r_EMB_Pt_20to25,r_EMB_Pt_25to30,r_EMB_Pt_30to35,r_EMB_Pt_Gt40 --parallel 16   -v2 --robustHesse 1 --saveShapes --saveWithUncertainties

    # mv fitDiagnostics_pt.Test.root $FITFILE
    # mv higgsCombine.Test.FitDiagnostics.mH${mH}.root output/$datacard_output_pt/cmb/
    # echo "[INFO] Already built Prefit/Postfit shapes"

    # python3 postfitter/postfitter.py -in ${FITFILE} -out output/${datacard_output_pt}/cmb/ --era ${ERA}

    # FILE=output/$datacard_output_pt/cmb/postfitshape_pt.${ERA}.root

    exit 0
fi

if [[ $MODE == "PLOT-MULTIPOSTFIT" ]]; then
    source utils/setup_root.sh



    for cat in "${categories[@]}" 
    do
        if [[ " ${dm_categories[@]} " =~ " $cat " ]]; then
            WORKSPACE=output/$datacard_output_dm/cmb/out_multidim_dm.root
            FILE=output/$datacard_output_dm/cmb/postfitshape.${ERA}.root
        fi
        if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
            WORKSPACE=output/$datacard_output_pt/cmb/out_multidim_pt.root
            FILE=output/$datacard_output_pt/cmb/postfitshape.${ERA}.root
        fi


        # create output folder if it does not exist
        if [ ! -d "output/postfitplots_emb_${TAG}_multifit/" ]; then
            mkdir -p output/postfitplots_emb_${TAG}_multifit/${WP}
        fi
        echo "[INFO] Postfits plots for category $cat"
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category $cat --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP} --prefit
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category $cat --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP}
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category 100 --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP} --prefit
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category 100 --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP}
    done
    exit 0
fi

if [[ $MODE == "POI_CORRELATION" ]]; then
    source utils/setup_root.sh
    FITFILE_dm=output/$datacard_output_dm/cmb/fitDiagnostics_dm.${ERA}.root
    # python corr_plot.py $ERA $FITFILE_dm
    python tau_id_es_measurement/poi_correlation.py $ERA $FITFILE_dm

    # FITFILE_pt=output/$datacard_output_pt/cmb/fitDiagnostics_pt.${ERA}.root
    # # python corr_plot.py $ERA $FITFILE_pt
    # python tau_id_es_measurement/poi_correlation.py $ERA $FITFILE_pt
fi



if [[ $MODE == "IMPACTS_ALL" ]]; then
    source utils/setup_cmssw_tauid.sh

    if [ ! -d "$impact_path/${ERA}/${CHANNEL}/${WP}" ]; then
        mkdir -p  $impact_path/${ERA}/${CHANNEL}/${WP}
    fi

        for cat in "${categories[@]}"

    do
        if [[ " ${dm_categories[@]} " =~ " $cat " ]]; then
            WORKSPACE_IMP=output/$datacard_output_dm/htt_mt_${cat}/out_multidim_${cat}_sep_cat.root
        fi
        if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
            WORKSPACE_IMP=output/$datacard_output_pt/htt_mt_${cat}/out_multidim_${cat}_sep_cat.root
        fi

        export cat
        . tau_id_es_measurement/tau_id_es_sim_fit_conf.sh

        echo "My values for ${cat}"
        echo ${id_fit_stri}
        echo ${min_id_sep}, ${max_id_sep}

    combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 123 \
        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${id_fit_stri}=${cent_id_sep} \
        --setParameterRanges r_EMB_${id_fit_stri}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep} \
        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
        --parallel 16 --doInitialFit 

    combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 123 \
        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${id_fit_stri}=${cent_id_sep} \
        --setParameterRanges r_EMB_${id_fit_stri}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep} \
        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
        --parallel 16 --doFits 

    combineTool.py -M Impacts -d $WORKSPACE_IMP -m 123 -o tauid_${WP}_impacts_r_${cat}.json  

    plotImpacts.py -i tauid_${WP}_impacts_r_${cat}.json -o tauid_${WP}_impacts_r_${cat}
    # # cleanup the fit files
    rm higgsCombine_paramFit*.root
    # rm robustHesse_paramFit*.root
    mv tauid_${WP}_impacts_r_${cat}* $impact_path/${ERA}/${CHANNEL}/${WP}
    done

    exit 0
fi
