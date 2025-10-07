export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL="mt"
ERA="2018"
NTUPLETAG="ff_and_cr_production_2018UL_mt__2025-09-10_w_syst_v2"
TAG="2025-09-10__test_2d_gof_binning__v6"
MODE=$1

VARIABLES_LIST=(
  # deltaR_2j1 deltaR_2j2 deltaR_1j1 deltaR_1j2 deltaR_12jj
  # deltaEta_1j1 deltaEta_1j2 deltaEta_2j1 deltaEta_2j2 deltaEta_12jj
  deltaEta_jj
  deltaR_jj
  jpt_1 jeta_1
  jpt_2 jeta_2
  mjj pt_dijet pt_ttjj
  #
  m_vis mt_tot pt_tt pt_vis
  pt_1 eta_1 mt_1
  pt_2 eta_2 mt_2
  deltaEta_ditaupair deltaR_ditaupair
  met njets nbtag
  m_fastmtt pt_fastmtt eta_fastmtt
)

VARIABLES_LIST_1D=(
  # deltaR_2j1 deltaR_2j2 deltaR_1j1 deltaR_1j2 deltaR_12jj
  # deltaEta_1j1 deltaEta_1j2 deltaEta_2j1 deltaEta_2j2 deltaEta_12jj
  jeta_1 jeta_2 deltaR_jj pt_ttjj pt_tt pt_fastmtt eta_fastmtt deltaEta_ditaupair met
  deltaEta_jj jpt_1 jpt_2  
  mjj pt_dijet mt_tot m_vis pt_vis m_fastmtt 
  #
  pt_1 eta_1 mt_1 pt_2 eta_2 mt_2
  deltaR_ditaupair njets nbtag
)

VARIABLES_1D=$(IFS=, ; echo "${VARIABLES_LIST_1D[*]}")

