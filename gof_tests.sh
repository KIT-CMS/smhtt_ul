export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw

set -e
set -o pipefail

CHANNEL="mt"
ERA="2018"
NTUPLETAG="ff_and_cr_production_2018UL_mt__2025-09-10_w_syst_v2"
TAG="2025-09-10__test_2d_gof_binning__v6"
YAML_FILE="config/gof_binning_mp2/binning_${ERA}_${CHANNEL}_2D.yaml"

FORCE_REPROCESSING=0

MODE=$1

# ---

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


echo "[INFO] Parsing variables from ${YAML_FILE} based on master 1D list..."
mapfile -t all_yaml_keys < <(grep '^[^ ]' "$YAML_FILE" | sed 's/://')  # all keys from the YAML.

declare -A master_vars_map
for var in "${VARIABLES_LIST_1D[@]}"; do
    master_vars_map["$var"]=1
done

final_variables_list=()
for key in "${all_yaml_keys[@]}"; do
    if [[ -v master_vars_map["$key"] ]]; then
        final_variables_list+=("$key")
        continue # 1D match
    fi

    for var1 in "${VARIABLES_LIST_1D[@]}"; do
        if [[ "$key" == "${var1}_"* ]]; then  # key starts with "var1_"
            var2=${key#${var1}_}
            
            if [[ -v master_vars_map["$var2"] ]]; then
                final_variables_list+=("$key")
                break # Found a valid combination
            fi
        fi
    done
done

# VARIABLES_LIST=( pt_vis )

VARIABLES_1D=$(IFS=, ; echo "${VARIABLES_LIST_1D[*]}")
VARIABLES=$(IFS=, ; echo "${final_variables_list[*]}")

echo "[INFO] Using ${#VARIABLES_LIST_1D[@]} master 1D variables."
echo "[INFO] Found ${#final_variables_list[@]} total matching variables (1D & 2D) in YAML to process."

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

THEORY_NUISANCES_TO_FREEZE="rgx{BR_Htt.*},rgx{LHE_.*},rgx{PS_scale.*},rgx{THU_.*},rgx{ggH_scale.*},rgx{vbf_scale.*}"

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

    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python3 shapes/convert_to_synced_shapes.py -e $ERA \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        -n 40 --gof

    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}*.root

    exit 0
