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
EXTENDED_TAG_UP=${11:-"M_pre_20to20_ext_up"}
EXTENDED_TAG_DOWN=${12:-"M_pre_20to20_ext_down"}
BIN_TAG=${13}
TES_precision=${14}
# For producing correction libs of a given era and channel! All files for different wp should be given with their tags.
TUPLE_list_parse=${15:-"defaultTUPLEa"}
# IFS=',' read -r -a TUPLE_list <<< "${TUPLE_list_parse}"
TUPLE_list=($TUPLE_list_parse)
WP_list_parse=${16:-"defaultVsJet"}
IFS=',' read -r -a WP_list <<< "${WP_list_parse}"
WP_VSe_list_parse=${17:-"defaultVsEle"}
IFS=',' read -r -a WP_VSe_list <<< "${WP_VSe_list_parse}"


echo ${NTUPLETAG}
echo ${WP}
echo "TES precision: ${TES_precision}"

VARIABLES="m_vis"
# VARIABLES="m_vis,pt_2,tau_decaymode_2"
POSTFIX="-TauID_ES"
ulimit -s unlimited
source utils/setup_ul_samples.sh ${NTUPLETAG} ${ERA}
# Debuggung breakpoint()with ipdb:
# pip3 install ipdb
export PYTHONBREAKPOINT="ipdb.set_trace"

# Datacard Setup
# old path: datacard_output_dm="datacards_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}_VSe${WP_VSe}"
datacard_output="datacards/${NTUPLETAG}/${TAG}/${ERA}/${WP}/${WP_VSe}"
echo "MY WP,WP_VSe,WP_VSmu is: " ${WP} ${WP_VSe} ${WP_VSmu}

# print the paths to be used
echo "KINGMAKER_BASEDIR: ${KINGMAKER_BASEDIR}"
echo "XSEC: ${XSEC_FRIENDS}"

all_categories=("DM0" "DM1" "DM1011" \
"DM0_PT20_40" "DM1_PT20_40" "DM1011_PT20_40" \
"DM0_PT40_200" "DM1_PT40_200" "DM1011_PT40_200")

# # Generates es_shifts from {ES_down} to ${ES_up} in 0.1 steps:
# es_shifts=()
# ES_up_int=$(printf "%.0f" "$(echo "${ES_up}*10" | bc -l)")
# ES_down_int=$(printf "%.0f" "$(echo "${ES_down}*10" | bc -l)")
# for i in $(seq ${ES_down_int} ${ES_up_int}); do
#     shift_val=$(printf "%.1f" "$(echo "${i} / 10" | bc -l)")
#     if [[ $shift_val == "0.0" ]]; then
#         es_shifts+=("EMB")  # Replace emb0p0 with EMB
#     elif [[ $shift_val == -* ]]; then
#         # Remove minus and replace the dot with "p"
#         formatted=${shift_val#-}
#         formatted=${formatted/./p}
#         es_shifts+=("embminus${formatted}")
#     else
#         formatted=${shift_val/./p}
#         es_shifts+=("emb${formatted}")
#     fi
# done
# echo "${es_shifts[@]}"