VARIABLES_LIST=(
  deltaEta_jj
  deltaEta_jj_pt_tt deltaEta_jj_m_fastmtt deltaEta_jj_met deltaEta_jj_pt_2
  deltaEta_jj_deltaR_ditaupair deltaEta_jj deltaEta_jj_njets deltaEta_jj_jpt_1
  deltaEta_jj_pt_1 deltaEta_jj_nbtag deltaEta_jj_eta_1 deltaEta_jj_deltaEta_ditaupair
  deltaEta_jj_mt_2 deltaEta_jj_pt_vis deltaEta_jj_jeta_2 deltaEta_jj_eta_2
  deltaEta_jj_pt_ttjj deltaEta_jj_mt_1 deltaEta_jj_mjj deltaEta_jj_pt_dijet
  deltaEta_jj_pt_fastmtt deltaEta_jj_eta_fastmtt deltaEta_jj_m_vis deltaEta_jj_deltaR_jj
  deltaEta_jj_jeta_1 deltaEta_jj_mt_tot deltaEta_jj_jpt_2
  #
  deltaR_jj
  deltaR_jj_mt_2 deltaR_jj_deltaEta_ditaupair deltaR_jj_njets deltaR_jj_m_vis
  deltaR_jj_deltaR_ditaupair deltaR_jj_eta_1 deltaR_jj_pt_fastmtt deltaR_jj deltaR_jj_pt_1
  deltaR_jj_mt_1 deltaR_jj_pt_vis deltaR_jj_mjj deltaR_jj_jeta_1 deltaR_jj_met
  deltaR_jj_eta_fastmtt deltaR_jj_eta_2 deltaR_jj_pt_2 deltaR_jj_jeta_2 deltaR_jj_nbtag
  deltaR_jj_mt_tot deltaR_jj_pt_tt deltaR_jj_jpt_2 deltaR_jj_jpt_1 deltaR_jj_pt_dijet
  deltaR_jj_m_fastmtt deltaR_jj_pt_ttjj
  #
  jpt_1
  jpt_1_pt_ttjj jpt_1_pt_dijet jpt_1_nbtag jpt_1_njets jpt_1_m_fastmtt jpt_1_pt_tt
  jpt_1_jeta_2 jpt_1_mt_2 jpt_1_pt_fastmtt jpt_1_met jpt_1_eta_2 jpt_1_deltaR_ditaupair
  jpt_1_eta_1 jpt_1_deltaEta_ditaupair jpt_1 jpt_1_jpt_2 jpt_1_eta_fastmtt jpt_1_m_vis
  jpt_1_mjj jpt_1_mt_1 jpt_1_pt_vis jpt_1_pt_1 jpt_1_pt_2 jpt_1_jeta_1 jpt_1_mt_tot
  #
  jeta_1
  jeta_1_pt_1 jeta_1_mt_1 jeta_1_eta_2 jeta_1_eta_1 jeta_1_m_fastmtt jeta_1_pt_vis
  jeta_1_jpt_2 jeta_1_pt_dijet jeta_1_mjj jeta_1_deltaEta_ditaupair jeta_1_pt_ttjj
  jeta_1_mt_2 jeta_1 jeta_1_pt_2 jeta_1_nbtag jeta_1_m_vis jeta_1_pt_tt
  jeta_1_deltaR_ditaupair jeta_1_pt_fastmtt jeta_1_eta_fastmtt jeta_1_met jeta_1_jeta_2
  jeta_1_njets jeta_1_mt_tot
  #
  jpt_2
  jpt_2 jpt_2_njets jpt_2_mt_tot jpt_2_m_vis jpt_2_m_fastmtt jpt_2_nbtag jpt_2_pt_vis
  jpt_2_mjj jpt_2_jeta_2 jpt_2_eta_2 jpt_2_deltaR_ditaupair jpt_2_eta_fastmtt
  jpt_2_deltaEta_ditaupair jpt_2_mt_2 jpt_2_eta_1 jpt_2_met jpt_2_mt_1 jpt_2_pt_fastmtt
  jpt_2_pt_tt jpt_2_pt_ttjj jpt_2_pt_dijet jpt_2_pt_2 jpt_2_pt_1
  #
  jeta_2
  jeta_2_pt_ttjj jeta_2_mt_tot jeta_2_mjj jeta_2_mt_1 jeta_2_pt_fastmtt jeta_2_m_fastmtt
  jeta_2_eta_1 jeta_2_deltaR_ditaupair jeta_2_pt_vis jeta_2_nbtag jeta_2 jeta_2_mt_2
  jeta_2_njets jeta_2_eta_fastmtt jeta_2_pt_2 jeta_2_eta_2 jeta_2_deltaEta_ditaupair
  jeta_2_met jeta_2_pt_tt jeta_2_pt_dijet jeta_2_pt_1 jeta_2_m_vis
  #
  mjj
  mjj_nbtag mjj_pt_fastmtt mjj_eta_fastmtt mjj_met mjj_pt_vis mjj_eta_1 mjj_pt_tt
  mjj_mt_tot mjj_eta_2 mjj_mt_2 mjj_deltaEta_ditaupair mjj_njets mjj mjj_pt_2 mjj_pt_ttjj
  mjj_m_vis mjj_m_fastmtt mjj_pt_dijet mjj_mt_1 mjj_deltaR_ditaupair mjj_pt_1
  #
  pt_dijet
  pt_dijet_pt_fastmtt pt_dijet_njets pt_dijet_pt_ttjj pt_dijet_pt_1 pt_dijet_pt_tt
  pt_dijet_met pt_dijet_pt_vis pt_dijet_m_vis pt_dijet_mt_tot pt_dijet_deltaEta_ditaupair
  pt_dijet_eta_2 pt_dijet_pt_2 pt_dijet_eta_fastmtt pt_dijet_mt_2 pt_dijet
  pt_dijet_deltaR_ditaupair pt_dijet_mt_1 pt_dijet_m_fastmtt pt_dijet_nbtag pt_dijet_eta_1
  #
  pt_ttjj
  pt_ttjj_pt_vis pt_ttjj_mt_tot pt_ttjj_eta_1 pt_ttjj_mt_1 pt_ttjj_deltaEta_ditaupair
  pt_ttjj_pt_1 pt_ttjj_pt_fastmtt pt_ttjj_pt_tt pt_ttjj_mt_2 pt_ttjj_deltaR_ditaupair
  pt_ttjj_eta_fastmtt pt_ttjj_m_fastmtt pt_ttjj_eta_2 pt_ttjj_nbtag pt_ttjj_njets pt_ttjj
  pt_ttjj_met pt_ttjj_pt_2 pt_ttjj_m_vis
  #
  m_vis
  m_vis_pt_1 m_vis_mt_1 m_vis_deltaR_ditaupair m_vis_pt_vis m_vis_pt_fastmtt m_vis_met
  m_vis_deltaEta_ditaupair m_vis_nbtag m_vis_pt_tt m_vis_njets m_vis m_vis_eta_2
  m_vis_eta_fastmtt m_vis_mt_2 m_vis_pt_2 m_vis_mt_tot m_vis_m_fastmtt m_vis_eta_1
  #
  mt_tot
  mt_tot_njets mt_tot_nbtag mt_tot_eta_fastmtt mt_tot_pt_1 mt_tot mt_tot_pt_fastmtt
  mt_tot_deltaR_ditaupair mt_tot_mt_2 mt_tot_mt_1 mt_tot_met mt_tot_m_fastmtt mt_tot_eta_2
  mt_tot_pt_vis mt_tot_pt_tt mt_tot_pt_2 mt_tot_eta_1 mt_tot_deltaEta_ditaupair
  #
  pt_tt
  pt_tt_pt_1 pt_tt_pt_vis pt_tt_deltaEta_ditaupair pt_tt_mt_2 pt_tt_pt_fastmtt
  pt_tt_eta_fastmtt pt_tt_m_fastmtt pt_tt_eta_2 pt_tt_pt_2 pt_tt_met pt_tt_njets
  pt_tt_mt_1 pt_tt_eta_1 pt_tt_deltaR_ditaupair pt_tt pt_tt_nbtag
  #
  pt_vis pt_vis_njets pt_vis_eta_fastmtt pt_vis_nbtag pt_vis_eta_1 pt_vis_deltaR_ditaupair
  pt_vis_mt_2 pt_vis_deltaEta_ditaupair pt_vis_m_fastmtt pt_vis_pt_fastmtt pt_vis_mt_1
  pt_vis_met pt_vis_eta_2 pt_vis pt_vis_pt_2 pt_vis_pt_1
  #
  pt_1
  pt_1_eta_1 pt_1_eta_2 pt_1_deltaR_ditaupair pt_1_pt_2 pt_1_deltaEta_ditaupair
  pt_1_m_fastmtt pt_1_mt_2 pt_1_pt_fastmtt pt_1_met pt_1_mt_1 pt_1_nbtag pt_1_eta_fastmtt
  pt_1 pt_1_njets
  #
  eta_1
  eta_1_pt_2 eta_1_pt_fastmtt eta_1 eta_1_mt_1 eta_1_njets eta_1_eta_2
  eta_1_deltaEta_ditaupair eta_1_nbtag eta_1_eta_fastmtt eta_1_m_fastmtt
  eta_1_deltaR_ditaupair eta_1_met eta_1_mt_2
  #
  mt_1
  mt_1_mt_2 mt_1_deltaR_ditaupair mt_1 mt_1_pt_fastmtt mt_1_pt_2 mt_1_met
  mt_1_deltaEta_ditaupair mt_1_njets mt_1_nbtag mt_1_m_fastmtt mt_1_eta_2 mt_1_eta_fastmtt
  #
  pt_2
  pt_2_njets pt_2_m_fastmtt pt_2_deltaEta_ditaupair pt_2_deltaR_ditaupair
  pt_2_eta_fastmtt pt_2_eta_2 pt_2_mt_2 pt_2_nbtag pt_2 pt_2_pt_fastmtt pt_2_met
  #
  eta_2
  eta_2_njets eta_2_nbtag eta_2_mt_2 eta_2_met eta_2_eta_fastmtt eta_2_pt_fastmtt
  eta_2_m_fastmtt eta_2_deltaEta_ditaupair eta_2 eta_2_deltaR_ditaupair
  #
  mt_2
  mt_2_njets mt_2_nbtag mt_2_pt_fastmtt mt_2 mt_2_deltaR_ditaupair mt_2_eta_fastmtt
  mt_2_m_fastmtt mt_2_deltaEta_ditaupair mt_2_met
  #
  deltaEta_ditaupair
  deltaEta_ditaupair_deltaR_ditaupair deltaEta_ditaupair_met deltaEta_ditaupair_eta_fastmtt
  deltaEta_ditaupair_njets deltaEta_ditaupair_m_fastmtt deltaEta_ditaupair_pt_fastmtt
  deltaEta_ditaupair_nbtag deltaEta_ditaupair
  #
  deltaR_ditaupair
  deltaR_ditaupair deltaR_ditaupair_nbtag deltaR_ditaupair_pt_fastmtt deltaR_ditaupair_njets
  deltaR_ditaupair_met deltaR_ditaupair_eta_fastmtt deltaR_ditaupair_m_fastmtt
  #
  met
  met_nbtag met met_pt_fastmtt met_njets met_m_fastmtt met_eta_fastmtt
  #
  njets
  njets_pt_fastmtt njets_eta_fastmtt njets njets_nbtag njets_m_fastmtt
  #
  nbtag
  nbtag nbtag_m_fastmtt nbtag_eta_fastmtt nbtag_pt_fastmtt
  #
  m_fastmtt
  m_fastmtt m_fastmtt_pt_fastmtt m_fastmtt_eta_fastmtt
  #
  pt_fastmtt
  pt_fastmtt_eta_fastmtt pt_fastmtt
  #
  eta_fastmtt
)


