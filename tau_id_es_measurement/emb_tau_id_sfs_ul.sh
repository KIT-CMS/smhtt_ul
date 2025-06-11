export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNELS_str=${1}
IFS=',' read -r -a CHANNELS <<< "${CHANNELS_str}"
ERA=${2}
NTUPLETAG=${3}
TAG=${4}
MODE=${5}
WP=${6}
WP_VSe=${7}
WP_VSmu=${8}
ES_up=${9}
ES_down=${10}
# For producing correction libs of a given era and channel! All files for different wp should be given with their tags.
TAG_list_parse=${11:-"M_post_8to8_flat_data,T_post_8to8_flat_data"}
IFS=',' read -r -a TAG_list <<< "${TAG_list_parse}"
WP_list_parse=${12:-"Medium,Tight"}
IFS=',' read -r -a WP_list <<< "${WP_list_parse}"
WP_VSe_list_parse=${13:-"VVLoose"}
IFS=',' read -r -a WP_VSe_list <<< "${WP_VSe_list_parse}"


echo ${NTUPLETAG}
echo ${WP}

VARIABLES="m_vis"
POSTFIX="-TauID_ES"
ulimit -s unlimited
source utils/setup_ul_samples.sh ${NTUPLETAG} ${ERA}

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


echo "MY WP,WP_VSe,WP_VSmu is: " ${WP} ${WP_VSe} ${WP_VSmu}
echo "My out path is: ${shapes_output}"
echo "My synchpath is ${shapes_output_synced}"

# print the paths to be used
echo "KINGMAKER_BASEDIR: ${KINGMAKER_BASEDIR}"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "FRIENDS: ${FRIENDS}"
echo "XSEC: ${XSEC_FRIENDS}"

# categories=("DM1" "DM1_PT20_40")
all_categories=("DM0" "DM1" "DM1011" \
"DM0_PT20_40" "DM1_PT20_40" "DM1011_PT20_40" \
"DM0_PT40_200" "DM1_PT40_200" "DM1011_PT40_200")
# dm_categories=("DM0" "DM1" "DM1011")

# Generates es_shifts from {ES_down} to ${ES_up} in 0.1 steps:
es_shifts=()
ES_up_int=$(printf "%.0f" "$(echo "${ES_up}*10" | bc -l)")
ES_down_int=$(printf "%.0f" "$(echo "${ES_down}*10" | bc -l)")
for i in $(seq ${ES_down_int} ${ES_up_int}); do
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

# Read out yaml file:
get_yaml_vals() {
    # Expecting two parameters: TAG and cat
    python3 -c "import yaml, sys; 
tag = sys.argv[1]; cat = sys.argv[2]; 
data = yaml.safe_load(open('tau_id_es_measurement/1Dscan_contours.yaml'));
min_id_sep, max_id_sep = data[tag][cat]['ID'];
min_es_sep, max_es_sep = data[tag][cat]['ES'];
cent_id_sep = data[tag][cat]['fit']['ID'];
cent_es_sep = data[tag][cat]['fit']['ES'];
print(min_id_sep, max_id_sep, cent_id_sep, min_es_sep, max_es_sep, cent_es_sep)" "$1" "$2"
}


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