# Read out yaml file:
get_yaml_vals() {
    python3 -c "import sys, yaml; 
tag = sys.argv[1]; 
cat = sys.argv[2]; 
scan_tag = sys.argv[3]; 
sigma = sys.argv[4];
data = yaml.safe_load(open(f'tau_id_es_measurement/confidence_yaml/1D_{scan_tag}_{tag}_{cat}_contours.yaml'));
if sigma == '1':
    min_id_sep, max_id_sep = data[tag][cat]['ID'];
    min_es_sep, max_es_sep = data[tag][cat]['ES'];
elif sigma == '2':
    min_id_sep, max_id_sep = data[tag][cat]['ID_2'];
    min_es_sep, max_es_sep = data[tag][cat]['ES_2'];
else:
    print('Invalid sigma value. Use \"1\" or \"2\".');
    sys.exit(1);
cent_id_sep = data[tag][cat]['fit']['ID'];
cent_es_sep = data[tag][cat]['fit']['ES'];
print(min_id_sep, max_id_sep, cent_id_sep, min_es_sep, max_es_sep, cent_es_sep)" "$1" "$2" "$3" "$4"
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
    python3 friends/build_friend_tree.py --basepath ${NTUPLES} --outputpath ${XSEC_FRIENDS} --nthreads 20 --dataset-config /work/jvoss/KingMaker_v15_Run2/sample_database/nanoAOD_v15/datasets.json
fi


if [[ $MODE == "BINNING" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Producing special binning for ${CHANNELS_str} -${ERA}-${NTUPLETAG}-${TAG}             #"
    echo "##############################################################################################"
    all_categories=("Inclusive" "DM0_PT20_40")
    CHANNELS=('mt')
    for CHANNEL in "${CHANNELS[@]}"
    do
        python3 gof/build_binning.py --channel ${CHANNEL} \
            --directory ${NTUPLES} --tag ${BIN_TAG} \
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
    all_categories=("DM0_PT20_40" "Inclusive")
    CHANNELS=('mt')
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
        #### Shape production:
        # Use "shapes_rootfile_ctrl" for ctrl shapes or "shapes_rootfile" for full shape productio 
        # Alsoremove --skip-systematic-variations in full shape production !!!
        python shapes/produce_shapes_tauid_es.py --channels ${CHANNEL} \
            --directory ${NTUPLES} \
            --${CHANNEL}-friend-directory ${XSEC_FRIENDS} \
            --era ${ERA} --num-processes 6 --num-threads 12 \
            --vs-jet-wp ${WP} \
            --vs-ele-wp ${WP_VSe} \
            --vs-mu-wp ${WP_VSmu} \
            --optimization-level 2 \
            --control-plot-set ${VARIABLES} \
            --output-file ${shapes_rootfile_ctrl} --validation-tag ${TAG} --binning-tag ${BIN_TAG} \
            --tes_precision ${TES_precision} --es-up ${ES_up} --es-down ${ES_down} --xrootd --skip-systematic-variations
            # --special-analysis "TauID_ES" \ --apply-tauid --control-plot-set ${VARIABLES}
        # #### SSOS estimations:
        # if [[ $CHANNEL == "mm" ]]; then
        #     python shapes/do_estimations.py -e ${ERA} -i ${shapes_rootfile} --do-qcd -s TauID_ES
        # fi
        if [[ $CHANNEL != "mm" ]]; then
            python shapes/do_estimations.py -e ${ERA} -i ${shapes_rootfile_ctrl} --do-qcd --do-emb-tt --tes_precision ${TES_precision} --es-up ${ES_up} --es-down ${ES_down}
            # -s TauID_ES
            for CATEGORY in "${all_categories[@]}"
            do
                python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile_ctrl} \
                    --variables ${VARIABLES} --channels ${CHANNEL} --normalize-by-bin-width \
                    --tag ${TAG} --vs-jet-wp ${WP} --vs-ele-wp ${WP_VSe} --embedding --category ${CATEGORY}
            done
        fi
        # #### Plotting:
        # if [[ $CHANNEL == "mm" ]]; then
        #     python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
        #                     --variables ${VARIABLES} --channels ${CHANNEL} --category control_region \
        #                     --tag ${TAG} --vs-jet-wp ${WP} --vs-ele-wp ${WP_VSe} --embedding #--normalize-by-bin-width
        # fi
        # if [[ $CHANNEL != "mm" ]]; then
        #     for CATEGORY in "${all_categories[@]}"
        #     do
        #         python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
        #                         --variables ${VARIABLES} --channels ${CHANNEL} --category ${CATEGORY} \
        #                         --tag ${TAG} --vs-jet-wp ${WP} --vs-ele-wp ${WP_VSe} --embedding --es_up ${ES_up} --es_down ${ES_down} --tes_precision ${TES_precision} \
        #                         --es_family_plot "embminus12p0,embminus6p0,emb4p0,emb8p0" #--normalize-by-bin-width
        #     done
        # fi
    done
fi

### No xrootD atm! Change in submit file when using dCache again !!!
if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
        if [ ! -d "${CONDOR_OUTPUT}" ]; then
            mkdir -p ${CONDOR_OUTPUT}
        fi
        if [ ! -d "${CONDOR_GRAPHS}" ]; then
            mkdir -p ${CONDOR_GRAPHS}
        fi
        echo "[INFO] Running on Condor"
        echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
        bash submit/submit_shape_production_tauid_es.sh ${ERA} ${CHANNEL} \
        "singlegraph" ${TAG} 0 ${NTUPLETAG} ${CONDOR_GRAPHS} ${CONDOR_OUTPUT} "TauID_ES" ${WP} ${WP_VSe} ${WP_VSmu} ${ES_up} ${ES_down} ${BIN_TAG} ${TES_precision}
        echo "[INFO] Jobs submitted"
    done
fi

if [[ $MODE == "CONDOR_REMNANTS" ]]; then
    CHANNEL=('mt')
    source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
    source utils/setup_ul_samples.sh ${NTUPLETAG} ${ERA}
    source utils/setup_root.sh
    echo ${CONDOR_OUTPUT}
    python submit/single_graph_job.py --input ${CONDOR_OUTPUT}/analysis_unit_graphs-${ERA}-${CHANNEL}-${TAG}.pkl --graph-number 80 --num-threads 4
fi

if [[ $MODE == "EXTENSIONS_CONDOR" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Moving extensions to the new output folder including the extension shapes             #"
    echo "##############################################################################################"
    ORIG_DIR=$(pwd)
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
        dest_dir="output/condor_shapes/analysis_unit_graphs-${ERA}-${CHANNEL}-${TAG}_extended"
        base_name="analysis_unit_graphs-${ERA}-${CHANNEL}-${TAG}_extended"
        echo "This is the new TAG the full shapes will be associated with further on: ${TAG}_extended"
        if [[ ${CHANNEL} == "mm" ]]; then
            mkdir -p "${dest_dir}"
            cp ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${TAG}/*.root "${dest_dir}"/
            cd "${dest_dir}" || { echo "Cannot change to directory ${dest_dir}"; exit 1; }
            counter=0
            # Loop through all files
            for file in *; do
                # Skip if not a file
                if [ ! -f "$file" ]; then
                    continue
                fi
                # Get file extension (if any)
                ext="${file##*.}"
                if [[ "$file" != *.* ]]; then
                    new_file="${base_name}-${counter}"
                else
                    new_file="${base_name}-${counter}.${ext}"
                fi
                echo "Renaming $file to $new_file"
                mv "$file" "$new_file"
                counter=$((counter + 1))
            done
            cd "${ORIG_DIR}"
        else
            src1="output/condor_shapes/analysis_unit_graphs-${ERA}-${CHANNEL}-${TAG}"
            src2="output/condor_shapes/analysis_unit_graphs-${ERA}-${CHANNEL}-${EXTENDED_TAG_UP}"
            src3="output/condor_shapes/analysis_unit_graphs-${ERA}-${CHANNEL}-${EXTENDED_TAG_DOWN}"

            # Create destination directory if it does not exist
            mkdir -p "${dest_dir}"

            # Copy all files from the three source directories into the destination directory
            for src in "$src1" "$src2" "$src3"; do
                if [ -d "$src" ]; then
                    cp "$src"/* "${dest_dir}"/
                else
                    echo "Warning: $src is not a directory, skipping."
                fi
            done

            # Change to the destination directory
            cd "${dest_dir}" || { echo "Cannot change to directory ${dest_dir}"; exit 1; }

            # Rename each file in the destination directory sequentially
            counter=0
            # Loop through all files (adjust glob if you want specific types only, e.g. *.root)
            for file in *; do
                # Skip if not a file
                if [ ! -f "$file" ]; then
                    continue
                fi
                # Get file extension (if any)
                ext="${file##*.}"
                if [[ "$file" != *.* ]]; then
                    # No extension found
                    new_file="${base_name}-${counter}"
                else
                    new_file="${base_name}-${counter}.${ext}"
                fi
                echo "Renaming $file to $new_file"
                mv "${file}" "${new_file}"
                counter=$((counter + 1))
            done
            cd "${ORIG_DIR}"
        fi
    done
fi

# echo "[INFO] If you want to use the extended shapes, use ${TAG}_extended as the TAG from here on!"

if [[ $MODE == "MERGE_CONDOR" ]]; then
    source utils/setup_root.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
        if [ ! -d "${CONDOR_OUTPUT}" ]; then
            mkdir -p ${CONDOR_OUTPUT}
        fi
        echo "[INFO] Merging outputs located in ... "
        hadd -j 5 -n 600 -f ${shapes_rootfile} output/shapes_condor/analysis_unit_graphs-${ERA}-${CHANNEL}-${TAG}/*.root
    done
fi

if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    EXTENSION="odd"
    NEW="fine"
    echo "Set correct extension snippet, atm: ${EXTENSION}"
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
        
        TAG_NEW="${TAG%_*}_${NEW}"
        NTUPLETAG_NEW="${NTUPLETAG%_*}_${NEW}"
        shapes_output_new="output/shapes/${NTUPLETAG_NEW}/${ERA}-${TAG_NEW}/${WP}/${WP_VSe}/${CHANNEL}"
        if [ ! -d "${shapes_output_new}" ]; then
            mkdir -p ${shapes_output_new}
        fi
        echo "[INFO] Merging outputs located in ... "
        if [[ $CHANNEL == "mt" ]]; then 
            TAG_EXTENSION="${TAG%_*}_${EXTENSION}"
            NTUPLETAG_EXTENSION="${NTUPLETAG%_*}_${EXTENSION}"
            shapes_output_extension="output/shapes/${NTUPLETAG_EXTENSION}/${ERA}-${TAG_EXTENSION}/${WP}/${WP_VSe}/${CHANNEL}"
            hadd -j 5 -n 600 ${shapes_output_new}/m_vis.root ${shapes_output}/m_vis.root ${shapes_output_extension}/m_vis.root
        fi
        if [[ $CHANNEL == "mm" ]]; then 
            hadd -j 5 -n 600 ${shapes_output_new}/m_vis.root ${shapes_output}/m_vis.root
        fi
        echo "New Tags for merged shapes: ${TAG_NEW} and ${NTUPLETAG_NEW} !!!"
    done
fi

if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"

    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
        if [ ! -d "${shapes_output_synced}" ]; then
            mkdir -p ${shapes_output_synced}
        fi
        #### Done in "CONTROL", as long as condor doesn't work:
        if [[ $CHANNEL == "mm" ]]; then
            python shapes/do_estimations.py -e ${ERA} -i ${shapes_rootfile} --do-qcd -s TauID_ES
        fi
        if [[ $CHANNEL != "mm" ]]; then
            python shapes/do_estimations.py -e ${ERA} -i ${shapes_rootfile} --do-qcd --do-emb-tt -s TauID_ES --tes_precision ${TES_precision} --es-up ${ES_up} --es-down ${ES_down}
        fi

        echo "##############################################################################################"
        echo "#     synced shapes                                      #"
        echo "##############################################################################################"


        python shapes/convert_to_synced_shapes.py -e ${ERA} \
            -i ${shapes_rootfile} \
            -o ${shapes_output_synced} \
            --variable-selection ${VARIABLES} \
            -n 1 \
            --es-up ${ES_up} \
            --es-down ${ES_down} \
            --tes_precision ${TES_precision}

        inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
        hadd -f ${shapes_output_synced}/${inputfile} ${shapes_output_synced}/synced*.root
    done
fi

# Plotting of full shapes, not just ctrl ones.
if [[ $MODE == "PLOT_CONTROL_ES" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#     Plotting                                      #"
    echo "##############################################################################################"
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
        # all_categories=("DM0" "DM0_PT40_200")
        if [[ $CHANNEL != "mm" ]]; then
            for CATEGORY in "${all_categories[@]}"
            do
                # (
                    # for es_sh in "${es_shifts[@]}"
                    # do
                    #     # (
                    #         python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile_synced} \
                    #         --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category ${CATEGORY} --energy_scale \
                    #         --es_shift ${es_sh} --tag ${TAG} --es_up ${ES_up} --es_down ${ES_down}
                    #     # ) &
                    # done
                # ) &
                python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
                        --variables ${VARIABLES} --channels ${CHANNEL} --category ${CATEGORY} --normalize-by-bin-width \
                        --tag ${TAG} --vs-jet-wp ${WP} --vs-ele-wp ${WP_VSe} --es_up ${ES_up} --es_down ${ES_down} --tes_precision ${TES_precision} --es_family_plot "embminus20p0,embminus10p0,emb10p0,emb20p0" --embedding
            done
        fi
        if [[ $CHANNEL == "mm" ]]; then
                    python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
                    --variables ${VARIABLES} --channels ${CHANNEL} --category control_region --tag ${TAG} --vs-jet-wp ${WP} --vs-ele-wp ${WP_VSe} --embedding --es_up ${ES_up} --es_down ${ES_down} --tes_precision ${TES_precision} --normalize-by-bin-width
        fi
    done
fi

# For the next steps combine need to be installed (if not already done)
# via e.g. source utils/install_combine_tauid.sh


if  [[ $MODE == "MAKE_SHAPE_UNC" ]]; then 
    source utils/setup_root.sh
    CHANNEL='mt'
    all_categories=("DM1011_PT20_40")
    for cat in "${all_categories[@]}"; do
        python shapes/make_extra_shape_unc.py --input="output/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced/htt_${CHANNEL}.inputs-sm-Run${ERA}-TauID_ES.root" \
            --output="output/${WP}-${ERA}-mt-${NTUPLETAG}-${TAG}/synced/htt_${CHANNEL}.inputs-sm-Run${ERA}-TauID_ES_shape_unc_Test.root" \
            --process=${cat} --scaleup=1.3 --scaledown=0.7 --scaleTES=0.03
    done
fi

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw_tauid.sh
    # all_categories=("DM1")
    for cat in "${all_categories[@]}"
    do
        # for category in "dm_binned"
        if [[ " ${all_categories[@]} " =~ " ${cat} " ]]; then
        datacard_output=${datacard_output}
        fi
        
        ${CMSSW_BASE}/bin/el9_amd64_gcc12/MorphingTauID2017 \
            --base_path=${PWD} \
            --input_folder_mt="output/shapes_synced/${NTUPLETAG}/${ERA}-${TAG}/${WP}/${WP_VSe}/${CHANNEL}/mt" \
            --input_folder_mm="output/shapes_synced/${NTUPLETAG}/${ERA}-${TAG}/${WP}/${WP_VSe}/${CHANNEL}/mm" \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=0 \
            --embedding=1 \
            --verbose=true \
            --postfix=${POSTFIX} \
            --use_control_region=true \
            --auto_rebin=false \
            --rebin_categories=false \
            --manual_rebin_for_yields=false \
            --categories=${cat} \
            --era=${ERA} \
            --tes_precision=${TES_precision} \
            --es_min=${ES_down} \
            --es_max=${ES_up} \
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
    # all_categories=("DM1")
    for cat in "${all_categories[@]}"; do
        # for category in "dm_binned"
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
          datacard_output=${datacard_output}
        fi
        THIS_PWD=${PWD}
        echo ${THIS_PWD}
        if [ ! -d "output/${datacard_output}" ]; then
            mkdir -p  output/${datacard_output}
        fi
        echo "Category: ${cat}"
        echo "[INFO] Create Multifit_Workspace for datacard in ${cat} category."
        combineTool.py -M T2W -i output/${datacard_output}/htt_mt_${cat}/ \
            -o workspace_${cat}_${TAG}_multidimfit.root --parallel 2 -m 125 \
            -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
            --PO "map=^.*/EMB_${cat}:r_EMB_${cat}[1,0.1,2.9]" --verbose 3
        
    done
fi

#  2D likelihood scan for tau ID + ES, we vary ID and ES

# That's reflected in min/max_id and min/max_es parameters that have corresponding ranges

mH=125

scan_2D_plot_path_unused="output/unused/scan_2D_"${TAG}

if [[ $MODE == "SCAN_2D" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create 2D scan folders"
    
    if [ ! -d "${scan_2D_plot_path_unused}" ]; then
            mkdir -p  ${scan_2D_plot_path_unused}
    fi
    if [ ! -d "tau_id_es_measurement/confidence_yaml" ]; then
            mkdir -p  "tau_id_es_measurement/confidence_yaml"
    fi

    # all_categories=("DM0_PT40_200")
    for cat in "${all_categories[@]}"
    do
        scan_2D_plot_path="output/plots/${TAG}/scans/${WP}/${WP_VSe}"
        scan_1D_plot_path="output/plots/${TAG}/scans/${WP}/${WP_VSe}"
        if [ ! -d "${scan_2D_plot_path}" ]; then
                mkdir -p  ${scan_2D_plot_path}
        fi
        if [ ! -d "${scan_1D_plot_path}" ]; then
                mkdir -p  ${scan_1D_plot_path}
        fi
        (
            if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output}
                min_id=0.11
                max_id=2.89
                min_es=-19.9
                max_es=19.9
                points_2D=289
                points_1D=17
                # points_2D=961
                # points_1D=31
                threads=8
            fi

            ### 2D scan ID-ES
            combineTool.py -M MultiDimFit -n .scan_2D_${cat}_${TAG} -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters r_EMB_${cat}=1.0,ES_${cat}=0.0 \
                --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es} \
                --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs r_EMB_${cat},ES_${cat} \
                --floatOtherPOIs=1 --points=${points_2D} --algo grid -m ${mH} --alignEdges=1 --parallel=${threads} --cminDefaultMinimizerStrategy 0

            echo "[INFO] Moving scan file to datacard folder ..."
            mv higgsCombine.scan_2D_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            
            ### 1D scans ID and ES:
            combineTool.py -M MultiDimFit -n .scan_1D_rEMB_${cat}_${TAG} \
                -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters r_EMB_${cat}=1.0,ES_${cat}=0.0 \
                --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es} \
                --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs r_EMB_${cat} --algo grid -m ${mH} --parallel=${threads} --cminDefaultMinimizerStrategy 0 \
                --floatOtherPOIs=1 --points=${points_1D} --alignEdges=1

            mv higgsCombine.scan_1D_rEMB_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            combineTool.py -M MultiDimFit -n .scan_1D_ES_${cat}_${TAG} \
                -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters ES_${cat}=0.0,r_EMB_${cat}=1.0 \
                --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es} \
                --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs ES_${cat} --algo grid -m ${mH} --parallel=${threads} --cminDefaultMinimizerStrategy 0 \
                --floatOtherPOIs=1 --points=${points_1D} --alignEdges=1

            mv higgsCombine.scan_1D_ES_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/


            echo "[INFO] Create plots for 2D and 1D scans"
            echo "[INFO] Input file: " output/${datacard_output}/htt_mt_${cat}/higgsCombine.scan_2D_${cat}_${TAG}.MultiDimFit.mH${mH}.root
            ### Plotting
            python3 tau_id_es_measurement/plot_2D_scan.py \
            --name-2D scan_2D_${cat}_${TAG} \
            --name-1D-ID scan_1D_rEMB_${cat}_${TAG} \
            --name-1D-ES scan_1D_ES_${cat}_${TAG} \
            --in-path output/${datacard_output}/htt_mt_${cat}/ \
            --tau-id-poi ${cat} --tau-es-poi ES_${cat} --outname ${cat} --tag ${TAG} --nbins ${points_1D} \
            --x-range ${min_id} ${max_id} --y-range ${min_es} ${max_es} --scale_range 0.2
            mv 2D_full_scan_${cat}_${TAG}* ${scan_2D_plot_path_unused}
            mv 1D_full_scan_tauES_${cat}_${TAG}* ${scan_2D_plot_path_unused}
            mv 1D_full_scan_tauID_${cat}_${TAG}* ${scan_2D_plot_path_unused}
            echo "[INFO]/[WARNING] If the yaml file contains Nones/nulls, the scanning window has to be adjusted!!! Remove affected categories from all_categories loop to not throw errors further down this script!!!!! (Nones/nulls are replaced with border values atm, thus no such errors should occur)"

            # sleep 5
            ### Do closeup of the full 2D scan.
            read min_id_2 max_id_2 cent_id_2 min_es_2 max_es_2 cent_es_2 < <(get_yaml_vals "${TAG}" "${cat}" "full_scan" "2")
            echo "For category ${cat} under TAG ${TAG}:"
            echo "ID range: ${min_id_2} to ${max_id_2} with fit = ${cent_id_2}"
            echo "ES range: ${min_es_2} to ${max_es_2} with fit = ${cent_es_2}"
            echo "My values for ${cat}"


            ### 2D scan ID-ES
            combineTool.py -M MultiDimFit -n .2D_closeup_scan_${cat}_${TAG} -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters r_EMB_${cat}=${cent_id_2},ES_${cat}=${cent_es_2} \
                --setParameterRanges r_EMB_${cat}=${min_id_2},${max_id_2}:ES_${cat}=${min_es_2},${max_es_2} \
                --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs r_EMB_${cat},ES_${cat} \
                --floatOtherPOIs=1 --points=${points_2D} --algo grid -m ${mH} --alignEdges=1 --parallel=${threads} --cminDefaultMinimizerStrategy 0

            echo "[INFO] Moving scan file to datacard folder ..."
            mv higgsCombine.2D_closeup_scan_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            
            ### 1D scan for r_EMB_${cat} (profiling ES_${cat})
            echo "[INFO] 1D scan for r_EMB_${cat} (profiling ES_${cat})"
            combineTool.py -M MultiDimFit -n .1D_closeup_scan_rEMB_${cat}_${TAG} \
                -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters ES_${cat}=${cent_es_2},r_EMB_${cat}=${cent_id_2} \
                --setParameterRanges r_EMB_${cat}=${min_id_2},${max_id_2}:ES_${cat}=${min_es_2},${max_es_2} \
                --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs r_EMB_${cat} --algo grid -m ${mH} --parallel=${threads} --cminDefaultMinimizerStrategy 0 \
                --floatOtherPOIs=1 --points=${points_1D} --alignEdges=1

            mv higgsCombine.1D_closeup_scan_rEMB_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            combineTool.py -M MultiDimFit -n .1D_closeup_scan_ES_${cat}_${TAG} \
                -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters ES_${cat}=${cent_es_2},r_EMB_${cat}=${cent_id_2} \
                --setParameterRanges r_EMB_${cat}=${min_id_2},${max_id_2}:ES_${cat}=${min_es_2},${max_es_2} \
                --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs ES_${cat} --algo grid -m ${mH} --parallel=${threads} --cminDefaultMinimizerStrategy 0 \
                --floatOtherPOIs=1 --points=${points_1D} --alignEdges=1

            mv higgsCombine.1D_closeup_scan_ES_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            echo "[INFO] Create plots for 2D and 1D scans"
            echo "[INFO] Input file: " output/${datacard_output}/htt_mt_${cat}/higgsCombine.2D_closeup_scan_${cat}_${TAG}.MultiDimFit.mH${mH}.root
            ### Plotting
            python3 tau_id_es_measurement/plot_2D_scan.py \
            --name-2D 2D_closeup_scan_${cat}_${TAG} \
            --name-1D-ID 1D_closeup_scan_rEMB_${cat}_${TAG} \
            --name-1D-ES 1D_closeup_scan_ES_${cat}_${TAG} \
            --in-path output/${datacard_output}/htt_mt_${cat}/ \
            --tau-id-poi ${cat} --tau-es-poi ES_${cat} --outname ${cat} --tag ${TAG} --nbins ${points_1D} \
            --x-range ${min_id_2} ${max_id_2} --y-range ${min_es_2} ${max_es_2} --scale_range 0.05 --closeup_scan
            src="2D_closeup_scan_${cat}_${TAG}_binned.pdf"
            if [ -f "${src}" ]; then
                mv "${src}" "${scan_2D_plot_path}/2D_closeup_scan_binned_${cat}.pdf"
            fi
            src="2D_closeup_scan_${cat}_${TAG}_binned.png"
            if [ -f "${src}" ]; then
                mv "${src}" "${scan_2D_plot_path}/2D_closeup_scan_binned_${cat}.png"
            fi
            src="2D_closeup_scan_${cat}_${TAG}_interpolated.pdf"
            if [ -f "${src}" ]; then
                mv "${src}" "${scan_2D_plot_path}/2D_closeup_scan_interpolated_${cat}.pdf"
            fi
            src="2D_closeup_scan_${cat}_${TAG}_interpolated.png"
            if [ -f "${src}" ]; then
                mv "${src}" "${scan_2D_plot_path}/2D_closeup_scan_interpolated_${cat}.png"
            fi
            src="1D_closeup_scan_tauID_${cat}_${TAG}.pdf"
            if [ -f "${src}" ]; then
                mv "${src}" "${scan_1D_plot_path}/1D_closeup_scan_tauID_${cat}.pdf"
            fi
            src="1D_closeup_scan_tauID_${cat}_${TAG}.png"
            if [ -f "${src}" ]; then
                mv "${src}" "${scan_1D_plot_path}/1D_closeup_scan_tauID_${cat}.png"
            fi
            src="1D_closeup_scan_tauES_${cat}_${TAG}.pdf"
            if [ -f "${src}" ]; then
                mv "${src}" "${scan_1D_plot_path}/1D_closeup_scan_tauES_${cat}.pdf"
            fi
            src="1D_closeup_scan_tauES_${cat}_${TAG}.png"
            if [ -f "${src}" ]; then
                mv "${src}" "${scan_1D_plot_path}/1D_closeup_scan_tauES_${cat}.png"
            fi
            echo "[INFO]/[WARNING] If the yaml file contains Nones/nulls, the scanning window has to be adjusted!!! Remove affected categories from all_categories loop to not throw errors further down this script!!!!! (Nones/nulls are replaced with border values atm, thus no such errors should occur)"
        ) &
    done
fi


if [[ $MODE == "MULTIFIT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    if [ ! -d "combine_logs" ]; then
            mkdir -p  "combine_logs"
    fi
    echo "[INFO] Create Workspace for all the datacards (fitting separately in every DM category)"    
    # all_categories=("DM1")
    for cat in "${all_categories[@]}"
    do
        (
            if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output}
            fi

            read min_id_sep max_id_sep cent_id_sep min_es_sep max_es_sep cent_es_sep < <(get_yaml_vals "${TAG}" "${cat}" "closeup_scan" "2")
            echo "For category ${cat} under TAG ${TAG}:"
            echo "ID range: ${min_id_sep} to ${max_id_sep} with fit = ${cent_id_sep}"
            echo "ES range: ${min_es_sep} to ${max_es_sep} with fit = ${cent_es_sep}"
            echo "My values for ${cat}"

            # Make temp dir for unique logging.
            start_dir=$(pwd)
            tmpdir=$(mktemp -d -p "${start_dir}")
            pushd "${tmpdir}" >/dev/null

            # Copy or link the input workspace and any other required files into tmpdir if needed
            cp ${start_dir}/output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root ./
            


            combineTool.py -M MultiDimFit -n .comb_sep_fit_${TAG}_${cat} \
            -d workspace_${cat}_${TAG}_multidimfit.root \
            --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep} \
            --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep} \
            --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001,Minuit2,Migrad,0:0.01 --cminPreScan \
            --redefineSignalPOIs r_EMB_${cat},ES_${cat} --floatOtherPOIs=1 --algo singles -m ${mH} \
            --saveWorkspace --saveFitResult --verbose=2 --cminDefaultMinimizerStrategy=1
            #--robustHesse 1
            
            ROOTFILE="higgsCombine.comb_sep_fit_${TAG}_${cat}.MultiDimFit.mH${mH}.root"

            # Add the WP, WP_VSe and WP_VSmu to the ROOT file
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
            # Move your outputs out of the tmp dir or it will be deleted!!!
            mv combine_logger.out combine_logger_${TAG}_${cat}.log
            cp combine_logger_${TAG}_${cat}.log ${start_dir}/combine_logs/

            cp multidimfit.comb_sep_fit_${TAG}_${cat}.root ${start_dir}/output/${datacard_output}/htt_mt_${cat}/
            cp higgsCombine.comb_sep_fit_${TAG}_${cat}.MultiDimFit.mH${mH}.root ${start_dir}/output/${datacard_output}/htt_mt_${cat}/

            popd >/dev/null
            rm -rf "${tmpdir}"

        ) &
    done
fi

if [[ $MODE == "POSTFIT_SINGLES_SHAPES" ]]; then
    source utils/setup_cmssw_tauid.sh
    all_categories=("DM1")
    for cat in "${all_categories[@]}"
    do
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output}
        fi

        WORKSPACE=output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root
        FITFILE=output/${datacard_output}/htt_mt_${cat}/multidimfit.comb_sep_fit_${TAG}_${cat}.root 

        PostFitShapesFromWorkspace -m ${mH} -w ${WORKSPACE} \
            --output output/${datacard_output}/htt_mt_${cat}/${TAG}_singles-prefit.root
        PostFitShapesFromWorkspace -m ${mH} -w ${WORKSPACE} \
            --output output/${datacard_output}/htt_mt_${cat}/${TAG}_singles-postfit-s.root \
            -f ${FITFILE}:fit_mdf --postfit || true 
            #--sampling=1 --samples 2000

    done
