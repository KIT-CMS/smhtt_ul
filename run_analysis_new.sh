export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL="mt"
ERA="2018"
NTUPLETAG="ff_and_cr_2018UL_mt__2026-03-27__v2"
# TAG="nn_output_groupedDNN__FF_adjusted__2026-04-30__v1"
# TAG="nn_output_groupedDNN__2026-04-30__v1"
# TAG="nn_output_groupedDNN__FF_adjusted__2026-05-07__1sigmatest__v1"
# TAG="test_new_nominal_1sigma_ff__v1"
# TAG="test_old_nominal_1sigma__ff__v1"

# TAG="test_old_nominal_1sigma__ff__half_fix__v1"
# TAG="nn_output_CENNT_ml_ff_fixed_ff_unct__adjusted_syst_test"
# TAG="nn_output_CENNT__2026-05-25__ml_ff_fixed_ff_unct__adjusted_syst_test"

# TAG="nn_output_SANNT__2026-05-29__ml_ff_fixed_ff_unct__adjusted_syst_test"

# ---

# TAG="nn_output_SANNT__2026-05-31__N2pmp100___ml_ff_fixed_ff_unct__adjusted_syst_test"

FORCE_REPROCESSING=1

MODE=$1
TAG=$2

POSTFIX="-ML"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Datacard Setup
datacard_output="datacards/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}"

# output_shapes="analysis_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
# shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
# 
# shapes_output_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
# shapes_rootfile=${shapes_output}.root
# shapes_rootfile_synced=${shapes_output_synced}_synced.root

# ---

shapes_dir="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
shapes_output_synced="${shapes_dir}/synced"
shapes_rootfile_synced="${shapes_output_synced}_synced.root"

candidate_files=($(find "$shapes_dir" -maxdepth 1 -name "*_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}.root" 2>/dev/null))

