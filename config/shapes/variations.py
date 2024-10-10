from ntuple_processor.utils import Cut
from ntuple_processor.utils import Weight

from ntuple_processor.variations import ReplaceVariable
from ntuple_processor.variations import ReplaceCut
from ntuple_processor.variations import ReplaceWeight
from ntuple_processor.variations import RemoveCut
from ntuple_processor.variations import RemoveWeight
from ntuple_processor.variations import AddCut
from ntuple_processor.variations import AddWeight
from ntuple_processor.variations import SquareWeight
from ntuple_processor.variations import ReplaceCutAndAddWeight
from ntuple_processor.variations import ReplaceMultipleCuts
from ntuple_processor.variations import ReplaceMultipleCutsAndAddWeight
from ntuple_processor.variations import ReplaceVariableReplaceCutAndAddWeight
from ntuple_processor.variations import ChangeDatasetReplaceMultipleCutsAndAddWeight

#  Variations needed for the various jet background estimations.
same_sign = ReplaceCut("same_sign", "os", Cut("q_1*q_2>0", "ss"))
boosted_same_sign = ReplaceCut("same_sign", "os", Cut("boosted_q_1*boosted_q_2>0", "ss"))

abcd_method = [
    ReplaceCut("abcd_same_sign", "os", Cut("q_1*q_2>0", "ss")),
    ReplaceCut(
        "abcd_anti_iso",
        "tau_iso",
        Cut(
            "(id_tau_vsJet_Tight_1>0.5 && id_tau_vsJet_Tight_2<0.5 && id_tau_vsJet_VLoose_2>0.5)",
            "tau_anti_iso",
        ),
    ),
    ReplaceMultipleCuts(
        "abcd_same_sign_anti_iso",
        ["os", "tau_iso"],
        [
            Cut("q_1*q_2>0", "ss"),
            Cut(
                "(id_tau_vsJet_Tight_1>0.5 && id_tau_vsJet_Tight_2<0.5 && id_tau_vsJet_VLoose_2>0.5)",
                "tau_anti_iso",
            ),
        ],
    ),
]

anti_iso_lt = ReplaceCutAndAddWeight(
    "anti_iso",
    "tau_iso",
    Cut("id_tau_vsJet_Medium_2<0.5&&id_tau_vsJet_VVVLoose_2>0.5", "tau_anti_iso"),
    # Weight("1.0", "fake_factor"),
    Weight("abs(fake_factor)", "fake_factor"),
)
boosted_anti_iso_lt = ReplaceCutAndAddWeight(
    "anti_iso",
    "tau_iso",
    Cut("id_boostedtau_iso_Loose_2<0.5", "tau_anti_iso"),
    # Weight("1.0", "fake_factor"),
    Weight("abs(fake_factor_boosted)", "fake_factor"),
)

# anti_iso_tt_mcl = ReplaceMultipleCutsAndAddWeight(
#     "anti_iso",
#     ["tau_iso", "ff_veto"],
#     [
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5 && id_tau_vsJet_Tight_1<0.5 && id_tau_vsJet_VLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Cut("gen_match_1 != 6", "tau_anti_iso"),
#     ],
#     # Weight("1.0", "fake_factor"),
#     Weight("ff2_nom", "fake_factor"),
# )

anti_iso_tt = ReplaceCutAndAddWeight(
    "anti_iso",
    "tau_iso",
    Cut(
        "((id_tau_vsJet_Medium_2>0.5 && id_tau_vsJet_Medium_1<0.5 && id_tau_vsJet_VVVLoose_1>0.5) || (id_tau_vsJet_Medium_1>0.5 && id_tau_vsJet_Medium_2<0.5 && id_tau_vsJet_VVVLoose_2>0.5))",
        "tau_anti_iso"
    ),
    # Weight("1.0", "fake_factor"),
    Weight("0.5 * abs(fake_factor_1) * (id_tau_vsJet_Medium_1 < 0.5) + 0.5 * abs(fake_factor_2) * (id_tau_vsJet_Medium_2 < 0.5)", "fake_factor"),
)
boosted_anti_iso_tt = ReplaceCutAndAddWeight(
    "anti_iso",
    "tau_iso",
    Cut(
        "((id_boostedtau_iso_Loose_2>0.5 && id_boostedtau_iso_Loose_1<0.5) || (id_boostedtau_iso_Loose_1>0.5 && id_boostedtau_iso_Loose_2<0.5))",
        "tau_anti_iso"
    ),
    # Weight("1.0", "fake_factor"),
    Weight("0.5 * fake_factor_boosted_1 * (id_boostedtau_iso_Loose_1<0.5) + 0.5 * fake_factor_boosted_2 * (id_boostedtau_iso_Loose_2<0.5)", "fake_factor"),
)

# wfakes_tt = ReplaceCut(
#     "wfakes", "ff_veto", Cut("(gen_match_1!=6 && gen_match_2 == 6)", "wfakes_cut")
# )
# wfakes_w_tt = AddCut(
#     "wfakes", Cut("(gen_match_1!=6 && gen_match_2 == 6)", "wfakes_cut")
# )

# anti_iso_split_lt = [
#     ReplaceCutAndAddWeight(
#         "anti_iso_w",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff_lt_wjets", "fake_factor"),
#     ),
#     ReplaceCutAndAddWeight(
#         "anti_iso_qcd",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff_lt_qcd", "fake_factor"),
#     ),
#     ReplaceCutAndAddWeight(
#         "anti_iso_tt",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff_lt_ttbar", "fake_factor"),
#     ),
# ]

#NMSSM variations
# MG_scale_choice=[
#         AddWeight("MG_scale_choiceUp", Weight("(muR1p0_muF1p0_scale_ht_weight)", "muR1p0_muF1p0_scale_ht_weight")),
#         AddWeight("MG_scale_choiceDown", Weight("(1.0/muR1p0_muF1p0_scale_ht_weight)", "muR1p0_muF1p0_scale_ht_weight"))
# ]
LHE_scale_norm=[
        AddWeight("LHE_scale_normUp", Weight("(lhe_scale_weight__LHEScaleWeightUp)", "muR2p0_muF2p0_weight")),
        AddWeight("LHE_scale_normDown", Weight("(lhe_scale_weight__LHEScaleWeightDown)", "muR0p5_muF0p5_weight"))
]
# PDF_scale=[
#         AddWeight("PDF_scaleUp",Weight("(NNPDF23_lo_as_0130_qed_weight)", "NNPDF23_lo_as_0130_qed_weight")),
#         AddWeight("PDF_scaleDown",  Weight("(1.0/NNPDF23_lo_as_0130_qed_weight)", "NNPDF23_lo_as_0130_qed_weight"))
# ]

# Pileup reweighting
pileup_reweighting = [
    ReplaceVariable("CMS_PileUpUp", "PileUpUp"),
    ReplaceVariable("CMS_PileUpDown", "PileUpDown")
]


# Energy scales.
# Previously defined with 2017 in name.
tau_es_3prong = [
    ReplaceVariable("CMS_scale_t_3prong_EraUp", "tauEs3prong0pizeroUp"),
    ReplaceVariable("CMS_scale_t_3prong_EraDown", "tauEs3prong0pizeroDown"),
]

