ERA="2018"
CHANNEL="mt"

# latest greatest
NTUPLETAG="ff_and_cr_2018UL_mt__2026-03-27__v2"

# do gof shapes
YAML_FILE="config/gof_binning/binning_${ERA}_${CHANNEL}_2D.yaml"
GOF_VARIABLES_LIST=(
  pt_1 eta_1 mt_1
  pt_2 eta_2 mt_2
  jpt_1 jeta_1
  jpt_2 jeta_2
  pt_tt pt_vis pt_dijet pt_ttjj
  mjj mt_tot m_vis met nbtag njets pzetamissvis
  deltaR_ditaupair deltaEta_ditaupair
  deltaR_jj deltaR_1j1 deltaR_1j2 deltaR_2j1 deltaR_2j2 deltaR_12j1 deltaR_12j2
  deltaEta_jj deltaEta_1j1 deltaEta_1j2 deltaEta_2j1 deltaEta_2j2 deltaEta_12j1 deltaEta_12j2
  eta_fastmtt m_fastmtt pt_fastmtt
  tau_decaymode_2
)

echo "[INFO] Parsing variables from ${YAML_FILE} based on master 1D list..."
mapfile -t all_yaml_keys < <(grep '^[^ ]' "$YAML_FILE" | sed 's/://')  # all keys from the YAML.

# map for master list
declare -A master_vars_map
for var in "${GOF_VARIABLES_LIST[@]}"; do
    master_vars_map["$var"]=1
done

#map for exclude list
declare -A exclude_vars_map
for var in "${__GOF_VARIABLES_LIST[@]}"; do
    exclude_vars_map["$var"]=1
done

final_variables_list=()
for key in "${all_yaml_keys[@]}"; do
    if [[ -v master_vars_map["$key"] ]]; then
        if [[ -v exclude_vars_map["$key"] ]]; then
            continue # Skip: This 1D variable was already produced.
        fi
        final_variables_list+=("$key")
        continue # 1D match
    fi

    for var1 in "${GOF_VARIABLES_LIST[@]}"; do
        if [[ "$key" == "${var1}_"* ]]; then  # key starts with "var1_"
            var2=${key#${var1}_}

            if [[ -v master_vars_map["$var2"] ]]; then
                if [[ -v exclude_vars_map["$var1"] && -v exclude_vars_map["$var2"] ]]; then
                    break
                fi
                final_variables_list+=("$key")
                break # Found a valid combination
            fi
        fi
    done
done

filter_gof_variables_string() {
    local all_vars="$1"
    local target="$2"

    IFS=',' read -r -a var_array <<< "$all_vars"

    local matched=()
    for var in "${var_array[@]}"; do
        if [[ "$var" == "$target" ]] || \
           [[ "$var" == "${target}_"* ]] || \
           [[ "$var" == *"_${target}" ]]; then
            matched+=("$var")
        fi
    done

    (IFS=, ; echo "${matched[*]}")
}

VARIABLES_1D=$(IFS=, ; echo "${GOF_VARIABLES_LIST[*]}")
GOF_VARIABLES=$(IFS=, ; echo "${final_variables_list[*]}")

# ---

MODE=$1

FRIENDS="fastmtt_v1"

# latest greatest
ADDITIONAL_MULTIFRIENDS="fakefactors_ml__2026-06-02__njets__with_additional_normalization__ti_squeeze__groupedScaler__v1"

BASETAG="ml_ff_sym_unct__ti_sq__groupedScaler__v1"

if [[ $MODE == "GOF" ]]; then
  TAG="gof_${BASETAG}"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --variables "${GOF_VARIABLES}"
    --with-systematic-variations
    --gof-inputs
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES

fi

if [[ $MODE == "GOF-SELECTED-VARIABLE" ]]; then
  SELECTED_VAR=$2
  if [[ -z "$SELECTED_VAR" ]]; then
    echo "[ERROR] GOF-SELECTED-VARIABLE mode requires target variable as second argument." >&2
    exit 1
  fi

  TAG="gof_${SELECTED_VAR}_${BASETAG}"
  
  REDUCED_GOF_VARIABLES=$(filter_gof_variables_string "$GOF_VARIABLES" "$SELECTED_VAR")

  echo "[INFO] Running GOF shapes for selected variable: ${SELECTED_VAR}"
  echo "[INFO] Filtered variables: ${REDUCED_GOF_VARIABLES}"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --variables "${REDUCED_GOF_VARIABLES}"
    --with-systematic-variations
    --gof-inputs
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
fi

if [[ $MODE == "CONTROL" ]]; then
  TAG="control_${BASETAG}"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
  )
  # using default variables defined in control_plots_ul.py
  # add `--with-systematic-variations` if finally needed with a distinct varaible selection (default too long)
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
  python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT
