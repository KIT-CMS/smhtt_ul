export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNELS_str=$1
IFS=',' read -r -a CHANNELS <<< "${CHANNELS_str}"
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5
WP=$6
WP_VSe=$7
# For producing correction libs of a given era and channel! All files for different wp should be given with their tags.
WP_list_parse=${8:-"Medium,Tight"}
IFS=',' read -r -a WP_list <<< "${WP_list_parse}"
WP_VSe_list_parse=${9:-"VVLoose"}
IFS=',' read -r -a WP_VSe_list <<< "${WP_VSe_list_parse}"
TAG_list_parse=${10:-"M_post_8to4,T_post_8to4"}
IFS=',' read -r -a TAG_list <<< "${TAG_list_parse}"

echo $NTUPLETAG
echo $WP

VARIABLES="m_vis"
POSTFIX="-TauID_ES"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Debuggung breakpoint()with ipdb:
# pip3 install ipdb
export PYTHONBREAKPOINT="ipdb.set_trace"

# [INFO] tau_id_es_measurement/tau_id_es_sim_fit_conf.sh contains all fit parameters.

# Datacard Setup

datacard_output_pt="datacards_pt_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_dm="datacards_dm_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_incl="datacards_incl_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

# datacard_output_dm_pt="datacards_dm_pt_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"
datacard_output_dm_pt="datacards_dm_pt_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}_VSe${WP_VSe}"

poi_path="poi_corr_${TAG}"

impact_path="impacts_${TAG}"


echo "MY WP,WP_VSe is: " ${WP} ${WP_VSe}
echo "My out path is: ${shapes_output}"
echo "My synchpath is ${shapes_output_synced}"

# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "FRIENDS: ${FRIENDS}"
echo "XSEC: ${XSEC_FRIENDS}"

categories=("DM1" "DM1_PT20_40")
# "DM11_PT20_40" sometimes does not have ZL => DY param breaks workspace ???
all_categories=("DM0" "DM1" "DM10" "DM11" \
"DM0_PT20_40" "DM1_PT20_40" "DM10_PT20_40" "DM11_PT20_40" \
"DM0_PT40_200" "DM1_PT40_200" "DM10_PT40_200" "DM11_PT40_200")
dm_categories=("DM0" "DM1" "DM10_11")

# Generates es_shifts from -8.0 to 4.0 in 0.1 steps:
es_shifts=()
for i in $(seq -80 40); do
    shift_val=$(printf "%.1f" "$(echo "${i} / 10" | bc -l)")
    if [[ $shift_val == -* ]]; then
        # Remove minus and replace the dot with "p"
        formatted=${shift_val#-}
        formatted=${formatted/./p}
        es_shifts+=("embminus${formatted}")
    else
        formatted=${shift_val/./p}
        es_shifts+=("emb${formatted}")
    fi
done
echo "${es_shifts[@]}"

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
    python3 friends/build_friend_tree.py --basepath ${KINGMAKER_BASEDIR_XROOTD} --outputpath root://cmsdcache-kit-disk.gridka.de/${XSEC_FRIENDS} --nthreads 20
fi


echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNELS_str} -${ERA}-${NTUPLETAG}                                         #"
echo "##############################################################################################"


if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}

        if [ ! -d "${shapes_output}" ]; then
            mkdir -p ${shapes_output}
        fi

        python shapes/produce_shapes_tauid_es.py --channels ${CHANNEL} \
            --directory ${NTUPLES} \
            --${CHANNEL}-friend-directory ${XSEC_FRIENDS} \
            --era ${ERA} --num-processes 4 --num-threads 8 \
            --vs-jet-wp ${WP} \
            --optimization-level 1 --skip-systematic-variations \
            --special-analysis "TauID_ES" \
            --control-plot-set ${VARIABLES} \
            --output-file ${shapes_output}  --xrootd  --validation-tag ${TAG}
    done
fi