tau_es_3prong1pizero = [
    ReplaceVariable("CMS_scale_t_3prong1pizero_EraUp", "tauEs3prong1pizeroUp"),
    ReplaceVariable("CMS_scale_t_3prong1pizero_EraDown", "tauEs3prong1pizeroDown"),
]

tau_es_1prong = [
    ReplaceVariable("CMS_scale_t_1prong_EraUp", "tauEs1prong0pizeroUp"),
    ReplaceVariable("CMS_scale_t_1prong_EraDown", "tauEs1prong0pizeroDown"),
]

tau_es_1prong1pizero = [
    ReplaceVariable("CMS_scale_t_1prong1pizero_EraUp", "tauEs1prong1pizeroUp"),
    ReplaceVariable("CMS_scale_t_1prong1pizero_EraDown", "tauEs1prong1pizeroDown"),
]

emb_tau_es_3prong = [
    ReplaceVariable("CMS_scale_t_emb_3prong_EraUp", "tauEs3prong0pizeroUp"),
    ReplaceVariable("CMS_scale_t_emb_3prong_EraDown", "tauEs3prong0pizeroDown"),
]

emb_tau_es_3prong1pizero = [
    ReplaceVariable("CMS_scale_t_emb_3prong1pizero_EraUp", "tauEs3prong1pizeroUp"),
    ReplaceVariable("CMS_scale_t_emb_3prong1pizero_EraDown", "tauEs3prong1pizeroDown"),
]

emb_tau_es_1prong = [
    ReplaceVariable("CMS_scale_t_emb_1prong_EraUp", "tauEs1prong0pizeroUp"),
    ReplaceVariable("CMS_scale_t_emb_1prong_EraDown", "tauEs1prong0pizeroDown"),
]

emb_tau_es_1prong1pizero = [
    ReplaceVariable("CMS_scale_t_emb_1prong1pizero_EraUp", "tauEs1prong1pizeroUp"),
    ReplaceVariable("CMS_scale_t_emb_1prong1pizero_EraDown", "tauEs1prong1pizeroDown"),
]
# boosted taus
boosted_tau_es_3prong = [
    ReplaceVariable("CMS_scale_boosted_t_3prong_EraUp", "boostedtauEs3prong0pizeroUp"),
    ReplaceVariable("CMS_scale_boosted_t_3prong_EraDown", "boostedtauEs3prong0pizeroDown"),
]
boosted_tau_es_1prong = [
    ReplaceVariable("CMS_scale_boosted_t_1prong_EraUp", "boostedtauEs1prong0pizeroUp"),
    ReplaceVariable("CMS_scale_boosted_t_1prong_EraDown", "boostedtauEs1prong0pizeroDown"),
]
boosted_tau_es_1prong1pizero = [
    ReplaceVariable("CMS_scale_boosted_t_1prong1pizero_EraUp", "boostedtauEs1prong1pizeroUp"),
    ReplaceVariable("CMS_scale_boosted_t_1prong1pizero_EraDown", "boostedtauEs1prong1pizeroDown"),
]

# Electron energy scale
ele_es = [
    ReplaceVariable("CMS_scale_eUp", "eleEsScaleUp"),
    ReplaceVariable("CMS_scale_eDown", "eleEsScaleDown"),
]

ele_res = [
    ReplaceVariable("CMS_res_eUp", "eleEsResoUp"),
    ReplaceVariable("CMS_res_eDown", "eleEsResoDown"),
]

# Jet energy scale split by sources.
jet_es = [
    ReplaceVariable("CMS_scale_j_AbsoluteUp", "jesUncAbsoluteUp"),
    ReplaceVariable("CMS_scale_j_AbsoluteDown", "jesUncAbsoluteDown"),
    ReplaceVariable("CMS_scale_j_Absolute_EraUp", "jesUncAbsolute2018Up"),
    ReplaceVariable("CMS_scale_j_Absolute_EraDown", "jesUncAbsolute2018Down"),
    ReplaceVariable("CMS_scale_j_FlavorQCDUp", "jesUncFlavorQCDUp"),
    ReplaceVariable("CMS_scale_j_FlavorQCDDown", "jesUncFlavorQCDDown"),
    ReplaceVariable("CMS_scale_j_BBEC1Up", "jesUncBBEC1Up"),
    ReplaceVariable("CMS_scale_j_BBEC1Down", "jesUncBBEC1Down"),
    ReplaceVariable("CMS_scale_j_BBEC1_EraUp", "jesUncBBEC12018Up"),
    ReplaceVariable("CMS_scale_j_BBEC1_EraDown", "jesUncBBEC12018Down"),
    ReplaceVariable("CMS_scale_j_HFUp", "jesUncHFUp"),
    ReplaceVariable("CMS_scale_j_HFDown", "jesUncHFDown"),
    ReplaceVariable("CMS_scale_j_HF_EraUp", "jesUncHF2018Up"),
    ReplaceVariable("CMS_scale_j_HF_EraDown", "jesUncHF2018Down"),
    ReplaceVariable("CMS_scale_j_EC2Up", "jesUncEC2Up"),
    ReplaceVariable("CMS_scale_j_EC2Down", "jesUncEC2Down"),
    ReplaceVariable("CMS_scale_j_EC2_EraUp", "jesUncEC22018Up"),
    ReplaceVariable("CMS_scale_j_EC2_EraDown", "jesUncEC22018Down"),
    ReplaceVariable("CMS_scale_j_RelativeBalUp", "jesUncRelativeBalUp"),
    ReplaceVariable("CMS_scale_j_RelativeBalDown", "jesUncRelativeBalDown"),
    ReplaceVariable("CMS_scale_j_RelativeSample_EraUp", "jesUncRelativeSample2018Up"),
    ReplaceVariable(
        "CMS_scale_j_RelativeSample_EraDown", "jesUncRelativeSample2018Down"
    ),
    ReplaceVariable("CMS_res_j_EraUp", "jerUncUp"),
    ReplaceVariable("CMS_res_j_EraDown", "jerUncDown"),
]
jet_es_hem = [
    ReplaceVariable("CMS_scale_j_HEMIssue_EraUp", "jesUncHEMIssueUp"),
    ReplaceVariable("CMS_scale_j_HEMIssue_EraDown", "jesUncHEMIssueDown"),
]

# MET variations.
met_unclustered = [
    ReplaceVariable("CMS_scale_met_unclustered_EraUp", "metUnclusteredEnUp"),
    ReplaceVariable("CMS_scale_met_unclustered_EraDown", "metUnclusteredEnDown"),
]

# Recoil correction uncertainties
recoil_resolution = [
    ReplaceVariable("CMS_htt_boson_res_met_EraUp", "metRecoilResolutionUp"),
    ReplaceVariable("CMS_htt_boson_res_met_EraDown", "metRecoilResolutionDown"),
]

recoil_response = [
    ReplaceVariable("CMS_htt_boson_scale_met_EraUp", "metRecoilResponseUp"),
    ReplaceVariable("CMS_htt_boson_scale_met_EraDown", "metRecoilResponseDown"),
]

# # fake met scaling in embedded samples
# TODO still needed ?
# emb_met_scale = [
#         ReplaceVariable("scale_embed_metUp", "emb_scale_metUp"),
#         ReplaceVariable("scale_embed_metDown", "emb_scale_metDown")
#         ]