fi
### Use the singles postit shapes rather than the fitdiagnostics, waaay less buggy !!!
if [[ $MODE == "POSTFIT_MULT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    all_categories=("DM1011_PT40_200")
    # ("DM0_PT40_200" "DM1011_PT40_200")

    for cat in "${all_categories[@]}"
    do
        # (
            if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output_dm}
            fi

            read min_id_post max_id_post cent_id_post min_es_post max_es_post cent_es_post < <(get_yaml_vals "${TAG}" "${cat}" "closeup_scan" "2")
            echo "For category ${cat} under TAG ${TAG}:"
            echo "ID range: ${min_id_post} to ${max_id_post} with fit = ${cent_id_post}"
            echo "ES range: ${min_es_post} to ${max_es_post} with fit = ${cent_es_post}"


            # Make temp dir for unique logging.
            start_dir=$(pwd)
            tmpdir_post=$(mktemp -d -p "${start_dir}")
            pushd "${tmpdir_post}" >/dev/null

            # Copy or link the input workspace and any other required files into tmpdir if needed
            WORKSPACE=${start_dir}/output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root
            FITFILE=${start_dir}/output/${datacard_output}/htt_mt_${cat}/fitDiagnostics_${cat}.${ERA}.root

            #--toys 100 --toysFrequentist
            combineTool.py -M FitDiagnostics  -d ${WORKSPACE} -m ${mH} -n .${TAG}.${cat} \
            --setParameters r_EMB_${cat}=${cent_id_post},ES_${cat}=${cent_es_post} \
            --setParameterRanges r_EMB_${cat}=${min_id_post},${max_id_post}:ES_${cat}=${min_es_post},${max_es_post}\
            --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001,Minuit2,Migrad,0:0.01 --cminPreScan \
            --parallel 20 --robustHesse 1 --saveWithUncertainties --saveWorkspace --cminDefaultMinimizerStrategy 0 \
            --cminDefaultMinimizerTolerance=0.1 --toys 100 --toysFrequentist \
            --redefineSignalPOIs r_EMB_${cat},ES_${cat} \
            2>&1 | tee -a combine_logger_${TAG}_${cat}_postfits_output.log
            mv fitDiagnostics.${TAG}.${cat}.root ${FITFILE}
            mv higgsCombine.${TAG}.${cat}.FitDiagnostics.mH${mH}*.root ${start_dir}/output/${datacard_output}/htt_mt_${cat}/

            PostFitShapesFromWorkspace -m ${mH} -w ${WORKSPACE} \
                --output ${start_dir}/output/${datacard_output}/htt_mt_${cat}/${TAG}-prefit.root
            # PostFitShapesFromWorkspace -m ${mH} -w ${WORKSPACE} \
            #     --output ${start_dir}/output/${datacard_output}/htt_mt_${cat}/${TAG}-postfit-b.root \
            #     -f ${FITFILE}:fit_b --postfit || true
            PostFitShapesFromWorkspace -m ${mH} -w ${WORKSPACE} \
                --output ${start_dir}/output/${datacard_output}/htt_mt_${cat}/${TAG}-postfit-s.root \
                -f ${FITFILE}:fit_s --postfit || true
            # echo "[INFO] Already built Prefit/Postfit shapes"

            # Old way, does normalization on shapes.
            # python3 ${start_dir}/postfitter/postfitter.py -in ${FITFILE} -out ${start_dir}/output/${datacard_output}/htt_mt_${cat}/ --era ${ERA} --category ${cat}


            # Move your outputs out of the tmp dir or it will be deleted!!!
            mv combine_logger.out combine_logger_${TAG}_${cat}_postfits.log
            cp combine_logger_${TAG}_${cat}_postfits.log ${start_dir}/combine_logs/
            cp combine_logger_${TAG}_${cat}_postfits_output.log ${start_dir}/combine_logs/
            # mv covariance_fit_s.png covariance_fit_s_${TAG}_${cat}.png
            # cp covariance_fit_s_${TAG}_${cat}.png ${start_dir}/output/${datacard_output}/htt_mt_${cat}/

            popd >/dev/null
            rm -rf "${tmpdir_post}"

        # ) &
    done
fi


if [[ $MODE == "GOF_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    all_categories=("DM0")
    mH=125
    for cat in "${all_categories[@]}"
    do
        # (
            if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output_dm_pt}
            fi

            WORKSPACE=output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root

            read min_id_post max_id_post cent_id_post min_es_post max_es_post cent_es_post < <(get_yaml_vals "${TAG}" "${cat}" "closeup_scan" "1")
            echo "For category ${cat} under TAG ${TAG}:"
            echo "ID range: ${min_id_post} to ${max_id_post} with fit = ${cent_id_post}"
            echo "ES range: ${min_es_post} to ${max_es_post} with fit = ${cent_es_post}"
        
            combineTool.py -M GoodnessOfFit ${WORKSPACE} --algo saturated -m ${mH} --freezeParameters MH -n .GOF_data_${cat}_${TAG} 
            combineTool.py -M GoodnessOfFit ${WORKSPACE} --algo saturated -m ${mH} --freezeParameters MH -n .GOF_toys_${cat}_${TAG} -t 100 \
            --toysFrequentist --setParameters r_EMB_${cat}=${cent_id_post},ES_${cat}=${cent_es_post}
            echo "[INFO] Moving GOF files to datacard folder ..."

            mv higgsCombine.GOF_data_${cat}_${TAG}.GoodnessOfFit.mH${mH}.root output/$datacard_output/htt_mt_${cat}/
            mv higgsCombine.GOF_toys_${cat}_${TAG}.GoodnessOfFit.mH${mH}.123456.root output/$datacard_output/htt_mt_${cat}/

            echo "[INFO] Collecting GOF results in json file and plotting ..."
            
            combineTool.py -M CollectGoodnessOfFit \
            --input output/$datacard_output/htt_mt_${cat}/higgsCombine.GOF_data_${cat}_${TAG}.GoodnessOfFit.mH${mH}.root \
            output/$datacard_output/htt_mt_${cat}/higgsCombine.GOF_toys_${cat}_${TAG}.GoodnessOfFit.mH${mH}.123456.root \
            -o output/$datacard_output/htt_mt_${cat}/gof_${cat}_${TAG}.json -m ${mH}

            # plotGof.py output/$datacard_output/htt_mt_${cat}/gof_${cat}_${TAG}.json --statistic saturated --mass 125.0 \
            # --category ${cat} -o output/$datacard_output/htt_mt_${cat}/gof_${cat}_${TAG}
            plotGof.py output/$datacard_output/htt_mt_${cat}/gof_${cat}_${TAG}.json --statistic saturated --mass 125.0 \
            -o output/plots/${TAG}/gof/gof_${cat} --category ${cat}
        # ) &

    done
fi


# Postfits ignores faulti fits, thus plotting them could ask about non existing files of bad fits!
if [[ $MODE == "PLOT_MULTIPOSTFIT_SEP" ]]; then
    source utils/setup_root.sh
    # CHANNELS=("mt")
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
        # all_categories=("DM1011" "DM1011_PT20_40" "DM1011_PT40_200" "DM1_PT20_40")
        # ("DM0_PT40_200" "DM1011_PT40_200")
        all_categories=("DM1")
        for cat in "${all_categories[@]}"
        do
            (
                if [[ " ${all_categories[@]} " =~ " ${cat} " ]]; then
                    # FILE=output/${datacard_output_dm}/htt_mt_${cat}/postfitshape.${cat}.${ERA}.root    # OLD from postfitter
                    FILE_pre=output/${datacard_output}/htt_mt_${cat}/${TAG}_singles-prefit.root
                    # FILE_post_b=output/${datacard_output_dm}/htt_mt_${cat}/${TAG}-postfit-b.root
                    FILE_post_s=output/${datacard_output}/htt_mt_${cat}/${TAG}_singles-postfit-s.root
                    output_postfit_plots=output/plots/${TAG}/postfits/${WP}/${WP_VSe}
                fi

                if [ ! -d ${output_postfit_plots} ]; then
                    mkdir -p ${output_postfit_plots}
                fi
                echo "[INFO] Postfits plots for category ${cat}"
                if [[ ${CHANNEL} != "mm" ]]; then
                    python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE_pre} --channel ${CHANNEL} --embedding --single-category ${cat} --categories "None" -o ${output_postfit_plots} --binning-tag ${BIN_TAG} --prefit --normalize-by-bin-width
                    # python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE_post_b} --channel ${CHANNEL} --embedding  --single-category ${cat} --categories "None" -o ${output_postfit_plots} --binning-tag ${BIN_TAG} --normalize-by-bin-width || true
                    python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE_post_s} --channel ${CHANNEL} --embedding --single-category ${cat} --categories "None" -o ${output_postfit_plots} --binning-tag ${BIN_TAG} --normalize-by-bin-width || true
                fi
                if [[ ${CHANNEL} == "mm" ]]; then
                    python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE_pre} --channel mm --embedding --single-category "Control Region" --categories "None" -o ${output_postfit_plots} --binning-tag ${BIN_TAG} --prefit
                    # python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE_post_b} --channel mm --embedding --single-category "Control Region" --categories "None" -o ${output_postfit_plots} --binning-tag ${BIN_TAG}
                    python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE_post_s} --channel mm --embedding --single-category "Control Region" --categories "None" -o ${output_postfit_plots} --binning-tag ${BIN_TAG}
                fi
            ) &
        done
    done