if [ ${#candidate_files[@]} -eq 1 ]; then
    shapes_rootfile="${candidate_files[0]}"
    shapes_prefix=$(basename "$shapes_rootfile" | cut -d'_' -f1)
    echo ">> Auto-detected shapes file: $shapes_rootfile (Type: $shapes_prefix)"
else
    if [ ${#candidate_files[@]} -gt 1 ]; then
        echo ">> WARNING: Multiple shape files found in $shapes_dir. Defaulting to 'analysis'."
    fi
    shapes_prefix="analysis"
    shapes_rootfile="${shapes_dir}/${shapes_prefix}_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}.root"
    echo ">> Target path initialized: $shapes_rootfile"
fi

shapes_output="${shapes_rootfile%.root}"

# ---

if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
fi

echo "###################################"
echo "#           Mode ${MODE}          #"
echo "###################################"

if [[ $MODE == "SYNC" ]]; then
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python shapes/convert_to_synced_shapes_without_emb_es_id.py -e $ERA \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        -n 1

    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}*.root

    exit 0
fi

# ---

if [[ $MODE == "SYNC-CONTROL" ]]; then
    source utils/setup_root.sh

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

if [[ $MODE == "DATACARD-CONTROL" ]]; then
    source utils/setup_cmssw.sh

    if [[ -z "${VARIABLES}" ]]; then
        variables_list=()
        for file in "$shapes_output_synced"/*-synced-*.root; do
            [ -f "$file" ] || continue
            var=$(basename "$file" | sed -E "s/^${ERA}[_-]${CHANNEL}-synced-//" | sed "s/\.root$//")
            variables_list+=("$var")
        done
    else
        IFS=',' read -r -a variables_list <<< "${VARIABLES}"
    fi

    echo "[INFO] Variables to process: ${variables_list[*]}"

    run_morphing() {
        VARIABLE=$1

        local datacard_output="output/control_with_systematics/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}_${VARIABLE}"
        local workspace_file="${datacard_output}/${CHANNEL}/workspace.root"

        if [[ -z "${FORCE_REPROCESSING}" && (-f "$workspace_file") ]]; then
            echo "[INFO] Workspace file for ${VARIABLE} already exists at ${workspace_file}. Skipping."
            return 0
        fi

        mkdir -p $datacard_output

        echo "[INFO] Processing variable: ${VARIABLE}"

        datacard_output="output/control_with_systematics/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}_${VARIABLE}"
        GOF_CATEGORY_NAME=${CHANNEL}_${VARIABLE}
        echo "[INFO] GOF category name: ${GOF_CATEGORY_NAME}"
        FILENAME="${ERA}-${CHANNEL}-synced-${VARIABLE}.root"

        CMSSW_BASE=CMSSW_14_1_0_pre4
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
            --train_emb=1 \
            --ggh_wg1=1 \
            --qqh_wg1=1
        THIS_PWD=${PWD}
        echo $THIS_PWD

        cd $datacard_output/${CHANNEL}
        for FILE in */*.txt; do
            if ! grep -q "autoMCStats" "$FILE"; then
                sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
            fi
        done
        
        if [ -d "$datacard_output/cmb" ]; then
            cd $datacard_output/cmb
            for FILE in */*.txt; do
                if ! grep -q "autoMCStats" "$FILE"; then
                    sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
                fi
            done
        fi

        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -o workspace.root -i $datacard_output/${CHANNEL}/125 --channel-masks
    }

    export -f run_morphing
    export NTUPLETAG TAG ERA CHANNEL shapes_output_synced CMSSW_BASE FORCE_REPROCESSING

    printf "%s\n" "${variables_list[@]}" | xargs -P 50 -I {} bash -c 'run_morphing "{}"'
    wait

    exit 0
fi

if [[ $MODE == "PREFIT-CONTROL" ]]; then
    source utils/setup_cmssw.sh

    if [[ -z "${VARIABLES}" ]]; then
        variables_list=()
        for file in "$shapes_output_synced"/*-synced-*.root; do
            [ -f "$file" ] || continue
            var=$(basename "$file" | sed -E "s/^${ERA}[_-]${CHANNEL}-synced-//" | sed "s/\.root$//")
            variables_list+=("$var")
        done
    else
        IFS=',' read -r -a variables_list <<< "${VARIABLES}"
    fi

    echo "[INFO] Variables to process for prefit: ${variables_list[*]}"

    run_prefit_for_variable() {
        VARIABLE=$1
        
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        
        if [[ "$shapes_prefix" == "control" ]]; then
            datacard_output="output/control_with_systematics/${NTUPLETAG}-${TAG}/${ID}"
        else
            datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        fi

        WORKSPACE=$datacard_output/${CHANNEL}/125/workspace.root
        final_prefit_file="${datacard_output}/${ID}-datacard-shapes-prefit.root"

        if [[ -z "${FORCE_REPROCESSING}" && (-f "$final_prefit_file") ]]; then
            echo "[INFO] Prefit file for ${VARIABLE} already exists. Skipping."
            return 0
        fi

        echo "[INFO] Processing prefit shapes for variable: ${VARIABLE}"

        local text_card=$(find "$datacard_output/cmb/125" -maxdepth 1 -name "*.txt" 2>/dev/null | head -n 1)
        if [[ -z "$text_card" ]]; then
            text_card=$(find "$datacard_output/${CHANNEL}/125" -maxdepth 1 -name "*.txt" 2>/dev/null | head -n 1)
        fi

        if [[ -f "$WORKSPACE" && -f "$text_card" ]]; then
            PostFitShapesFromWorkspace -m 125 -w "$WORKSPACE" \
                --output "$final_prefit_file" \
                -d "$text_card" > /dev/null 2>&1
            echo "[DONE] Created prefit shapes for $VARIABLE"
        else
            echo "[ERROR] Missing workspace or text card for variable $VARIABLE"
            return 1
        fi
    }

    export -f run_prefit_for_variable
    export ERA CHANNEL NTUPLETAG TAG FORCE_REPROCESSING shapes_prefix

    echo "[INFO] Starting parallel pre-fit shape generation..."
    
    printf "%s\n" "${variables_list[@]}" | xargs -P 50 -I {} bash -c 'run_prefit_for_variable "{}"'

    echo "[INFO] All pre-fit files complete."
    exit 0
fi

if [[ $MODE == "PLOT-PREFIT-CONTROL" ]]; then
    source utils/setup_root.sh
    source utils/common_args.sh
    
    if [[ "$shapes_prefix" == "control" ]]; then
        export SUMMARYFOLDER="output/control_with_systematics/${NTUPLETAG}-${TAG}/plots"
    else
        export SUMMARYFOLDER="output/gof/${NTUPLETAG}-${TAG}/plots"
    fi
    [ -d "$SUMMARYFOLDER" ] || mkdir -p "$SUMMARYFOLDER"

    if [[ -z "${VARIABLES}" ]]; then
        variables_list=()
        for file in "$shapes_output_synced"/*-synced-*.root; do
            [ -f "$file" ] || continue
            var=$(basename "$file" | sed -E "s/^${ERA}[_-]${CHANNEL}-synced-//" | sed "s/\.root$//")
            variables_list+=("$var")
        done
    else
        IFS=',' read -r -a variables_list <<< "${VARIABLES}"
    fi

    run_plot_prefit() {
        VARIABLE=$1
        
        source utils/setup_root.sh
        source utils/common_args.sh

        ID=${ERA}_${CHANNEL}_${VARIABLE}
        
        if [[ "$shapes_prefix" == "control" ]]; then
            datacard_output="output/control_with_systematics/${NTUPLETAG}-${TAG}/${ID}"
        else
            datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        fi
        PLOTDIR=${datacard_output}/plots

        final_plot_pdf="${PLOTDIR}/${ID}_prefit.pdf"
        final_plot_png="${PLOTDIR}/${ID}_prefit.png"

        if [[ -z "${FORCE_REPROCESSING}" && (-f "$final_plot_pdf" || -f "$final_plot_png") ]]; then
            echo "[INFO] Prefit plots for ${VARIABLE} already exist. Skipping."
            [ -f "${SUMMARYFOLDER}/${ID}_prefit.pdf" ] || cp "${PLOTDIR}"/*.p{df,ng} "$SUMMARYFOLDER" 2> /dev/null
            return 0
        fi

        PREFITFILE=${datacard_output}/${ID}-datacard-shapes-prefit.root
        
        [ -d "$PLOTDIR" ] || mkdir -p "$PLOTDIR"
        
        echo "[INFO] Processing plots for variable: ${VARIABLE}"

        AXIS_FLAG="-l"
        if [[ " ${LOG_VARIABLES} " =~ " ${VARIABLE} " ]]; then
            AXIS_FLAG=""
        fi

        python3 plotting/plot_shapes_gof_new.py \
            --region "Nominal" \
            --era $ERA \
            --channel $CHANNEL \
            --input-file $PREFITFILE \
            --variable $VARIABLE \
            --embedding \
            --fake-factor \
            --output-folder "${PLOTDIR}" \
            --suffix "_prefit" \
            --gof-binning-config "config/gof_binning/binning_${ERA}_${CHANNEL}_2D.yaml" \
            --replace-close-to-zero-with-zero

        cp "${PLOTDIR}"/*.p{df,ng} "$SUMMARYFOLDER" 2>/dev/null
        
        echo "[DONE] Finished plotting ${VARIABLE}"
    }

    export -f run_plot_prefit
    export ERA CHANNEL NTUPLETAG TAG FORCE_REPROCESSING SUMMARYFOLDER shapes_prefix

    echo "[INFO] Starting parallel pre-fit plotting..."
    
    printf "%s\n" "${variables_list[@]}" | xargs -P 100 -I {} bash -c 'run_plot_prefit "{}"'
    echo "[INFO] All plotting jobs complete."
    exit 0
fi































if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw.sh
    # inputfile
    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"

    ${CMSSW_BASE}/bin/el9_amd64_gcc12/MorphingSMRun2Legacy \
        --base_path=$PWD \
        --input_folder_mt=$shapes_output_synced \
        --real_data=false \
        --classic_bbb=false \
        --binomial_bbb=false \
        --jetfakes=1 \
        --embedding=1 \
        --postfix="-ML" \
        --channel=${CHANNEL} \
        --auto_rebin=true \
        --stxs_signals="stxs_stage0_syst" \
        --categories="stxs_stage0_syst" \
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

if [[ $MODE == "FIT" ]]; then
    source utils/setup_cmssw.sh
        combineTool.py \
        -M MultiDimFit \
        -m 125 \
        -d output/$datacard_output/$CHANNEL/125/workspace.root \
        --algo singles \
        --robustFit 1 \
        --X-rtd MINIMIZER_analytic \
        --cminDefaultMinimizerStrategy 0 \
        -n $ERA -v1 \
        --parallel 1 --there
    for RESDIR in output/$datacard_output/$CHANNEL/125; do
        echo "[INFO] Printing fit result for category $(basename $RESDIR)"
        FITFILE=${RESDIR}/higgsCombine${ERA}.MultiDimFit.mH125.root
        python datacards/print_fitresult.py ${FITFILE}
    done
    exit 0
fi

if [[ $MODE == "FIT-SPLIT" ]]; then
    # source utils/setup_cmssw.sh
    ./fitting/fit_split_by_unc_cons.sh $datacard_output $ERA $CHANNEL 0 "inclusive"
    ./fitting/fit_split_by_unc_cons.sh $datacard_output $ERA $CHANNEL 0 "stage0"
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

if [[ $MODE == "IMPACTS" ]]; then
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

    combineTool.py -M Impacts -d $WORKSPACE -m 125 -o sm_${ERA}_${CHANNEL}_impacts.json
    plotImpacts.py -i sm_${ERA}_${CHANNEL}_impacts.json -o sm_${ERA}_${CHANNEL}_impacts
    # cleanup the fit files
    rm higgsCombine*.root
    mv sm_${ERA}_${CHANNEL}_impacts.pdf output/$datacard_output/
    mv sm_${ERA}_${CHANNEL}_impacts.json output/$datacard_output/
    exit 0
fi
