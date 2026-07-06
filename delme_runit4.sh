PRE="/work/amonsch/HiggsToTauTau/2018Redone/smhtt_ul.2026-04-01_ml_parallel_tmp"
CMSSW_BASE=${PRE}/CMSSW_14_1_0_pre4
CHANNEL=mt
ERA=2018
NTUPLETAG="ff_and_cr_2018UL_mt__2026-03-27__v2"

N_CORES=64

TAG=$1
shift

MODES=()
EXCLUDES=()
IS_TOYS=0
STAGE0=0
USE_DATA=0

while (( $# > 0 )); do
    case "$1" in
        --stage0)
            STAGE0=1
            ;;
        --use-data)
            USE_DATA=1
            ;;
        --exclude)
            shift
            IFS=',' read -ra ADDS <<< "$1"
            EXCLUDES+=("${ADDS[@]}")
            ;;
        --exclude=*)
            IFS=',' read -ra ADDS <<< "${1#*=}"
            EXCLUDES+=("${ADDS[@]}")
            ;;
        *)
            base_arg=${1%-TOYS}
            MODES+=( "$base_arg" )
            if [[ "$1" != "$base_arg" ]]; then
                IS_TOYS=1
            fi
            ;;
    esac
    shift
done

if (( ${#MODES[@]} == 0 )); then
    MODES=( "ALL" )
fi

BLIND_ONLY_MODES=( "BIAS" "BIAS-METHOD-A" "GOF-BKG" "GOF-BKG-INDIVIDUAL" "PULLS-BKG" )

if (( USE_DATA )); then
    for bmode in "${BLIND_ONLY_MODES[@]}"; do
        named=0
        for m in "${MODES[@]}"; do
            [[ "$m" == "$bmode" ]] && { named=1; break; }
        done
        (( named )) || EXCLUDES+=( "$bmode" )
    done
fi

has_mode() {
    local search=$1
    local mode
    for mode in "${EXCLUDES[@]}"; do
        if [[ "$mode" == "$search" ]]; then
            return 1
        fi
    done
    for mode in "${MODES[@]}"; do
        if [[ "$mode" == "$search" || "$mode" == "ALL" ]]; then
            return 0
        fi
    done
    return 1
}

DATACARD_SUFFIX=${DATACARD_SUFFIX:-""}
datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/datacards${DATACARD_SUFFIX}"
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

NEEDS_WS=0
for target in "PREFIT" "FITDIAGNOSTICS" "POSTFIT" "FIT-SINGLES" "FIT-GRID" "IMPACTS"; do
    if has_mode "$target"; then
        NEEDS_WS=1
        break
    fi
done

if (( NEEDS_WS )) && [[ ! -f "$ABS_WS" ]]; then
    echo "[INFO] Downstream mode active but Multi-POI workspace missing. Injecting WORKSPACE..."
    MODES+=( "WORKSPACE" )
fi

if has_mode "IMPACTS-INCLUSIVE" && [[ ! -f "$ABS_WS_INCL" ]]; then
    echo "[INFO] Inclusive mode active but workspace_inclusive.root missing. Injecting WORKSPACE-INCLUSIVE..."
    MODES+=( "WORKSPACE-INCLUSIVE" )
fi

if has_mode "WORKSPACE" || has_mode "WORKSPACE-INCLUSIVE"; then
    if [[ ! -f "$ABS_BASE/combined.txt.cmb" ]]; then
        echo "[INFO] Workspace generation required but combined datacard missing. Injecting DATACARD..."
        MODES+=( "DATACARD" )
    fi
fi

if has_mode "FIT-GRID"; then
    if [[ ! -f "$ABS_BASE/fits${DIR_SUFF}/higgsCombine.snap.MultiDimFit.mH125.root" ]]; then
        echo "[INFO] Grid scan mode active but snapshot file missing. Injecting FIT-SINGLES..."
        MODES+=( "FIT-SINGLES" )
    fi
fi

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

if (( STAGE0 )); then
    STXS_SIGNALS="stxs_stage0_syst"
    POIS=( "r_qqH_201to210" "r_ggH_101to116" )
else
    STXS_SIGNALS="stxs_stage1p2_syst"
    POIS=( "r_qqH_201to210" "r_ggH_101to104" "r_ggH_105to106" "r_ggH_107to109" "r_ggH_110to116" )
fi
POI_CSV=$(IFS=, ; echo "${POIS[*]}")

PO_MAPS=()
for POI in "${POIS[@]}"; do
    range=${POI#r_*_}
    PO_MAPS+=( "--PO" "\"map=.*bin${range}.*\$:${POI}[1,-5,5]\"" )
done

SET_PARAMS=""
RANGES=""
for POI in "${POIS[@]}"; do
    SET_PARAMS+="${POI}=1.0,"
    RANGES+="${POI}=-5.0,5.0:"
done
SET_PARAMS=${SET_PARAMS%,}
RANGES=${RANGES%:}

OPTS_FIT=(
    "--robustFit" "1"
    "--X-rtd" "MINIMIZER_analytic"
    "--X-rtd" "FITTER_DYN_STEP"
    "--X-rtd" "FAST_VERTICAL_MORPH" 
    "--cminDefaultMinimizerStrategy" "1"
    "--setParameterRanges" "$RANGES"
    "--setParameters" "$SET_PARAMS"
)

OPTS_FALLBACK=(
     "--cminFallbackAlgo" "Minuit2,0:0.1"             # 1. Try Strategy 0 with looser tolerance (0.1)
     "--cminFallbackAlgo" "Minuit2,2:0.1"             # 2. Try Strategy 2 (Hessian) with looser tolerance (0.1)
     "--cminFallbackAlgo" "Minuit2,0:1.0"             # 3. Try Strategy 0 with very loose tolerance (1.0)
     "--cminFallbackAlgo" "Minuit2,2:1.0"             # 4. Try Strategy 2 (Hessian) with very loose tolerance (1.0)
     "--cminFallbackAlgo" "Minuit2,Simplex,0:1.0"     # 5. Try Simplex if Migrad fails entirely
     "--X-rtd" "FITTER_NEVER_GIVE_UP"                 # 6. Do not abort on intermediate failures
     "--X-rtd" "FITTER_BOUND"                         # 7. Prevent out-of-boundary parameters from crashing
     "--cminSetZeroPoint" "1"                         # 8. Shift NLL reference to 0 for numerical precision
     "--X-rtd" "MINIMIZER_MaxCalls=9999999"           # 9. Prevent premature exit before convergence
)

OPTS_FIT+=( "${OPTS_FALLBACK[@]}" )

OPTS_BIAS=(
    "--robustFit" "1"
    "--X-rtd" "MINIMIZER_analytic"
    "--X-rtd" "FITTER_DYN_STEP"
    "--cminDefaultMinimizerStrategy" "1"
    "--setParameterRanges" "$RANGES"
    "${OPTS_FALLBACK[@]}"
)

if (( IS_TOYS )); then
    OPTS_FIT+=("-t" "1" "-s" "$SEED")
    echo "[INFO] Toy mode enabled (Seed: $SEED)"
fi

POI_TRANSLATIONS='{
    "r_qqH_201to210": "VBF incl.",
    "r_ggH_101to116": "ggH incl.",
    "r_qqH_201to202": "VBF: N_{jets} #leq 1",
    "r_qqH_203to210": "VBF: N_{jets} #geq 2",
    "r_ggH_101to104": "ggH: p_{T}^{H} #geq 200 GeV",
    "r_ggH_105to106": "ggH: N_{jets} = 0",
    "r_ggH_107to109": "ggH: N_{jets} = 1",
    "r_ggH_110to116": "ggH: N_{jets} #geq 2"
}'

write_fitdiag_to_json_py() {
# for PULLS-BKG
cat << 'EOF' > fitdiag_to_impacts_json.py
import ROOT, json, sys

ROOT.gROOT.SetBatch(True)

infile, outfile = sys.argv[1], sys.argv[2]
f = ROOT.TFile.Open(infile)
fr = f.Get("fit_b") if f and not f.IsZombie() else None
if not fr:
    raise RuntimeError(f"fit_b not found in {infile}")

pars = fr.floatParsFinal()
params = []
for i in range(pars.getSize()):
    p = pars.at(i)
    val, err = p.getVal(), p.getError()
    if p.hasAsymError():
        lo, hi = val + p.getAsymErrorLo(), val + p.getAsymErrorHi()
    else:
        lo, hi = val - err, val + err
    params.append({
        "name": p.GetName(),
        "type": "Gaussian",
        "groups": [],
        "prefit": [-1.0, 0.0, 1.0],
        "fit": [lo, val, hi],
    })
f.Close()

with open(outfile, "w") as jf:
    json.dump({"POIs": [], "method": "fitdiag_bonly", "params": params}, jf, indent=2)

print(f"wrote {len(params)} nuisances -> {outfile}")
EOF
}

write_calculate_bias_pulls_py() {
cat << 'EOF' > calculate_bias_pulls.py
import ROOT, os, json, glob, math
ROOT.gROOT.SetBatch(True)

pois = os.environ["POI_CSV"].split(",")
gen = float(os.environ.get("GEN_VALUE", "1.0"))  # injected truth (per-POI scalar)
pattern = os.environ["FILE_PATTERN"]  # one multidimfit.<name>.root per toy

files = glob.glob(pattern)
if not files:
    raise RuntimeError(f"No fit-result files matched: {pattern}")

# Each file = one toy. fit_mdf holds best-fit value AND Hesse error per POI,
# both read from floatParsFinal() -> no covariance indexing, no interval rows.
results = {}
for poi in pois:
    pulls, vals, errs = [], [], []
    skipped = 0
    for fpath in files:
        f = ROOT.TFile.Open(fpath)
        fr = f.Get("fit_mdf") if f and not f.IsZombie() else None
        if not fr:
            skipped += 1
            if f:
                f.Close()
            continue
        p = fr.floatParsFinal().find(poi)
        if not p:
            skipped += 1; f.Close(); continue
        val, err = p.getVal(), p.getError()
        if err <= 0 or not math.isfinite(err) or not math.isfinite(val):
            skipped += 1; f.Close(); continue
        pulls.append((val - gen) / err)
        vals.append(val); errs.append(err)
        f.Close()

    print(f"{poi:>20s}: kept {len(pulls)} / {len(files)} toys (skipped {skipped})")
    if len(pulls) < 5:
        raise RuntimeError(f"Too few valid toys for {poi} ({len(pulls)}).")

    n_bins = 40
    h = ROOT.TH1F(f"h_pull_{poi}", ";pull;toys", n_bins, -5, 5)
    for x in pulls:
        h.Fill(x)
    r = h.Fit("gaus", "S Q")
    results[poi] = {
        "mean": r.Parameter(1),
        "mean_err": r.ParError(1),
        "sigma": r.Parameter(2),
        "sigma_err": r.ParError(2),
        "n_toys": len(pulls),
        "gen": gen,
        "pulls": pulls,
        "vals": vals,
        "errs": errs,
        "n_bins": n_bins,
        "chi2": r.Chi2(),
        "ndf": r.Ndf(),
    }
    print(f"{poi:>20s}: mean={r.Parameter(1):+.3f}+-{r.ParError(1):.3f}  "
          f"sigma={r.Parameter(2):.3f}+-{r.ParError(2):.3f}")

with open("bias_results.json", "w") as jf:
    json.dump(results, jf, indent=2)
EOF
}

get_failed_impact_params() {
    local pattern=$1
    local prefix=$2

    python3 -c '
import ROOT, glob, sys
pattern = sys.argv[1]
prefix = sys.argv[2]
failed = []
for f in glob.glob(pattern):
    tf = ROOT.TFile.Open(f)
    if not tf or tf.IsZombie():
        name = f.split(prefix)[1].split(".MultiDimFit")[0]
        failed.append(name)
        continue
    tree = tf.Get("limit")
    if not tree or tree.GetEntries() < 3:
        name = f.split(prefix)[1].split(".MultiDimFit")[0]
        failed.append(name)
    tf.Close()
print(",".join(failed))
' "$pattern" "$prefix"
}

_run_datacard() {
    local out_folder=$1
    local real_data=$2
    shift 2
    local extra_args=("$@")

    python3 "${CMSSW_BASE}/src/CombineHarvester/SMRun2Legacy/scripts/make_datacards.py" \
        --base-path="$PWD" \
        --input-folder-${CHANNEL}="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced" \
        --real-data="${real_data}" \
        --bbb=true \
        --jetfakes=true \
        --embedding=true \
        --postfix="-ML" \
        --channels="${CHANNEL}" \
        --rebinning-strategy="combine" \
        --rebinning-using-combine-uncert-fraction 0.1 \
        --convert-shapes-to-lnN=true \
        --stxs-signals="$STXS_SIGNALS" \
        --era="${ERA}" \
        --output-folder="${out_folder}" \
        --ggh-wg1=true \
        --qqh-wg1=true \
        "${extra_args[@]}"
}

make_shapes() {
    # $1 = postfit output suffix (e.g. "" for nominal, ".stat_singles" for a component)
    # $2 = "file.root:fit_mdf" => also produce postfit; omit => prefit only
    local suffix=$1
    local fitres=$2
    local outdir="$ABS_BASE/shapes${DIR_SUFF}"
    mkdir -p "$outdir"

    # prefit = nominal eval of bare workspace => fit-independent => generate once
    if [[ ! -f "$outdir/datacard-shapes-prefit.root" ]]; then
        PostFitShapesFromWorkspace -w "$ABS_WS" -m 125 -d "$ABS_BASE/combined.txt.cmb" \
            --output "$outdir/datacard-shapes-prefit.root"
    fi

    if [[ -n "$fitres" ]]; then
        PostFitShapesFromWorkspace -w "$ABS_WS" -m 125 -d "$ABS_BASE/combined.txt.cmb" \
            -f "$fitres" --postfit --samples 2000 \
            --output "$outdir/datacard-shapes-postfit${suffix}.root"
    fi

    make_collections "$outdir"
}

if has_mode "PLOT-NN-OUTPUT-PREFIT"; then
    echo "[INFO] Running PLOT-NN-OUTPUT-PREFIT sequence..."

    STAGE0_FLAG=()
    (( STAGE0 )) && STAGE0_FLAG=( --stage0 )

    echo "[INFO] Preparing .for_plotting inputs using recursive script execution..."
    env DATACARD_SUFFIX=".for_plotting" FORCE_REAL_DATA="true" bash "$0" "$TAG" DATACARD WORKSPACE PREFIT "${STAGE0_FLAG[@]}"
    (
        # Attempt to load conda activation functions if not inherited by subshell
        # env setup commands for the SANNT.dev environment (scripts not migrated)
        if declare -f get_conda > /dev/null; then
            get_conda
        elif [ -f ~/.bashrc ]; then
            source ~/.bashrc
            if declare -f get_conda > /dev/null; then get_conda; fi
        fi
        
        conda activate SANNT.dev
        export PYTHONPATH="/work/amonsch/Documents/_M_Code/nll-training:$PYTHONPATH"

        python3 ${PRE}/plotting/plot_ml_shapes_control_new.py \
            --base-path "$PWD/output" \
            --era "$ERA" \
            --channel "$CHANNEL" \
            --ntupletag "$NTUPLETAG" \
            --tag "$TAG" \
            "${STAGE0_FLAG[@]}" \
            --mask-signal-region
    )
    echo "[INFO] PLOT-NN-OUTPUT-PREFIT sequence completed."
fi

if has_mode "DATACARD"; then
    echo "[INFO] Run make_datacards.py"
    real_data="${FORCE_REAL_DATA:-false}"
    (( USE_DATA )) && real_data="true"
    _run_datacard "$datacard_output" "$real_data" --categories="${STXS_SIGNALS}"
    
    make_collections "$ABS_BASE"
    echo "[INFO] Done datacard creation"
fi

if has_mode "WORKSPACE"; then
    echo "[INFO] Create Multi-POI workspace"
    combineTool.py -M T2W -o workspace.root -i $datacard_output/${CHANNEL}/125 -m 125 \
        --parallel ${N_CORES} \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        "${PO_MAPS[@]}"
    
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
        "${OPTS_FIT_DIAG[@]}"

    run_logged pulls.txt python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
        -a fitDiagnostics.fitdiag.root -g pulls.root
        
    popd > /dev/null

    make_collections "$ABS_BASE/diagnostics${DIR_SUFF}"
fi

if has_mode "FIT-SINGLES"; then
    echo "[INFO] MultiDimFit Singles (Stat+Syst / Stat-only / Stat+Sys no BBB)"
    mkdir -p "$ABS_BASE/fits${DIR_SUFF}"
    pushd "$ABS_BASE/fits${DIR_SUFF}" > /dev/null

    run_logged sys_singles.txt combineTool.py -M MultiDimFit -d $ABS_WS -m 125 \
        --algo singles -n .sys_singles --floatOtherPOIs 1 \
        --parallel ${N_CORES} "${OPTS_FIT[@]}"

    run_logged snap.txt combineTool.py -M MultiDimFit -d $ABS_WS -m 125 \
        --algo singles -n .snap --saveWorkspace --saveFitResult --robustHesse 1 --floatOtherPOIs 1 \
        --parallel ${N_CORES} "${OPTS_FIT[@]}"
    FITDIR="$ABS_BASE/fits${DIR_SUFF}"
    make_shapes "" "$FITDIR/multidimfit.snap.root:fit_mdf"

    run_logged snap.txt combineTool.py -M MultiDimFit -d $ABS_WS -m 125 \
        --algo singles -n .snap --saveWorkspace --floatOtherPOIs 1 \
        --parallel ${N_CORES} "${OPTS_FIT[@]}"

    run_logged sys_nobbb_singles.txt combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
        --algo singles -n .sys_nobbb_singles --floatOtherPOIs 1 \
        --snapshotName MultiDimFit --freezeNuisanceGroups autoMCStats --freezeParameters 'rgx{.*_bin_.*}' \
        --parallel ${N_CORES} "${OPTS_FIT[@]}"
    run_logged stat_singles.txt combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
        --algo singles -n .stat_singles --floatOtherPOIs 1 \
        --snapshotName MultiDimFit --freezeParameters allConstrainedNuisances \
        --parallel ${N_CORES} "${OPTS_FIT[@]}"
    run_logged sys_stat_bbb_singles.txt combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
        --algo singles -n .sys_stat_bbb_singles --floatOtherPOIs 1 \
        --snapshotName MultiDimFit --freezeNuisanceGroups ^autoMCStats \
        --parallel ${N_CORES} "${OPTS_FIT[@]}"
        
    popd > /dev/null
    make_collections "$ABS_BASE/fits${DIR_SUFF}"
fi

if has_mode "PLOT-NN-OUTPUT-POSTFIT"; then
    echo "[INFO] Running PLOT-NN-OUTPUT-POSTFIT sequence..."

    STAGE0_FLAG=()
    (( STAGE0 )) && STAGE0_FLAG=( --stage0 )

    (
        # Attempt to load conda activation functions if not inherited by subshell
        # env setup commands for the SANNT.dev environment (scripts not migrated)
        if declare -f get_conda > /dev/null; then
            get_conda
        elif [ -f ~/.bashrc ]; then
            source ~/.bashrc
            if declare -f get_conda > /dev/null; then get_conda; fi
        fi
        
        conda activate SANNT.dev
        export PYTHONPATH="/work/amonsch/Documents/_M_Code/nll-training:$PYTHONPATH"

        python3 ${PRE}/plotting/plot_ml_shapes_control_new.py \
            --base-path "$PWD/output" \
            --era "$ERA" \
            --channel "$CHANNEL" \
            --ntupletag "$NTUPLETAG" \
            --tag "$TAG" \
            "${STAGE0_FLAG[@]}" \
            --is-postfit

        python3 ${PRE}/plotting/plot_ml_shapes_control_new.py \
            --base-path "$PWD/output" \
            --era "$ERA" \
            --channel "$CHANNEL" \
            --ntupletag "$NTUPLETAG" \
            --tag "$TAG" \
            "${STAGE0_FLAG[@]}"
    )
fi

if has_mode "FIT-GRID"; then
    echo "[INFO] MultiDimFit Grid Scans"
    mkdir -p "$ABS_BASE/fits${DIR_SUFF}"
    pushd "$ABS_BASE/fits${DIR_SUFF}" > /dev/null

    for POI in "${POIS[@]}"; do
        run_logged "sys_grid_${POI}.txt" combineTool.py -M MultiDimFit -d $ABS_WS -m 125 \
            --algo grid --points 101 -n .sys_grid_${POI} --floatOtherPOIs 1 \
            -P $POI \
            --job-mode interactive --parallel ${N_CORES} "${OPTS_FIT[@]}"
        run_logged "sys_nobbb_grid_${POI}.txt" combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
            --algo grid --points 101 -n .sys_nobbb_grid_${POI} --floatOtherPOIs 1 \
            -P $POI \
            --snapshotName MultiDimFit --freezeNuisanceGroups autoMCStats --freezeParameters 'rgx{.*_bin_.*}' \
            --job-mode interactive --parallel ${N_CORES} "${OPTS_FIT[@]}"

        run_logged "sys_stat_bbb_grid_${POI}.txt" combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
            --algo grid --points 101 -n .sys_stat_bbb_grid_${POI} --floatOtherPOIs 1 \
            -P $POI \
            --snapshotName MultiDimFit --freezeNuisanceGroups ^autoMCStats \
            --job-mode interactive --parallel ${N_CORES} "${OPTS_FIT[@]}"

        # Use variable $SNAP_FILE to prevent Toy seed mismatch
        run_logged "stat_grid_${POI}.txt" combineTool.py -M MultiDimFit -d "$SNAP_FILE" -m 125 \
            --algo grid --points 101 -n .stat_grid_${POI} --floatOtherPOIs 1 \
            -P $POI \
            --snapshotName MultiDimFit --freezeParameters allConstrainedNuisances \
            --job-mode interactive --parallel ${N_CORES} "${OPTS_FIT[@]}"
    done
    popd > /dev/null
    make_collections "$ABS_BASE/fits${DIR_SUFF}"
fi

if has_mode "IMPACTS"; then
    # see https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/tutorial2023_unfolding/unfolding_exercise/#impacts
    echo "[INFO] Running Impacts (Single Pass for All POIs)"
    mkdir -p "$ABS_BASE/impacts${DIR_SUFF}"
    pushd "$ABS_BASE/impacts${DIR_SUFF}" > /dev/null

    if (( IS_TOYS )); then
        OPTS_FALLBACK+=("-t" "1" "-s" "$SEED")
    fi

    OPTS_IMPACTS_FIT=(
        "--setCrossingTolerance" "0.001"
        "--stepSize" "0.05"
        "--setRobustFitStrategy" "0"
        "--setRobustFitTolerance" "0.1"
    )

    # intial fit
    run_logged "impacts_initial.txt" combineTool.py -M Impacts -d "$ABS_WS" -n .impacts -m 125 \
        --redefineSignalPOIs $POI_CSV --doInitialFit  \
        --parallel ${N_CORES} "${OPTS_FIT[@]}" "${OPTS_IMPACTS_FIT[@]}"

    # standard fit approach. best case: all parameters converge here
    run_logged "impacts_fits.txt" combineTool.py -M Impacts -d "$ABS_WS" -n .impacts -m 125 \
        --redefineSignalPOIs $POI_CSV --doFits \
        --cminPreFit 2 --cminPreScan --cminDefaultMinimizerTolerance 0.1 \
        --job-mode interactive --parallel ${N_CORES} "${OPTS_FIT[@]}" "${OPTS_IMPACTS_FIT[@]}"

    # For everything that did not worked: searching for fewer than 3 entries in their ROOT files
    FAILED_PARAMS=$(get_failed_impact_params "higgsCombine_paramFit_.impacts_*.MultiDimFit.mH125.root" "_paramFit_.impacts_")

    # everything enters here should be resolved within first retry
    if [[ -n "$FAILED_PARAMS" ]]; then
        echo "[INFO] initial strategy failed for: $FAILED_PARAMS. Retrying with different strategy..."
        OPTS_FIT_RETRY=("${OPTS_FIT[@]/--cminDefaultMinimizerStrategy 1/--cminDefaultMinimizerStrategy 0}")
        run_logged "impacts_fits_retry.txt" combineTool.py -M Impacts -d "$ABS_WS" -n .impacts -m 125 \
            --redefineSignalPOIs $POI_CSV --doFits \
            --named "$FAILED_PARAMS" \
            --cminDefaultMinimizerTolerance 0.1 \
            --job-mode interactive --parallel ${N_CORES} "${OPTS_FIT_RETRY[@]}" "${OPTS_IMPACTS_FIT[@]}"

        # If not: last resort: perhaps Simplex, loose tolerance 1.0. If its still failing: perhaps not fixable here?
        FAILED_PARAMS_L2=$(get_failed_impact_params "higgsCombine_paramFit_.impacts_*.MultiDimFit.mH125.root" "_paramFit_.impacts_")
        if [[ -n "$FAILED_PARAMS_L2" ]]; then
            echo "[WARNING] adjusted strategy failed for: $FAILED_PARAMS_L2. Retrying with different strategy..."
            OPTS_FIT_RETRY_L2=("${OPTS_FIT[@]/--cminDefaultMinimizerStrategy 1/--cminDefaultMinimizerStrategy 0}")

            run_logged "impacts_fits_retry_l2.txt" combineTool.py -M Impacts -d "$ABS_WS" -n .impacts -m 125 \
                --redefineSignalPOIs $POI_CSV --doFits \
                --named "$FAILED_PARAMS_L2" \
                --cminDefaultMinimizerTolerance 1.0 \
                --cminFallbackAlgo Minuit2,Simplex,0:1.0 \
                --job-mode interactive --parallel ${N_CORES} "${OPTS_FIT_RETRY_L2[@]}" "${OPTS_IMPACTS_FIT[@]}"
        fi
    fi

    run_logged "impacts_json.txt" combineTool.py -M Impacts -d "$ABS_WS" -n .impacts -o impacts.json -m 125 \
        --parallel ${N_CORES} --redefineSignalPOIs $POI_CSV

    echo "$POI_TRANSLATIONS" > "$ABS_BASE/impacts${DIR_SUFF}/poi_translations.json"
    pushd "$ABS_BASE/impacts${DIR_SUFF}" > /dev/null
    for POI in "${POIS[@]}"; do
        echo "[INFO] Generating impact plot for $POI"
        plotImpacts.py -i impacts.json -o impacts_${POI} --POI $POI --translate poi_translations.json
    done

    popd > /dev/null
    make_collections "$ABS_BASE/impacts${DIR_SUFF}"
fi

if has_mode "IMPACTS-INCLUSIVE"; then
    echo "[INFO] Impacts Inclusive (POI=r)"
    mkdir -p "$ABS_BASE/impacts_inclusive${DIR_SUFF}"
    pushd "$ABS_BASE/impacts_inclusive${DIR_SUFF}" > /dev/null
    
    OPTS_INCL=(
        "--setCrossingTolerance" "0.001"
        "--stepSize" "0.05"
        "--robustFit" "1"
        "--X-rtd" "FITTER_NEW_CROSSING_ALGO"
        "--X-rtd" "MINIMIZER_analytic"
        "--X-rtd" "FITTER_DYN_STEP"
        "--X-rtd" "FAST_VERTICAL_MORPH"
        "--cminDefaultMinimizerStrategy" "1"
        "--setParameterRanges" "r=-5.0,5.0"
        "--setParameters" "r=1.0"
    )

    if (( IS_TOYS )); then
        OPTS_INCL+=("-t" "1" "-s" "$SEED")
    fi

    OPTS_INCL+=( "${OPTS_FALLBACK[@]}" )

    # similar to IMPACTS

    run_logged impacts_incl_initial.txt combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl -m 125 \
        --redefineSignalPOIs r --doInitialFit \
        --parallel ${N_CORES} "${OPTS_INCL[@]}"
        
    run_logged impacts_incl_fits.txt combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl -m 125 \
        --redefineSignalPOIs r --doFits \
        --cminPreFit 2 --cminPreScan --cminDefaultMinimizerTolerance 0.1  \
        --job-mode interactive --parallel ${N_CORES} "${OPTS_INCL[@]}"

    FAILED_PARAMS=$(get_failed_impact_params "higgsCombine_paramFit_.impacts_incl_*.MultiDimFit.mH125.root" "_paramFit_.impacts_incl_")
    if [[ -n "$FAILED_PARAMS" ]]; then
        echo "[INFO] initial strategy failed for: $FAILED_PARAMS. Retrying with different strategy..."
        OPTS_INCL_RETRY=("${OPTS_INCL[@]/--cminDefaultMinimizerStrategy 1/--cminDefaultMinimizerStrategy 0}")
        
        run_logged "impacts_incl_fits_retry.txt" combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl -m 125 \
            --redefineSignalPOIs r --doFits \
            --named "$FAILED_PARAMS" \
            --cminDefaultMinimizerTolerance 0.1 \
            --job-mode interactive --parallel ${N_CORES} "${OPTS_INCL_RETRY[@]}"

        FAILED_PARAMS_L2=$(get_failed_impact_params "higgsCombine_paramFit_.impacts_incl_*.MultiDimFit.mH125.root" "_paramFit_.impacts_incl_")
        if [[ -n "$FAILED_PARAMS_L2" ]]; then
            echo "[WARNING] adjusted strategy failed for: $FAILED_PARAMS_L2. Retrying with different strategy..."
            OPTS_INCL_RETRY_L2=("${OPTS_INCL[@]/--cminDefaultMinimizerStrategy 1/--cminDefaultMinimizerStrategy 0}")
            
            run_logged "impacts_incl_fits_retry_l2.txt" combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl -m 125 \
                --redefineSignalPOIs r --doFits \
                --named "$FAILED_PARAMS_L2" \
                --cminDefaultMinimizerTolerance 1.0 \
                --cminFallbackAlgo Minuit2,Simplex,0:1.0 \
                --job-mode interactive --parallel ${N_CORES} "${OPTS_INCL_RETRY_L2[@]}"
        fi
    fi

    run_logged impacts_incl_json.txt combineTool.py -M Impacts -d "$ABS_WS_INCL" -n .impacts_incl -o impacts_incl.json -m 125 \
        --redefineSignalPOIs r \
        --parallel ${N_CORES} "${OPTS_INCL[@]}"

    echo "$POI_TRANSLATIONS" > "$ABS_BASE/impacts_inclusive${DIR_SUFF}/poi_translations.json"
    pushd "$ABS_BASE/impacts_inclusive${DIR_SUFF}" > /dev/null    
    plotImpacts.py -i impacts_incl.json -o impacts_incl --translate poi_translations.json

    popd > /dev/null
    make_collections "$ABS_BASE/impacts_inclusive${DIR_SUFF}"
fi

if has_mode "PULLS-BKG"; then
    echo "[INFO] Pulls/constraints (bkg-only, r=0) via FitDiagnostics"

    orig_datacard_output=$datacard_output
    orig_ABS_BASE=$ABS_BASE
    orig_ABS_WS=$ABS_WS

    datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/pulls_bkg/datacards"
    ABS_BASE="$PWD/$datacard_output/${CHANNEL}/125"

    _run_datacard "${datacard_output}" "true" \
        --categories="stxs_stage1p2_syst_bkg_only" \
        --nn-output-gof-bkg-only=true

    make_collections "$ABS_BASE"

    PULL_FIT_OPTS=(
        "--setParameters" "r=0"
        "--freezeParameters" "r"
        "--saveWithUncertainties"
        "--robustHesse" "1"
        "--cminDefaultMinimizerStrategy" "1"
        "${OPTS_FALLBACK[@]}"
    )

    get_bg_name() {
        case "$1" in
            10) echo "embedding" ;; 
            11) echo "jetFakes" ;; 
            12) echo "ttbar" ;; 
            13) echo "dyjets" ;; 
            14) echo "diboson" ;; 
            *) echo "cat_$1" ;; 
        esac
    }

    write_fitdiag_to_json_py
    PULL_PY="$PWD/fitdiag_to_impacts_json.py"

    # --- inclusive ---
    echo "[INFO] Inclusive bkg-only FitDiagnostics"

    combineTool.py -M T2W -o workspace.root -i "$datacard_output/${CHANNEL}/125" -m 125 \
        --parallel ${N_CORES}

    pushd "$ABS_BASE" > /dev/null

    run_logged fitdiag.pulls_incl.txt combine -M FitDiagnostics -d workspace.root -m 125 \
        -n .pulls_incl "${PULL_FIT_OPTS[@]}"
    python3 "$PULL_PY" fitDiagnostics.pulls_incl.root pulls_incl.json

    make_collections "$ABS_BASE"

    popd > /dev/null

    # --- per category ---

    mkdir -p "$ABS_BASE/individual_pulls"
    ln -sfn "../../common" "$ABS_BASE/individual_pulls/common"

    for card_path in "$ABS_BASE"/htt_${CHANNEL}_*_${ERA}.txt; do
        [ -e "$card_path" ] || continue

        card_file=$(basename "$card_path")
        cat_id=$(echo "$card_file" | cut -d'_' -f3)
        bg_name=$(get_bg_name "$cat_id")

        echo "[INFO] === Pulls for ${bg_name} (ID ${cat_id}) ==="

        bg_dir="$ABS_BASE/individual_pulls/$bg_name"

        mkdir -p "$bg_dir"
        cp "$card_path" "$bg_dir/"

        pushd "$bg_dir" > /dev/null

        combineTool.py -M T2W -o workspace.root -i "$card_file" -m 125

        run_logged fitdiag.pulls.txt combine -M FitDiagnostics -d workspace.root -m 125 \
            -n .pulls "${PULL_FIT_OPTS[@]}"

        python3 "$PULL_PY" fitDiagnostics.pulls.root "pulls_${bg_name}.json"

        make_collections "$bg_dir"

        popd > /dev/null
    done

    datacard_output=$orig_datacard_output; ABS_BASE=$orig_ABS_BASE; ABS_WS=$orig_ABS_WS
    echo "[INFO] Done bkg-only pulls/constraints"
