export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNELS_str=${1}
IFS=',' read -r -a CHANNELS <<< "${CHANNELS_str}"
# CHANNEL=${1}
ERA=${2}
NTUPLETAG=${3}
TAG=${4}
MODE=${5}
WP=${6}
WP_VSe=${7}
WP_VSmu=${8}
FF_FRIENDS_TAG=${9:-"default_FF_friends"}
ES_up=${10:-"0"}
ES_down=${11:-"0"}
EXTENDED_TAG_UP=${12:-"M_pre_20to20_ext_up"}
EXTENDED_TAG_DOWN=${13:-"M_pre_20to20_ext_down"}
BIN_TAG=${14:-"default"}
# For producing correction libs of a given era and channel! All files for different wp should be given with their tags.
TAG_list_parse=${15:-"M_post_8to8_,T_post_8to8_"}
IFS=',' read -r -a TAG_list <<< "${TAG_list_parse}"
WP_list_parse=${16:-"Medium,Tight"}
IFS=',' read -r -a WP_list <<< "${WP_list_parse}"
WP_VSe_list_parse=${17:-"VVLoose"}
IFS=',' read -r -a WP_VSe_list <<< "${WP_VSe_list_parse}"


echo ${NTUPLETAG}
echo ${WP}

VARIABLES="m_vis,pt_1,pt_2"
POSTFIX="-FFS"
ulimit -s unlimited
source utils/setup_ul_samples_hh.sh ${NTUPLETAG} ${ERA} 
#${FF_FRIENDS_TAG} ${FAST_MTT_FRIENDS_TAG}

# Debuggung breakpoint()with ipdb:
# pip3 install ipdb
# export PYTHONBREAKPOINT="ipdb.set_trace"

# Datacard Setup, only for single channel use! If multiple are parsed these paths are wrong!!!
# datacard_output_dm_pt="datacards_dm_pt_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}_VSe${WP_VSe}"
# datacard_output="datacards/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}"
# output_shapes="hh_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
# shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
# shapes_output_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
# shapes_rootfile=${shapes_output}.root
# shapes_rootfile_synced=${shapes_output_synced}_synced.root
# CONDOR_OUTPUT=output/condor_shapes/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}

poi_path="poi_corr_${TAG}"

impact_path="impacts_${TAG}"


echo "MY WP,WP_VSe,WP_VSmu is: " ${WP} ${WP_VSe} ${WP_VSmu}
# echo "My out path is: ${shapes_output}"
echo "My synchpath is ${shapes_output_synced}"

# print the paths to be used
echo "KINGMAKER_BASEDIR: ${KINGMAKER_BASEDIR}"
# echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "FRIENDS: ${FF_FRIENDS}"
echo "XSEC: ${XSEC_FRIENDS}"
echo "PZETA: ${PZETAMISSVIS_FRIENDS}"

# all_categories=("Inclusive")


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
    python3 friends/build_friend_tree.py --basepath ${NTUPLES} --outputpath ${XSEC_FRIENDS} --nthreads 20
fi