fi

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw.sh
    run_morphing() {
        VARIABLE=$1

        local datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}_${VARIABLE}"
        local workspace_file="${datacard_output}/${CHANNEL}/workspace.root"

        if [[ -z "${FORCE_REPROCESSING}" && (-f "$workspace_file") ]]; then
            echo "[INFO] Workspace file for ${VARIABLE} already exists at ${workspace_file}. Skipping."
            return 0
        fi

        echo "[INFO] Processing variable: ${VARIABLE}"

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
    export NTUPLETAG TAG ERA CHANNEL shapes_output_synced CMSSW_BASE FORCE_REPROCESSING

    echo ${VARIABLES//,/ } | tr ' ' '\n' | xargs -n 1 -P 60 -I {} bash -c 'run_morphing "{}"'

    wait

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

if [[ $MODE == "GOF" ]]; then
    source utils/setup_cmssw.sh

    run_gof_for_variable() {
        VARIABLE=$1
        
        ID=${ERA}_${CHANNEL}_${VARIABLE}

        local output_dir="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        local final_json="$output_dir/gof.json"
        local final_plot_pdf="$output_dir/gof.pdf"
        local final_plot_png="$output_dir/gof.png"
        local final_root_file="$output_dir/higgsCombineTest.${ID}.GoodnessOfFit.mH125.root"

        if [[ -z "${FORCE_REPROCESSING}" && (-f "$final_json" && (-f "$final_plot_pdf" || -f "$final_plot_png") && -f "$final_root_file") ]]; then
            echo "[INFO] All output files for ${VARIABLE} in ${output_dir} already exist. Skipping."
            return 0
        fi

        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        WORKSPACE=$datacard_output/${CHANNEL}/125/workspace.root
        MASS=125
        NUM_TOYS=100 # multiply x10 later on

        FREEZE_OPTS="--setParameters r=0 --freezeParameters r,${THEORY_NUISANCES_TO_FREEZE} --fixedSignalStrength=0"

        # for ALGO in "saturated" "KS" "AD"; do
        for ALGO in "saturated"; do
            if [[ "$ALGO" == "saturated" ]]; then
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE ${FREEZE_OPTS} -v 1 -V
            else
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE --plots ${FREEZE_OPTS} -v 1 -V
            fi

            TOYSOPT=""
            if [[ "$ALGO" == "saturated" ]]; then
                TOYSOPT="--toysFrequentist"
            fi

            for SEED in {1230..1239}; do
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s ${SEED} -t $NUM_TOYS $TOYSOPT -V ${FREEZE_OPTS} >/dev/null &
            done
            wait

            DATA_FILE="higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root"
            INPUT_FILES=()

            for SEED in {1230..1239}; do
                TOY_FILE="higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.${SEED}.root"
                INPUT_FILES+=("$DATA_FILE" "$TOY_FILE")
            done

            # Collect results
            combineTool.py -M CollectGoodnessOfFit --input "${INPUT_FILES[@]}"
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
    export NTUPLETAG TAG ERA CHANNEL THEORY_NUISANCES_TO_FREEZE FORCE_REPROCESSING

    echo ${VARIABLES//,/ } | tr ' ' '\n' | xargs -n 1 -P 1 -I {} bash -c 'run_gof_for_variable "{}"'

    wait

    echo "[INFO] All GOF jobs complete. Creating summary plot."
    source utils/setup_root.sh
    python3 gof/plot_gof_summary_updated.py --variables $VARIABLES_1D --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL --threshold 0.00013225 --test-type gof
    python3 gof/plot_gof_summary_updated.py --variables $VARIABLES_1D --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL --threshold 0.00013225 --test-type gof_KS
    python3 gof/plot_gof_summary_updated.py --variables $VARIABLES_1D --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL --threshold 0.00013225 --test-type gof_AD    
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

        final_postfit_file="${datacard_output}/${ID}-datacard-shapes-postfit-b.root"
        if [[ -z "${FORCE_REPROCESSING}" && (-f "$final_postfit_file") ]]; then
            echo "[INFO] Final post-fit file for ${VARIABLE} already exists. Skipping."
            continue
        fi

        echo "[INFO] Processing variable: ${VARIABLE}"

        combine \
            -M FitDiagnostics \
            -m 125 -d $WORKSPACE \
            --robustFit 1 \
            --robustHesse 1 \
            -n .$ID \
            --verbose 2 \
            --setParameters r=0 --freezeParameters r,${THEORY_NUISANCES_TO_FREEZE} \
            --X-rtd MINIMIZER_analytic \
            --setRobustFitAlgo=Minuit2,Migrad  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001,Minuit2,Migrad,0:0.01 --cminPreScan \
            --saveShapes --saveWithUncertainties \
            --saveNormalizations --cminDefaultMinimizerTolerance 0.1 \
            --stepSize=0.01 \
            --cminDefaultMinimizerStrategy 2 2>&1 |
            tee .${ID}-${VARIABLE}.log
        
        if [ $? -ne 0 ]; then
            echo "[ERROR] The combine fit failed for variable: ${VARIABLE}. Check the log file .${ID}-${VARIABLE}.log for details. Skipping."
            rm -f fitDiagnostics.${ID}.root
            continue
        fi

        FITFILE=${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root
        mv fitDiagnostics.${ID}.root $FITFILE
        echo "done 1"
        # python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
        python3 diffNuisances.py \
            ${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root -a \
            -f html >${datacard_output}/nuisances.html
	    PostFitShapesFromWorkspace -m 125 -w $WORKSPACE \
            --output ${datacard_output}/${ID}-datacard-shapes-prefit.root \
            -d ${datacard_output}/cmb/125/htt_${CHANNEL}_300_${ERA}.txt
        PostFitShapesFromWorkspace -m 125 -w $WORKSPACE \
            --output ${datacard_output}/${ID}-datacard-shapes-postfit-b.root \
            -f ${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root:fit_b --postfit --sampling \
            -d ${datacard_output}/cmb/125/htt_${CHANNEL}_300_${ERA}.txt
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

        final_plot_pdf="${PLOTDIR}/${ID}_postfit.pdf"
        final_plot_png="${PLOTDIR}/${ID}_postfit.png"

        if [[ -z "${FORCE_REPROCESSING}" && (-f "$final_plot_pdf" || -f "$final_plot_png") ]]; then
            echo "[INFO] Post-fit plots for ${VARIABLE} already exist. Skipping."
            [ -f "${SUMMARYFOLDER}/${ID}_postfit.pdf" ] || cp "${PLOTDIR}"/*.p{df,ng} $SUMMARYFOLDER &> /dev/null
            continue
        fi

        PREFITFILE=${datacard_output}/${ID}-datacard-shapes-prefit.root
        POSTFITFILE=${datacard_output}/${ID}-datacard-shapes-postfit-b.root
        [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
        echo "[INFO] Using postfitshapes from $FILE"
        for OPTION in "" "--png"; do
            python3 gof/plot_shapes_gof.py -i $PREFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor --embedding \
                --gof-variable $VARIABLE -o ${PLOTDIR} -l
            python3 gof/plot_shapes_gof.py -i $POSTFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor --embedding \
                --gof-variable $VARIABLE -o ${PLOTDIR} -l
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
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        # WORKSPACE=$datacard_output/${CHANNEL}/125/workspace.root
        WORKSPACE=$(pwd)/${datacard_output}/${CHANNEL}/125/workspace.root
        IMPACTSDIR=${datacard_output}/impacts
            
            # --- DEFINE FINAL OUTPUT PATHS AND ADD SKIP LOGIC ---
            FINAL_JSON_PATH="${IMPACTSDIR}/impacts_${ID}.json"
            FINAL_PDF_PATH="${IMPACTSDIR}/impacts_${ID}.pdf"

            if [[ -f "$FINAL_JSON_PATH" && -f "$FINAL_PDF_PATH" ]]; then
                echo "[INFO] Impact plots for ${VARIABLE} already exist in ${IMPACTSDIR}. Skipping."
                continue
            fi
        
        mkdir -p $IMPACTSDIR
            
            echo "[INFO] Running impacts for variable: ${VARIABLE}"

        ROBUST_OPTS=(
            "--robustFit 1 \
                --robustHesse 1 \
                --setRobustFitAlgo Minuit2,Migrad \
                --cminDefaultMinimizerStrategy 2 \
                --cminDefaultMinimizerTolerance 0.1 \
                --stepSize=0.01 \
                --cminPreScan \
                --cminFallbackAlgo Minuit2,Migrad,0:0.01,Minuit2,Migrad,0:0.01 \
                --X-rtd FITTER_NEW_CROSSING_ALGO \
                --X-rtd FITTER_NEVER_GIVE_UP \
                --X-rtd MINIMIZER_analytic"
        )

        (cd $IMPACTSDIR && combineTool.py -M Impacts -d $WORKSPACE -m 125 \
                -n "_${ID}" \
                --doInitialFit \
            --parallel 16 \
                "${ROBUST_OPTS[@]}")

            (cd $IMPACTSDIR && combineTool.py -M Impacts -d $WORKSPACE -m 125 \
                -n "_${ID}" \
                --doFits \
                --parallel 16 \
                "${ROBUST_OPTS[@]}")
        
        (cd $IMPACTSDIR && combineTool.py -M Impacts -d $WORKSPACE -m 125 \
                -n "_${ID}" \
                -o $FINAL_JSON_PATH)

        plotImpacts.py -i $FINAL_JSON_PATH -o ${FINAL_PDF_PATH%.pdf}
        rm ${IMPACTSDIR}/higgsCombine*_${ID}.*.root
        exit 0
    done
    exit 0
fi