if [[ $MODE == "BINNING" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Producing special binning for ${CHANNELS_str} -${ERA}-${NTUPLETAG}-${TAG}             #"
    echo "##############################################################################################"
    CHANNELS=('mt')
    for CHANNEL in "${CHANNELS[@]}"
    do
        python3 gof/build_binning.py --channel ${CHANNEL} \
            --directory ${NTUPLES} --tag ${TAG} \
            --wp-vsjet ${WP} --wp-vse ${WP_VSe} --wp-vsmu ${WP_VSmu} \
            --era ${ERA} --variables ${VARIABLES} --${CHANNEL}-friend-directory ${XSEC_FRIENDS} \
            --output-folder "config/gof_binning" --DM-categories "${all_categories[@]}"
    done
fi




echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNELS_str} -${ERA}-${NTUPLETAG}                             #"
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
            --vs-ele-wp ${WP_VSe} \
            --vs-mu-wp ${WP_VSmu} \
            --optimization-level 1 --skip-systematic-variations \
            --special-analysis "TauID_ES" \
            --control-plot-set ${VARIABLES} \
            --output-file ${shapes_output}  --xrootd  --validation-tag ${TAG} \
            --es-up ${ES_up} --es-down ${ES_down}
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
            -vs-ele-wp ${WP_VSe} \
            --vs-mu-wp ${WP_VSmu} \
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
        "singlegraph" ${TAG} 0 ${NTUPLETAG} ${CONDOR_OUTPUT} "TauID_ES" ${WP} ${WP_VSe} ${WP_VSmu} ${ES_up} ${ES_down}
        echo "[INFO] Jobs submitted"
    done
fi


if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}

        echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
        hadd -j 5 -n 600 -f ${shapes_rootfile} ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${TAG}/*.root
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
            python shapes/do_estimations.py -e ${ERA} -i ${shapes_rootfile} --do-qcd --do-emb-tt -s TauID_ES --es-up ${ES_up} --es-down ${ES_down}
        fi
        if [[ $CHANNEL == "mm" ]]; then
            python shapes/do_estimations.py -e ${ERA} -i ${shapes_rootfile} --do-qcd -s TauID_ES --es-up ${ES_up} --es-down ${ES_down}
        fi

        echo "##############################################################################################"
        echo "#     synced shapes                                      #"
        echo "##############################################################################################"

        # if the output folder does not exist, create it
        if [ ! -d "${shapes_output_synced}" ]; then
            mkdir -p ${shapes_output_synced}
        fi

        python shapes/convert_to_synced_shapes.py -e ${ERA} \
            -i ${shapes_rootfile} \
            -o ${shapes_output_synced} \
            --variable-selection ${VARIABLES} \
            -n 1 \
            --es-up ${ES_up} \
            --es-down ${ES_down}

        inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
        hadd -f ${shapes_output_synced}/${inputfile} ${shapes_output_synced}/${ERA}-${CHANNEL}*.root
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
                    --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category ${CATEGORY} --energy_scale --es_shift ${es_sh} --tag ${TAG} --es_up ${ES_up} --es-down ${ES_down}
                done
            done
        fi
        if [[ $CHANNEL == "mm" ]]; then
                    python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
                    --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category control_region --energy_scale --tag ${TAG}
        fi
    done
fi

# For the next steps combine need to be installed (if not already done)
# via e.g. source utils/install_combine_tauid.sh

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw_tauid.sh
    # all_categories=("DM0")
    for cat in "${all_categories[@]}"
    do
        # for category in "dm_binned"
        if [[ " ${all_categories[@]} " =~ " ${cat} " ]]; then
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
            sed -i '$s/$/\nr_DY_incl_'${cat}' rateParam * EMB_'${cat}' 1.0 [0.5,1.5]/' "${file_mt}"
            if grep -q "ZL" "${file_mt}"; then
                sed -i '$s/$/\nr_DY_incl_'${cat}' rateParam * ZL 1.0 [0.5,1.5]/' "${file_mt}"
            fi
            sed -i '$s/$/\nr_DY_incl_'${cat}' rateParam * ZJ 1.0 [0.5,1.5]/' "${file_mt}"
        done
        for file_mm in output/${datacard_output}/htt_mt_${cat}/htt_mm_*.txt; do
            sed -i '$s/$/\nr_DY_incl_'${cat}' rateParam * MUEMB 1.0 [0.5,1.5]/' "${file_mm}"
        done
    done
fi


if  [[ $MODE == "WORKSPACE" ]]; then 
    source utils/setup_cmssw_tauid.sh
    # all_categories=("DM0")
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

        echo "[INFO] Create Multifit_Workspace for datacard in ${cat} category."
        combineTool.py -M T2W -i output/${datacard_output}/htt_mt_${cat}/ \
            -o workspace_${cat}_${TAG}_multidimfit.root --parallel 4 -m 125 \
            -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
            --PO "map=^.*/EMB_${cat}:r_EMB_${cat}[1,0.1,1.9]"
        
    done
fi


#  2D likelihood scan for tau ID + ES, we vary ID from 0.5 to 1.5 abd ES from -8.0 % to +8.0%

# That's reflected in min/max_id and min/max_es parameters that have corresponding ranges

min_id=0
max_id=0
min_es=0
max_es=0

mH=125

scan_2D_plot_path="scan_2D_"${TAG}