VARIABLES=$(IFS=, ; echo "${VARIABLES_LIST[*]}")

VARIABLES_LIST_1D=( 
    nbtag
    jeta_1
    jeta_2
    deltaR_jj
    pt_ttjj
    pt_tt pt_fastmtt eta_fastmtt deltaEta_ditaupair met deltaEta_jj jpt_1 jpt_2     mjj pt_dijet mt_tot m_vis pt_vis m_fastmtt    pt_1 eta_1 mt_1 pt_2 eta_2 mt_2   deltaR_ditaupair njets )


POSTFIX="-ML"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

output_shapes="gof_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
output_shapes="control_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
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
echo "###################################"
echo "#           Mode ${MODE}          #"
echo "###################################"

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

if [[ $MODE == "GOF-BINNING" ]]; then
    source utils/setup_root.sh
    ./gof/create_gof_binning.sh $CHANNEL $ERA $NTUPLETAG $VARIABLES
fi

if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    # python shapes/produce_shapes.py --channels $CHANNEL $NNSCORE_FRIENDS \
    #     --directory $NTUPLES \
    #     --${CHANNEL}-friend-directory $FRIENDS \
    #     --era $ERA --num-processes 4 --num-threads 6 \
    #     --optimization-level 1 --skip-systematic-variations \
    #     --output-file $shapes_output

    # python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-ff --do-qcd

    # now plot the shapes by looping over the categories
    for category in "ggh" "qqh" "ztt" "tt" "ff" "misc" "xxh"; do
        python3 plotting/plot_ml_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --channel ${CHANNEL} --embedding --fake-factor --category ${category} --output-dir output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/controlplots --normalize-by-bin-width
    done