# TODO: check this LOCAL part
PROCESSES="emb"
number="_emb_ssos"
if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh $CHANNEL $ERA $NTUPLETAG $TAG $MODE $WP

        python shapes/produce_shapes_tauid_es.py --channels ${CHANNEL} \
            --directory ${NTUPLES} \
            --${CHANNEL}-friend-directory ${XSEC_FRIENDS} \
            --era ${ERA} --num-processes 3 --num-threads 9 \
            --vs-jet-wp ${WP} \
            --optimization-level 1 \
            --special-analysis "TauID" \
            --process-selection ${PROCESSES} \
            --control-plot-set ${VARIABLES} \
            --optimization-level 1 \
            --output-file ${shapes_output}${number} --xrootd --validation-tag ${TAG} --es
    done
fi


if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        if [ ! -d "${CONDOR_OUTPUT}" ]; then
            mkdir -p ${CONDOR_OUTPUT}
        fi

        echo "[INFO] Running on Condor"
        echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
        bash submit/submit_shape_production_tauid_es.sh ${ERA} ${CHANNEL} \
            "singlegraph" ${TAG} 0 ${NTUPLETAG} ${CONDOR_OUTPUT} "TauID_ES" ${WP}
        echo "[INFO] Jobs submitted"
    done
fi


if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}

        echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
        hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
    done
fi


if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"

    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}

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
    done
fi