fi

if [[ $MODE == "CONTROL-WITH-SYST" ]]; then
  TAG="control_with_uncertainties_${BASETAG}"

  GOF_VARIABLES_LIST=(
    pt_1 eta_1 mt_1
    pt_2 eta_2 mt_2
    jpt_1 jeta_1
    jpt_2 jeta_2
    pt_tt pt_vis pt_dijet pt_ttjj
    mjj mt_tot m_vis met nbtag njets pzetamissvis
    deltaR_ditaupair deltaEta_ditaupair
    deltaR_jj deltaR_1j1 deltaR_1j2 deltaR_2j1 deltaR_2j2 deltaR_12j1 deltaR_12j2
    eta_fastmtt m_fastmtt pt_fastmtt
    tau_decaymode_2
  )

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --with-systematic-variations
    --enable-cut-ordering
    --locally
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
fi

if [[ $MODE == "CONTROL-NJET-SPLIT" ]]; then
  TAG="control_njet_split_${BASETAG}"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --control-plots-njet-split
  )
  # using default variables defined in control_plots_ul.py
  # add `--with-systematic-variations` if finally needed with a distinct varaible selection (default too long)
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
  # python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT
fi

if [[ $MODE == "CONFIG" ]]; then
  TAG="config_${BASETAG}"
  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --collect-config-only
    --with-systematic-variations
    --config-output-file unmodified_2018_mt_training_${TAG}__all_variables.yaml
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
fi

if [[ $MODE == "NN-OUTPUT-CENNT" ]]; then
  # latest greatest
  TAG="nn_output_CENNT__2026-06-22__${BASETAG}"
  ADDITIONAL_MULTIFRIENDS="${ADDITIONAL_MULTIFRIENDS} nn_output_CENNT_groupedDNN_FF_adjusted__2026-06-22__groupedScaler_pruned__v1"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --with-systematic-variations
    --analysis-units
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
  # python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT
fi

if [[ $MODE == "NN-OUTPUT-CENNT-STAGE0" ]]; then
  # latest greatest
  TAG="nn_output_CENNT__stage0__2026-06-22__${BASETAG}"
  ADDITIONAL_MULTIFRIENDS="${ADDITIONAL_MULTIFRIENDS} nn_output_CENNT_groupedDNN_FF_adjusted__2026-06-22__groupedScaler_pruned__stage0__v1"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --with-systematic-variations
    --analysis-units
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
  # python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT
fi

if [[ $MODE == "NN-OUTPUT-SANNT" ]]; then
  # latest greatest
  TAG="nn_output_SANNT__2026-06-22_groupedScaler_best_of_1400__seed_21__${BASETAG}"
  ADDITIONAL_MULTIFRIENDS="${ADDITIONAL_MULTIFRIENDS} nn_output_SANNT_groupedDNN__2026-06-22__best_of_1400__seed_21__fixed__v1" 

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --with-systematic-variations
    --analysis-units
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
  # python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT
fi

if [[ $MODE == "NN-OUTPUT-SANNT-STAGE0" ]]; then
  # latest greatest
  TAG="nn_output_SANNT__stage0__2026-06-22_groupedScaler_best_of_1400__seed_21__${BASETAG}"
  ADDITIONAL_MULTIFRIENDS="${ADDITIONAL_MULTIFRIENDS} nn_output_SANNT_groupedDNN__2026-06-22__best_of_1400__seed_21__fixed__stage0__v1"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --with-systematic-variations
    --analysis-units
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
  # python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT
fi


if [[ $MODE == "CONTROL-DNN-SPLIT-CENNT" ]]; then
  TAG="control_CENNT_dnn_split_${BASETAG}"
  ADDITIONAL_MULTIFRIENDS="${ADDITIONAL_MULTIFRIENDS} nn_output_CENNT_groupedDNN_FF_adjusted__2026-06-22__groupedScaler_pruned__v1"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --control-plots-dnn-split
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
  # python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT
fi

if [[ $MODE == "CONTROL-DNN-SPLIT-SANNT" ]]; then
  TAG="control_SANNT_dnn_split_${BASETAG}"
  ADDITIONAL_MULTIFRIENDS="${ADDITIONAL_MULTIFRIENDS} nn_output_SANNT_groupedDNN__2026-06-22__best_of_1400__seed_21__fixed__v1"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --control-plots-dnn-split
  )
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
  # python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT
fi