fi

if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $FRIENDS \
        --era $ERA --num-processes 4 --num-threads 12 \
        --optimization-level 1 --gof-inputs \
        --control-plot-set ${VARIABLES} \
        --output-file $shapes_output
fi

if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_ul.sh $ERA $CHANNEL \
        "singlegraph" $TAG 1 $NTUPLETAG $CONDOR_OUTPUT ${VARIABLES} $NNSCORE_FRIENDS
    echo "[INFO] Jobs submitted"
fi

if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../control_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    # python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-ff --do-qcd

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python shapes/convert_to_synced_shapes.py -e $ERA \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        -n 40 --gof

    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}*.root

    exit 0
fi

if [[ $MODE == "DATACARD_" ]]; then
    source utils/setup_cmssw.sh
    # Datacard Setup
    for VARIABLE in ${VARIABLES//,/ }; do
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}_${VARIABLE}"
        GOF_CATEGORY_NAME=${CHANNEL}_${VARIABLE}
        FILENAME="${ERA}-${CHANNEL}-synced-${VARIABLE}.root"
        # ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
        ${CMSSW_BASE}/bin/el9_amd64_gcc12/MorphingSMRun2Legacy \
            --base_path=$PWD \
            --input_folder_mt=$shapes_output_synced \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=1 \
            --embedding=1 \
            --postfix="-ML" \
            --channel=${CHANNEL} \
            --auto_rebin=false \
            --rebin_categories=false \
            --stxs_signals="stxs_stage0" \
            --categories="gof" \
            --era=${ERA} \
            --gof_category_name=$GOF_CATEGORY_NAME \
            --output=$datacard_output \
            --train_ff=1 \
            --train_stage0=1 \
            --train_emb=1
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd $datacard_output/${CHANNEL}
        for FILE in */*.txt; do
            sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
        done
        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -o workspace.root -i $datacard_output/${CHANNEL}/125 --channel-masks
    done
    exit 0
fi

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw.sh
    run_morphing() {
        VARIABLE=$1
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}_${VARIABLE}"
        GOF_CATEGORY_NAME=${CHANNEL}_${VARIABLE}
        FILENAME="${ERA}-${CHANNEL}-synced-${VARIABLE}.root"
        # ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
        ${CMSSW_BASE}/bin/el9_amd64_gcc12/MorphingSMRun2Legacy \
            --base_path=$PWD \
            --input_folder_mt=$shapes_output_synced \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=1 \
            --embedding=1 \
            --postfix="-ML" \
            --channel=${CHANNEL} \
            --auto_rebin=false \
            --rebin_categories=false \
            --stxs_signals="stxs_stage0" \
            --categories="gof" \
            --era=${ERA} \
            --gof_category_name=$GOF_CATEGORY_NAME \
            --output=$datacard_output \
            --train_ff=1 \
            --train_stage0=1 \
            --train_emb=1
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd $datacard_output/${CHANNEL}
        for FILE in */*.txt; do
            sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
        done
        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -o workspace.root -i $datacard_output/${CHANNEL}/125 --channel-masks
    }

    export -f run_morphing
    export NTUPLETAG TAG ERA CHANNEL shapes_output_synced CMSSW_BASE

    echo ${VARIABLES//,/ } | tr ' ' '\n' | xargs -n 1 -P 60 -I {} bash -c 'run_morphing "{}"'

    exit 0
fi

if [[ $MODE == "DATACARD-MC" ]]; then
    source utils/setup_cmssw.sh
    # Datacard Setup
    for VARIABLE in ${VARIABLES//,/ }; do
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}_${VARIABLE}"
        GOF_CATEGORY_NAME=${CHANNEL}_${VARIABLE}
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
            --auto_rebin=false \
            --rebin_categories=false \
            --stxs_signals="stxs_stage0" \
            --categories="gof" \
            --era=${ERA} \
            --gof_category_name=$GOF_CATEGORY_NAME \
            --output=$datacard_output \
            --train_ff=1 \
            --train_stage0=1 --train_emb=1
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd $datacard_output/${CHANNEL}
        for FILE in */*.txt; do
            sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
        done
        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -o workspace.root -i $datacard_output/${CHANNEL}/125 --channel-masks
    done
    exit 0
fi

if [[ $MODE == "GOF_" ]]; then
    source utils/setup_cmssw.sh
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        WORKSPACE=$datacard_output/${CHANNEL}/125/workspace.root
        MASS=125
        NUM_TOYS=100 # multiply x10
        for ALGO in "saturated" "KS" "AD"; do
            # Get test statistic value
            if [[ "$ALGO" == "saturated" ]]; then
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE --fixedSignalStrength=0 -v 1
            else
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE --plots --fixedSignalStrength=0
            fi

            # Throw toys
            TOYSOPT=""
            if [[ "$ALGO" == "saturated" ]]; then
                TOYSOPT="--toysFreq"
            fi

            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1230 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1231 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1232 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1233 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1234 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1235 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1236 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1237 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1238 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1239 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            wait
            # Collect results
            combineTool.py -M CollectGoodnessOfFit --input \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1230.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1231.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1232.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1233.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1234.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1235.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1236.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1237.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1238.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1239.root \
                --output output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json

            mv higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.123?.root output/gof/${NTUPLETAG}-${TAG}/${ID}/
            if [[ "$ALGO" == "saturated" ]]; then
                mv output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json output/gof/${NTUPLETAG}-${TAG}/${ID}/gof.json
            fi

            # Plot
            if [[ "$ALGO" != "saturated" ]]; then
                plotGof.py --statistic $ALGO --mass $MASS.0 --output gof_${ALGO} output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json
                mv htt_${CHANNEL}_300_${ERA}gof_${ALGO}.p{df,ng} output/gof/${NTUPLETAG}-${TAG}/${ID}/
                python3 plotting/gof/plot_gof_metrics.py -e $ERA -g $ALGO -o output/gof/${NTUPLETAG}-${TAG}/${ID}/ -i output/gof/${NTUPLETAG}-${TAG}/${ID}/higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root
            else
                plotGof.py --statistic $ALGO --mass $MASS.0 --output output/gof/${NTUPLETAG}-${TAG}/${ID}/gof output/gof/${NTUPLETAG}-${TAG}/${ID}/gof.json
            fi
        done
    done
    source utils/setup_root.sh
    python3 gof/plot_gof_summary.py --variables $VARIABLES --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL
    exit 0
fi


if [[ $MODE == "GOF" ]]; then
    source utils/setup_cmssw.sh

    # Define a function to process a single variable
    run_gof_for_variable() {
        VARIABLE=$1
        
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        WORKSPACE=$datacard_output/${CHANNEL}/125/workspace.root
        MASS=125
        NUM_TOYS=100 # multiply x10
        for ALGO in "saturated" "KS" "AD"; do
            # Get test statistic value
            if [[ "$ALGO" == "saturated" ]]; then
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE --fixedSignalStrength=0 -v 1
            else
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE --plots --fixedSignalStrength=0
            fi

            # Throw toys
            TOYSOPT=""
            if [[ "$ALGO" == "saturated" ]]; then
                TOYSOPT="--toysFreq"
            fi

            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1230 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1231 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1232 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1233 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1234 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1235 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1236 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1237 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1238 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1239 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            wait
            # Collect results
            combineTool.py -M CollectGoodnessOfFit --input \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1230.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1231.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1232.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1233.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1234.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1235.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1236.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1237.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1238.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1239.root \
                --output output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json

            mv higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.123?.root output/gof/${NTUPLETAG}-${TAG}/${ID}/
            if [[ "$ALGO" == "saturated" ]]; then
                mv output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json output/gof/${NTUPLETAG}-${TAG}/${ID}/gof.json
            fi

            # Plot
            if [[ "$ALGO" != "saturated" ]]; then
                plotGof.py --statistic $ALGO --mass $MASS.0 --output gof_${ALGO} output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json
                mv htt_${CHANNEL}_300_${ERA}gof_${ALGO}.p{df,ng} output/gof/${NTUPLETAG}-${TAG}/${ID}/
                python3 plotting/gof/plot_gof_metrics.py -e $ERA -g $ALGO -o output/gof/${NTUPLETAG}-${TAG}/${ID}/ -i output/gof/${NTUPLETAG}-${TAG}/${ID}/higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root
            else
                plotGof.py --statistic $ALGO --mass $MASS.0 --output output/gof/${NTUPLETAG}-${TAG}/${ID}/gof output/gof/${NTUPLETAG}-${TAG}/${ID}/gof.json
            fi
        done
    }
    
    export -f run_gof_for_variable
    export NTUPLETAG TAG ERA CHANNEL

    # echo ${VARIABLES//,/ } | tr ' ' '\n' | xargs -n 1 -P 5 -I {} bash -c 'run_gof_for_variable "{}"'

    # --- These commands run AFTER all parallel jobs are finished ---
    
    echo "[INFO] All GOF jobs complete. Creating summary plot."
    source utils/setup_root.sh
    python3 gof/plot_gof_summary_updated.py --variables $VARIABLES_1D --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL --threshold 0.05 --test-type gof
    python3 gof/plot_gof_summary_updated.py --variables $VARIABLES_1D --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL --threshold 0.05 --test-type gof_KS
    python3 gof/plot_gof_summary_updated.py --variables $VARIABLES_1D --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL --threshold 0.05 --test-type gof_AD    
    exit 0
fi

  


if [[ $MODE == "GOF-SUMMARY" ]]; then
    source utils/setup_root.sh
    python3 gof/plot_gof_summary.py --variables $VARIABLES --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL

fi

if [[ $MODE == "POSTFIT" ]]; then
    source utils/setup_cmssw.sh
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        WORKSPACE=$datacard_output/${CHANNEL}/125/workspace.root
        combine \
            -M FitDiagnostics \
            -m 125 -d $WORKSPACE \
            --robustFit 1 -v1 \
            --robustHesse 1 \
            -n .$ID \
            --setParameters r=0 --freezeParameters r \
            --X-rtd MINIMIZER_analytic \
            --cminDefaultMinimizerStrategy 0 |
            tee $LOGFILE
        FITFILE=${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root
        mv fitDiagnostics.${ID}.root $FITFILE
        #python combine/check_mlfit.py fitDiagnostics${ERA}.root
        # root -l $FITFILE <<< "fit_b->Print(); fit_s->Print()"
        echo "done 1"
        # python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
        python3 diffNuisances.py \
            ${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root -a \
            -f html >${datacard_output}/nuisances.html
        echo "done 2"
	PostFitShapesFromWorkspace -m 125 -w $WORKSPACE \
            --output ${datacard_output}/${ID}-datacard-shapes-prefit.root \
            -d ${datacard_output}/cmb/125/htt_${CHANNEL}_300_${ERA}.txt
        echo "done 3"
        PostFitShapesFromWorkspace -m 125 -w $WORKSPACE \
            --output ${datacard_output}/${ID}-datacard-shapes-postfit-b.root \
            -f ${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root:fit_b --postfit --sampling \
            -d ${datacard_output}/cmb/125/htt_${CHANNEL}_300_${ERA}.txt
        echo "done 4"
    done
    exit 0

fi

if [[ $MODE == "PLOT-POSTFIT" ]]; then
    source utils/setup_root.sh
    SUMMARYFOLDER=output/gof/${NTUPLETAG}-${TAG}/plots
    [ -d $SUMMARYFOLDER ] || mkdir -p $SUMMARYFOLDER
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        PLOTDIR=${datacard_output}/plots
        PREFITFILE=${datacard_output}/${ID}-datacard-shapes-prefit.root
        POSTFITFILE=${datacard_output}/${ID}-datacard-shapes-postfit-b.root
        [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
        echo "[INFO] Using postfitshapes from $FILE"
        # python3 plotting/plot_shapes.py -i $FILE -o $PLOTDIR \
        #         -c ${channel} -e $ERA --categories $CATEGORIES \
        #         --fake-factor --embedding --normalize-by-bin-width \
        #         -l --train-ff True --train-emb True
        # CATEGORIES="stxs_stage0"

        # python3 plotting/plot_shapes_combined.py -i $FILE -o $PLOTDIR -c ${CHANNEL} -e $ERA --categories "None" --fake-factor --embedding -l --train-ff True --train-emb True --combine-backgrounds
        # python3 plotting/plot_shapes_combined.py -i $FILE -o $PLOTDIR -c ${CHANNEL} -e $ERA --categories "None" --fake-factor --embedding -l --train-ff True --train-emb True --combine-backgrounds
        for OPTION in "" "--png"; do
            python3 gof/plot_shapes_gof.py -i $PREFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor --embedding \
                --gof-variable $VARIABLE -o ${PLOTDIR}
            python3 gof/plot_shapes_gof.py -i $POSTFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor --embedding \
                --gof-variable $VARIABLE -o ${PLOTDIR}
        done
        cp ${PLOTDIR}/*.p{df,ng} $SUMMARYFOLDER
    done
    exit 0
fi

if [[ $MODE == "PLOT-POSTFIT-MC" ]]; then
    source utils/setup_root.sh
    SUMMARYFOLDER=output/gof/${NTUPLETAG}-${TAG}/plots
    [ -d $SUMMARYFOLDER ] || mkdir -p $SUMMARYFOLDER
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        PLOTDIR=${datacard_output}/plots
        PREFITFILE=${datacard_output}/${ID}-datacard-shapes-prefit.root
        POSTFITFILE=${datacard_output}/${ID}-datacard-shapes-postfit-b.root
        [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
        echo "[INFO] Using postfitshapes from $FILE"
        for OPTION in "" "--png"; do
            python3 gof/plot_shapes_gof.py -i $PREFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor \
                --gof-variable $VARIABLE -o ${PLOTDIR}
            python3 gof/plot_shapes_gof.py -i $POSTFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor \
                --gof-variable $VARIABLE -o ${PLOTDIR}
        done
        cp ${PLOTDIR}/*.p{df,ng} $SUMMARYFOLDER
    done
    exit 0
fi

if [[ $MODE == "IMPACTS" ]]; then
    source utils/setup_cmssw.sh
    WORKSPACE=output/$datacard_output/mt/125/workspace.root
    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --doInitialFit --robustFit 1 \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --robustFit 1 --doFits \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 -o sm_${ERA}_${CHANNEL}.json
    plotImpacts.py -i sm_${ERA}_${CHANNEL}.json -o sm_${ERA}_${CHANNEL}_impacts
    # cleanup the fit files
    rm higgsCombine*.root
    exit 0
fi
