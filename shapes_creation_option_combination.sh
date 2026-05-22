ERA="2018"
CHANNEL="mt"
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

VARIABLES_1D=$(IFS=, ; echo "${GOF_VARIABLES_LIST[*]}")
GOF_VARIABLES=$(IFS=, ; echo "${final_variables_list[*]}")

# ---

MODE=$1

FRIENDS="fastmtt_v1"
ADDITIONAL_MULTIFRIENDS="fakefactors_ml__2026-05-21__v10"

if [[ $MODE == "GOF" ]]; then
  TAG="gof_ml_ff_fixed_ff_unct__adjusted_syst_test"

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

if [[ $MODE == "CONTROL" ]]; then
  TAG="control_ml_ff_fixed_ff_unct__adjusted_syst_test"

  KWARGS=(
    --channel "${CHANNEL}"
    --era "${ERA}"
    --tag "${TAG}"
    --ntupletag "${NTUPLETAG}"
    --additional-friends "${FRIENDS}"
    --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
    --enable-cut-ordering
    --locally
    --control-plots
  )
  # using default variables defined in control_plots_ul.py
  # add `--with-systematic-variations` if finally needed with a distinct varaible selection (default too long)
  python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
  python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT

fi

if [[ $MODE == "NN-OUTPUT" ]]; then
  echo "TODO"
fi









# TAG="nn_output_groupedDNN__FF_adjusted__2026-05-07__1sigmatest__v1_control"
# FRIENDS="fastmtt_v1"
# ADDITIONAL_MULTIFRIENDS="fakefactors_ml_1sigma_unct__2026-05-07__v1 nn_output_CENNT_groupedDNN_FF_adjusted__2026-04-30__v1"

# KWARGS=(
#   --channel "${CHANNEL}"
#   --era "${ERA}"
#   --tag "${TAG}"
#   --ntupletag "${NTUPLETAG}"
#   --additional-friends "${FRIENDS}"
#   --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
#   --enable-cut-ordering
#   --control-plots
#   --locally
# )
# python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
# python3 control_plots_ul.py "${KWARGS[@]}" --mode PLOT


# TAG="nn_output_groupedDNN__FF_adjusted__2026-04-30__v1__config"

# FRIENDS="fastmtt_v1"
# ADDITIONAL_MULTIFRIENDS="fakefactors_ml_2sigma_unct_v1"

# KWARGS=(
#   --channel "${CHANNEL}"
#   --era "${ERA}"
#   --tag "${TAG}"
#   --ntupletag "${NTUPLETAG}"
#   --additional-friends "${FRIENDS}"
#   --additional-multifriends "${ADDITIONAL_MULTIFRIENDS}"
#   --enable-cut-ordering
#   --locally
#   --collect-config-only
#   --with-systematic-variations
#   --control-plots
#   --config-output-file unmodified_2018_mt_training_config_with_ml_ff.yaml
# )
# python3 control_plots_ul.py "${KWARGS[@]}" --mode SHAPES
