ERA="2018"
NTUPLETAG="ff_and_cr_production_2018UL_mt_et_tt__2024-12-31_wo_filterbits_v1"

FF_FRIENDS_W_EMBEDDING=(
  # "2025-02-12__ff_with_embedding__more_corrections_right_mt_cut__v3"
  # "2025-02-03__ff_with_embedding__poly_1__v4"
  "2025-03-01__ff__one_dim__w_e__poly1__pt_1__v2"
  "2025-03-01__ff__one_dim__w_e__binwise__pt_1__v2"
  "2025-03-01__ff__one_dim__w_e__poly1__tau_decaymode_2__v2"
  "2025-03-01__ff__one_dim__w_e__binwise__tau_decaymode_2__v2"
  "2025-03-01__ff__one_dim__w_e__poly1__pt_1__tau_decaymode_2__v2"
  "2025-03-01__ff__one_dim__w_e__binwise__pt_1__tau_decaymode_2__v2"
)
FF_FRIENDS_WO_EMBEDDING=(
  # "2025-02-12__ff_without_embedding__more_corrections_right_mt_cut__v3"
  # "2025-02-03__ff_without_embedding__poly_1__v4"
  "2025-03-01__ff__one_dim__wo_e__poly1__pt_1__v2"
  "2025-03-01__ff__one_dim__wo_e__binwise__pt_1__v2"
  "2025-03-01__ff__one_dim__wo_e__poly1__tau_decaymode_2__v2"
  "2025-03-01__ff__one_dim__wo_e__binwise__tau_decaymode_2__v2"
  "2025-03-01__ff__one_dim__wo_e__poly1__pt_1__tau_decaymode_2__v2"
  "2025-03-01__ff__one_dim__wo_e__binwise__pt_1__tau_decaymode_2__v2"
)

FF_TAG=(
  "__ff__1D__poly1__pt_1"
  "__ff__1D__binned__pt_1"
  "__ff__1D__poly1__tau_decaymode_2"
  "__ff__1D__binned__tau_decaymode_2"
  "__ff__1D__poly1__pt_1__tau_decaymode_2"
  "__ff__1D__binned__pt_1__tau_decaymode_2"
)

DO="plot"
CHANNEL="mt"

FF_TYPE=(
  "fake_factor_w_bias_corr"
  "fake_factor_with_DR_SR_corr"
  "fake_factor"
  #
  "raw_fake_factor"
  #
  "raw_wjets_fake_factor"
  "raw_ttbar_fake_factor"
  "raw_qcd_fake_factor"
  #
  "raw_wjets_fake_factor_w_bias_corr"
  "raw_ttbar_fake_factor_w_bias_corr"
  "raw_qcd_fake_factor_w_bias_corr"
  #
  "raw_wjets_fake_factor_w_DR_SR_corr"
  "raw_ttbar_fake_factor_w_DR_SR_corr"
  "raw_qcd_fake_factor_w_DR_SR_corr"
  #
  "raw_wjets_fake_factor_w_DR_SR_and_bias_corr"
  "raw_ttbar_fake_factor_w_DR_SR_and_bias_corr"
  "raw_qcd_fake_factor_w_DR_SR_and_bias_corr"
)

SELECTION_OPTION=(
  "CR"
  "CR"
  "CR"
  #
  "CR"
  #
  "DR;ff;wjet"
  "DR;ff;ttbar"
  "DR;ff;qcd"
  #
  "DR;ff;wjet"
  "DR;ff;ttbar"
  "DR;ff;qcd"
  #
  "DR;ff;wjet"
  "DR;ff;ttbar"
  "DR;ff;qcd"
  #
  "DR;ff;wjet"
  "DR;ff;ttbar"
  "DR;ff;qcd"
)

for n in "${!FF_TAG[@]}"; do

  _FRIENDS_WITH_EMBEDDING="${FF_FRIENDS_W_EMBEDDING[${n}]}"
  _FRIENDS_WITHOUT_EMBEDDING="${FF_FRIENDS_WO_EMBEDDING[${n}]}"
  _FF_TAG="${FF_TAG[${n}]}"

  for i in "${!FF_TYPE[@]}"; do
    _FF_TYPE="${FF_TYPE[${i}]}"
    _SELECTION_OPTION="${SELECTION_OPTION[${i}]}"

    BASE="bash control_plots_ul.sh \
                --channel ${CHANNEL} \
                --era ${ERA} \
                --ntupletag ${NTUPLETAG} \
                --selection_option ${_SELECTION_OPTION} \
                --selection_option_estimation ${_SELECTION_OPTION}"

    TAG="${_FF_TAG}__${_FF_TYPE}__${_SELECTION_OPTION}__with_embedding"
    if [[ "${DO}" == "all" || "${DO}" == "xs" ]]; then
      ${BASE} --tag ${TAG} --mode XSEC
      ${BASE} --tag ${TAG} --mode "SHAPES" --ff_friends_tag ${_FRIENDS_WITH_EMBEDDING} --ff_type ${_FF_TYPE}
      mv routine_output.log routine_output_${TAG}.log
    fi

    if [[ "${DO}" == "all" || "${DO}" == "plot" ]]; then
      for plotmode in "emb+ff"; do
          ${BASE} --tag ${TAG} --mode PLOT --plotversion ${plotmode}
      done
    fi

    TAG="${_FF_TAG}__${_FF_TYPE}__${_SELECTION_OPTION}__without_embedding"
    echo ${TAG}
    if [[ "${DO}" == "all" || "${DO}" == "xs" ]]; then
      ${BASE} --tag ${TAG} --mode XSEC
      ${BASE} --tag ${TAG} --mode "SHAPES" --ff_friends_tag ${_FRIENDS_WITHOUT_EMBEDDING} --ff_type ${_FF_TYPE}
      mv routine_output.log routine_output_${TAG}.log
    fi

    if [[ "${DO}" == "all" || "${DO}" == "plot" ]]; then
      wait
      for plotmode in "classic+classic" "classic+ff" "emb+classic"; do
        (
          ${BASE} --tag ${TAG} --mode PLOT --plotversion ${plotmode}
        ) &
      done
      wait
    fi
  done
done