fi

if [[ $MODE == "POI_CORRELATION_SEP" ]]; then
    source utils/setup_root.sh
    # all_categories=("DM0")
    for cat in "${all_categories[@]}"
    do
        poi_path="output/plots/${TAG}/corr/${WP}/${WP_VSe}/"
        # FITFILE_dm=output/${datacard_output_dm}/htt_mt_${cat}/fitDiagnostics_${cat}.${ERA}.root
        FITFILE_dm=output/${datacard_output}/htt_mt_${cat}/multidimfit.comb_sep_fit_${TAG}_${cat}.root
        if [ ! -d "${poi_path}" ]; then
            mkdir -p  ${poi_path}
        fi
        
        python tau_id_es_measurement/poi_correlation.py ${ERA} ${FITFILE_dm} ${cat} ${TAG} || true
        PDFFILE="POIS_correlations_ID_ES_${cat}.pdf"
        PNGFILE="POIS_correlations_ID_ES_${cat}.png"
        if [ -f "${PDFFILE}" ] && [ -f "${PNGFILE}" ]; then
            mv "${PDFFILE}" "${PNGFILE}" "${poi_path}"
        else
            mv "${PDFFILE}" "${poi_path}"
            echo "[Info] No png, only pdf."
        fi
    done
fi


if [[ $MODE == "IMPACTS_ALL" ]]; then
    source utils/setup_cmssw_tauid.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        echo "[INFO] Channel: ${CHANNEL}"
        if [[ ${CHANNEL} != "mm" ]]; then
            source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP} ${WP_VSe}
            
            # all_categories=("DM0" "DM1_PT40_200")
            for cat in "${all_categories[@]}"
            do
                (
                    impact_path="output/plots/${TAG}/impacts/${WP}/${WP_VSe}"
                    if [ ! -d "${impact_path}" ]; then
                        mkdir -p  ${impact_path}
                    fi
                    start_dir=$(pwd)
                    if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                        WORKSPACE_IMP=${start_dir}/output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root
                        # WORKSPACE_IMP=output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root
                    fi

                    read min_id_sep max_id_sep cent_id_sep min_es_sep max_es_sep cent_es_sep < <(get_yaml_vals "${TAG}" "${cat}" "closeup_scan" "2")
                    echo "For category ${cat} under TAG ${TAG}:"
                    echo "ID range: ${min_id_sep} to ${max_id_sep} with fit = ${cent_id_sep}"
                    echo "ES range: ${min_es_sep} to ${max_es_sep} with fit = ${cent_es_sep}"
                    
                    
                    ### Make temp dir for unique logging.
                    start_dir=$(pwd)
                    tmpdir_imp=$(mktemp -d -p "${start_dir}")
                    pushd "${tmpdir_imp}" >/dev/null

                    ### Copy or link the input workspace and any other required files into tmpdir if needed
                    cp "${WORKSPACE_IMP}" ./

                    ### Impacts for r_EMB_DMXY
                    # If fits go bad try: --approx {hesse,robust} or --noInitialFit
                    combineTool.py -M Impacts  -d workspace_${cat}_${TAG}_multidimfit.root -m 125 \
                        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep} \
                        --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep} \
                        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                        --parallel 4 --doInitialFit --redefineSignalPOIs r_EMB_${cat},ES_${cat} --cminDefaultMinimizerStrategy=0 \
                        --cminDefaultMinimizerTolerance=0.1 \
                        2>&1 | tee -a combine_logger_${TAG}_${cat}_impacts_output.log
                        #--robustHesse 1

                    combineTool.py -M Impacts  -d workspace_${cat}_${TAG}_multidimfit.root -m 125 \
                        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep} \
                        --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep} \
                        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                        --parallel 4 --doFit --redefineSignalPOIs r_EMB_${cat},ES_${cat} --cminDefaultMinimizerStrategy=2 \
                        --cminDefaultMinimizerTolerance=0.1 --noInitialFit \
                        2>&1 | tee -a combine_logger_${TAG}_${cat}_impacts_output.log
                        #--robustHesse 1

                    combineTool.py -M Impacts -d workspace_${cat}_${TAG}_multidimfit.root -m 125 -o tauid_impacts_${cat}.json  --redefineSignalPOIs r_EMB_${cat},ES_${cat} \
                    2>&1 | tee -a combine_logger_${TAG}_${cat}_impacts_output.log

                    cp tauid_impacts_${cat}.json ${start_dir}/${impact_path}
                    
                    ### Plotting:
                    plotImpacts.py -i ${start_dir}/${impact_path}/tauid_impacts_${cat}.json -o tauid_impacts_${cat}_ID --POI r_EMB_${cat}
                    plotImpacts.py -i ${start_dir}/${impact_path}/tauid_impacts_${cat}.json -o tauid_impacts_${cat}_ES --POI ES_${cat}

                    plotImpacts.py -i ${start_dir}/${impact_path}/tauid_impacts_${cat}.json -o top10_tauid_impacts_${cat}_ID --POI r_EMB_${cat} --per-page 10 --max-pages 1
                    plotImpacts.py -i ${start_dir}/${impact_path}/tauid_impacts_${cat}.json -o top10_tauid_impacts_${cat}_ES --POI ES_${cat} --per-page 10 --max-pages 1
                    
                    mv tauid_impacts_${cat}_ID* ${start_dir}/${impact_path}
                    mv tauid_impacts_${cat}_ES* ${start_dir}/${impact_path}
                    mv top10_tauid_impacts_${cat}_ID* ${start_dir}/${impact_path}
                    mv top10_tauid_impacts_${cat}_ES* ${start_dir}/${impact_path}

                    cp combine_logger_${TAG}_${cat}_impacts_output.log ${start_dir}/combine_logs/

                    popd >/dev/null
                    rm -rf "${tmpdir_imp}"

                ) &
            done
        fi
    done