# Energy scales of leptons faking tau leptons.
# Inclusive in eta
# TODO do we need the ones without barrel / endcap plit ?
# ele_fake_es = [
#         ReplaceVariable("CMS_ZLShape_et_1prong_EraUp", "tauEleFakeEsOneProngCommonUp"),
#         ReplaceVariable("CMS_ZLShape_et_1prong_EraDown", "tauEleFakeEsOneProngCommonDown"),
#         ReplaceVariable("CMS_ZLShape_et_1prong1pizero_EraUp", "tauEleFakeEsOneProngPiZerosCommonUp"),
#         ReplaceVariable("CMS_ZLShape_et_1prong1pizero_EraDown", "tauEleFakeEsOneProngPiZerosCommonDown"),
#         ]

# Eta binned uncertainty
ele_fake_es_1prong = [
    ReplaceVariable("CMS_ZLShape_et_1prong_barrel_EraUp", "tauEleFakeEs1prongBarrelUp"),
    ReplaceVariable(
        "CMS_ZLShape_et_1prong_barrel_EraDown", "tauEleFakeEs1prongBarrelDown"
    ),
    ReplaceVariable("CMS_ZLShape_et_1prong_endcap_EraUp", "tauEleFakeEs1prongEndcapUp"),
    ReplaceVariable(
        "CMS_ZLShape_et_1prong_endcap_EraDown", "tauEleFakeEs1prongEndcapDown"
    ),
]

ele_fake_es_1prong1pizero = [
    ReplaceVariable(
        "CMS_ZLShape_et_1prong1pizero_barrel_EraUp", "tauEleFakeEs1prong1pizeroBarrelUp"
    ),
    ReplaceVariable(
        "CMS_ZLShape_et_1prong1pizero_barrel_EraDown",
        "tauEleFakeEs1prong1pizeroBarrelDown",
    ),
    ReplaceVariable(
        "CMS_ZLShape_et_1prong1pizero_endcap_EraUp", "tauEleFakeEs1prong1pizeroEndcapUp"
    ),
    ReplaceVariable(
        "CMS_ZLShape_et_1prong1pizero_endcap_EraDown",
        "tauEleFakeEs1prong1pizeroEndcapDown",
    ),
]

ele_fake_es = ele_fake_es_1prong + ele_fake_es_1prong1pizero

# TODO add split by decay mode ?
# mu_fake_es_1prong = [
#         ReplaceVariable("CMS_ZLShape_mt_1prong_EraUp", "tauMuFakeEsOneProngUp"),
#         ReplaceVariable("CMS_ZLShape_mt_1prong_EraDown", "tauMuFakeEsOneProngDown")
#         ]

# mu_fake_es_1prong1pizero = [
#         ReplaceVariable("CMS_ZLShape_mt_1prong1pizero_EraUp", "tauMuFakeEsOneProngPiZerosUp"),
#         ReplaceVariable("CMS_ZLShape_mt_1prong1pizero_EraDown", "tauMuFakeEsOneProngPiZerosDown")
#         ]

mu_fake_es_inc = [
    ReplaceVariable("CMS_ZLShape_mt_EraUp", "tauMuFakeEsUp"),
    ReplaceVariable("CMS_ZLShape_mt_EraDown", "tauMuFakeEsDown"),
]

# # B-tagging uncertainties.
btagging = [
    ReplaceVariable("CMS_btag_b_HFUp", "btagUncHFUp"),
    ReplaceVariable("CMS_btag_b_HFDown", "btagUncHFDown"),
    ReplaceVariable("CMS_btag_b_HFstats1_EraUp", "btagUncHFstats1Up"),
    ReplaceVariable("CMS_btag_b_HFstats1_EraDown", "btagUncHFstats1Down"),
    ReplaceVariable("CMS_btag_b_HFstats2_EraUp", "btagUncHFstats2Up"),
    ReplaceVariable("CMS_btag_b_HFstats2_EraDown", "btagUncHFstats2Down"),
    ReplaceVariable("CMS_btag_j_LFUp", "btagUncLFUp"),
    ReplaceVariable("CMS_btag_j_LFDown", "btagUncLFDown"),
    ReplaceVariable("CMS_btag_j_LFstats1_EraUp", "btagUncLFstats1Up"),
    ReplaceVariable("CMS_btag_j_LFstats1_EraDown", "btagUncLFstats1Down"),
    ReplaceVariable("CMS_btag_j_LFstats2_EraUp", "btagUncLFstats2Up"),
    ReplaceVariable("CMS_btag_j_LFstats2_EraDown", "btagUncLFstats2Down"),
    ReplaceVariable("CMS_btag_c_CFerr1Up", "btagUncCFerr1Up"),
    ReplaceVariable("CMS_btag_c_CFerr1Down", "btagUncCFerr1Down"),
    ReplaceVariable("CMS_btag_c_CFerr2Up", "btagUncCFerr2Up"),
    ReplaceVariable("CMS_btag_c_CFerr2Down", "btagUncCFerr2Down"),
]

particleNet_Xbb = [
    ReplaceVariable("CMS_XbbTag_fj_EraUp", "pNetXbbSFUp"),
    ReplaceVariable("CMS_XbbTag_fj_EraDown", "pNetXbbSFDown")
]

# Efficiency corrections.
# Tau ID efficiency.

# TODO add high pt tau ID efficiency
tau_id_eff_lt = [
    ReplaceVariable("CMS_eff_t_30-35_EraUp", "vsJetTau30to35Up"),
    ReplaceVariable("CMS_eff_t_30-35_EraDown", "vsJetTau30to35Down"),
    ReplaceVariable("CMS_eff_t_35-40_EraUp", "vsJetTau35to40Up"),
    ReplaceVariable("CMS_eff_t_35-40_EraDown", "vsJetTau35to40Down"),
    ReplaceVariable("CMS_eff_t_40-500_EraUp", "vsJetTau40to500Up"),
    ReplaceVariable("CMS_eff_t_40-500_EraDown", "vsJetTau40to500Down"),
    ReplaceVariable("CMS_eff_t_500-1000_EraUp", "vsJetTau500to1000Up"),
    ReplaceVariable("CMS_eff_t_500-1000_EraDown", "vsJetTau500to1000Down"),
    ReplaceVariable("CMS_eff_t_1000-Inf_EraUp", "vsJetTau1000toInfUp"),
    ReplaceVariable("CMS_eff_t_1000-Inf_EraDown", "vsJetTau1000toInfDown"),
]

