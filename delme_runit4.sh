CMSSW_BASE=CMSSW_14_1_0_pre4
CHANNEL=mt
ERA=2018
datacard_output="2026-05-05__datacard_nn_output"
TAG="nn_output_groupedDNN__FF_adjusted__2026-04-30__v1"

MODE=$1

ABS_BASE="$PWD/$datacard_output/${CHANNEL}/125"
ABS_WS="$ABS_BASE/workspace.root"
ABS_WS_INCL="$ABS_BASE/workspace_inclusive.root"

# VSCode nesting anchor files
make_collections() {
    local dir=$1
    local exts=("root" "json" "png" "pdf" "txt" "out" "C" "cmb")
    
    # Enable nullglob so empty matches return empty array
    shopt -q nullglob; local ng=$?
    shopt -s nullglob

    for ext in "${exts[@]}"; do
        local files=("$dir"/*."$ext")
        if (( ${#files[@]} > 0 )); then
            touch "$dir/_.$ext.collection"
        fi
    done
    
    # Restore nullglob state
    (( ng == 0 )) || shopt -u nullglob
}

POIS=( "r_qqH_201to202" "r_qqH_203to210" "r_ggH_101to104" "r_ggH_105to106" "r_ggH_107to109" "r_ggH_110to116" )
POI_CSV=$(IFS=, ; echo "${POIS[*]}")

SET_PARAMS=""
RANGES=""
for POI in "${POIS[@]}"; do
    SET_PARAMS+="${POI}=1.0,"
    RANGES+="${POI}=-5.0,5.0:"
done
SET_PARAMS=${SET_PARAMS%,}
RANGES=${RANGES%:}

OPTS_FIT=(
    "--robustFit 1"
    "--X-rtd MINIMIZER_analytic"
    "--X-rtd FITTER_DYN_STEP"
    "--cminDefaultMinimizerStrategy 0"
    "--setParameterRanges $RANGES"
    "--setParameters $SET_PARAMS"
    "-m 125"
)

if (( IS_TOYS )); then
    OPTS_FIT+=("-t" "1" "-s" "19")
fi

if [[ "$MODE" == "DATACARD" || "$MODE" == "ALL" ]]; then
    echo "[INFO] Run make_datacards.py"
    python3 ${CMSSW_BASE}/src/CombineHarvester/SMRun2Legacy/scripts/make_datacards.py \
        --base-path=$PWD \
        --input-folder-${CHANNEL}="output/2018-mt-ff_and_cr_2018UL_mt__2026-03-27__v2-${TAG}/synced" \
        --real-data=false \
        --bbb=true \
        --jetfakes=true \
        --embedding=true \
        --postfix="-ML" \
        --channels=${CHANNEL} \
        --rebinning-strategy="combine" \
        --convert-shapes-to-lnN=true \
        --stxs-signals="stxs_stage1p2_syst" \
        --categories="stxs_stage1p2_syst" \
        --era=${ERA} \
        --output-folder=$datacard_output \
        --ggh-wg1=true \
        --qqh-wg1=true
    
    make_collections "$ABS_BASE"
    echo "[INFO] Done datacard creation"
fi

if [[ "$MODE" == "WORKSPACE" || "$MODE" == "ALL" ]]; then
    echo "[INFO] Create Multi-POI workspace"
    combineTool.py -M T2W -o workspace.root -i $datacard_output/${CHANNEL}/125 --parallel 4 -m 125 \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=.*bin201to202.*$:r_qqH_201to202[1,-5,5]"' \
        --PO '"map=.*bin203to210.*$:r_qqH_203to210[1,-5,5]"' \
        --PO '"map=.*bin101to104.*$:r_ggH_101to104[1,-5,5]"' \
        --PO '"map=.*bin105to106.*$:r_ggH_105to106[1,-5,5]"' \
        --PO '"map=.*bin107to109.*$:r_ggH_107to109[1,-5,5]"' \
        --PO '"map=.*bin110to116.*$:r_ggH_110to116[1,-5,5]"'
    
    make_collections "$ABS_BASE"
fi

if [[ "$MODE" == "WORKSPACE-INCLUSIVE" || "$MODE" == "ALL" ]]; then
    echo "[INFO] Create 1-POI inclusive workspace (POI=r)"
    combineTool.py -M T2W -o workspace_inclusive.root -i $datacard_output/${CHANNEL}/125 --parallel 4 -m 125

    make_collections "$ABS_BASE"
fi

if [[ "$MODE" == "PREFIT" || "$MODE" == "ALL" ]]; then
    echo "[INFO] Extract pre-fit shapes"
    mkdir -p "$ABS_BASE/shapes"
    PostFitShapesFromWorkspace -w $ABS_WS \
        -m 125 -d $ABS_BASE/combined.txt.cmb \
        --output $ABS_BASE/shapes/datacard-shapes-prefit.root
        
    make_collections "$ABS_BASE/shapes"
fi

if [[ "$MODE" == "FITDIAGNOSTICS" || "$MODE" == "ALL" ]]; then
    echo "[INFO] FitDiagnostics & Pulls"
    mkdir -p "$ABS_BASE/diagnostics"
    pushd "$ABS_BASE/diagnostics" > /dev/null
    
    combine -M FitDiagnostics -d $ABS_WS -n .fitdiag \
        --redefineSignalPOIs $POI_CSV \
        --plots --saveShapes --saveWithUncertainties --saveOverallShapes --numToysForShapes 1000 \
        $(printf "%s " "${OPTS_FIT[@]}")

    python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
        -a fitDiagnostics.fitdiag.root -g pulls.root | tee pulls.txt
        
    popd > /dev/null

    make_collections "$ABS_BASE/diagnostics"
fi

if [[ "$MODE" == "POSTFIT" || "$MODE" == "ALL" ]]; then
    echo "[INFO] PostFit Shapes (Multi-POI)"
    mkdir -p "$ABS_BASE/shapes"
    PostFitShapesFromWorkspace -w $ABS_WS \
        -m 125 -d $ABS_BASE/combined.txt.cmb \
        -f $ABS_BASE/diagnostics/fitDiagnostics.fitdiag.root:fit_s \
        --output $ABS_BASE/shapes/datacard-shapes-postfit.root \
        --postfit --sampling
        
    make_collections "$ABS_BASE/shapes"
fi

if [[ "$MODE" == "FIT-SINGLES" || "$MODE" == "ALL" ]]; then
    echo "[INFO] MultiDimFit Singles (Stat+Syst / Stat-only)"
    mkdir -p "$ABS_BASE/fits"
    pushd "$ABS_BASE/fits" > /dev/null

    combineTool.py -M MultiDimFit -d $ABS_WS --algo singles -n .sys_singles $(printf "%s " "${OPTS_FIT[@]}")
    combineTool.py -M MultiDimFit -d $ABS_WS --algo singles -n .snap --saveWorkspace $(printf "%s " "${OPTS_FIT[@]}")
    combineTool.py -M MultiDimFit -d "higgsCombine.snap.MultiDimFit.mH125.root" \
        --snapshotName MultiDimFit --algo singles -n .stat_singles \
        --freezeParameters allConstrainedNuisances $(printf "%s " "${OPTS_FIT[@]}")
        
    popd > /dev/null

    make_collections "$ABS_BASE/fits"
fi

if [[ "$MODE" == "FIT-GRID" || "$MODE" == "ALL" ]]; then
    echo "[INFO] MultiDimFit Grid Scans"
    mkdir -p "$ABS_BASE/fits"
    pushd "$ABS_BASE/fits" > /dev/null

    for POI in "${POIS[@]}"; do
        combineTool.py -M MultiDimFit -d $ABS_WS \
            --algo grid --points 301 -n .sys_grid_${POI} -P $POI --parallel 32 $(printf "%s " "${OPTS_FIT[@]}")
        
        combineTool.py -M MultiDimFit -d "higgsCombine.snap.MultiDimFit.mH125.root" --snapshotName MultiDimFit \
            --algo grid --points 301 -n .stat_grid_${POI} -P $POI \
            --freezeParameters allConstrainedNuisances --parallel 32 $(printf "%s " "${OPTS_FIT[@]}")
    done
    popd > /dev/null

    make_collections "$ABS_BASE/fits"
fi

if [[ "$MODE" == "IMPACTS" || "$MODE" == "ALL" ]]; then
    echo "[INFO] Impacts per POI"
    mkdir -p "$ABS_BASE/impacts"
    pushd "$ABS_BASE/impacts" > /dev/null
    
    for POI in "${POIS[@]}"; do
        echo "[INFO] Computing impacts for $POI"
        
        combineTool.py -M Impacts -d "$ABS_WS" -n .impacts_${POI} --redefineSignalPOIs $POI --doInitialFit $(printf "%s " "${OPTS_FIT[@]}")
        combineTool.py -M Impacts -d "$ABS_WS" -n .impacts_${POI} --redefineSignalPOIs $POI --doFits --parallel 32 --cminPreFit 2 --cminPreScan --cminDefaultMinimizerTolerance 0.01 $(printf "%s " "${OPTS_FIT[@]}")
        combineTool.py -M Impacts -d "$ABS_WS" -n .impacts_${POI} --redefineSignalPOIs $POI -o impacts_${POI}.json $(printf "%s " "${OPTS_FIT[@]}")
        
        plotImpacts.py -i impacts_${POI}.json -o impacts_${POI}
    done
    
    popd > /dev/null

    make_collections "$ABS_BASE/impacts"
fi

if [[ "$MODE" == "IMPACTS-INCLUSIVE" || "$MODE" == "ALL" ]]; then
    echo "[INFO] Impacts Inclusive (POI=r)"
    mkdir -p "$ABS_BASE/impacts_inclusive"
    pushd "$ABS_BASE/impacts_inclusive" > /dev/null
    
    OPTS_INCL=(
        "--robustFit 1"
        "--X-rtd MINIMIZER_analytic"
        "--X-rtd FITTER_DYN_STEP"
        "--cminDefaultMinimizerStrategy 0"
        "--setParameterRanges r=-5.0,5.0"
        "-m 125"
    )
    
    combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl --redefineSignalPOIs r --doInitialFit $(printf "%s " "${OPTS_INCL[@]}")
    combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl --redefineSignalPOIs r --doFits --parallel 32 --cminPreFit 2 --cminPreScan --cminDefaultMinimizerTolerance 0.01 $(printf "%s " "${OPTS_INCL[@]}")
    combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl --redefineSignalPOIs r -o impacts_incl.json $(printf "%s " "${OPTS_INCL[@]}")
    
    plotImpacts.py -i impacts_incl.json -o impacts_incl
    
    popd > /dev/null

    make_collections "$ABS_BASE/impacts_inclusive"
fi