fi

if has_mode "GOF-BKG"; then
    echo "[INFO] Run make_datacards.py for GoF Background-only"

    orig_datacard_output=$datacard_output
    orig_ABS_BASE=$ABS_BASE
    orig_ABS_WS=$ABS_WS

    datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/bkg_only_gof/datacards"
    ABS_BASE="$PWD/$datacard_output/${CHANNEL}/125"
    ABS_WS="$ABS_BASE/workspace.root"

    _run_datacard "${datacard_output}" "true" \
        --categories="stxs_stage1p2_syst_bkg_only" \
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

    make_shapes "" ""
    combine -M MultiDimFit "$ABS_WS" -m 125 \
        --algo none --saveFitResult --robustHesse 1 -n .gof_postfit \
        --setParameters r=0 --freezeParameters "r,${THEORY_NUISANCES_TO_FREEZE}" \
        --cminDefaultMinimizerStrategy 1 "${OPTS_FALLBACK[@]}"
    make_shapes "" "$ABS_BASE/multidimfit.gof_postfit.root:fit_mdf"

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

if has_mode "GOF-BKG-INDIVIDUAL"; then
    echo "[INFO] Running Goodness-of-Fit Background-Only per Category..."

    orig_datacard_output=$datacard_output
    orig_ABS_BASE=$ABS_BASE
    orig_ABS_WS=$ABS_WS

    datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/bkg_only_gof/datacards"
    ABS_BASE="$PWD/$datacard_output/${CHANNEL}/125"

    if [ ! -d "$ABS_BASE" ] || [ -z "$(ls -A "$ABS_BASE"/htt_${CHANNEL}_*_${ERA}.txt 2>/dev/null)" ]; then
        echo "[INFO] Background-only datacards not found. Creating on-the-fly..."
        _run_datacard "${datacard_output}" "true" \
            --categories="stxs_stage1p2_syst_bkg_only" \
            --nn-output-gof-bkg-only=true

        make_collections "$ABS_BASE"
    else
        echo "[INFO] Reusing existing background-only datacards from $ABS_BASE"
    fi

    get_bg_name() {
        local cat_id=$1
        case "$cat_id" in
            10) echo "embedding" ;;
            11) echo "jetFakes" ;;
            12) echo "ttbar" ;;
            13) echo "dyjets" ;;
            14) echo "diboson" ;;
            *) echo "cat_${cat_id}" ;;
        esac
    }

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

    # Resolve relative path for text2workspace globally
    mkdir -p "$ABS_BASE/individual_gof"
    ln -sfn "../../common" "$ABS_BASE/individual_gof/common"

    for card_path in "$ABS_BASE"/htt_${CHANNEL}_*_${ERA}.txt; do
        [ -e "$card_path" ] || continue
        
        card_file=$(basename "$card_path")
        cat_id=$(echo "$card_file" | cut -d'_' -f3)
        bg_name=$(get_bg_name "$cat_id")

        echo "[INFO] === Starting GoF for Background: ${bg_name} (ID: ${cat_id}) ==="

        bg_dir="$ABS_BASE/individual_gof/$bg_name"
        mkdir -p "$bg_dir"

        cp "$card_path" "$bg_dir/"
        pushd "$bg_dir" > /dev/null

        combineTool.py -M T2W -o workspace.root -i "$card_file" -m 125
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
        make_collections "$bg_dir"
    done

    datacard_output=$orig_datacard_output
    ABS_BASE=$orig_ABS_BASE
    ABS_WS=$orig_ABS_WS

    echo "[INFO] Done GoF background-only individual workflow"