emb_tau_id_eff_lt = [
    # ReplaceVariable("CMS_eff_t_emb_20-25_EraUp", "vsJetTau20to25Up"),
    # ReplaceVariable("CMS_eff_t_emb_20-25_EraDown", "vsJetTau20to25Down"),
    # ReplaceVariable("CMS_eff_t_emb_25-30_EraUp", "vsJetTau25to30Up"),
    # ReplaceVariable("CMS_eff_t_emb_25-30_EraDown", "vsJetTau25to30Down"),
    ReplaceVariable("CMS_eff_t_emb_30-35_EraUp", "vsJetTau30to35Up"),
    ReplaceVariable("CMS_eff_t_emb_30-35_EraDown", "vsJetTau30to35Down"),
    ReplaceVariable("CMS_eff_t_emb_35-40_EraUp", "vsJetTau35to40Up"),
    ReplaceVariable("CMS_eff_t_emb_35-40_EraDown", "vsJetTau35to40Down"),
    ReplaceVariable("CMS_eff_t_emb_40-Inf_EraUp", "vsJetTau40toInfUp"),
    ReplaceVariable("CMS_eff_t_emb_40-Inf_EraDown", "vsJetTau40toInfDown"),
]
# tauid variations used for correlation with mc ones
emb_tau_id_eff_lt_corr = [
    ReplaceVariable("CMS_eff_t_30-35_EraUp", "vsJetTau30to35Up"),
    ReplaceVariable("CMS_eff_t_30-35_EraDown", "vsJetTau30to35Down"),
    ReplaceVariable("CMS_eff_t_35-40_EraUp", "vsJetTau35to40Up"),
    ReplaceVariable("CMS_eff_t_35-40_EraDown", "vsJetTau35to40Down"),
    ReplaceVariable("CMS_eff_t_40-500_EraUp", "vsJetTau40toInfUp"),
    ReplaceVariable("CMS_eff_t_40-500_EraDown", "vsJetTau40toInfDown"),
]

# boosted taus
boosted_tau_id_eff_lt = [
    # ReplaceVariable("CMS_eff_boosted_t_30-35_EraUp", "oldIsoTau30to35Up"),
    # ReplaceVariable("CMS_eff_boosted_t_30-35_EraDown", "oldIsoTau30to35Down"),
    # ReplaceVariable("CMS_eff_boosted_t_35-40_EraUp", "oldIsoTau35to40Up"),
    # ReplaceVariable("CMS_eff_boosted_t_35-40_EraDown", "oldIsoTau35to40Down"),
    ReplaceVariable("CMS_eff_boosted_t_40-500_EraUp", "oldIsoTau40to500Up"),
    ReplaceVariable("CMS_eff_boosted_t_40-500_EraDown", "oldIsoTau40to500Down"),
    ReplaceVariable("CMS_eff_boosted_t_500-1000_EraUp", "oldIsoTau500to1000Up"),
    ReplaceVariable("CMS_eff_boosted_t_500-1000_EraDown", "oldIsoTau500to1000Down"),
    ReplaceVariable("CMS_eff_boosted_t_1000-Inf_EraUp", "oldIsoTau1000toInfUp"),
    ReplaceVariable("CMS_eff_boosted_t_1000-Inf_EraDown", "oldIsoTau1000toInfDown"),
]

tau_id_eff_tt = [
    ReplaceVariable("CMS_eff_t_dm0_EraUp", "vsJetTauDM0Up"),
    ReplaceVariable("CMS_eff_t_dm0_EraDown", "vsJetTauDM0Down"),
    ReplaceVariable("CMS_eff_t_dm1_EraUp", "vsJetTauDM1Up"),
    ReplaceVariable("CMS_eff_t_dm1_EraDown", "vsJetTauDM1Down"),
    ReplaceVariable("CMS_eff_t_dm10_EraUp", "vsJetTauDM10Up"),
    ReplaceVariable("CMS_eff_t_dm10_EraDown", "vsJetTauDM10Down"),
    ReplaceVariable("CMS_eff_t_dm11_EraUp", "vsJetTauDM11Up"),
    ReplaceVariable("CMS_eff_t_dm11_EraDown", "vsJetTauDM11Down"),
]

emb_tau_id_eff_tt = [
    ReplaceVariable("CMS_eff_t_emb_dm0_EraUp", "vsJetTauDM0Up"),
    ReplaceVariable("CMS_eff_t_emb_dm0_EraDown", "vsJetTauDM0Down"),
    ReplaceVariable("CMS_eff_t_emb_dm1_EraUp", "vsJetTauDM1Up"),
    ReplaceVariable("CMS_eff_t_emb_dm1_EraDown", "vsJetTauDM1Down"),
    ReplaceVariable("CMS_eff_t_emb_dm10_EraUp", "vsJetTauDM10Up"),
    ReplaceVariable("CMS_eff_t_emb_dm10_EraDown", "vsJetTauDM10Down"),
    ReplaceVariable("CMS_eff_t_emb_dm11_EraUp", "vsJetTauDM11Up"),
    ReplaceVariable("CMS_eff_t_emb_dm11_EraDown", "vsJetTauDM11Down"),
]

# boosted taus
boosted_tau_id_eff_tt = [
    ReplaceVariable("CMS_eff_boosted_t_dm0_EraUp", "oldIsoTauDM0Up"),
    ReplaceVariable("CMS_eff_boosted_t_dm0_EraDown", "oldIsoTauDM0Down"),
    ReplaceVariable("CMS_eff_boosted_t_dm1_EraUp", "oldIsoTauDM1Up"),
    ReplaceVariable("CMS_eff_boosted_t_dm1_EraDown", "oldIsoTauDM1Down"),
    ReplaceVariable("CMS_eff_boosted_t_dm10_EraUp", "oldIsoTauDM10Up"),
    ReplaceVariable("CMS_eff_boosted_t_dm10_EraDown", "oldIsoTauDM10Down"),
]

# Jet to tau fake rate (for MC if no FFs).
jet_to_tau_fake = [
    AddWeight(
        "CMS_htt_fake_j_EraUp",
        Weight("max(1.0-pt_2*0.002, 0.6)", "jetToTauFake_weight"),
    ),
    AddWeight(
        "CMS_htt_fake_j_EraDown",
        Weight("min(1.0+pt_2*0.002, 1.4)", "jetToTauFake_weight"),
    ),
]
jet_to_tau_fake_boosted = [
    AddWeight(
        "CMS_htt_boosted_fake_j_EraUp",
        Weight("max(1.0-boosted_pt_2*0.002, 0.6)", "jetToTauFake_weight"),
    ),
    AddWeight(
        "CMS_htt_boosted_fake_j_EraDown",
        Weight("min(1.0+boosted_pt_2*0.002, 1.4)", "jetToTauFake_weight"),
    ),
]
# vsEle ID
zll_et_fake_rate = [
    ReplaceVariable("CMS_fake_e_Barrel_EraUp", "vsEleBarrelUp"),
    ReplaceVariable("CMS_fake_e_Barrel_EraDown", "vsEleBarrelDown"),
    ReplaceVariable("CMS_fake_e_Endcap_EraUp", "vsEleEndcapUp"),
    ReplaceVariable("CMS_fake_e_Endcap_EraDown", "vsEleEndcapDown"),
]

# boosted taus
boosted_zll_et_fake_rate = [
    ReplaceVariable("CMS_fake_boosted_e_Barrel_EraUp", "antiEleBarrelUp"),
    ReplaceVariable("CMS_fake_boosted_e_Barrel_EraDown", "antiEleBarrelDown"),
    ReplaceVariable("CMS_fake_boosted_e_Endcap_EraUp", "antiEleEndcapUp"),
    ReplaceVariable("CMS_fake_boosted_e_Endcap_EraDown", "antiEleEndcapDown"),
]