if [[ $MODE == "SCAN_2D" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create 2D scan folder"
    if [ ! -d "${scan_2D_plot_path}" ]; then
            mkdir -p  ${scan_2D_plot_path}
    fi

    all_categories=("DM0" "DM1" "DM1011")
    for cat in "${all_categories[@]}"
    do
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
            datacard_output=${datacard_output_dm_pt}
            min_id=0.1
            max_id=1.9
            min_es=-8.0
            max_es=8.0
        fi

        # 2D scan ID-ES
        combineTool.py -M MultiDimFit -n .scan_2D_${cat}_${TAG} -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
            --setParameters ES_${cat}=0.0,r_EMB_${cat}=1.0,r_DY_incl_${cat}=1.0 \
            --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es}:r_DY_incl_${cat}=0.5,1.5 \
            --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
            --redefineSignalPOIs ES_${cat},r_EMB_${cat} \
            --floatOtherPOIs=1 --points=841 --algo grid -m ${mH} --alignEdges=1 --parallel 12 --cminDefaultMinimizerStrategy 0

        echo "[INFO] Moving scan file to datacard folder ..."
        mv higgsCombine.scan_2D_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

        
        # 1D scan for r_EMB_${cat} (profiling ES_${cat})
        echo "[INFO] 1D scan for r_EMB_${cat} (profiling ES_${cat})"
        combineTool.py -M MultiDimFit -n .scan_1D_rEMB_${cat}_${TAG} \
            -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
            --setParameters ES_${cat}=0.0,r_EMB_${cat}=1.0,r_DY_incl_${cat}=1.0 \
            --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es}:r_DY_incl_${cat}=0.5,1.5 \
            --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --X-rtd REMOVE_CONSTANT_ZERO_POINT=1 \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
            --redefineSignalPOIs r_EMB_${cat} --algo grid -m ${mH} --parallel 12 --cminDefaultMinimizerStrategy 0 --saveNLL \
            --points=29 --alignEdges=1

        mv higgsCombine.scan_1D_rEMB_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

        combineTool.py -M MultiDimFit -n .scan_1D_ES_${cat}_${TAG} \
            -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
            --setParameters ES_${cat}=0.0,r_EMB_${cat}=1.0,r_DY_incl_${cat}=1.0 \
            --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es}:r_DY_incl_${cat}=0.5,1.5 \
            --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --X-rtd REMOVE_CONSTANT_ZERO_POINT=1 \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
            --redefineSignalPOIs ES_${cat} --algo grid -m ${mH} --parallel 12 --cminDefaultMinimizerStrategy 0 --saveNLL \
            --points=29 --alignEdges=1

        mv higgsCombine.scan_1D_ES_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

        echo "[INFO] Create plots for 2D and 1D scans"
        echo "[INFO] Input file: " output/${datacard_output}/htt_mt_${cat}/higgsCombine.scan_2D_${cat}_${TAG}.MultiDimFit.mH${mH}.root
        # Plotting
        python3 tau_id_es_measurement/plot_2D_scan.py \
        --name-2D scan_2D_${cat}_${TAG} \
        --name-1D-ID scan_1D_rEMB_${cat}_${TAG} \
        --name-1D-ES scan_1D_ES_${cat}_${TAG} \
        --in-path output/${datacard_output}/htt_mt_${cat}/ \
        --tau-id-poi ${cat} --tau-es-poi ES_${cat} --outname ${cat} --tag ${TAG} --nbins 29 \
        --x-range ${min_id} ${max_id} --y-range ${min_es} ${max_es} --scale_range 0.1
        mv scan_2D_${cat}_${TAG}* ${scan_2D_plot_path}
        # mv 1D_projections_2Dscan_${cat}* ${scan_2D_plot_path}
        # mv 1D_profiles_2Dscan_${cat}_${TAG}* ${scan_2D_plot_path}
        mv 1D_fit_tau* ${scan_2D_plot_path}
        echo "[INFO]/[WARNING] If the yaml file contains Nones/nulls, the scanning window has to be adjusted!!! Remove affected categories from all_categories loop to not throw errors further down this script!!!!!"
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
#. tau_id_es_measurement/tau_id_es_sim_fit_conf.sh

min_id_sep=0
max_id_sep=0

min_es_sep=0
max_es_sep=0

cent_id_sep=0
cent_es_sep=0