fi

if has_mode "GOF-SB" && (( USE_DATA )); then

    # TODO: read through it and verify!

    echo "[INFO] Run make_datacards.py for GoF S+B (signal + background, unblinded)"

    orig_datacard_output=$datacard_output
    orig_ABS_BASE=$ABS_BASE
    orig_ABS_WS=$ABS_WS

    datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/sb_gof/datacards"
    ABS_BASE="$PWD/$datacard_output/${CHANNEL}/125"
    ABS_WS="$ABS_BASE/workspace.root"

    _run_datacard "${datacard_output}" "true" --categories="${STXS_SIGNALS}"

    make_collections "$ABS_BASE"

    echo "[INFO] Create GoF S+B multiSignalModel workspace"
    combineTool.py -M T2W -o workspace.root -i "$datacard_output/${CHANNEL}/125" -m 125 \
        --parallel ${N_CORES} \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        "${PO_MAPS[@]}"

    echo "[INFO] Running GoF (S+B, POIs + all NPs floating)..."
    pushd "$ABS_BASE" > /dev/null

    # S+B GoF: POIs float (redefined), all NPs float, nothing frozen.
    # Differs from GOF-BKG: no r=0, no --fixedSignalStrength, no theory freeze.
    GOF_FIT_OPTS=(
        "--redefineSignalPOIs" "$POI_CSV"
        "--setParameterRanges" "$RANGES"
        "--cminDefaultMinimizerStrategy" "2"
        "--cminDefaultMinimizerTolerance" "0.1"
        "--cminPreScan"
        "--cminFallbackAlgo" "Minuit2,Migrad,0:0.01,Minuit2,Migrad,0:0.01"
        "--X-rtd" "FITTER_NEW_CROSSING_ALGO"
        "--X-rtd" "FITTER_NEVER_GIVE_UP"
        "--X-rtd" "MINIMIZER_analytic"
        "--X-rtd" "SIMPLE_RUNTIME_CHANGES"
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

    echo "[INFO] Done GoF S+B workflow"
fi

if has_mode "BIAS"; then
    echo "[INFO] Classic Bias Test: Asimov data only"

    orig_datacard_output=$datacard_output
    orig_ABS_BASE=$ABS_BASE
    orig_ABS_WS=$ABS_WS

    datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/bias_test/datacards"
    ABS_BASE="$PWD/$datacard_output/${CHANNEL}/125"
    ABS_WS="$ABS_BASE/workspace_bias.root"

    _run_datacard "${datacard_output}" "false" \
        --categories="${STXS_SIGNALS}" \
        --bias-test=true

    make_collections "$ABS_BASE"

    combineTool.py -M T2W -o workspace_bias.root -i "$datacard_output/${CHANNEL}/125" -m 125 \
        --parallel ${N_CORES} \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        "${PO_MAPS[@]}"

    N_BIAS_JOBS=${N_BIAS_JOBS:-60}
    N_BIAS_TOYS=${N_BIAS_TOYS:-1200}
    TOYS_PER_JOB=$(( N_BIAS_TOYS / N_BIAS_JOBS ))

    pushd "$ABS_BASE" > /dev/null

    mkdir -p toys
    ( cd toys
      for (( JOB_IDX=0; JOB_IDX<N_BIAS_JOBS; JOB_IDX++ )); do
        (
          for (( K=0; K<TOYS_PER_JOB; K++ )); do
            TOY_SEED=$(( SEED + JOB_IDX*TOYS_PER_JOB + K ))
            combine -M MultiDimFit "$ABS_WS" -m 125 \
                -t 1 \
                -s "$TOY_SEED" \
                --redefineSignalPOIs $POI_CSV \
                --algo none \
                --toysFrequentist \
                --saveToys \
                --robustHesse 1 \
                --saveFitResult \
                --setParameters "$SET_PARAMS" \
                "${OPTS_BIAS[@]}" \
                -n ".BiasTest.j${JOB_IDX}.t${K}" >/dev/null 2>&1
          done
        ) &
      done
      wait
    )

    export POI_CSV; export GEN_VALUE=1.0
    export FILE_PATTERN="toys/multidimfit.BiasTest.*.root"
    write_calculate_bias_pulls_py
    run_logged bias_pulls.txt python3 calculate_bias_pulls.py
    popd > /dev/null
    make_collections "$ABS_BASE"

    datacard_output=$orig_datacard_output; ABS_BASE=$orig_ABS_BASE; ABS_WS=$orig_ABS_WS
    echo "[INFO] Done classic Bias Test"
fi

if has_mode "BIAS-METHOD-A"; then
    echo "[INFO] Bias Test: toys around data-postfit nuisance state"

    orig_datacard_output=$datacard_output
    orig_ABS_BASE=$ABS_BASE
    orig_ABS_WS=$ABS_WS

    datacard_output="output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/bias_test_method_a/datacards"
    ABS_BASE="$PWD/$datacard_output/${CHANNEL}/125"
    ABS_WS="$ABS_BASE/workspace_method_a.root"

    _run_datacard "${datacard_output}" "true" --categories="${STXS_SIGNALS}"

    make_collections "$ABS_BASE"

    combineTool.py -M T2W -o workspace_method_a.root -i "$datacard_output/${CHANNEL}/125" -m 125 \
        --parallel ${N_CORES} --channel-masks \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        "${PO_MAPS[@]}"

    SIGNAL_BIN_IDS=(100 101 102 103 104)
    (( STAGE0 )) && SIGNAL_BIN_IDS=(100 101)

    FIT_MASKS=""
    EVAL_MASKS=""

    for BINID in "${SIGNAL_BIN_IDS[@]}"; do
        FIT_MASKS+="mask_htt_${CHANNEL}_${BINID}_${ERA}=1,"
        EVAL_MASKS+="mask_htt_${CHANNEL}_${BINID}_${ERA}=0,"
    done

    FIT_MASKS=${FIT_MASKS%,}
    EVAL_MASKS=${EVAL_MASKS%,}

    pushd "$ABS_BASE" > /dev/null

    # Profile NPs on real data, signal masked, POIs frozen 0 -> snapshot
    run_logged methodA_data_profile.txt combine -M MultiDimFit workspace_method_a.root -m 125 \
        --redefineSignalPOIs $POI_CSV \
        --setParameters "${FIT_MASKS},${SET_PARAMS//=1.0/=0.0}" \
        --freezeParameters $POI_CSV \
        --saveWorkspace -n .methodA_dataprofile \
        "${OPTS_BIAS[@]}"

    SNAP_DATA="$ABS_BASE/higgsCombine.methodA_dataprofile.MultiDimFit.mH125.root"

    N_BIAS_JOBS=${N_BIAS_JOBS:-60}
    N_BIAS_TOYS=${N_BIAS_TOYS:-1200}
    TOYS_PER_JOB=$(( N_BIAS_TOYS / N_BIAS_JOBS ))

    # Toys from data-postfit snapshot, signal unmasked, SM injected (POIs=1)
    mkdir -p toys
    ( cd toys
      for (( JOB_IDX=0; JOB_IDX<N_BIAS_JOBS; JOB_IDX++ )); do
        (
          for (( K=0; K<TOYS_PER_JOB; K++ )); do
            TOY_SEED=$(( SEED + JOB_IDX*TOYS_PER_JOB + K ))
            combine -M MultiDimFit "$SNAP_DATA" -m 125 --snapshotName MultiDimFit \
                -t 1 \
                -s "$TOY_SEED" \
                --redefineSignalPOIs $POI_CSV \
                --algo none \
                --toysFrequentist \
                --saveToys \
                --robustHesse 1 \
                --saveFitResult \
                --setParameters "${EVAL_MASKS},${SET_PARAMS}" \
                "${OPTS_BIAS[@]}" \
                -n ".BiasTest_methodA.j${JOB_IDX}.t${K}" >/dev/null 2>&1
          done
        ) &
      done
      wait
    )

    export POI_CSV; export GEN_VALUE=1.0
    export FILE_PATTERN="toys/multidimfit.BiasTest_methodA.*.root"
    write_calculate_bias_pulls_py
    run_logged methodA_pulls.txt python3 calculate_bias_pulls.py
    popd > /dev/null
    make_collections "$ABS_BASE"

    datacard_output=$orig_datacard_output; ABS_BASE=$orig_ABS_BASE; ABS_WS=$orig_ABS_WS
    echo "[INFO] Done Method-A Bias Test"
fi