# vsMu ID
zll_mt_fake_rate_up = [
    ReplaceVariable(f"CMS_fake_m_Wheel{region}_EraUp", f"vsMuWheel{region}Up")
    for region in ["1", "2", "3", "4", "5"]
]
zll_mt_fake_rate_down = [
    ReplaceVariable(f"CMS_fake_m_Wheel{region}_EraDown", f"vsMuWheel{region}Down")
    for region in ["1", "2", "3", "4", "5"]
]

zll_mt_fake_rate = zll_mt_fake_rate_up + zll_mt_fake_rate_down

# boosted taus
boosted_zll_mt_fake_rate_up = [
    ReplaceVariable(f"CMS_fake_boosted_m_Wheel{region}_EraUp", f"antiMuWheel{region}Up")
    for region in ["1", "2", "3", "4", "5"]
]
boosted_zll_mt_fake_rate_down = [
    ReplaceVariable(f"CMS_fake_boosted_m_Wheel{region}_EraDown", f"antiMuWheel{region}Down")
    for region in ["1", "2", "3", "4", "5"]
]

boosted_zll_mt_fake_rate = boosted_zll_mt_fake_rate_up + boosted_zll_mt_fake_rate_down

# # Trigger efficiency uncertainties.
trigger_eff_mt = [
    ReplaceVariable("CMS_eff_trigger_mt_EraUp", "singleMuonTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_mt_EraDown", "singleMuonTriggerSFDown"),
]
trigger_eff_mt_emb = [
    ReplaceVariable("CMS_eff_trigger_emb_mt_EraUp", "singleMuonTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_emb_mt_EraDown", "singleMuonTriggerSFDown"),
]

trigger_eff_et = [
    ReplaceVariable("CMS_eff_trigger_et_EraUp", "singleElectronTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_et_EraDown", "singleElectronTriggerSFDown"),
]
trigger_eff_et_emb = [
    ReplaceVariable("CMS_eff_trigger_emb_et_EraUp", "singleElectronTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_emb_et_EraDown", "singleElectronTriggerSFDown"),
]

trigger_eff_tt = [
    ReplaceVariable("CMS_eff_trigger_tt_EraUp", "ditauTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_tt_EraDown", "ditauTriggerSFDown"),
]
trigger_eff_tt_emb = [
    ReplaceVariable("CMS_eff_trigger_emb_tt_EraUp", "ditauTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_emb_tt_EraDown", "ditauTriggerSFDown"),
]

# boosted taus
# trigger_eff_boosted_mt = [
#     ReplaceWeight(
#         "CMS_eff_trigger_boosted_mt_EraUp", "trgweight", Weight("trg_wgt_single_mu50_boosted__boostedSingleMuonTriggerSFUp * (boosted_pt_1 >= 55) + trg_wgt_single_mu24_boosted__boostedSingleMuonTriggerSFUp * ((boosted_pt_1 >= 25) && (boosted_pt_1 < 55))", "trgweight")
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_boosted_mt_EraDown", "trgweight", Weight("trg_wgt_single_mu50_boosted__boostedSingleMuonTriggerSFDown * (boosted_pt_1 >= 55) + trg_wgt_single_mu24_boosted__boostedSingleMuonTriggerSFDown * ((boosted_pt_1 >= 25) && (boosted_pt_1 < 55))", "trgweight")
#     ),
# ]
trigger_eff_boosted_mt = [
    ReplaceVariable("CMS_eff_trigger_boosted_mt_EraUp", "boostedSingleMuonTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_boosted_mt_EraDown", "boostedSingleMuonTriggerSFDown"),
]
trigger_eff_boosted_et = [
    ReplaceVariable("CMS_eff_trigger_boosted_et_EraUp", "boostedSingleElectronTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_boosted_et_EraDown", "boostedSingleElectronTriggerSFDown"),
]
trigger_eff_boosted_tt = [
    ReplaceVariable("CMS_eff_trigger_boosted_tt_EraUp", "fatjetTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_boosted_tt_EraDown", "fatjetTriggerSFDown"),
]