if [[ $MODE == "PLOT_CONTROL_ES" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        if [[ $CHANNEL != "mm" ]]; then
            for CATEGORY in "${all_categories[@]}"
            do
                for es_sh in "${es_shifts[@]}"
                do 
                    python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
                    --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category ${CATEGORY} --energy_scale --es_shift ${es_sh} --tag ${TAG} --normalize-by-bin-width
                done
            done
        fi
        if [[ $CHANNEL == "mm" ]]; then
                    python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
                    --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category control_region --energy_scale --tag $TAG --normalize-by-bin-width
        fi
    done
fi

# For the next steps combine need to be installed (if not already done)
# via e.g. source utils/install_combine_tauid.sh

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw_tauid.sh
    # all_categories=("DM11_PT20_40")
    for cat in "${all_categories[@]}"
    do
        # for category in "dm_binned"
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
        datacard_output=${datacard_output_dm_pt}
        fi
        
        $CMSSW_BASE/bin/el9_amd64_gcc12/MorphingTauID2017 \
            --base_path=${PWD} \
            --input_folder_mt="output/${WP}-${ERA}-mt-${NTUPLETAG}-${TAG}/synced" \
            --input_folder_mm="output/${WP}-${ERA}-mm-${NTUPLETAG}-${TAG}/synced" \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=0 \
            --embedding=1 \
            --verbose=true \
            --postfix=${POSTFIX} \
            --use_control_region=true \
            --auto_rebin=true \
            --categories=${cat} \
            --era=${ERA} \
            --output=${datacard_output} 
        
        # Add rate parameter for DY inclusive scaling:
        for file_mt in output/${datacard_output}/htt_mt_${cat}/htt_mt_*.txt; do
            echo "[Datacard file to use]: ${file_mt}"
            sed -i '$s/$/\nr_DY_incl_'${cat}' rateParam * EMB_'${cat}' 1.0 [0.8,1.2]/' "${file_mt}"
            sed -i '$s/$/\nr_DY_incl_'${cat}' rateParam * ZL 1.0 [0.8,1.2]/' "${file_mt}"
            sed -i '$s/$/\nr_DY_incl_'${cat}' rateParam * ZJ 1.0 [0.8,1.2]/' "${file_mt}"
        done
        for file_mm in output/${datacard_output}/htt_mt_${cat}/htt_mm_*.txt; do
            sed -i '$s/$/\nr_DY_incl_'${cat}' rateParam * MUEMB 1.0 [0.8,1.2]/' "${file_mm}"
        done
    done
fi


if  [[ $MODE == "WORKSPACE" ]]; then 
    source utils/setup_cmssw_tauid.sh
    # all_categories=("DM11_PT20_40")
    for cat in "${all_categories[@]}"
    do
        # for category in "dm_binned"
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
          datacard_output=${datacard_output_dm_pt}
        fi
        THIS_PWD=${PWD}
        echo $THIS_PWD
        if [ ! -d "output/${datacard_output}" ]; then
            mkdir -p  output/${datacard_output}
        fi

        # echo "[INFO] Create 2D_Scan_Workspace for datacard in ${cat} category."
        # combineTool.py -M T2W -i output/$datacard_output/htt_mt_${cat}/ \
        #     -o workspace_${cat}_2dscan.root --parallel 4 -m 125 \
        #     -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        #     --PO "map=^.*/EMB_${cat}:r_EMB_${cat}[1,0.5,1.5]"

        echo "[INFO] Create Multifit_Workspace for datacard in ${cat} category."
        combineTool.py -M T2W -i output/$datacard_output/htt_mt_${cat}/ \
            -o workspace_${cat}_multidimfit.root --parallel 4 -m 125 \
            -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
            --PO "map=^.*/EMB_${cat}:r_EMB_${cat}[1,0.5,1.5]"
    done
fi

            # --PO "map=^.*/EMB_${cat}:r_DY[1,0.8,1.2]" \ This breaks the multifit !!!
#  2D likelihood scan for tau ID + ES, we vary ID from 0.5 to 1.5 abd ES from -8.0 % to +4.0%

# That's reflected in min/max_id and min/max_es parameters that have corresponding ranges


min_id=0
max_id=0
min_es=0
max_es=0

mH=125

scan_2D_plot_path="scan_2D_"${TAG}

if [[ $MODE == "SCAN_2D" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create 2D scan"
    # all_categories=("DM1_PT20_40" "DM10_PT20_40" "DM11_PT20_40" "DM0_PT40_200" "DM1_PT40_200" "DM10_PT40_200" "DM11_PT40_200")
    for cat in "${all_categories[@]}"
    do
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
            datacard_output=${datacard_output_dm_pt}
            min_id=0.5
            max_id=1.5
            min_es=-8.0
            max_es=4.0
        fi
        if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
            datacard_output=$datacard_output_pt
            min_id=0.5
            max_id=1.5
            min_es=-8.0
            max_es=4.0
        fi

        combineTool.py -M MultiDimFit -n .scan_2D_${cat} -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_multidimfit.root \
            --setParameters ES_${cat}=-1.0,r_EMB_${cat}=0.9,r_DY_incl_${cat}=1.0 --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es}:r_DY_incl_${cat}=0.8,1.2 \
            --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
            --redefineSignalPOIs ES_${cat},r_EMB_${cat} \
            --floatOtherPOIs=1 --points=400 --algo grid -m ${mH} --alignEdges=1 --parallel 12

        echo "[INFO] Moving scan file to datacard folder ..."
        mv higgsCombine.scan_2D_${cat}.MultiDimFit.mH${mH}.root output/$datacard_output/htt_mt_${cat}/

        echo "[INFO] Plotting 2D scan ..."
        echo "[INFO] Input file: " output/$datacard_output/htt_mt_${cat}/higgsCombine.scan_2D_${cat}.MultiDimFit.mH${mH}.root
        echo "But before we create a folder for 2D scans"

        if [ ! -d "${scan_2D_plot_path}" ]; then
            mkdir -p  ${scan_2D_plot_path}
        fi

        python3 tau_id_es_measurement/plot_2D_scan.py --name scan_2D_${cat} --in-path output/$datacard_output/htt_mt_${cat}/ \
        --tau-id-poi ${cat} --tau-es-poi ES_${cat} --outname ${cat} --nbins 20
        mv scan_2D_${cat}* ${scan_2D_plot_path}
        mv 1D_projections_2Dscan_${cat}* ${scan_2D_plot_path}
        mv 1D_profiles_2Dscan_${cat}* ${scan_2D_plot_path}
    done

fi


fix_es=-1.4
fix_id=1.097

probl_nuisance="ES_DM1"

probl_categories=("DM1")

if [[ $MODE == "PROBL_NUIS_SCAN" ]]; then

    source utils/setup_cmssw_tauid.sh

   echo "[INFO] Create 1D scan for problematic nuisance parameter ${probl_nuisance}"
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh $CHANNEL $ERA $NTUPLETAG $TAG $MODE $WP
        for cat in "${probl_categories[@]}"
        do
            if [[ " ${dm_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output_dm_pt}
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
    done
fi

# This script sets all necessary fit parameters. Check if they are correctly exported!
. tau_id_es_measurement/tau_id_es_sim_fit_conf.sh

if [[ $MODE == "MULTIFIT" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create Workspace for all the DM datacards"
    combineTool.py -M T2W -i output/${datacard_output_dm_pt}/cmb \
                -o out_multidim_dm.root \
                --parallel 3 -m 125 \
                -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
                --PO '"map=^.*/EMB_DM0:r_EMB_DM0[1,${min_id_dm0},${max_id_dm0}]"' \
                --PO '"map=^.*/EMB_DM1:r_EMB_DM1[1,${min_id_dm1},${max_id_dm1}]"' \
                --PO '"map=^.*/EMB_DM10_11:r_EMB_DM10_11[1,${min_id_dm10_11},${max_id_dm10_11}]"'  

    combineTool.py -M MultiDimFit -n .comb_dm_fit -d output/${datacard_output_dm_pt}/cmb/out_multidim_dm.root \
    --setParameters ES_DM0=${es_dm0},ES_DM1=${es_dm1},ES_DM10_11=${es_dm10_11},r_EMB_DM0=${id_dm0},r_EMB_DM1=${id_dm1},r_EMB_DM10_11=${id_dm10_11} \
    --setParameterRanges r_EMB_DM0=${min_id_dm0},${max_id_dm0}:r_EMB_DM1=${min_id_dm1},${max_id_dm1}:r_EMB_DM10_11=${min_id_dm10_11},${max_id_dm10_11}:ES_DM0=${min_es_dm0},${max_es_dm0}:ES_DM1=${min_es_dm1},${max_es_dm1}:ES_DM10_11=${min_es_dm10_11},${max_es_dm10_11} \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_DM0,ES_DM1,ES_DM10_11,r_EMB_DM0,r_EMB_DM1,r_EMBDM_10_11 --floatOtherPOIs=1 \
    --points=400 --algo singles

    mv higgsCombine.comb_dm_fit.MultiDimFit.mH120.root output/${datacard_output_dm_pt}/cmb/


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
    # categories=("DM0")
    for cat in "${all_categories[@]}"
    do
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
            datacard_output=${datacard_output_dm_pt}
        fi
        if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
            datacard_output=$datacard_output_pt
        fi

        export cat
        . tau_id_es_measurement/tau_id_es_sim_fit_conf.sh

        echo "My values for ${cat}"
        echo ${min_id_sep}, ${max_id_sep}


        combineTool.py -M MultiDimFit -n .comb_sep_fit_${cat} -d output/$datacard_output/htt_mt_${cat}/workspace_${cat}_multidimfit.root \
        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
        --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.8,1.2 \
        --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001,Minuit2,Migrad,0:0.01 --cminPreScan \
        --redefineSignalPOIs ES_${cat},r_EMB_${cat} --floatOtherPOIs=1 --points=400 --algo singles -m ${mH} \
        --saveWorkspace --saveFitResult --verbose 2
        
        ROOTFILE="higgsCombine.comb_sep_fit_${cat}.MultiDimFit.mH${mH}.root"

        # Add the WP and WP_VSe to the ROOT file
        root -l -b <<-EOF
        {
            // Open the file for update
            TFile *f = TFile::Open("${ROOTFILE}", "UPDATE");
            if (!f || f->IsZombie()) {
                std::cerr << "Error opening file ${ROOTFILE}" << std::endl;
                exit(1);
            }
            // Create a TParameter to hold the WP value (or any string metadata you need)
            // For a string, you might use a TNamed:
            TNamed *wpInfo = new TNamed("WP", "${WP}");
            wpInfo->Write("WP", TObject::kOverwrite);
            TNamed *wpVSeInfo = new TNamed("WP_VSe", "${WP_VSe}");
            wpVSeInfo->Write("WP_VSe", TObject::kOverwrite);
            f->Close();
        }
EOF

        mv multidimfit.comb_sep_fit_${cat}.root output/${datacard_output}/htt_mt_${cat}/
        mv higgsCombine.comb_sep_fit_${cat}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/
    done
fi


if [[ $MODE == "POSTFIT_MULT" ]]; then
    source utils/setup_cmssw_tauid.sh

    WORKSPACE=output/$datacard_output_dm/cmb/out_multidim_dm.root
    echo "[INFO] Printing fit result for category $(basename $RESDIR)"
    FITFILE=output/$datacard_output_dm/cmb/fitDiagnostics_dm.${ERA}.root
   
    combineTool.py -M FitDiagnostics  -d ${WORKSPACE} -m ${mH} \
    --setParameters ES_DM0=${es_dm0},ES_DM1=${es_dm1},ES_DM10_11=${es_dm10_11},r_EMB_DM0=${id_dm0},r_EMB_DM1=${id_dm1},r_EMB_DM10_11=${id_dm10_11} \
    --setParameterRanges r_EMB_DM0=${min_id_dm0},${max_id_dm0}:r_EMB_DM1=${min_id_dm1},${max_id_dm1}:r_EMB_DM10_11=${min_id_dm10_11},${max_id_dm10_11}:ES_DM0=${min_es_dm0},${max_es_dm0}:ES_DM1=${min_es_dm1},${max_es_dm1}:ES_DM10_11=${min_es_dm10_11},${max_es_dm10_11} \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_DM0,ES_DM1,ES_DM10_11,r_EMB_DM0,r_EMB_DM1,r_EMB_DM10_11  \
    --parallel 16   -v2 --robustHesse 1 --saveShapes --saveWithUncertainties
    mv fitDiagnostics.Test.root ${FITFILE}
    mv higgsCombine.Test.FitDiagnostics.mH${mH}.root output/$datacard_output_dm/cmb/
    echo "[INFO] Already built Prefit/Postfit shapes"

    python3 postfitter/postfitter.py -in ${FITFILE} -out output/${datacard_output_dm}/cmb/ --era ${ERA} --category ""

fi


if [[ $MODE == "POSTFIT_MULT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    all_categories=("DM1_PT40_200")
    for cat in "${all_categories[@]}"
    do
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
            datacard_output=${datacard_output_dm_pt}
        fi
        if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
            datacard_output=$datacard_output_pt
        fi
        export cat
        . tau_id_es_measurement/tau_id_es_sim_fit_conf.sh

        WORKSPACE=output/$datacard_output/htt_mt_${cat}/workspace_${cat}_multidimfit.root
        echo "[INFO] Printing fit result for category $(basename $RESDIR)"
        FITFILE=output/${datacard_output_dm_pt}/htt_mt_${cat}/fitDiagnostics_${cat}.${ERA}.root
    
        combineTool.py -M FitDiagnostics  -d ${WORKSPACE} -m ${mH} \
        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
        --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.8,1.2 \
        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
        --redefineSignalPOIs ES_${cat},r_EMB_${cat} \
        --parallel 16 -v2 --robustHesse 1 --saveShapes --saveWithUncertainties
        mv fitDiagnostics.Test.root ${FITFILE}
        mv higgsCombine.Test.FitDiagnostics.mH${mH}.root output/${datacard_output_dm_pt}/htt_mt_${cat}/
        echo "[INFO] Already built Prefit/Postfit shapes"

        python3 postfitter/postfitter.py -in ${FITFILE} -out output/${datacard_output_dm_pt}/htt_mt_${cat}/ --era ${ERA} --category ${cat}

    done
fi


if [[ $MODE == "GOF_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    # categories=("DM1")
    mH=125
    for cat in "${all_categories[@]}"
    do
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
            datacard_output=${datacard_output_dm_pt}
        fi
        if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
            datacard_output=$datacard_output_pt
        fi

        WORKSPACE=output/$datacard_output/htt_mt_${cat}/workspace_${cat}_multidimfit.root
        echo "[INFO] Make gof calculations $(basename $RESDIR)"
    
        combineTool.py -M GoodnessOfFit ${WORKSPACE} --algo saturated -m ${mH} --freezeParameters MH -n .GOF_data_${cat} 
        combineTool.py -M GoodnessOfFit ${WORKSPACE} --algo saturated -m ${mH} --freezeParameters MH -n .GOF_toys_${cat} -t 1000 \
        --toysFrequentist 
        
        echo "[INFO] Moving GOF files to datacard folder ..."

        mv higgsCombine.GOF_data_${cat}.GoodnessOfFit.mH${mH}.root output/$datacard_output/htt_mt_${cat}/
        mv higgsCombine.GOF_toys_${cat}.GoodnessOfFit.mH${mH}.123456.root output/$datacard_output/htt_mt_${cat}/

        echo "[INFO] Collecting GOF results in json file and plotting ..."
        
        combineTool.py -M CollectGoodnessOfFit \
        --input output/$datacard_output/htt_mt_${cat}/higgsCombine.GOF_data_${cat}.GoodnessOfFit.mH${mH}.root \
         output/$datacard_output/htt_mt_${cat}/higgsCombine.GOF_toys_${cat}.GoodnessOfFit.mH${mH}.123456.root \
        -o output/$datacard_output/htt_mt_${cat}/gof_${cat}.json -m ${mH}

        plotGof.py output/$datacard_output/htt_mt_${cat}/gof_${cat}.json --statistic saturated --mass 125.0 \
        -o output/$datacard_output/htt_mt_${cat}/gof_${cat}

    done
fi


if [[ $MODE == "PLOT_MULTIPOSTFIT" ]]; then
    source utils/setup_root.sh

    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        for cat in "${all_categories[@]}"
        do
            if [[ " ${dm_categories[@]} " =~ " ${cat} " ]]; then
                FILE=output/$datacard_output_dm/cmb/postfitshape.${ERA}.root
            fi
            if [[ " ${pt_categories[@]} " =~ " ${cat} " ]]; then
                FILE=output/$datacard_output_pt/cmb/postfitshape.${ERA}.root
            fi


            # create output folder if it does not exist
            if [ ! -d "output/postfitplots_emb_${TAG}_multifit/" ]; then
                mkdir -p output/postfitplots_emb_${TAG}_multifit/${WP}
            fi
            echo "[INFO] Postfits plots for category ${cat}"
            if [[ ${CHANNEL} != "mm" ]]; then
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category ${cat} --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP} --prefit
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category ${cat} --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP}
            fi
            if [[ ${CHANNEL} == "mm" ]]; then
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category "Control Region" --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP} --prefit
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category "Control Region" --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP}
            fi
        done
    done
    exit 0
fi

# Postfits ignores faulti fits, thus plotting them could ask about non existing files of bad fits!
if [[ $MODE == "PLOT_MULTIPOSTFIT_SEP" ]]; then
    source utils/setup_root.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        # categories=("DM1_PT20_40")
        for cat in "${all_categories[@]}"
        do
            if [[ " ${all_categories[@]} " =~ " ${cat} " ]]; then
                FILE=output/${datacard_output_dm_pt}/htt_mt_${cat}/postfitshape.${cat}.${ERA}.root
            fi
            # if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
            #     FILE=output/$datacard_output_pt/cmb/postfitshape.${ERA}.root
            # fi


            # create output folder if it does not exist
            if [ ! -d "output/postfitplots_emb_${TAG}_multifit_sep/" ]; then
                mkdir -p output/postfitplots_emb_${TAG}_multifit_sep/${WP}
            fi
            echo "[INFO] Postfits plots for category ${cat}"
            if [[ ${CHANNEL} != "mm" ]]; then
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category $cat --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --prefit
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category $cat --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP}
            fi
            if [[ ${CHANNEL} == "mm" ]]; then
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category "Control Region" --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --prefit
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category "Control Region" --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP}
            fi
        done
    done
    exit 0
fi

if [[ $MODE == "POI_CORRELATION" ]]; then
    source utils/setup_root.sh
    FITFILE_dm=output/$datacard_output_dm/cmb/fitDiagnostics_dm.${ERA}.root
    if [ ! -d "${poi_path}/${ERA}/${CHANNEL}/${WP}" ]; then
            mkdir -p  ${poi_path}/${ERA}/cmb/${WP}
    fi
    python tau_id_es_measurement/poi_correlation.py $ERA $FITFILE_dm "DM"
    mv "${ERA}_DM_POIS_correlations_ID_ES.png" ${poi_path}/${ERA}/cmb/${WP}
fi

if [[ $MODE == "POI_CORRELATION_SEP" ]]; then
    source utils/setup_root.sh
    for cat in "${all_categories[@]}"
    do
        FITFILE_dm=output/${datacard_output_dm_pt}/htt_mt_${cat}/fitDiagnostics_${cat}.${ERA}.root
        if [ ! -d "${poi_path}/${ERA}/${cat}/${WP}" ]; then
            mkdir -p  ${poi_path}/${ERA}/${cat}/${WP}
        fi
        python tau_id_es_measurement/poi_correlation.py ${ERA} ${FITFILE_dm} ${cat}
        mv "${ERA}_${cat}_POIS_correlations_ID_ES.png" ${poi_path}/${ERA}/${cat}/${WP}
    done
fi



if [[ $MODE == "IMPACTS_ALL" ]]; then
    source utils/setup_cmssw_tauid.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        echo "[INFO] Channel: ${CHANNEL}"
        if [[ ${CHANNEL} != "mm" ]]; then
            source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
            if [ ! -d "$impact_path/${ERA}/${CHANNEL}/${WP}" ]; then
                mkdir -p  $impact_path/${ERA}/${CHANNEL}/${WP}
            fi
            # "DM10_PT20_40" "DM0_PT40_200" "DM10_PT40_200" 
            all_categories=("DM10_PT20_40" "DM0_PT40_200" "DM10_PT40_200")
            for cat in "${all_categories[@]}"

            do
                if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                    WORKSPACE_IMP=output/${datacard_output_dm_pt}/htt_mt_${cat}/workspace_${cat}_multidimfit.root
                fi
                if [[ " ${pt_categories[@]} " =~ " $cat " ]]; then
                    WORKSPACE_IMP=output/$datacard_output_pt/htt_mt_${cat}/out_multidim_${cat}_sep_cat.root
                fi

                export cat
                . tau_id_es_measurement/tau_id_es_sim_fit_conf.sh

                echo "My values for ${cat}"
                echo ${cat}
                echo ${min_id_sep}, ${max_id_sep}

                ### Impacts for r_EMB_DMXY
                combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 125 \
                    --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
                    --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.8,1.2 \
                    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                    --parallel 16 --doInitialFit --redefineSignalPOIs ES_${cat},r_EMB_${cat}

                combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 125 \
                    --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
                    --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.8,1.2 \
                    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                    --parallel 16 --doFits --redefineSignalPOIs r_EMB_${cat}

                combineTool.py -M Impacts -d ${WORKSPACE_IMP} -m 125 -o tauid_${WP}_impacts_r_${cat}.json  --redefineSignalPOIs r_EMB_${cat}

                plotImpacts.py -i tauid_${WP}_impacts_r_${cat}.json -o tauid_${WP}_impacts_r_${cat}
                # # cleanup the fit files
                rm higgsCombine_paramFit*.root
                rm higgsCombine_initialFit*.root
                # rm robustHesse_paramFit*.root
                mv tauid_${WP}_impacts_r_${cat}* $impact_path/${ERA}/${CHANNEL}/${WP}

                ### Impacts for ES_DMXY:
                combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 125 \
                    --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
                    --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.8,1.2 \
                    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                    --parallel 16 --doInitialFit --redefineSignalPOIs ES_${cat}
                
                combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 125 \
                    --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
                    --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.8,1.2 \
                    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                    --parallel 16 --doFits --redefineSignalPOIs ES_${cat}
                
                combineTool.py -M Impacts -d ${WORKSPACE_IMP} -m 125 -o tauid_${WP}_impacts_r_${cat}_ES.json --redefineSignalPOIs ES_${cat}
                
                plotImpacts.py -i tauid_${WP}_impacts_r_${cat}_ES.json -o tauid_${WP}_impacts_r_${cat}_ES
                # # cleanup the fit files
                rm higgsCombine_paramFit*.root
                rm higgsCombine_initialFit*.root
                # rm robustHesse_paramFit*.root
                mv tauid_${WP}_impacts_r_${cat}_ES* $impact_path/${ERA}/${CHANNEL}/${WP}


            done
        fi
    done
fi


# Read out scale factors from the fitfiles. Loop needed for different wps in the datacard path!
if [[ $MODE == "CORRECTION_LIB" ]]; then
    source utils/setup_root.sh

    CHANNELS=("mt")
    for CHANNEL in "${CHANNELS[@]}"
    do
        input_files_list=()
        bin_names_list=()
        for cat in "${all_categories[@]}"
        do
            for VSjet in "${WP_list[@]}"
            do
                for VSe in "${WP_VSe_list[@]}"
                do
                    for TAG_it in "${TAG_list[@]}"
                    do
                        datacard_path="datacards_dm_pt_${TAG_it}/${NTUPLETAG}-${TAG_it}/${ERA}_tauid_${VSjet}_VSe${VSe}"
                        
                        # Check if the file exists
                        if [ ! -f "output/${datacard_path}/htt_mt_${cat}/higgsCombine.comb_sep_fit_${cat}.MultiDimFit.mH125.root" ]; then
                            echo "File output/${datacard_path}/htt_mt_${cat}/higgsCombine.comb_sep_fit_${cat}.MultiDimFit.mH125.root does not exist."
                            continue
                        else
                            # Add file to list of fitfiles
                            input_file="output/${datacard_path}/htt_mt_${cat}/higgsCombine.comb_sep_fit_${cat}.MultiDimFit.mH125.root"
                            input_files_list+=("${input_file}")
                            # Add bin name to list of names
                            bin_names_list+=("${cat}")
                        fi
                    done
                done
            done
        done
        # Join lists into comma-separated strings
        input_files_str=$(IFS=, ; echo "${input_files_list[*]}")
        bin_names_str=$(IFS=, ; echo "${bin_names_list[*]}")

        python3 friends/create_xpog_json_v2.py \
            --user_out_tag "${NTUPLETAG}" \
            --era "${ERA}" \
            --channel "${CHANNEL}" \
            --input_files ${input_files_str} \
            --binnames ${bin_names_str}

        # mv ...
    done

fi