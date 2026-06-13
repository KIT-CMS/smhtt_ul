CMSSW_BASE=CMSSW_14_1_0_pre4
CHANNEL=mt
ERA=2018
NTUPLETAG="ff_and_cr_2018UL_mt__2026-03-27__v2"

N_CORES=64

TAG=$1
shift

# If no modes specified, default to ALL
if (( $# == 0 )); then
    set -- "ALL"
fi

MODES=()
IS_TOYS=0
for arg in "$@"; do
    base_arg=${arg%-TOYS}
    MODES+=( "$base_arg" )
    if [[ "$arg" != "$base_arg" ]]; then
        IS_TOYS=1
    fi
done

has_mode() {
    local search=$1
    local mode
    for mode in "${MODES[@]}"; do
        if [[ "$mode" == "$search" || "$mode" == "ALL" ]]; then
            return 0
        fi
    done
    return 1
}

datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/datacards"
mkdir -p "$datacard_output"

DIR_SUFF=""
SEED="19"
SNAP_FILE="higgsCombine.snap.MultiDimFit.mH125.root"

if (( IS_TOYS )); then
    DIR_SUFF="_toys"
    SNAP_FILE="higgsCombine.snap.MultiDimFit.mH125.${SEED}.root"
fi

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

run_logged() {
    local logfile=$1
    shift

    "$@" 2>&1 | tee "$logfile"
    return ${PIPESTATUS[0]}
}

POIS=( "r_qqH_201to210" "r_ggH_101to104" "r_ggH_105to106" "r_ggH_107to109" "r_ggH_110to116" )
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
    "--cminDefaultMinimizerStrategy 1"
    "--setParameterRanges $RANGES"
    "--setParameters $SET_PARAMS"
)

OPTS_FALLBACK=(
    "--cminFallbackAlgo Minuit2,0:0.1"           # 1. Try Strategy 0 with looser tolerance (0.1)
    "--cminFallbackAlgo Minuit2,0:1.0"           # 2. Try Strategy 0 with very loose tolerance (1.0)
    "--cminFallbackAlgo Minuit2,Simplex,0:1.0"   # 3. Try Simplex if Migrad fails entirely
    "--X-rtd FITTER_NEVER_GIVE_UP"               # 4. Do not abort on intermediate failures
    "--X-rtd FITTER_BOUND"                       # 5. Prevent out-of-boundary parameters from crashing
)

OPTS_FIT+=( "${OPTS_FALLBACK[@]}" )

if (( IS_TOYS )); then
    OPTS_FIT+=("-t" "1" "-s" "$SEED")
    echo "[INFO] Toy mode enabled (Seed: $SEED)"
fi

if has_mode "DATACARD"; then
    echo "[INFO] Run make_datacards.py"
    python3 ${CMSSW_BASE}/src/CombineHarvester/SMRun2Legacy/scripts/make_datacards.py \
        --base-path=$PWD \
        --input-folder-${CHANNEL}="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced" \
        --real-data=false \
        --bbb=true \
        --jetfakes=true \
        --embedding=true \
        --postfix="-ML" \
        --channels=${CHANNEL} \
        --rebinning-strategy="combine" \
        --rebinning-using-combine-uncert-fraction 0.1 \
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

if has_mode "WORKSPACE"; then
    echo "[INFO] Create Multi-POI workspace"
    combineTool.py -M T2W -o workspace.root -i $datacard_output/${CHANNEL}/125 -m 125 \
        --parallel ${N_CORES} \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=.*bin201to210.*$:r_qqH_201to210[1,-5,5]"' \
        --PO '"map=.*bin101to104.*$:r_ggH_101to104[1,-5,5]"' \
        --PO '"map=.*bin105to106.*$:r_ggH_105to106[1,-5,5]"' \
        --PO '"map=.*bin107to109.*$:r_ggH_107to109[1,-5,5]"' \
        --PO '"map=.*bin110to116.*$:r_ggH_110to116[1,-5,5]"'
    
    make_collections "$ABS_BASE"
fi

if has_mode "WORKSPACE-INCLUSIVE"; then
    echo "[INFO] Create 1-POI inclusive workspace (POI=r)"
    combineTool.py -M T2W -o workspace_inclusive.root -i $datacard_output/${CHANNEL}/125 -m 125 \
        --parallel ${N_CORES}

    make_collections "$ABS_BASE"
fi

if has_mode "PREFIT"; then
    echo "[INFO] Extract pre-fit shapes"
    mkdir -p "$ABS_BASE/shapes${DIR_SUFF}"
    PostFitShapesFromWorkspace -w $ABS_WS -m 125 -d $ABS_BASE/combined.txt.cmb \
        --output $ABS_BASE/shapes${DIR_SUFF}/datacard-shapes-prefit.root

    make_collections "$ABS_BASE/shapes${DIR_SUFF}"
fi

if has_mode "FITDIAGNOSTICS"; then
    echo "[INFO] FitDiagnostics & Pulls"
    mkdir -p "$ABS_BASE/diagnostics${DIR_SUFF}"
    pushd "$ABS_BASE/diagnostics${DIR_SUFF}" > /dev/null
    
    run_logged fitDiagnostics.fitdiag.txt combine -M FitDiagnostics -d $ABS_WS -n .fitdiag -m 125 \
        --redefineSignalPOIs $POI_CSV \
        --plots --saveWithUncertainties \
        $(printf "%s " "${OPTS_FIT[@]}")

    run_logged pulls.txt python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
        -a fitDiagnostics.fitdiag.root -g pulls.root
        
    popd > /dev/null

    make_collections "$ABS_BASE/diagnostics${DIR_SUFF}"
fi

if has_mode "POSTFIT"; then
    echo "[INFO] PostFit Shapes (Multi-POI)"
    mkdir -p "$ABS_BASE/shapes${DIR_SUFF}"
    
    if (( IS_TOYS )); then
        echo "[WARNING] PostFitShapesFromWorkspace extracts expected PostFit shapes, but plotted data points will be Asimov!"
        echo "[WARNING] To plot Toy data points, extract 'data' manually from fitDiagnostics.fitdiag.root."
    fi

    PostFitShapesFromWorkspace -w $ABS_WS -m 125 -d $ABS_BASE/combined.txt.cmb \
        -f $ABS_BASE/diagnostics${DIR_SUFF}/fitDiagnostics.fitdiag.root:fit_s \
        --output $ABS_BASE/shapes${DIR_SUFF}/datacard-shapes-postfit.root \
        --postfit
        
    make_collections "$ABS_BASE/shapes${DIR_SUFF}"
fi

if has_mode "FIT-SINGLES"; then
    echo "[INFO] MultiDimFit Singles (Stat+Syst / Stat-only / Stat+Sys no BBB)"
    mkdir -p "$ABS_BASE/fits${DIR_SUFF}"
    pushd "$ABS_BASE/fits${DIR_SUFF}" > /dev/null

    run_logged sys_singles.txt combineTool.py -M MultiDimFit -d $ABS_WS -m 125 \
        --algo singles -n .sys_singles --floatOtherPOIs 1 \
        --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")
    run_logged snap.txt combineTool.py -M MultiDimFit -d $ABS_WS -m 125 \
        --algo singles -n .snap --saveWorkspace --floatOtherPOIs 1 \
        --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")
    run_logged sys_nobbb_singles.txt combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
        --algo singles -n .sys_nobbb_singles --floatOtherPOIs 1 \
        --snapshotName MultiDimFit --freezeNuisanceGroups autoMCStats --freezeParameters 'rgx{.*_bin_.*}' \
        --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")
    run_logged stat_singles.txt combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
        --algo singles -n .stat_singles --floatOtherPOIs 1 \
        --snapshotName MultiDimFit --freezeParameters allConstrainedNuisances \
        --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")
    run_logged sys_stat_bbb_singles.txt combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
        --algo singles -n .sys_stat_bbb_singles --floatOtherPOIs 1 \
        --snapshotName MultiDimFit --freezeNuisanceGroups ^autoMCStats \
        --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")
        
    popd > /dev/null
    make_collections "$ABS_BASE/fits${DIR_SUFF}"
fi

if has_mode "FIT-GRID"; then
    echo "[INFO] MultiDimFit Grid Scans"
    mkdir -p "$ABS_BASE/fits${DIR_SUFF}"
    pushd "$ABS_BASE/fits${DIR_SUFF}" > /dev/null

    for POI in "${POIS[@]}"; do
        run_logged "sys_grid_${POI}.txt" combineTool.py -M MultiDimFit -d $ABS_WS -m 125 \
            --algo grid --points 101 -n .sys_grid_${POI} --floatOtherPOIs 1 \
            -P $POI \
            --job-mode interactive --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")
        run_logged "sys_nobbb_grid_${POI}.txt" combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
            --algo grid --points 101 -n .sys_nobbb_grid_${POI} --floatOtherPOIs 1 \
            -P $POI \
            --snapshotName MultiDimFit --freezeNuisanceGroups autoMCStats --freezeParameters 'rgx{.*_bin_.*}' \
            --job-mode interactive --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")

        run_logged "sys_stat_bbb_grid_${POI}.txt" combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
            --algo grid --points 101 -n .sys_stat_bbb_grid_${POI} --floatOtherPOIs 1 \
            -P $POI \
            --snapshotName MultiDimFit --freezeNuisanceGroups ^autoMCStats \
            --job-mode interactive --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")

        # Use variable $SNAP_FILE to prevent Toy seed mismatch
        run_logged "stat_grid_${POI}.txt" combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
            --algo grid --points 101 -n .stat_grid_${POI} --floatOtherPOIs 1 \
            -P $POI \
            --snapshotName MultiDimFit --freezeParameters allConstrainedNuisances \
            --job-mode interactive --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")
    done
    popd > /dev/null
    make_collections "$ABS_BASE/fits${DIR_SUFF}"
fi

if has_mode "IMPACTS"; then
    # see https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/tutorial2023_unfolding/unfolding_exercise/#impacts
    echo "[INFO] Running Impacts (Single Pass for All POIs)"
    mkdir -p "$ABS_BASE/impacts${DIR_SUFF}"
    pushd "$ABS_BASE/impacts${DIR_SUFF}" > /dev/null
    
    run_logged "impacts_initial.txt" combineTool.py -M Impacts -d "$ABS_WS" -n .impacts -m 125 \
        --redefineSignalPOIs $POI_CSV --doInitialFit  \
        --parallel ${N_CORES} $(printf "%s " "${OPTS_FIT[@]}")
        
    run_logged "impacts_fits.txt" combineTool.py -M Impacts -d "$ABS_WS" -n .impacts -m 125 \
        --redefineSignalPOIs $POI_CSV --doFits \
        --cminPreFit 2 --cminPreScan --cminDefaultMinimizerTolerance 0.01 \
        --job-mode interactive --parallel ${N_CORES}  $(printf "%s " "${OPTS_FIT[@]}")
        
    run_logged "impacts_json.txt" combineTool.py -M Impacts -d "$ABS_WS" -n .impacts -o impacts.json -m 125 \
        --redefineSignalPOIs $POI_CSV \
        --parallel ${N_CORES}
    
    for POI in "${POIS[@]}"; do
        echo "[INFO] Generating impact plot for $POI"
        plotImpacts.py -i impacts.json -o impacts_${POI} --POI $POI
    done
    
    popd > /dev/null
    make_collections "$ABS_BASE/impacts${DIR_SUFF}"
fi

if has_mode "IMPACTS-INCLUSIVE"; then
    echo "[INFO] Impacts Inclusive (POI=r)"
    mkdir -p "$ABS_BASE/impacts_inclusive${DIR_SUFF}"
    pushd "$ABS_BASE/impacts_inclusive${DIR_SUFF}" > /dev/null
    
    OPTS_INCL=(
        "--robustFit 1"
        "--X-rtd MINIMIZER_analytic"
        "--X-rtd FITTER_DYN_STEP"
        "--cminDefaultMinimizerStrategy 1"
        "--setParameterRanges r=-5.0,5.0"
        "-m 125"
    )
    if (( IS_TOYS )); then
        OPTS_INCL+=("-t" "1" "-s" "$SEED")
    fi

    OPTS_INCL+=( "${OPTS_FALLBACK[@]}" )
    
    run_logged impacts_incl_initial.txt combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl -m 125 \
         --redefineSignalPOIs r --doInitialFit \
         --parallel ${N_CORES} $(printf "%s " "${OPTS_INCL[@]}")
    run_logged impacts_incl_fits.txt combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl -m 125 \
        --redefineSignalPOIs r --doFits --cminPreFit 2 --cminPreScan --cminDefaultMinimizerTolerance 0.01  \
        --job-mode interactive --parallel ${N_CORES} $(printf "%s " "${OPTS_INCL[@]}")
    run_logged impacts_incl_json.txt combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl -o impacts_incl.json -m 125 \
        --redefineSignalPOIs r \
        --parallel ${N_CORES} $(printf "%s " "${OPTS_INCL[@]}")
    
    plotImpacts.py -i impacts_incl.json -o impacts_incl
    
    popd > /dev/null
    make_collections "$ABS_BASE/impacts_inclusive${DIR_SUFF}"
fi

if has_mode "GOF-BKG"; then
    echo "[INFO] Run make_datacards.py for GoF Background-only"

    orig_datacard_output=$datacard_output
    orig_ABS_BASE=$ABS_BASE
    orig_ABS_WS=$ABS_WS

    datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/bkg_only_gof/datacards"
    ABS_BASE="$PWD/$datacard_output/${CHANNEL}/125"
    ABS_WS="$ABS_BASE/workspace.root"

    python3 ${CMSSW_BASE}/src/CombineHarvester/SMRun2Legacy/scripts/make_datacards.py \
        --base-path=$PWD \
        --input-folder-${CHANNEL}="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced" \
        --real-data=true \
        --bbb=true \
        --jetfakes=true \
        --embedding=true \
        --postfix="-ML" \
        --channels=${CHANNEL} \
        --rebinning-strategy="combine" \
        --rebinning-using-combine-uncert-fraction 0.1 \
        --convert-shapes-to-lnN=true \
        --era=${ERA} \
        --stxs-signals="stxs_stage1p2_syst" \
        --output-folder="${datacard_output}" \
        --categories="stxs_stage1p2_syst_bkg_only" \
        --ggh-wg1=true \
        --qqh-wg1=true \
        --nn-output-gof-bkg-only=true

    make_collections "$ABS_BASE"

    echo "[INFO] Create GoF background-only workspace"
    combineTool.py -M T2W -o workspace.root -i "$datacard_output/${CHANNEL}/125" -m 125 \
        --parallel ${N_CORES}

    echo "[INFO] Running GoF..."
    pushd "$ABS_BASE" > /dev/null

    THEORY_NUISANCES_TO_FREEZE="rgx{BR_Htt.*},rgx{LHE_.*},rgx{PS_scale.*},rgx{THU_.*},rgx{ggH_scale.*},rgx{vbf_scale.*}"
    GOF_FIT_OPTS=(
        "--setParameters" "r=0"
        "--fixedSignalStrength=0"
        "--cminDefaultMinimizerStrategy" "2"
        "--cminDefaultMinimizerTolerance" "0.1"
        "--cminPreScan"
        "--cminFallbackAlgo" "Minuit2,Migrad,0:0.01,Minuit2,Migrad,0:0.01"
        "--X-rtd" "FITTER_NEW_CROSSING_ALGO"
        "--X-rtd" "FITTER_NEVER_GIVE_UP"
        "--X-rtd" "MINIMIZER_analytic"
        "--X-rtd" "SIMPLE_RUNTIME_CHANGES"
        "--freezeParameters" "r,${THEORY_NUISANCES_TO_FREEZE}"
    )

    run_logged gof_observed.txt combine -M GoodnessOfFit workspace.root -m 125 --algo=saturated -n .Observed "${GOF_FIT_OPTS[@]}"

    for SEED_VAL in {1930..1939}; do
        combine -M GoodnessOfFit workspace.root -m 125 --algo=saturated \
            -t 100 -s "$SEED_VAL" --toysFrequentist -n .Toys \
            "${GOF_FIT_OPTS[@]}" \
            >/dev/null 2>&1 &
    done
    wait

    TOY_FILES=()
    for SEED_VAL in {1930..1939}; do
        TOY_FILES+=("higgsCombine.Toys.GoodnessOfFit.mH125.${SEED_VAL}.root")
    done

    run_logged gof_collect.txt combineTool.py -M CollectGoodnessOfFit \
        --input higgsCombine.Observed.GoodnessOfFit.mH125.root "${TOY_FILES[@]}" \
        --output gof.json

    plotGof.py --statistic saturated --mass 125.0 --output gof gof.json

    popd > /dev/null

    make_collections "$ABS_BASE"

    datacard_output=$orig_datacard_output
    ABS_BASE=$orig_ABS_BASE
    ABS_WS=$orig_ABS_WS

    echo "[INFO] Done GoF background-only workflow"
fi

if has_mode "BIAS"; then
    echo "[INFO] Run make_datacards.py for Multi-Signal Bias Test (Asimov templates)"
    
    orig_datacard_output=$datacard_output
    orig_ABS_BASE=$ABS_BASE
    orig_ABS_WS=$orig_ABS_WS

    datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/bias_test/datacards"
    ABS_BASE="$PWD/$datacard_output/${CHANNEL}/125"
    ABS_WS="$ABS_BASE/workspace.root"

    python3 ${CMSSW_BASE}/src/CombineHarvester/SMRun2Legacy/scripts/make_datacards.py \
        --base-path=$PWD \
        --input-folder-${CHANNEL}="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced" \
        --real-data=false \
        --bbb=true \
        --jetfakes=true \
        --embedding=true \
        --postfix="-ML" \
        --channels=${CHANNEL} \
        --rebinning-strategy="combine" \
        --rebinning-using-combine-uncert-fraction 0.1 \
        --convert-shapes-to-lnN=true \
        --stxs-signals="stxs_stage1p2_syst" \
        --categories="stxs_stage1p2_syst" \
        --era=${ERA} \
        --output-folder="${datacard_output}" \
        --ggh-wg1=true \
        --qqh-wg1=true \
        --bias-test=true
    
    make_collections "$ABS_BASE"

    echo "[INFO] Create Multi-POI bias workspace"
    combineTool.py -M T2W -o workspace_bias_test.root -i "$datacard_output/${CHANNEL}/125" -m 125 \
        --parallel ${N_CORES} \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=.*bin201to210.*$:r_qqH_201to210[1,-5,5]"' \
        --PO '"map=.*bin101to104.*$:r_ggH_101to104[1,-5,5]"' \
        --PO '"map=.*bin105to106.*$:r_ggH_105to106[1,-5,5]"' \
        --PO '"map=.*bin107to109.*$:r_ggH_107to109[1,-5,5]"' \
        --PO '"map=.*bin110to116.*$:r_ggH_110to116[1,-5,5]"'

    N_BIAS_JOBS=${N_BIAS_JOBS:-20}
    N_BIAS_TOYS=${N_BIAS_TOYS:-1000}
    TOYS_PER_JOB=$(( N_BIAS_TOYS / N_BIAS_JOBS ))

    echo "[INFO] Running parallelized Multi-POI Bias Fits (${N_BIAS_JOBS} jobs x ${TOYS_PER_JOB} toys each)..."
    pushd "$ABS_BASE" > /dev/null

    for (( JOB_IDX=0; JOB_IDX<N_BIAS_JOBS; JOB_IDX++ )); do
        SEED_VAL=$(( SEED + JOB_IDX ))
        combine -M MultiDimFit workspace_bias_test.root -m 125 \
            -t "$TOYS_PER_JOB" \
            -s "$SEED_VAL" \
            --algo singles \
            --cl=0.68 \
            --saveToys \
            --floatOtherPOIs 1 \
            $(printf "%s " "${OPTS_FIT[@]}") \
            -n ".BiasTest.job${JOB_IDX}" \
            >/dev/null 2>&1 &
    done
    wait

    echo "[INFO] Extracting pulls and computing bias from parallel jobs..."

    export POI_CSV
    export SEED

    cat << 'EOF' > calculate_bias_pulls.py
import ROOT, os, json, glob, numpy as np
from tqdm import tqdm

ROOT.gROOT.SetBatch(True)

pois = os.environ["POI_CSV"].split(",")
files = glob.glob("higgsCombine.BiasTest.job*.MultiDimFit.mH125.*.root")

toy_entries = {}

for file_path in tqdm(files, desc="Processing files"):
    f = ROOT.TFile.Open(file_path, "READ")
    tree = f.Get("limit")
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        if hasattr(tree, "iToy") and tree.iToy == 0:
            continue
        if (itoy := f"{file_path}_{tree.iToy}") not in toy_entries:
            toy_entries[itoy] = []
        entry_vals = {poi: getattr(tree, poi) for poi in pois}
        entry_vals["quantileExpected"] = tree.quantileExpected
        toy_entries[itoy].append(entry_vals)
    f.Close()

results = {}

for poi in pois:
    pulls, vals, errs = [], [], []
    for itoy, entries in tqdm(toy_entries.items(), desc=f"Processing toys for {poi}"):
        if not (best_fit_entries := [e for e in entries if e["quantileExpected"] == -1]):
            continue

        best_fit = best_fit_entries[0]
        val, all_vals = best_fit[poi], [e[poi] for e in entries]
        
        err_lo, err_hi = val - min(all_vals), max(all_vals) - val
        err = 0.5 * (err_lo + err_hi)

        pull = (val - 1.0) / err
        # pull = (1.0 - val) / err  # the cobine docu definition

        pulls.append(pull)
        vals.append(val)
        errs.append(err)

    h_pull = ROOT.TH1F(f"h_pull_{poi}", "", 30, -4, 4)
    for p in pulls:
        h_pull.Fill(p)

    fit_res = h_pull.Fit("gaus", "S Q")

    results[poi] = {
        "mean": fit_res.Parameter(1),
        "mean_err": fit_res.ParError(1),
        "sigma": fit_res.Parameter(2),
        "sigma_err": fit_res.ParError(2),
        "raw_mean_bias": np.mean(vals) - 1.0,
        "raw_mean_err": np.mean(errs),
        "individual_pulls": pulls
    }

with open("bias_results.json", "w") as jf:
    json.dump(results, jf, indent=2)
EOF

    python3 calculate_bias_pulls.py

    popd > /dev/null
    make_collections "$ABS_BASE"

    datacard_output=$orig_datacard_output
    ABS_BASE=$orig_ABS_BASE
    ABS_WS=$orig_ABS_WS
    echo "[INFO] Done Bias Test workflow"
fi