# TODO cross triggers
# trigger_eff_mt = [
#     ReplaceWeight(
#         "CMS_eff_trigger_mt_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singlelep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_mt_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singlelep_down", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_mt_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_crosslep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_mt_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_crosslep_down", "triggerweight"),
#     ),
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_mt_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight("mtau_triggerweight_ic_dm{dm}_up".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_mt_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight("mtau_triggerweight_ic_dm{dm}_down".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# trigger_eff_mt_emb = [
#     ReplaceWeight(
#         "CMS_eff_trigger_emb_mt_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singlelep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_emb_mt_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singlelep_down", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_emb_mt_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_crosslep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_emb_mt_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_crosslep_down", "triggerweight"),
#     ),
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_mt_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight("mtau_triggerweight_ic_dm{dm}_up".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_mt_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight("mtau_triggerweight_ic_dm{dm}_down".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# trigger_eff_et = [
#     ReplaceWeight(
#         "CMS_eff_trigger_et_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singlelep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_et_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singlelep_down", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_et_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_crosslep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_et_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_crosslep_down", "triggerweight"),
#     ),
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_et_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight("etau_triggerweight_ic_dm{dm}_up".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_et_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight("etau_triggerweight_ic_dm{dm}_down".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# trigger_eff_et_emb = [
#     ReplaceWeight(
#         "CMS_eff_trigger_emb_et_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singlelep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_emb_et_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singlelep_down", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_emb_et_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_crosslep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_emb_et_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_crosslep_down", "triggerweight"),
#     ),
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_et_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight("etau_triggerweight_ic_dm{dm}_up".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_et_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight("etau_triggerweight_ic_dm{dm}_down".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# TODO Tau Triggers
# tau_trigger_eff_tt = [
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_tt_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_lowpt_dm{dm}_up".format(dm=dm), "triggerweight"
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_tt_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_lowpt_dm{dm}_down".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_tt_dm{dm}_highpT_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_highpt_dm{dm}_up".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_tt_dm{dm}_highpT_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_highpt_dm{dm}_down".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraUp",
#         "triggerweight",
#         Weight("tautau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraDown",
#         "triggerweight",
#         Weight("tautau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# tau_trigger_eff_tt_emb = [
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_tt_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_lowpt_dm{dm}_up".format(dm=dm), "triggerweight"
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_tt_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_lowpt_dm{dm}_down".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_tt_dm{dm}_highpT_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_highpt_dm{dm}_up".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_tt_dm{dm}_highpT_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_highpt_dm{dm}_down".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraUp",
#         "triggerweight",
#         Weight("tautau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraDown",
#         "triggerweight",
#         Weight("tautau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# Embedding specific variations.
# TODO Embedding electron scale
emb_e_es = [
    ReplaceVariable("CMS_scale_e_barrel_embUp", "eleEsBarrelUp"),
    ReplaceVariable("CMS_scale_e_barrel_embDown", "eleEsBarrelDown"),
    ReplaceVariable("CMS_scale_e_endcap_embUp", "eleEsEndcapUp"),
    ReplaceVariable("CMS_scale_e_endcap_embDown", "eleEsEndcapDown"),
]

# TODO add embeddedDecayModeWeight

# emb_decay_mode_eff_lt = [
#     ReplaceWeight(
#         "CMS_3ProngEff_EraUp",
#         "decayMode_SF",
#         Weight(
#             "(pt_2<100)*embeddedDecayModeWeight_effUp_pi0Nom+(pt_2>=100)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_3ProngEff_EraDown",
#         "decayMode_SF",
#         Weight(
#             "(pt_2<100)*embeddedDecayModeWeight_effDown_pi0Nom+(pt_2>=100)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_1ProngPi0Eff_EraUp",
#         "decayMode_SF",
#         Weight(
#             "(pt_2<100)*embeddedDecayModeWeight_effNom_pi0Up+(pt_2>=100)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_1ProngPi0Eff_EraDown",
#         "decayMode_SF",
#         Weight(
#             "(pt_2<100)*embeddedDecayModeWeight_effNom_pi0Down+(pt_2>=100)",
#             "decayMode_SF",
#         ),CMS_scale_e_barrel_embUp
#     ),
# ]

# emb_decay_mode_eff_tt = [
#     ReplaceWeight(
#         "CMS_3ProngEff_EraUp",
#         "decayMode_SF",
#         Weight(
#             "(pt_2>=100)+(pt_1<100)*embeddedDecayModeWeight_effUp_pi0Nom+(pt_1>=100)*(pt_2<100)*((decayMode_2==0)*0.983+(decayMode_2==1)*0.983*1.051+(decayMode_2==10)*0.983*0.983*0.983+(decayMode_2==11)*0.983*0.983*0.983*1.051)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_3ProngEff_EraDown",
#         "decayMode_SF",
#         Weight(
#             "(pt_2>=100)+(pt_1<100)*embeddedDecayModeWeight_effDown_pi0Nom+(pt_1>=100)*(pt_2<100)*((decayMode_2==0)*0.967+(decayMode_2==1)*0.967*1.051+(decayMode_2==10)*0.967*0.967*0.967+(decayMode_2==11)*0.967*0.967*0.967*1.051)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_1ProngPi0Eff_EraUp",
#         "decayMode_SF",
#         Weight(
#             "(pt_2>=100)+(pt_1<100)*embeddedDecayModeWeight_effNom_pi0Up+(pt_1>=100)*(pt_2<100)*((decayMode_2==0)*0.975+(decayMode_2==1)*0.975*1.065+(decayMode_2==10)*0.975*0.975*0.975+(decayMode_2==11)*0.975*0.975*0.975*1.065)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_1ProngPi0Eff_EraDown",
#         "decayMode_SF",
#         Weight(
#             "(pt_2>=100)+(pt_1<100)*embeddedDecayModeWeight_effNom_pi0Down+(pt_1>=100)*(pt_2<100)*((decayMode_2==0)*0.975+(decayMode_2==1)*0.975*1.037+(decayMode_2==10)*0.975*0.975*0.975+(decayMode_2==11)*0.975*0.975*0.975*1.037)",
#             "decayMode_SF",
#         ),
#     ),
# ]


prefiring = [
    ReplaceWeight(
        "CMS_prefiringUp", "prefireWeight", Weight("prefiringweightup", "prefireWeight")
    ),
    ReplaceWeight(
        "CMS_prefiringDown",
        "prefireWeight",
        Weight("prefiringweightdown", "prefireWeight"),
    ),
]

zpt = [
    SquareWeight("CMS_ZPt_Shape_EraUp", "ZPtMassReweightWeight"),
    RemoveWeight("CMS_ZPt_Shape_EraDown", "ZPtMassReweightWeight"),
]

top_pt = [
    SquareWeight("CMS_topPt_ShapeUp", "topPtReweightWeight"),
    RemoveWeight("CMS_topPt_ShapeDown", "topPtReweightWeight"),
]

# TODO add fake factors
_ff_variations_lt = [
    # "ff_tt_morphed_{shift}",
    # "ff_tt_sf_{shift}",
    # "ff_corr_tt_syst_{shift}",
    # "ff_frac_w_{shift}",
    # "ff_qcd_dr0_njet0_morphed_stat_{shift}",
    # "ff_qcd_dr0_njet1_morphed_stat_{shift}",
    # "ff_qcd_dr0_njet2_morphed_stat_{shift}",
    # "ff_w_dr0_njet0_morphed_stat_{shift}",
    # "ff_w_dr0_njet1_morphed_stat_{shift}",
    # "ff_w_dr0_njet2_morphed_stat_{shift}",
    # "ff_w_dr1_njet0_morphed_stat_{shift}",
    # "ff_w_dr1_njet1_morphed_stat_{shift}",
    # "ff_w_dr1_njet2_morphed_stat_{shift}",
    # "ff_tt_dr0_njet0_morphed_stat_{shift}",
    # "ff_tt_dr0_njet1_morphed_stat_{shift}",
    # "ff_w_lepPt_{shift}",
    # "ff_corr_w_lepPt_{shift}",
    # "ff_w_mc_{shift}",
    # "ff_corr_w_mt_{shift}",
    # "ff_w_mt_{shift}",
    # "ff_qcd_mvis_{shift}",
    # "ff_qcd_mvis_osss_{shift}",
    # "ff_corr_qcd_mvis_{shift}",
    # "ff_corr_qcd_mvis_osss_{shift}",
    # "ff_qcd_muiso_{shift}",
    # "ff_corr_qcd_muiso_{shift}",
    # "ff_qcd_mc_{shift}",
    "QCDFFslopeUnc",
    "QCDFFnormUnc",
    "QCDFFmcSubUnc",
    "WjetsFFslopeUnc",
    "WjetsFFnormUnc",
    "WjetsFFmcSubUnc",
    "ttbarFFslopeUnc",
    "ttbarFFnormUnc",
    "fracQCDUnc",
    "fracWjetsUnc",
    "fracTTbarUnc",
    "QCDClosureLeadingLepPtCorr",
    "QCDClosureSubleadingTauMassCorr",
    "QCDDRtoSRCorr",
    "WjetsClosureLeadingLepPtCorr",
    "WjetsClosureSubleadingTauMassCorr",
    "WjetsDRtoSRCorr",
    "ttbarClosureLeadingLepPtCorr",
    "ttbarClosureSubleadingTauMassCorr",
]
#  Variations on the jet backgrounds estimated with the fake factor method.
ff_variations_lt = [
    ReplaceCutAndAddWeight(
        "anti_iso_CMS_{syst}_{ch}_{era}".format(syst=syst+shift, era="Era", ch="Channel"),
        "tau_iso",
        Cut("id_tau_vsJet_Medium_2<0.5&&id_tau_vsJet_VVVLoose_2>0.5", "tau_anti_iso"),
        Weight(
            "fake_factor__{syst}".format(syst=syst+shift), "fake_factor"
        ),
    )
    for shift in ["Up", "Down"]
    for syst in _ff_variations_lt
]

_ff_variations_tau_es_lt = [
    "tauEs1prong0pizero",
    "tauEs1prong1pizero",
    "tauEs3prong0pizero",
    "tauEs3prong1pizero",
]
# Propagation of tau ES systematics on jetFakes process
ff_variations_tau_es_lt = [
    ReplaceCutAndAddWeight(
        "anti_iso_CMS_{syst}_{ch}_{era}".format(syst=syst+shift, era="Era", ch="Channel"),
        "tau_iso",
        Cut("id_tau_vsJet_Medium_2<0.5&&id_tau_vsJet_VVVLoose_2>0.5", "tau_anti_iso"),
        Weight(
            "fake_factor__{syst}".format(syst=syst+shift), "fake_factor"
        ),
    )
    for shift in ["Up", "Down"]
    for syst in _ff_variations_tau_es_lt
]

# boosted taus
_ff_variations_boosted_lt = [
    "QCDFFslopeUnc",
    "QCDFFnormUnc",
    "QCDFFmcSubUnc",
    "WjetsFFslopeUnc",
    "WjetsFFnormUnc",
    "WjetsFFmcSubUnc",
    "ttbarFFslopeUnc",
    "ttbarFFnormUnc",
    "fracQCDUnc",
    "fracWjetsUnc",
    "fracTTbarUnc",
    "QCDClosureLeadingLepPtCorr",
    "QCDClosureSubleadingTauMassCorr",
    "QCDDRtoSRCorr",
    "WjetsClosureLeadingLepPtCorr",
    "WjetsClosureSubleadingTauMassCorr",
    "WjetsDRtoSRCorr",
    "ttbarClosureLeadingLepPtCorr",
    "ttbarClosureSubleadingTauMassCorr",
]
#  Variations on the jet backgrounds estimated with the fake factor method.
ff_variations_boosted_lt = [
    ReplaceCutAndAddWeight(
        "anti_iso_CMS_boostedtau_{syst}_{ch}_{era}".format(syst=syst+shift, era="Era", ch="Channel"),
        "tau_iso",
        Cut("id_boostedtau_iso_Loose_2<0.5", "tau_anti_iso"),
        Weight(
            "fake_factor_boosted__{syst}".format(syst=syst+shift), "fake_factor"
        ),
    )
    for shift in ["Up", "Down"]
    for syst in _ff_variations_boosted_lt
]
# ff_variations_tau_es_lt = [
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraDown",
#         "tauEs1prong0pizeroDown",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraUp",
#         "tauEs1prong0pizeroUp",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraDown",
#         "tauEs1prong1pizeroDown",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraUp",
#         "tauEs1prong1pizeroUp",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraDown",
#         "tauEs3prong0pizeroDown",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraUp",
#         "tauEs3prong0pizeroUp",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraDown",
#         "tauEs3prong1pizeroDown",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraUp",
#         "tauEs3prong1pizeroUp",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
# ]

_ff_variations_tau_es_emb_lt = [
    "tauEs1prong0pizero",
    "tauEs1prong1pizero",
    "tauEs3prong0pizero",
    "tauEs3prong1pizero",
]
# Propagation of tau ES systematics on jetFakes process for emb only for correlation
ff_variations_tau_es_emb_lt = [
    ReplaceCutAndAddWeight(
        "anti_iso_CMS_emb_{syst}_{ch}_{era}".format(syst=syst+shift, era="Era", ch="Channel"),
        "tau_iso",
        Cut("id_tau_vsJet_Medium_2<0.5&&id_tau_vsJet_VVVLoose_2>0.5", "tau_anti_iso"),
        Weight(
            "fake_factor__{syst}".format(syst=syst+shift), "fake_factor"
        ),
    )
    for shift in ["Up", "Down"]
    for syst in _ff_variations_tau_es_lt
]
# ff_variations_tau_es_emb_lt = [
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_emb_1prong_EraDown",
#         "tauEs1prong0pizeroDown",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_emb_1prong_EraUp",
#         "tauEs1prong0pizeroUp",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_emb_1prong1pizero_EraDown",
#         "tauEs1prong1pizeroDown",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_emb_1prong1pizero_EraUp",
#         "tauEs1prong1pizeroUp",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_emb_3prong_EraDown",
#         "tauEs3prong0pizeroDown",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_emb_3prong_EraUp",
#         "tauEs3prong0pizeroUp",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_emb_3prong1pizero_EraDown",
#         "tauEs3prong1pizeroDown",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_emb_3prong1pizero_EraUp",
#         "tauEs3prong1pizeroUp",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff2_nom", "fake_factor"),
#     ),
# ]

_ff_variations_tt_1 = [
    # "ff2_nom_qcd_stat_njet0_jet_pt_low_unc1{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet0_jet_pt_low_unc2{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet0_jet_pt_low_unc3{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet0_jet_pt_med_unc1{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet0_jet_pt_med_unc2{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet0_jet_pt_med_unc3{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet0_jet_pt_high_unc1{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet0_jet_pt_high_unc2{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet0_jet_pt_high_unc3{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet1_jet_pt_low_unc1{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet1_jet_pt_low_unc2{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet1_jet_pt_low_unc3{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet1_jet_pt_med_unc1{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet1_jet_pt_med_unc2{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet1_jet_pt_med_unc3{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet1_jet_pt_high_unc1{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet1_jet_pt_high_unc2{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_njet1_jet_pt_high_unc3{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_dR_unc1{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_dR_unc2{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_pt_unc1{ch}{era}{shift}",
    # "ff2_nom_qcd_stat_pt_unc2{ch}{era}{shift}",
    # "ff2_nom_qcd_syst{ch}{era}{shift}",
    # "ff2_nom_ttbar_syst{ch}{era}{shift}",
    # "ff2_nom_wjets_syst{ch}{era}{shift}",
    # "ff2_nom_qcd_syst_dr_closure{ch}{era}{shift}",
    # "ff2_nom_qcd_syst_pt_2_closure{ch}{era}{shift}",
    # "ff2_nom_qcd_syst_met_closure{ch}{era}{shift}",
    # "ff2_nom_syst_alt_func{ch}{era}{shift}",
    "QCDFFslopeUnc",
    "QCDFFnormUnc",
    "QCDFFmcSubUnc",
    "ttbarFFslopeUnc",
    "ttbarFFnormUnc",
    "fracQCDUnc",
    "fracWjetsUnc",
    "fracTTbarUnc",
    "QCDClosureSubleadingLepPtCorr",
    "QCDClosureLeadingTauMassCorr",
    "QCDDRtoSRCorr",
    "ttbarClosureSubleadingLepPtCorr",
    "ttbarClosureLeadingTauMassCorr",
]
_ff_variations_tt_2 = [
    "QCDSubleadingFFslopeUnc",
    "QCDSubleadingFFnormUnc",
    "QCDSubleadingFFmcSubUnc",
    "ttbarSubleadingFFslopeUnc",
    "ttbarSubleadingFFnormUnc",
    "fracQCDSubleadingUnc",
    "fracWjetsSubleadingUnc",
    "fracTTbarSubleadingUnc",
    "QCDSubleadingClosureLeadingLepPtCorr",
    "QCDSubleadingClosureSubleadingTauMassCorr",
    "QCDSubleadingDRtoSRCorr",
    "ttbarSubleadingClosureLeadingLepPtCorr",
    "ttbarSubleadingClosureSubleadingTauMassCorr",
]
ff_variations_tt_1 = [
    ReplaceCutAndAddWeight(
        "anti_iso_CMS_{syst}_{ch}_{era}".format(syst=syst+shift, era="Era", ch="tt"),
        "tau_iso",
        Cut(
            "((id_tau_vsJet_Medium_2>0.5 && id_tau_vsJet_Medium_1<0.5 && id_tau_vsJet_VVVLoose_1>0.5) || (id_tau_vsJet_Medium_1>0.5 && id_tau_vsJet_Medium_2<0.5 && id_tau_vsJet_VVVLoose_2>0.5))",
            "tau_anti_iso",
        ),
        Weight(
            "0.5 * fake_factor_1__{syst} * (id_tau_vsJet_Medium_1 < 0.5) + 0.5 * fake_factor_2 * (id_tau_vsJet_Medium_2 < 0.5)".format(syst=syst+shift),
            "fake_factor",
        ),
    )
    for shift in ["Up", "Down"]
    for syst in _ff_variations_tt_1
]
ff_variations_tt_2 = [
    ReplaceCutAndAddWeight(
        "anti_iso_CMS_{syst}_{ch}_{era}".format(syst=syst+shift, era="Era", ch="tt"),
        "tau_iso",
        Cut(
            "((id_tau_vsJet_Medium_2>0.5 && id_tau_vsJet_Medium_1<0.5 && id_tau_vsJet_VVVLoose_1>0.5) || (id_tau_vsJet_Medium_1>0.5 && id_tau_vsJet_Medium_2<0.5 && id_tau_vsJet_VVVLoose_2>0.5))",
            "tau_anti_iso",
        ),
        Weight(
            "0.5 * fake_factor_1 * (id_tau_vsJet_Medium_1 < 0.5) + 0.5 * fake_factor_2__{syst} * (id_tau_vsJet_Medium_2 < 0.5)".format(syst=syst+shift),
            "fake_factor",
        ),
    )
    for shift in ["Up", "Down"]
    for syst in _ff_variations_tt_2
]
ff_variations_tt = ff_variations_tt_1 + ff_variations_tt_2

# boosted taus
_ff_variations_boosted_tt_1 = [
    "QCDFFslopeUnc",
    "QCDFFnormUnc",
    "QCDFFmcSubUnc",
    "ttbarFFslopeUnc",
    "ttbarFFnormUnc",
    "fracQCDUnc",
    "fracWjetsUnc",
    "fracTTbarUnc",
    "QCDClosureSubleadingLepPtCorr",
    "QCDClosureLeadingTauMassCorr",
    "QCDDRtoSRCorr",
    "ttbarClosureSubleadingLepPtCorr",
    "ttbarClosureLeadingTauMassCorr",
]
_ff_variations_boosted_tt_2 = [
    "QCDSubleadingFFslopeUnc",
    "QCDSubleadingFFnormUnc",
    "QCDSubleadingFFmcSubUnc",
    "ttbarSubleadingFFslopeUnc",
    "ttbarSubleadingFFnormUnc",
    "fracQCDSubleadingUnc",
    "fracWjetsSubleadingUnc",
    "fracTTbarSubleadingUnc",
    "QCDSubleadingClosureLeadingLepPtCorr",
    "QCDSubleadingClosureSubleadingTauMassCorr",
    "QCDSubleadingDRtoSRCorr",
    "ttbarSubleadingClosureLeadingLepPtCorr",
    "ttbarSubleadingClosureSubleadingTauMassCorr",
]
ff_variations_boosted_tt_1 = [
    ReplaceCutAndAddWeight(
        "anti_iso_CMS_boostedtau_{syst}_{ch}_{era}".format(syst=syst+shift, era="Era", ch="tt"),
        "tau_iso",
        Cut(
            "((id_boostedtau_iso_Loose_2>0.5 && id_boostedtau_iso_Loose_1<0.5) || (id_boostedtau_iso_Loose_1>0.5 && id_boostedtau_iso_Loose_2<0.5))",
            "tau_anti_iso",
        ),
        Weight(
            "0.5 * fake_factor_boosted_1__{syst} * (id_boostedtau_iso_Loose_1 < 0.5) + 0.5 * fake_factor_boosted_2 * (id_boostedtau_iso_Loose_2 < 0.5)".format(syst=syst+shift),
            "fake_factor",
        ),
    )
    for shift in ["Up", "Down"]
    for syst in _ff_variations_boosted_tt_1
]
ff_variations_boosted_tt_2 = [
    ReplaceCutAndAddWeight(
        "anti_iso_CMS_boostedtau_{syst}_{ch}_{era}".format(syst=syst+shift, era="Era", ch="tt"),
        "tau_iso",
        Cut(
            "((id_boostedtau_iso_Loose_2>0.5 && id_boostedtau_iso_Loose_1<0.5) || (id_boostedtau_iso_Loose_1>0.5 && id_boostedtau_iso_Loose_2<0.5))",
            "tau_anti_iso",
        ),
        Weight(
            "0.5 * fake_factor_boosted_1 * (id_boostedtau_iso_Loose_1 < 0.5) + 0.5 * fake_factor_boosted_2__{syst} * (id_boostedtau_iso_Loose_2 < 0.5)".format(syst=syst+shift),
            "fake_factor",
        ),
    )
    for shift in ["Up", "Down"]
    for syst in _ff_variations_boosted_tt_2
]
ff_variations_boosted_tt = ff_variations_boosted_tt_1 + ff_variations_boosted_tt_2

# ff_variations_tt_mcl = [
#     ReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_{syst}".format(
#             syst=syst.format(shift=shift.capitalize(), era="_Era", ch="_tt")
#         ),
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight(
#             "{syst}".format(syst=syst.format(shift="_" + shift, era="", ch="")),
#             "fake_factor",
#         ),
#     )
#     for shift in ["up", "down"]
#     for syst in _ff_variations_tt
# ]

# # tt channel for embedded processes
# ff_variations_tau_es_tt = [
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraDown",
#         "tauEs1prong0pizeroDown",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraUp",
#         "tauEs1prong0pizeroUp",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraDown",
#         "tauEs1prong1pizeroDown",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraUp",
#         "tauEs1prong1pizeroUp",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraDown",
#         "tauEs3prong0pizeroDown",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraUp",
#         "tauEs3prong0pizeroUp",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraDown",
#         "tauEs3prong1pizeroDown",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraUp",
#         "tauEs3prong1pizeroUp",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("ff2_nom", "fake_factor"),
#     ),
# ]

# # tt channel for mcl processes
# ff_variations_tau_es_tt_mcl = [
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraDown",
#         "tauEs1prong0pizeroDown",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraUp",
#         "tauEs1prong0pizeroUp",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraDown",
#         "tauEs1prong1pizeroDown",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraUp",
#         "tauEs1prong1pizeroUp",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraDown",
#         "tauEs3prong0pizeroDown",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraUp",
#         "tauEs3prong0pizeroUp",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraDown",
#         "tauEs3prong1pizeroDown",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("ff2_nom", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraUp",
#         "tauEs3prong1pizeroUp",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("ff2_nom", "fake_factor"),
#     ),
# ]

# qcd_variations_em = [
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_rate_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_rateup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_rate_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_ratedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_shape_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_shapeup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_shape_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_shapedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_shape2_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_shape2up_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_shape2_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_shape2down_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_rate_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_rateup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_rate_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_ratedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_shape_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_shapeup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_shape_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_shapedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_shape2_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_shape2up_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_shape2_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_shape2down_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_rate_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_rateup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_rate_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_ratedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_shape_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_shapeup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_shape_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_shapedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_shape2_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_shape2up_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_shape2_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_shape2down_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_iso_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_extrap_up_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_iso_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_extrap_down_Weight", "qcd_weight"),
#     ),
# ]