fi


# Read out scale factors from the fitfiles. VSmu not supported by tau POG, thus not in corrlibs!
if [[ $MODE == "CORRECTION_LIB" ]]; then
    source utils/setup_root.sh
    tuple_number=${#TUPLE_list[@]}
    echo "Received ${tuple_number} elements (total of $((tuple_number / 2)) tuples)."
    CHANNELS=("mt")
    for CHANNEL in "${CHANNELS[@]}"
    do
        input_files_list=()
        bin_names_list=()
        # all_categories=("DM0" "DM1" "DM1011")
        for cat in "${all_categories[@]}"
        do
            for VSjet in "${WP_list[@]}"
            do
                for VSe in "${WP_VSe_list[@]}"
                do
                    for (( i=0; i<${tuple_number}; i+=2 ))
                    do
                        TAG="${TUPLE_list[i]}"
                        NTUP="${TUPLE_list[i+1]}"
                        datacard_path="datacards/${NTUP}/${TAG}/${ERA}/${VSjet}/${VSe}"
                        
                        # Check if the file exists (Does all possibilities, thus there will always be 2*len(all_categories) missing file messages!)
                        if [ ! -f "output/${datacard_path}/htt_mt_${cat}/higgsCombine.comb_sep_fit_${TAG}_${cat}.MultiDimFit.mH${mH}.root" ]; then
                            echo "File output/${datacard_path}/htt_mt_${cat}/higgsCombine.comb_sep_fit_${TAG}_${cat}.MultiDimFit.mH${mH}.root does not exist."
                            continue
                        else
                            # Add file to list of fitfiles
                            input_file="output/${datacard_path}/htt_mt_${cat}/higgsCombine.comb_sep_fit_${TAG}_${cat}.MultiDimFit.mH${mH}.root"
                            input_files_list+=("${input_file}")
                            # Add bin name to list of names
                            bin_names_list+=("${cat}")
                        fi
                    done
                done
            done
        done
        # Join lists into comma-separated strings, the lists contain duplicate the python script deals with that.
        input_files_str=$(IFS=, ; echo "${input_files_list[*]}")
        bin_names_str=$(IFS=, ; echo "${bin_names_list[*]}")
        echo "[INFO] Input files: ${input_files_str}"
        echo "[INFO] Bin names: ${bin_names_str}"
        python3 friends/create_xpog_json_v15.py \
            --nTuple_tags "${TUPLE_list[*]}" \
            --era "${ERA}" \
            --channel "${CHANNEL}" \
            --input_files ${input_files_str} \
            --binnames ${bin_names_str}

        echo "[INFO] Created XPOG json file for ${ERA} era."
        sf_list=("ID" "ES")
        for VSjet in "${WP_list[@]}"
        do
            for VSe in "${WP_VSe_list[@]}"
            do
                for sf in "${sf_list[@]}"
                do
                    for (( i=0; i<${tuple_number}; i+=2 ))
                    do
                        TAG="${TUPLE_list[i]}"
                        NTUP="${TUPLE_list[i+1]}"
                        PDFFILE="Tau${sf}_${CHANNEL}_${VSjet}_${VSe}_${TAG}_${NTUP}.pdf"
                        PNGFILE="Tau${sf}_${CHANNEL}_${VSjet}_${VSe}_${TAG}_${NTUP}.png"
                        echo "File name now should be: ${PDFFILE}"
                        # Check if the files exists before proceeding
                        if [ ! -f "${PDFFILE}" ] && [ ! -f "${PNGFILE}" ]; then
                            echo "[Info] No plot files found for ${sf}, skipping..."
                            continue
                        fi
                        sf_plot_path="output/plots/${TAG}/sfs/${VSjet}/${VSe}"
                        if [ ! -d "${sf_plot_path}" ]; then
                                mkdir -p  ${sf_plot_path}
                        fi
                        if [ -f "${PDFFILE}" ] && [ -f "${PNGFILE}" ]; then
                            mv "${PNGFILE}" "${sf_plot_path}/Tau${sf}.png"
                            mv "${PDFFILE}" "${sf_plot_path}/Tau${sf}.pdf"
                        elif [ -f "${PDFFILE}" ]; then
                            mv "${PDFFILE}" "${sf_plot_path}/Tau${sf}.pdf"
                            echo "[Info] No png, only pdf."
                        elif [ -f "${PNGFILE}" ]; then
                            mv "${PNGFILE}" "${sf_plot_path}/Tau${sf}.png"
                            echo "[Info] No pdf, only png."
                        fi
                    done
                done
            done
        done
    done
    mv DeepTau2018v2p5_id_es_embedding* Tau_SFs_DT2p5/
fi

# Generate LaTeX figures and tables for the results.
if [[ $MODE == "LATEX" ]]; then
    python3 LaTeX/gen_latex_figures.py
    mv *.tex LaTeX/
fi