if [[ $MODE == "MULTIFIT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create Workspace for all the datacards (fitting separately in every DM category)"    
    all_categories=("DM0" "DM1" "DM1011")
    for cat in "${all_categories[@]}"
    do
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
            datacard_output=${datacard_output_dm_pt}
        fi

        
        read min_id_sep max_id_sep cent_id_sep min_es_sep max_es_sep cent_es_sep < <(get_yaml_vals "${TAG}" "${cat}")
        echo "For category ${cat} under TAG ${TAG}:"
        echo "ID range: ${min_id_sep} to ${max_id_sep} with fit = ${cent_id_sep}"
        echo "ES range: ${min_es_sep} to ${max_es_sep} with fit = ${cent_es_sep}"
        echo "My values for ${cat}"


        combineTool.py -M MultiDimFit -n .comb_sep_fit_${cat} \
        -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
        --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.5,1.5 \
        --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001,Minuit2,Migrad,0:0.01 --cminPreScan \
        --redefineSignalPOIs r_EMB_${cat},ES_${cat} --floatOtherPOIs=1 --algo singles -m ${mH} \
        --saveWorkspace --saveFitResult --verbose 2 --cminDefaultMinimizerStrategy 0
        
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
            TNamed *wpVSmuInfo = new TNamed("WP_VSmu", "${WP_VSmu}");
            wpVSmuInfo->Write("WP_VSmu", TObject::kOverwrite);
            f->Close();
        }
EOF

        mv multidimfit.comb_sep_fit_${cat}.root output/${datacard_output}/htt_mt_${cat}/
        mv higgsCombine.comb_sep_fit_${cat}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/
    done
fi



if [[ $MODE == "POSTFIT_MULT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    all_categories=("DM0" "DM1" "DM1011")
    for cat in "${all_categories[@]}"
    do
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
            datacard_output=${datacard_output_dm_pt}
        fi

        read min_id_sep max_id_sep cent_id_sep min_es_sep max_es_sep cent_es_sep < <(get_yaml_vals "${TAG}" "${cat}")
        echo "For category ${cat} under TAG ${TAG}:"
        echo "ID range: ${min_id_sep} to ${max_id_sep} with fit = ${cent_id_sep}"
        echo "ES range: ${min_es_sep} to ${max_es_sep} with fit = ${cent_es_sep}"

        WORKSPACE=output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root
        
        FITFILE=output/${datacard_output}/htt_mt_${cat}/fitDiagnostics_${cat}.${ERA}.root
    
        combineTool.py -M FitDiagnostics  -d ${WORKSPACE} -m ${mH} -n .${TAG} \
        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --parallel 16 --robustHesse 1 --saveShapes --saveWithUncertainties --cminDefaultMinimizerStrategy 0 \
        --redefineSignalPOIs ES_${cat},r_EMB_${cat}

        mv fitDiagnostics.${TAG}.root ${FITFILE}
        mv higgsCombine.${TAG}.FitDiagnostics.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/
        echo "[INFO] Already built Prefit/Postfit shapes"

        python3 postfitter/postfitter.py -in ${FITFILE} -out output/${datacard_output}/htt_mt_${cat}/ --era ${ERA} --category ${cat}

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

        WORKSPACE=output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root
    
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


# Postfits ignores faulti fits, thus plotting them could ask about non existing files of bad fits!
if [[ $MODE == "PLOT_MULTIPOSTFIT_SEP" ]]; then
    source utils/setup_root.sh
    # CHANNELS=("mt")
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        all_categories=("DM0" "DM1" "DM1011")
        for cat in "${all_categories[@]}"
        do
            if [[ " ${all_categories[@]} " =~ " ${cat} " ]]; then
                FILE=output/${datacard_output_dm_pt}/htt_mt_${cat}/postfitshape.${cat}.${ERA}.root
            fi


            # create output folder if it does not exist
            if [ ! -d "output/postfitplots_emb_${TAG}_multifit_sep/" ]; then
                mkdir -p output/postfitplots_emb_${TAG}_multifit_sep/${WP}
            fi
            echo "[INFO] Postfits plots for category ${cat}"
            if [[ ${CHANNEL} != "mm" ]]; then
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category ${cat} --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --normalize-by-bin-width --prefit 
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category ${cat} --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --normalize-by-bin-width
            fi
            if [[ ${CHANNEL} == "mm" ]]; then
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category "Control Region" --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --normalize-by-bin-width --prefit
                python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category "Control Region" --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --normalize-by-bin-width
            fi
        done
    done
    exit 0
fi

if [[ $MODE == "POI_CORRELATION_SEP" ]]; then
    source utils/setup_root.sh
    all_categories=("DM0" "DM1" "DM1011")
    for cat in "${all_categories[@]}"
    do
        FITFILE_dm=output/${datacard_output_dm_pt}/htt_mt_${cat}/fitDiagnostics_${cat}.${ERA}.root
        if [ ! -d "${poi_path}/${ERA}/${cat}/${WP}" ]; then
            mkdir -p  ${poi_path}/${ERA}/${cat}/${WP}
        fi
        python tau_id_es_measurement/poi_correlation.py ${ERA} ${FITFILE_dm} ${cat} ${TAG}
        mv "${ERA}_${cat}_${TAG}_POIS_correlations_ID_ES.png" ${poi_path}/${ERA}/${cat}/${WP}
        
    done
fi



if [[ $MODE == "IMPACTS_ALL" ]]; then
    source utils/setup_cmssw_tauid.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        echo "[INFO] Channel: ${CHANNEL}"
        if [[ ${CHANNEL} != "mm" ]]; then
            source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
            if [ ! -d "${impact_path}/${ERA}/${CHANNEL}/${WP}" ]; then
                mkdir -p  ${impact_path}/${ERA}/${CHANNEL}/${WP}
            fi
            all_categories=("DM1011")
            for cat in "${all_categories[@]}"

            do
                if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                    WORKSPACE_IMP=output/${datacard_output_dm_pt}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root
                fi

                read min_id_sep max_id_sep cent_id_sep min_es_sep max_es_sep cent_es_sep < <(get_yaml_vals "${TAG}" "${cat}")
                echo "For category ${cat} under TAG ${TAG}:"
                echo "ID range: ${min_id_sep} to ${max_id_sep} with fit = ${cent_id_sep}"
                echo "ES range: ${min_es_sep} to ${max_es_sep} with fit = ${cent_es_sep}"

                ### Impacts for r_EMB_DMXY
                combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 125 \
                    --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
                    --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.5,1.5 \
                    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                    --parallel 16 --doInitialFit --redefineSignalPOIs r_EMB_${cat},ES_${cat} --cminDefaultMinimizerStrategy 0

                combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 125 \
                    --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
                    --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.5,1.5 \
                    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                    --parallel 16 --doFits --redefineSignalPOIs r_EMB_${cat},ES_${cat} --cminDefaultMinimizerStrategy 0

                combineTool.py -M Impacts -d ${WORKSPACE_IMP} -m 125 -o tauid_${WP}_impacts_${cat}_${TAG}.json  --redefineSignalPOIs r_EMB_${cat},ES_${cat} --cminDefaultMinimizerStrategy 0

                plotImpacts.py -i tauid_${WP}_impacts_${cat}_${TAG}.json -o tauid_${WP}_impacts_r_${cat}_${TAG} --POI r_EMB_${cat}
                plotImpacts.py -i tauid_${WP}_impacts_${cat}_${TAG}.json -o tauid_${WP}_impacts_${cat}_${TAG}_ES --POI ES_${cat}
                # # cleanup the fit files
                rm higgsCombine_paramFit*.root
                rm higgsCombine_initialFit*.root
                # rm robustHesse_paramFit*.root
                mv tauid_${WP}_impacts_r_${cat}_${TAG}* ${impact_path}/${ERA}/${CHANNEL}/${WP}
                mv tauid_${WP}_impacts_${cat}_${TAG}* ${impact_path}/${ERA}/${CHANNEL}/${WP}
            done
        fi
    done
fi


# Read out scale factors from the fitfiles. VSmu not supported by tau POG, thus not in corrlibs!
if [[ $MODE == "CORRECTION_LIB" ]]; then
    source utils/setup_root.sh

    CHANNELS=("mt")
    for CHANNEL in "${CHANNELS[@]}"
    do
        input_files_list=()
        bin_names_list=()
        all_categories=("DM0" "DM1" "DM1011")
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
            --nTuple_tag "${NTUPLETAG}" \
            --era "${ERA}" \
            --channel "${CHANNEL}" \
            --input_files ${input_files_str} \
            --binnames ${bin_names_str}

        # mv ...
    done

fi