if [[ $MODE == "BINNING" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Producing special binning for ${CHANNELS_str} -${ERA}-${NTUPLETAG}-${TAG}             #"
    echo "##############################################################################################"
    # CHANNELS=('mt')
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


DEFAULT_VARIABLES_LIST=(
pt_1 eta_1 phi_1 tau_decaymode_1 mt_1 iso_1 mass_1
  pt_2 eta_2 phi_2 tau_decaymode_2 mt_2 iso_2 mass_2
  jpt_1 jeta_1 jphi_1 jphi_2
  jpt_2 jeta_2 
  bpair_btag_value_1 
  bpair_btag_value_2
  pt_tautau pt_tautaubb pt_vis pt_dijet
  mjj mt_tot m_vis mass_tautaubb
  met metphi  metSumEt
  n_jets n_bjets pt_fastmtt eta_fastmtt phi_fastmtt m_fastmtt
  deltaR_ditaupair sum_deltaR_tt_bb bpair_deltaR bpair_m_inv bpair_pt_dijet
  ) 
# not in ntuples yet: pt_ttjj beta_1 beta_2 bpt_1 bpt_2 btag_value_1 btag_value_2 # consistency with pt_tt ??? pzetamissvis_bb pzetamissvis_bbtautau # not needed? mTdileptonMET
# Usual:
# pt_1 eta_1 phi_1 tau_decaymode_1 mt_1 iso_1 mass_1
#   pt_2 eta_2 phi_2 tau_decaymode_2 mt_2 iso_2 mass_2
#   jpt_1 jeta_1 jphi_1 jphi_2
#   jpt_2 jeta_2 
#   bpair_btag_value_1 
#   bpair_btag_value_2
#   pt_tautau pt_tautaubb pt_vis pt_dijet
#   mjj mt_tot m_vis mass_tautaubb
#   met metphi  metSumEt
#   n_bjets n_jets
#   deltaR_ditaupair sum_deltaR_tt_bb bpair_deltaR bpair_m_inv bpair_pt_dijet

diLep_VARIABLES_LIST=(
  pt_1 eta_1 phi_1 mass_1
  pt_2 eta_2 phi_2 mass_2
  pt_vis
  m_vis met
)

if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    procs=("data" "hh2b2tau" "ztt" "zl" "zj" "w" "stl" "stt" "stj" "ggh" "qqh" "ttl" "ttt" "ttj" "tth" "vvl" "vvt" "vvj" "vh")
    
    for CHANNEL in "${CHANNELS[@]}"
    do
        if [ ! -d "output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}" ]; then
            mkdir -p "output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
        fi
        output_shapes="hh_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
        shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
        # python shapes/produce_shapes.py --channels ${CHANNEL} \
        #     --directory ${NTUPLES} --process-selection "${procs[@]}" \
        #     --${CHANNEL}-friend-directory ${XSEC_FRIENDS} ${FF_FRIENDS} ${FASTMTT_FRIENDS} \
        #     --era ${ERA} --num-processes 16 --num-threads 24 \
        #     --optimization-level 2 --skip-systematic-variations \
        #     --output-file ${shapes_output} --control-plots --control-plot-set ${DEFAULT_VARIABLES_LIST[@]}  \
        #     --vs-jet-wp ${WP} --vs-ele-wp ${WP_VSe} --validation-tag ${TAG} --ff-type fake_factor --apply-tauid

        # python shapes/do_estimations.py -e ${ERA} -i ${shapes_output}.root --do-qcd --do-ff #--do-emb-tt

        # now plot the shapes by looping over the categories
        # for category in "ggh" "qqh" "ztt" "tt" "ff" "misc" "xxh"; do
        python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --channels ${CHANNEL} --tag ${TAG} --variables ${DEFAULT_VARIABLES_LIST[@]} --add-signals #--fake-factor # --embedding --category ${category}
        # done
        #  for category in "ggh" "qqh" "ztt" "tt" "ff" "misc" "xxh"; do
        #     python3 plotting/plot_ml_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --channel ${CHANNEL} --category ${category} --output-dir output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/controlplots --normalize-by-bin-width # --embedding --fake-factor 
        # done
    done
fi


if [[ $MODE == "ML_setup" ]]; then
    source utils/setup_root.sh
    procs=("data" "hh2b2tau" "ztt" "zl" "zj" "w" "stl" "stt" "stj" "ggh" "qqh" "ttl" "ttt" "ttj" "tth" "vvl" "vvt" "vvj" "vh")
    
    for CHANNEL in "${CHANNELS[@]}"
    do
        if [ ! -d "output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}" ]; then
            mkdir -p "output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
        fi
        output_shapes="hh_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
        shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
        ml_output="/work/jvoss/hh_non_res/smhtt_ul/ML_inputs_FF"
        python shapes/produce_shapes.py --channels ${CHANNEL} \
            --directory ${NTUPLES} --process-selection "${procs[@]}" \
            --${CHANNEL}-friend-directory ${XSEC_FRIENDS} ${FF_FRIENDS} ${FASTMTT_FRIENDS} --xrootd \
            --era ${ERA} --num-processes 12 --num-threads 16 \
            --optimization-level 2 --skip-systematic-variations \
            --output-file ${shapes_output}_ML_FF --control-plots --control-plot-set "m_vis"  \
            --vs-jet-wp Medium --vs-ele-wp VVLoose --validation-tag ${TAG} --ff-type fake_factor \
            --collect-config-only --config-output-file ${ml_output} --apply-tauid

        CONFIG_OUTPUT_FILE="${ERA}__${CHANNEL}__ML_inputs_FF"
        python trainings/adjust_config.py --configs ${CONFIG_OUTPUT_FILE} --modified-config ${ERA}__${CHANNEL}__ML_inputs_FF_modified.yaml --common-setup-config trainings/setup.yaml


        python trainings/create_training_dataset.py --config ${ERA}__${CHANNEL}__ML_inputs_FF_modified.yaml \
            --base-dataset-directory "/ceph/${USER}/smhtt_ul_ML/data/${TAG}/${CHANNEL}" --common-setup-config trainings/setup.yaml

    done
fi


# TODO: update this LOCAL part
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
            --output-file ${shapes_output}${number} --xrootd --validation-tag ${TAG} --binning-tag ${BIN_TAG} --es
    done
fi


if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    # for CHANNEL in "${CHANNELS[@]}"
    # do
    # source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
    if [ ! -d "${CONDOR_OUTPUT}" ]; then
        mkdir -p ${CONDOR_OUTPUT}
    fi
    
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_ul.sh ${ERA} ${CHANNEL} \
    "singlegraph" ${TAG} 0 ${NTUPLETAG} ${CONDOR_OUTPUT} "" ${FF_FRIENDS_TAG} ${WP} ${WP_VSe}
    echo "[INFO] Jobs submitted"
    # done
fi


if [[ $MODE == "EXTENSIONS" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Moving extensions to the new output folder including the extension shapes             #"
    echo "##############################################################################################"
    ORIG_DIR=$(pwd)
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
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


if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    # for CHANNEL in "${CHANNELS[@]}"
    # do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        if [ ! -d "${shapes_output}" ]; then
            mkdir -p ${shapes_output}
        fi
        echo "[INFO] Merging outputs located in ... "
        hadd -j 5 -n 600 -f ${shapes_rootfile} output/condor_shapes/analysis_unit_graphs-${ERA}-${CHANNEL}-${TAG}/*.root
    # done
fi


if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"

    # for CHANNEL in "${CHANNELS[@]}"
    # do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        if [ ! -d "${shapes_output}" ]; then
            mkdir -p ${shapes_output}
        fi
        if [ ! -d "${shapes_output_synced}" ]; then
            mkdir -p ${shapes_output_synced}
        fi
        if [[ $CHANNEL != "mm" ]]; then
            python shapes/do_estimations.py -e ${ERA} -i ${shapes_rootfile} --do-qcd --do-emb-tt --do-ff
        fi
        if [[ $CHANNEL == "mm" ]]; then
            python shapes/do_estimations.py -e ${ERA} -i ${shapes_rootfile} --do-qcd 
        fi

        echo "##############################################################################################"
        echo "#     synced shapes                                      #"
        echo "##############################################################################################"


        python shapes/convert_to_synced_shapes.py -e ${ERA} \
            -i ${shapes_rootfile} \
            -o ${shapes_output_synced} \
            --variable-selection ${VARIABLES} \
            -n 1 

        inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
        hadd -f ${shapes_output_synced}/${inputfile} ${shapes_output_synced}/${ERA}-${CHANNEL}*.root
    # done
fi


if [[ $MODE == "PLOT_CONTROL_ES" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#     Plotting                                      #"
    echo "##############################################################################################"
    # for CHANNEL in "${CHANNELS[@]}"
    # do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        if [ ! -d "${shapes_output}" ]; then
            mkdir -p ${shapes_output}
        fi
        all_categories=("DM1011_PT20_40")
        if [[ $CHANNEL != "mm" ]]; then
            for CATEGORY in "${all_categories[@]}"
            do
                # (
                        python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
                        --variables ${VARIABLES} --channels ${CHANNEL} --category ${CATEGORY} --tag ${TAG} --fake-factor
                # ) &
            done
        fi
        if [[ $CHANNEL == "mm" ]]; then
                    python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
                    --variables ${VARIABLES} --channels ${CHANNEL} --category control_region --tag ${TAG}
        fi
    # done
fi

# For the next steps combine need to be installed (if not already done)
# via e.g. source utils/install_combine_tauid.sh

##### CHECK THE NEXT PARTS! MIGHT NOT WORK FOR DI_HIGGS!!! #####

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
    source utils/setup_cmssw.sh
    # inputfile
    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"

    ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
        --base_path=$PWD \
        --input_folder_mt=$shapes_output_synced \
        --real_data=false \
        --classic_bbb=false \
        --binomial_bbb=false \
        --jetfakes=1 \
        --postfix="-ML" \
        --channel=${CHANNEL} \
        --auto_rebin=true \
        --stxs_signals="stxs_stage0" \
        --categories="stxs_stage0" \
        --era=${ERA} \
        --output=output/$datacard_output \
        --use_automc=true \
        --train_ff=1 \
        --train_stage0=1
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


if  [[ $MODE == "WORKSPACE" ]]; then 
    source utils/setup_cmssw_tauid.sh
    all_categories=("DM1011_PT20_40")
    for cat in "${all_categories[@]}"; do
        # for category in "dm_binned"
        if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
          datacard_output=${datacard_output_dm_pt}
        fi
        THIS_PWD=${PWD}
        echo ${THIS_PWD}
        if [ ! -d "output/${datacard_output}" ]; then
            mkdir -p  output/${datacard_output}
        fi
        echo "Category: ${cat}"
        echo "[INFO] Create Multifit_Workspace for datacard in ${cat} category."
        combineTool.py -M T2W -i output/${datacard_output}/htt_mt_${cat}/ \
            -o workspace_${cat}_${TAG}_multidimfit.root --parallel 4 -m 125 \
            -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
            --PO "map=^.*/EMB_${cat}:r_EMB_${cat}[1,0.1,4.0]" --verbose 3
        
    done
fi
# ws range old 0.1 to 1.9

#  2D likelihood scan for tau ID + ES, we vary ID and ES

# That's reflected in min/max_id and min/max_es parameters that have corresponding ranges

mH=125

scan_2D_plot_path="scan_2D_"${TAG}

if [[ $MODE == "SCAN_2D" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create 2D scan folder"
    if [ ! -d "${scan_2D_plot_path}" ]; then
            mkdir -p  ${scan_2D_plot_path}
    fi
    if [ ! -d "tau_id_es_measurement/confidence_yaml" ]; then
            mkdir -p  "tau_id_es_measurement/confidence_yaml"
    fi

    all_categories=("DM1011_PT20_40")
    for cat in "${all_categories[@]}"
    do
        # (
            if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output_dm_pt}
                min_id=0.11
                max_id=3.89
                min_es=-19.9
                max_es=19.9
                points_2D=289
                points_1D=17
            fi

            # 2D scan ID-ES
            combineTool.py -M MultiDimFit -n .scan_2D_${cat}_${TAG} -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters r_EMB_${cat}=1.0,ES_${cat}=0.0 \
                --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es} \
                --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs r_EMB_${cat},ES_${cat} \
                --floatOtherPOIs=1 --points=${points_2D} --algo grid -m ${mH} --alignEdges=1 --parallel 12 --cminDefaultMinimizerStrategy 0

            echo "[INFO] Moving scan file to datacard folder ..."
            mv higgsCombine.scan_2D_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            
            # 1D scans ID and ES:
            combineTool.py -M MultiDimFit -n .scan_1D_rEMB_${cat}_${TAG} \
                -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters r_EMB_${cat}=1.0,ES_${cat}=0.0 \
                --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es} \
                --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs r_EMB_${cat} --algo grid -m ${mH} --parallel 12 --cminDefaultMinimizerStrategy 0 \
                --floatOtherPOIs=1 --points=${points_1D} --alignEdges=1

            mv higgsCombine.scan_1D_rEMB_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            combineTool.py -M MultiDimFit -n .scan_1D_ES_${cat}_${TAG} \
                -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters ES_${cat}=0.0,r_EMB_${cat}=1.0 \
                --setParameterRanges r_EMB_${cat}=${min_id},${max_id}:ES_${cat}=${min_es},${max_es} \
                --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs ES_${cat} --algo grid -m ${mH} --parallel 12 --cminDefaultMinimizerStrategy 0 \
                --floatOtherPOIs=1 --points=${points_1D} --alignEdges=1

            mv higgsCombine.scan_1D_ES_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/


            echo "[INFO] Create plots for 2D and 1D scans"
            echo "[INFO] Input file: " output/${datacard_output}/htt_mt_${cat}/higgsCombine.scan_2D_${cat}_${TAG}.MultiDimFit.mH${mH}.root
            # Plotting
            python3 tau_id_es_measurement/plot_2D_scan.py \
            --name-2D scan_2D_${cat}_${TAG} \
            --name-1D-ID scan_1D_rEMB_${cat}_${TAG} \
            --name-1D-ES scan_1D_ES_${cat}_${TAG} \
            --in-path output/${datacard_output}/htt_mt_${cat}/ \
            --tau-id-poi ${cat} --tau-es-poi ES_${cat} --outname ${cat} --tag ${TAG} --nbins ${points_1D} \
            --x-range ${min_id} ${max_id} --y-range ${min_es} ${max_es} --scale_range 0.05
            # mv 2D_full_scan_${cat}_${TAG}* ${scan_2D_plot_path}
            # mv 1D_full_scan_tauES_${cat}_${TAG}* ${scan_2D_plot_path}
            # mv 1D_full_scan_tauID_${cat}_${TAG}* ${scan_2D_plot_path}
            # echo "[INFO]/[WARNING] If the yaml file contains Nones/nulls, the scanning window has to be adjusted!!! Remove affected categories from all_categories loop to not throw errors further down this script!!!!! (Nones/nulls are replaced with border values atm, thus no such errors should occur)"

            # sleep 5
            # Do closeup of the full 2D scan.
            read min_id_2 max_id_2 cent_id_2 min_es_2 max_es_2 cent_es_2 < <(get_yaml_vals "${TAG}" "${cat}" "full_scan" "2")
            echo "For category ${cat} under TAG ${TAG}:"
            echo "ID range: ${min_id_2} to ${max_id_2} with fit = ${cent_id_2}"
            echo "ES range: ${min_es_2} to ${max_es_2} with fit = ${cent_es_2}"
            echo "My values for ${cat}"

            # Calculate the number of points for the closeup scan:
            # 1. Calculate the range for ES
            es_range=$(echo "${max_es_2} - ${min_es_2}" | bc)
            # 2. Calculate the number of points for ES
                # The 0.1 is the fines ES granularity (atm), it is not used for 2D scan as it will lead to too many points to scan.
            es_points_full=$(echo "scale=0; ${es_range} / 0.1" | bc)
            es_points=$(echo "scale=0; ${es_range} / 0.25" | bc)
            # 3. Round upwards to integer
                # Protect against too many point
            es_points=$(echo "($es_points+0.999999)/1" | bc)
            if (( es_points > 17 )); then
                es_points=17
            fi
            # 4. Use square for total points of 2D scan, it applies the sqrt of it to each axis
            total_points=$(echo "${es_points} * ${es_points}" | bc)
            echo "[INFO] Total points for closeup scan: ${total_points} (ES points: ${es_points})"

            # 2D scan ID-ES
            combineTool.py -M MultiDimFit -n .closeup_scan_2D_${cat}_${TAG} -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters r_EMB_${cat}=${cent_id_2},ES_${cat}=${cent_es_2} \
                --setParameterRanges r_EMB_${cat}=${min_id_2},${max_id_2}:ES_${cat}=${min_es_2},${max_es_2} \
                --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs r_EMB_${cat},ES_${cat} \
                --floatOtherPOIs=1 --points=289 --algo grid -m ${mH} --alignEdges=1 --parallel 12 --cminDefaultMinimizerStrategy 0

            echo "[INFO] Moving scan file to datacard folder ..."
            mv higgsCombine.closeup_scan_2D_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            
            # 1D scan for r_EMB_${cat} (profiling ES_${cat})
            echo "[INFO] 1D scan for r_EMB_${cat} (profiling ES_${cat})"
            combineTool.py -M MultiDimFit -n .closeup_scan_1D_rEMB_${cat}_${TAG} \
                -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters ES_${cat}=${cent_es_2},r_EMB_${cat}=${cent_id_2} \
                --setParameterRanges r_EMB_${cat}=${min_id_2},${max_id_2}:ES_${cat}=${min_es_2},${max_es_2} \
                --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs r_EMB_${cat} --algo grid -m ${mH} --parallel 12 --cminDefaultMinimizerStrategy 0 \
                --floatOtherPOIs=1 --points=17 --alignEdges=1

            mv higgsCombine.closeup_scan_1D_rEMB_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            combineTool.py -M MultiDimFit -n .closeup_scan_1D_ES_${cat}_${TAG} \
                -d output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root \
                --setParameters ES_${cat}=${cent_es_2},r_EMB_${cat}=${cent_id_2} \
                --setParameterRanges r_EMB_${cat}=${min_id_2},${max_id_2}:ES_${cat}=${min_es_2},${max_es_2} \
                --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,1:0.01 --cminPreScan \
                --redefineSignalPOIs ES_${cat} --algo grid -m ${mH} --parallel 12 --cminDefaultMinimizerStrategy 0 \
                --floatOtherPOIs=1 --points=17 --alignEdges=1

            mv higgsCombine.closeup_scan_1D_ES_${cat}_${TAG}.MultiDimFit.mH${mH}.root output/${datacard_output}/htt_mt_${cat}/

            echo "[INFO] Create plots for 2D and 1D scans"
            echo "[INFO] Input file: " output/${datacard_output}/htt_mt_${cat}/higgsCombine.closeup_scan_2D_${cat}_${TAG}.MultiDimFit.mH${mH}.root
            # Plotting
            python3 tau_id_es_measurement/plot_2D_scan.py \
            --name-2D closeup_scan_2D_${cat}_${TAG} \
            --name-1D-ID closeup_scan_1D_rEMB_${cat}_${TAG} \
            --name-1D-ES closeup_scan_1D_ES_${cat}_${TAG} \
            --in-path output/${datacard_output}/htt_mt_${cat}/ \
            --tau-id-poi ${cat} --tau-es-poi ES_${cat} --outname ${cat} --tag ${TAG} --nbins 17 \
            --x-range ${min_id_2} ${max_id_2} --y-range ${min_es_2} ${max_es_2} --scale_range 0.05 --closeup_scan
            # mv 2D_closeup_scan_${cat}_${TAG}* ${scan_2D_plot_path}
            # mv 1D_closeup_scan_tauES_${cat}_${TAG}* ${scan_2D_plot_path}
            # mv 1D_closeup_scan_tauID_${cat}_${TAG}* ${scan_2D_plot_path}
            # echo "[INFO]/[WARNING] If the yaml file contains Nones/nulls, the scanning window has to be adjusted!!! Remove affected categories from all_categories loop to not throw errors further down this script!!!!! (Nones/nulls are replaced with border values atm, thus no such errors should occur)"
        # ) &
    done
fi


if [[ $MODE == "MULTIFIT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    if [ ! -d "combine_logs" ]; then
            mkdir -p  "combine_logs"
    fi
    echo "[INFO] Create Workspace for all the datacards (fitting separately in every DM category)"    
    # all_categories=("DM0_PT40_200" "DM1011_PT40_200")
    for cat in "${all_categories[@]}"
    do
        (
            if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output_dm_pt}
            fi

            read min_id_sep max_id_sep cent_id_sep min_es_sep max_es_sep cent_es_sep < <(get_yaml_vals "${TAG}" "${cat}" "closeup_scan" "1")
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
            --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
            --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.5,1.5 \
            --robustFit=1 --setRobustFitAlgo=Minuit2 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001,Minuit2,Migrad,0:0.01 --cminPreScan \
            --redefineSignalPOIs r_EMB_${cat},ES_${cat} --floatOtherPOIs=1 --algo singles -m ${mH} \
            --saveWorkspace --saveFitResult --verbose 2 --cminDefaultMinimizerStrategy 0 
            
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


if [[ $MODE == "POSTFIT_MULT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    all_categories=("DM1011_PT20_40")
    for cat in "${all_categories[@]}"
    do
        # (
            if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output_dm_pt}
            fi

            read min_id_post max_id_post cent_id_post min_es_post max_es_post cent_es_post < <(get_yaml_vals "${TAG}" "${cat}" "closeup_scan" "1")
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

    
            combineTool.py -M FitDiagnostics  -d ${WORKSPACE} -m ${mH} -n .${TAG}.${cat} \
            --setParameters r_EMB_${cat}=${cent_id_post},ES_${cat}=${cent_es_post} \
            --setParameterRanges r_EMB_${cat}=${min_id_post},${max_id_post}:ES_${cat}=${min_es_post},${max_es_post}\
            --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001,Minuit2,Migrad,0:0.01 --cminPreScan --verbose 1 \
            --parallel 20 --robustHesse 1 --saveShapes --saveWithUncertainties --cminDefaultMinimizerStrategy 0 \
            --saveNormalizations --cminDefaultMinimizerTolerance=0.1 \
            --redefineSignalPOIs r_EMB_${cat},ES_${cat} \
            2>&1 | tee -a combine_logger_${TAG}_${cat}_postfits_output.log

            mv fitDiagnostics.${TAG}.${cat}.root ${FITFILE}
            mv higgsCombine.${TAG}.${cat}.FitDiagnostics.mH${mH}.root ${start_dir}/output/${datacard_output}/htt_mt_${cat}/
            echo "[INFO] Already built Prefit/Postfit shapes"

            python3 ${start_dir}/postfitter/postfitter.py -in ${FITFILE} -out ${start_dir}/output/${datacard_output}/htt_mt_${cat}/ --era ${ERA} --category ${cat}


            # Move your outputs out of the tmp dir or it will be deleted!!!
            mv combine_logger.out combine_logger_${TAG}_${cat}_postfits.log
            cp combine_logger_${TAG}_${cat}_postfits.log ${start_dir}/combine_logs/
            cp combine_logger_${TAG}_${cat}_postfits_output.log ${start_dir}/combine_logs/

            popd >/dev/null
            rm -rf "${tmpdir_post}"

        # ) &
    done
fi


if [[ $MODE == "GOF_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    # categories=("DM1")
    mH=125
    for cat in "${all_categories[@]}"
    do
        (
            if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                datacard_output=${datacard_output_dm_pt}
            fi

            WORKSPACE=output/${datacard_output}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root
        
            combineTool.py -M GoodnessOfFit ${WORKSPACE} --algo saturated -m ${mH} --freezeParameters MH -n .GOF_data_${cat}_${TAG} 
            combineTool.py -M GoodnessOfFit ${WORKSPACE} --algo saturated -m ${mH} --freezeParameters MH -n .GOF_toys_${cat}_${TAG} -t 1000 \
            --toysFrequentist 
            
            echo "[INFO] Moving GOF files to datacard folder ..."

            mv higgsCombine.GOF_data_${cat}_${TAG}.GoodnessOfFit.mH${mH}.root output/$datacard_output/htt_mt_${cat}/
            mv higgsCombine.GOF_toys_${cat}_${TAG}.GoodnessOfFit.mH${mH}.123456.root output/$datacard_output/htt_mt_${cat}/

            echo "[INFO] Collecting GOF results in json file and plotting ..."
            
            combineTool.py -M CollectGoodnessOfFit \
            --input output/$datacard_output/htt_mt_${cat}/higgsCombine.GOF_data_${cat}_${TAG}.GoodnessOfFit.mH${mH}.root \
            output/$datacard_output/htt_mt_${cat}/higgsCombine.GOF_toys_${cat}_${TAG}.GoodnessOfFit.mH${mH}.123456.root \
            -o output/$datacard_output/htt_mt_${cat}/gof_${cat}_${TAG}.json -m ${mH}

            plotGof.py output/$datacard_output/htt_mt_${cat}/gof_${cat}_${TAG}.json --statistic saturated --mass 125.0 \
            -o output/$datacard_output/htt_mt_${cat}/gof_${cat}_${TAG}
        ) &

    done
fi


# Postfits ignores faulti fits, thus plotting them could ask about non existing files of bad fits!
if [[ $MODE == "PLOT_MULTIPOSTFIT_SEP" ]]; then
    source utils/setup_root.sh
    # CHANNELS=("mt")
    for CHANNEL in "${CHANNELS[@]}"
    do
        source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
        all_categories=("DM1011_PT20_40")
        for cat in "${all_categories[@]}"
        do
            # (
                if [[ " ${all_categories[@]} " =~ " ${cat} " ]]; then
                    FILE=output/${datacard_output_dm_pt}/htt_mt_${cat}/postfitshape.${cat}.${ERA}.root
                fi


                # create output folder if it does not exist
                if [ ! -d "output/postfitplots_emb_${TAG}_multifit_sep/" ]; then
                    mkdir -p output/postfitplots_emb_${TAG}_multifit_sep/${WP}
                fi
                echo "[INFO] Postfits plots for category ${cat}"
                if [[ ${CHANNEL} != "mm" ]]; then
                    python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category ${cat} --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --binning-tag ${BIN_TAG} --prefit 
                    python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category ${cat} --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --binning-tag ${BIN_TAG}
                fi
                if [[ ${CHANNEL} == "mm" ]]; then
                    python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category "Control Region" --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --binning-tag ${BIN_TAG} --prefit
                    python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category "Control Region" --categories "None" -o output/postfitplots_emb_${TAG}_multifit_sep/${WP} --binning-tag ${BIN_TAG}
                fi
            # ) &
        done
    done
fi

if [[ $MODE == "POI_CORRELATION_SEP" ]]; then
    source utils/setup_root.sh
    # all_categories=("DM1011")
    for cat in "${all_categories[@]}"
    do
        FITFILE_dm=output/${datacard_output_dm_pt}/htt_mt_${cat}/fitDiagnostics_${cat}.${ERA}.root
        if [ ! -d "${poi_path}" ]; then
            mkdir -p  ${poi_path}
        fi
        python tau_id_es_measurement/poi_correlation.py ${ERA} ${FITFILE_dm} ${cat} ${TAG} || true
        PDFFILE="${ERA}_${cat}_${TAG}_POIS_correlations_ID_ES.pdf"
        PNGFILE="${ERA}_${cat}_${TAG}_POIS_correlations_ID_ES.png"
        if [ -f "${PDFFILE}" ] && [ -f "${PNGFILE}" ]; then
            mv "${PDFFILE}" "${PNGFILE}" "${poi_path}"
        else
            echo "[WARNING] No plots for ${cat}."
        fi
    done
fi


if [[ $MODE == "IMPACTS_ALL" ]]; then
    source utils/setup_cmssw_tauid.sh
    for CHANNEL in "${CHANNELS[@]}"
    do
        echo "[INFO] Channel: ${CHANNEL}"
        if [[ ${CHANNEL} != "mm" ]]; then
            source utils/setup_shapes.sh ${CHANNEL} ${ERA} ${NTUPLETAG} ${TAG} ${MODE} ${WP}
            if [ ! -d "${impact_path}" ]; then
                mkdir -p  ${impact_path}
            fi
            # all_categories=("DM0")
            all_categories=("DM1011_PT20_40")
            for cat in "${all_categories[@]}"
            do
                # (
                    start_dir=$(pwd)
                    if [[ " ${all_categories[@]} " =~ " $cat " ]]; then
                        WORKSPACE_IMP=${start_dir}/output/${datacard_output_dm_pt}/htt_mt_${cat}/workspace_${cat}_${TAG}_multidimfit.root
                    fi

                    read min_id_sep max_id_sep cent_id_sep min_es_sep max_es_sep cent_es_sep < <(get_yaml_vals "${TAG}" "${cat}" "closeup_scan" "2")
                    echo "For category ${cat} under TAG ${TAG}:"
                    echo "ID range: ${min_id_sep} to ${max_id_sep} with fit = ${cent_id_sep}"
                    echo "ES range: ${min_es_sep} to ${max_es_sep} with fit = ${cent_es_sep}"

                    
                    # Make temp dir for unique logging.
                    start_dir=$(pwd)
                    tmpdir_imp=$(mktemp -d -p "${start_dir}")
                    pushd "${tmpdir_imp}" >/dev/null

                    # Copy or link the input workspace and any other required files into tmpdir if needed
                    cp "${WORKSPACE_IMP}" ./

                    ### Impacts for r_EMB_DMXY
                    combineTool.py -M Impacts  -d workspace_${cat}_${TAG}_multidimfit.root -m 125 \
                        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
                        --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.5,1.5 \
                        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                        --parallel 12 --doInitialFit --redefineSignalPOIs r_EMB_${cat},ES_${cat} --cminDefaultMinimizerStrategy 2

                    combineTool.py -M Impacts  -d workspace_${cat}_${TAG}_multidimfit.root -m 125 \
                        --setParameters ES_${cat}=${cent_es_sep},r_EMB_${cat}=${cent_id_sep},r_DY_incl_${cat}=1.0 \
                        --setParameterRanges r_EMB_${cat}=${min_id_sep},${max_id_sep}:ES_${cat}=${min_es_sep},${max_es_sep}:r_DY_incl_${cat}=0.5,1.5 \
                        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
                        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
                        --parallel 12 --doFits --redefineSignalPOIs r_EMB_${cat},ES_${cat} --cminDefaultMinimizerStrategy 2

                    combineTool.py -M Impacts -d workspace_${cat}_${TAG}_multidimfit.root -m 125 -o tauid_${WP}_impacts_${cat}_${TAG}.json  --redefineSignalPOIs r_EMB_${cat},ES_${cat} --cminDefaultMinimizerStrategy 2

                    plotImpacts.py -i tauid_${WP}_impacts_${cat}_${TAG}.json -o tauid_${WP}_impacts_r_${cat}_${TAG} --POI r_EMB_${cat}
                    plotImpacts.py -i tauid_${WP}_impacts_${cat}_${TAG}.json -o tauid_${WP}_impacts_${cat}_${TAG}_ES --POI ES_${cat}
                    
                    mv tauid_${WP}_impacts_r_${cat}_${TAG}* ${start_dir}/${impact_path}
                    mv tauid_${WP}_impacts_${cat}_${TAG}* ${start_dir}/${impact_path}

                    popd >/dev/null
                    rm -rf "${tmpdir_imp}"

                # ) &
            done
        fi
    done
fi


# Read out scale factors from the fitfiles. VSmu not supported by tau POG, thus not in corrlibs!
if [[ $MODE == "CORRECTION_LIB" ]]; then
    source utils/setup_root.sh
    if [ ! -d "Tau_ID_ES_${NTUPLETAG}" ]; then
                mkdir -p  Tau_ID_ES_${NTUPLETAG}
            fi
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
                    for TAG_it in "${TAG_list[@]}"
                    do
                        datacard_path="datacards_dm_pt_${TAG_it}/${NTUPLETAG}-${TAG_it}/${ERA}_tauid_${VSjet}_VSe${VSe}"
                        
                        # Check if the file exists (Does all possibilities, thus there will always be 2*len(all_categories) missing file messages!)
                        if [ ! -f "output/${datacard_path}/htt_mt_${cat}/higgsCombine.comb_sep_fit_${TAG_it}_${cat}.MultiDimFit.mH${mH}.root" ]; then
                            echo "File output/${datacard_path}/htt_mt_${cat}/higgsCombine.comb_sep_fit_${TAG_it}_${cat}.MultiDimFit.mH${mH}.root does not exist."
                            continue
                        else
                            # Add file to list of fitfiles
                            input_file="output/${datacard_path}/htt_mt_${cat}/higgsCombine.comb_sep_fit_${TAG_it}_${cat}.MultiDimFit.mH${mH}.root"
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

        mv Tau*_${ERA}_UL_${CHANNEL}*_${NTUPLETAG}* Tau_ID_ES_${NTUPLETAG}
    done

fi

# Generate LaTeX figures and tables for the results.
if [[ $MODE == "LATEX" ]]; then
    python3 LaTeX/gen_latex_figures.py
    mv *.tex LaTeX/
fi
