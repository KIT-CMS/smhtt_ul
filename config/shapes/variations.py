from ntuple_processor.utils import Cut
from ntuple_processor.utils import Weight

from ntuple_processor.variations import ChangeDataset
from ntuple_processor.variations import ReplaceCut
from ntuple_processor.variations import ReplaceWeight
from ntuple_processor.variations import RemoveCut
from ntuple_processor.variations import RemoveWeight
from ntuple_processor.variations import AddCut
from ntuple_processor.variations import AddWeight
from ntuple_processor.variations import SquareWeight
from ntuple_processor.variations import ReplaceCutAndAddWeight
from ntuple_processor.variations import ReplaceMultipleCuts

#  Variations needed for the various jet background estimations.
same_sign = ReplaceCut("same_sign", "os", Cut("q_1*q_2>0", "ss"))

# TODO: In order to properly use this variation friend trees with the correct weights need to be created.
same_sign_em = ReplaceCutAndAddWeight("same_sign", "os",
                                      Cut("q_1*q_2>0", "ss"),
                                      Weight("em_qcd_osss_binned_Weight", "qcd_weight")
                                      )
abcd_method = [ReplaceCut("abcd_same_sign", "os", Cut("q_1*q_2>0", "ss")),
               ReplaceCut("abcd_anti_iso", "tau_iso",
                          Cut("(byMediumDeepTau2017v2p1VSjet_1>0.5&&byMediumDeepTau2017v2p1VSjet_2<0.5&&byLooseDeepTau2017v2p1VSjet_2>0.5)", "tau_anti_iso")),
               ReplaceMultipleCuts("abcd_same_sign_anti_iso", ["os", "tau_iso"],
                           [Cut("q_1*q_2>0", "ss"),
                            Cut("(byMediumDeepTau2017v2p1VSjet_1>0.5&&byMediumDeepTau2017v2p1VSjet_2<0.5&&byLooseDeepTau2017v2p1VSjet_2>0.5)", "tau_anti_iso")])
]

anti_iso_lt = ReplaceCutAndAddWeight("anti_iso", "tau_iso",
                                     Cut("byMediumDeepTau2017v2p1VSjet_2<0.5&&byVVVLooseDeepTau2017v2p1VSjet_2>0.5", "tau_anti_iso"),
                                     Weight("ff_total", "fake_factor")
                                     )
anti_iso_tt = ReplaceCutAndAddWeight("anti_iso", "tau_iso",
                                     Cut("(byMediumDeepTau2017v2p1VSjet_2>0.5&&byMediumDeepTau2017v2p1VSjet_1<0.5&&byVVVLooseDeepTau2017v2p1VSjet_1>0.5)", "tau_anti_iso"),
                                     Weight("ff_total", "fake_factor")
                                     )
anti_iso_split_lt = [ReplaceCutAndAddWeight("anti_iso_w", "tau_iso",
                                     Cut("byMediumDeepTau2017v2p1VSjet_2<0.5&&byVVVLooseDeepTau2017v2p1VSjet_2>0.5", "tau_anti_iso"),
                                     Weight("ff_lt_wjets", "fake_factor")
                                     ),
                     ReplaceCutAndAddWeight("anti_iso_qcd", "tau_iso",
                                     Cut("byMediumDeepTau2017v2p1VSjet_2<0.5&&byVVVLooseDeepTau2017v2p1VSjet_2>0.5", "tau_anti_iso"),
                                     Weight("ff_lt_qcd", "fake_factor")
                                     ),
                     ReplaceCutAndAddWeight("anti_iso_tt", "tau_iso",
                                     Cut("byMediumDeepTau2017v2p1VSjet_2<0.5&&byVVVLooseDeepTau2017v2p1VSjet_2>0.5", "tau_anti_iso"),
                                     Weight("ff_lt_ttbar", "fake_factor")
                                     ),
                    ]

# Energy scales.
# Previously defined with 2017 in name.
tau_es_3prong = [
        ChangeDataset("CMS_scale_t_3prong_EraUp", "tauEsThreeProngUp"),
        ChangeDataset("CMS_scale_t_3prong_EraDown", "tauEsThreeProngDown")
        ]

tau_es_3prong1pizero = [
        ChangeDataset("CMS_scale_t_3prong1pizero_EraUp", "tauEsThreeProngOnePiZeroUp"),
        ChangeDataset("CMS_scale_t_3prong1pizero_EraDown", "tauEsThreeProngOnePiZeroDown")
        ]

tau_es_1prong = [
        ChangeDataset("CMS_scale_t_1prong_EraUp", "tauEsOneProngUp"),
        ChangeDataset("CMS_scale_t_1prong_EraDown", "tauEsOneProngDown")
        ]

tau_es_1prong1pizero = [
        ChangeDataset("CMS_scale_t_1prong1pizero_EraUp", "tauEsOneProngOnePiZeroUp"),
        ChangeDataset("CMS_scale_t_1prong1pizero_EraDown", "tauEsOneProngOnePiZeroDown")
        ]

emb_tau_es_3prong = [
        ChangeDataset("CMS_scale_t_emb_3prong_EraUp", "tauEsThreeProngUp"),
        ChangeDataset("CMS_scale_t_emb_3prong_EraDown", "tauEsThreeProngDown")
        ]

emb_tau_es_3prong1pizero = [
        ChangeDataset("CMS_scale_t_emb_3prong1pizero_EraUp", "tauEsThreeProngOnePiZeroUp"),
        ChangeDataset("CMS_scale_t_emb_3prong1pizero_EraDown", "tauEsThreeProngOnePiZeroDown")
        ]

emb_tau_es_1prong = [
        ChangeDataset("CMS_scale_t_emb_1prong_EraUp", "tauEsOneProngUp"),
        ChangeDataset("CMS_scale_t_emb_1prong_EraDown", "tauEsOneProngDown")
        ]

emb_tau_es_1prong1pizero = [
        ChangeDataset("CMS_scale_t_emb_1prong1pizero_EraUp", "tauEsOneProngOnePiZeroUp"),
        ChangeDataset("CMS_scale_t_emb_1prong1pizero_EraDown", "tauEsOneProngOnePiZeroDown")
        ]


# Electron energy scale
ele_es = [
        ChangeDataset("CMS_scale_eUp", "eleScaleUp"),
        ChangeDataset("CMS_scale_eDown", "eleScaleDown")
        ]

ele_res = [
        ChangeDataset("CMS_res_eUp", "eleSmearUp"),
        ChangeDataset("CMS_res_eDown", "eleSmearDown")
        ]

# Jet energy scale split by sources.
jet_es = [
        ChangeDataset("CMS_scale_j_AbsoluteUp", "jecUncAbsoluteUp"),
        ChangeDataset("CMS_scale_j_AbsoluteDown", "jecUncAbsoluteDown"),
        ChangeDataset("CMS_scale_j_Absolute_EraUp", "jecUncAbsoluteYearUp"),
        ChangeDataset("CMS_scale_j_Absolute_EraDown", "jecUncAbsoluteYearDown"),
        ChangeDataset("CMS_scale_j_BBEC1Up", "jecUncBBEC1Up"),
        ChangeDataset("CMS_scale_j_BBEC1Down", "jecUncBBEC1Down"),
        ChangeDataset("CMS_scale_j_BBEC1_EraUp", "jecUncBBEC1YearUp"),
        ChangeDataset("CMS_scale_j_BBEC1_EraDown", "jecUncBBEC1YearDown"),
        ChangeDataset("CMS_scale_j_EC2Up", "jecUncEC2Up"),
        ChangeDataset("CMS_scale_j_EC2Down", "jecUncEC2Down"),
        ChangeDataset("CMS_scale_j_EC2_EraUp", "jecUncEC2YearUp"),
        ChangeDataset("CMS_scale_j_EC2_EraDown", "jecUncEC2YearDown"),
        ChangeDataset("CMS_scale_j_HFUp", "jecUncHFUp"),
        ChangeDataset("CMS_scale_j_HFDown", "jecUncHFDown"),
        ChangeDataset("CMS_scale_j_HF_EraUp", "jecUncHFYearUp"),
        ChangeDataset("CMS_scale_j_HF_EraDown", "jecUncHFYearDown"),
        ChangeDataset("CMS_scale_j_FlavorQCDUp", "jecUncFlavorQCDUp"),
        ChangeDataset("CMS_scale_j_FlavorQCDDown", "jecUncFlavorQCDDown"),
        ChangeDataset("CMS_scale_j_RelativeBalUp", "jecUncRelativeBalUp"),
        ChangeDataset("CMS_scale_j_RelativeBalDown", "jecUncRelativeBalDown"),
        ChangeDataset("CMS_scale_j_RelativeSample_EraUp", "jecUncRelativeSampleYearUp"),
        ChangeDataset("CMS_scale_j_RelativeSample_EraDown", "jecUncRelativeSampleYearDown"),
        ChangeDataset("CMS_res_j_EraUp", "jerUncUp"),
        ChangeDataset("CMS_res_j_EraDown", "jerUncDown"),
        ]


# MET variations.
met_unclustered = [
        ChangeDataset("CMS_scale_met_unclusteredUp", "metUnclusteredEnUp"),
        ChangeDataset("CMS_scale_met_unclusteredDown", "metUnclusteredEnDown")
        ]

# Recoil correction uncertainties
recoil_resolution = [
        ChangeDataset("CMS_htt_boson_res_met_EraUp", "metRecoilResolutionUp"),
        ChangeDataset("CMS_htt_boson_res_met_EraDown", "metRecoilResolutionDown")
        ]

recoil_response = [
        ChangeDataset("CMS_htt_boson_scale_met_EraUp", "metRecoilResponseUp"),
        ChangeDataset("CMS_htt_boson_scale_met_EraDown", "metRecoilResponseDown")
        ]

# Energy scales of leptons faking tau leptons.
ele_fake_es_1prong = [
        ChangeDataset("CMS_ZLShape_et_1prong_barrel_EraUp", "tauEleFakeEsOneProngBarrelUp"),
        ChangeDataset("CMS_ZLShape_et_1prong_barrel_EraDown", "tauEleFakeEsOneProngBarrelDown"),
        ChangeDataset("CMS_ZLShape_et_1prong_endcap_EraUp", "tauEleFakeEsOneProngEndcapUp"),
        ChangeDataset("CMS_ZLShape_et_1prong_endcap_EraDown", "tauEleFakeEsOneProngEndcapDown"),
        ]

ele_fake_es_1prong1pizero = [
        ChangeDataset("CMS_ZLShape_et_1prong1pizero_barrel_EraUp", "tauEleFakeEsOneProngPiZerosBarrelUp"),
        ChangeDataset("CMS_ZLShape_et_1prong1pizero_barrel_EraDown", "tauEleFakeEsOneProngPiZerosBarrelDown"),
        ChangeDataset("CMS_ZLShape_et_1prong1pizero_endcap_EraUp", "tauEleFakeEsOneProngPiZerosEndcapUp"),
        ChangeDataset("CMS_ZLShape_et_1prong1pizero_endcap_EraDown", "tauEleFakeEsOneProngPiZerosEndcapDown"),
        ]

mu_fake_es_1prong = [
        ChangeDataset("CMS_ZLShape_mt_1prong_EraUp", "tauMuFakeEsOneProngUp"),
        ChangeDataset("CMS_ZLShape_mt_1prong_EraDown", "tauMuFakeEsOneProngDown")
        ]

mu_fake_es_1prong1pizero = [
        ChangeDataset("CMS_ZLShape_mt_1prong1pizero_EraUp", "tauMuFakeEsOneProngPiZerosUp"),
        ChangeDataset("CMS_ZLShape_mt_1prong1pizero_EraDown", "tauMuFakeEsOneProngPiZerosDown")
        ]

# B-tagging uncertainties.
btag_eff = [
        ChangeDataset("CMS_htt_eff_b_EraUp", "btagEffUp"),
        ChangeDataset("CMS_htt_eff_b_EraDown", "btagEffDown")
        ]

mistag_eff = [
        ChangeDataset("CMS_htt_mistag_b_EraUp", "btagMistagUp"),
        ChangeDataset("CMS_htt_mistag_b_EraDown", "btagMistagDown")
        ]

# Efficiency corrections.
# Tau ID efficiency.
tau_id_eff_lt = [
        ReplaceWeight("CMS_eff_t_30-35_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 30 && pt_2 <= 35)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 30 || pt_2 > 35)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_30-35_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 30 && pt_2 <= 35)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 30 || pt_2 > 35)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_35-40_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 35 && pt_2 <= 40)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 35 || pt_2 > 40)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_35-40_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 35 && pt_2 <= 40)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 35 || pt_2 > 40)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_40-500_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 40 && pt_2 <= 500)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 40 || pt_2 > 500)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_40-500_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 40 && pt_2 <= 500)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 40 || pt_2 > 500)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_500-1000_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 500 && pt_2 <= 1000)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 500 || pt_2 > 1000)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_500-1000_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 500 && pt_2 <= 1000)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 500 || pt_2 > 1000)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_1000-inf_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 1000)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 1000)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_1000-inf_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 1000)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 1000)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ]

emb_tau_id_eff_lt = [
        ReplaceWeight("CMS_eff_t_emb_30-35_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 30 && pt_2 <= 35)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 30 || pt_2 > 35)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_30-35_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 30 && pt_2 <= 35)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 30 || pt_2 > 35)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_35-40_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 35 && pt_2 <= 40)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 35 || pt_2 > 40)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_35-40_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 35 && pt_2 <= 40)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 35 || pt_2 > 40)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_40-500_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 40 && pt_2 <= 500)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 40 || pt_2 > 500)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_40-500_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 40 && pt_2 <= 500)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 40 || pt_2 > 500)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_500-1000_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 500 && pt_2 <= 1000)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 500 || pt_2 > 1000)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_500-1000_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 500 && pt_2 <= 1000)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 500 || pt_2 > 1000)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_1000-inf_EraUp", "taubyIsoIdWeight", Weight("(((pt_2 >= 1000)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 1000)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_1000-inf_EraDown", "taubyIsoIdWeight", Weight("(((pt_2 >= 1000)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((pt_2 < 1000)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ]

tau_id_eff_tt = [
        ReplaceWeight("CMS_eff_t_dm0_EraUp", "taubyIsoIdWeight", Weight("(((decayMode_1==0)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=0)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==0)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=0)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_dm0_EraDown", "taubyIsoIdWeight", Weight("(((decayMode_1==0)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=0)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==0)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=0)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_dm1_EraUp", "taubyIsoIdWeight", Weight("(((decayMode_1==1)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=1)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==1)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=1)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_dm1_EraDown", "taubyIsoIdWeight", Weight("(((decayMode_1==1)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=1)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==1)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=1)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_dm10_EraUp", "taubyIsoIdWeight", Weight("(((decayMode_1==10)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=10)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==10)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=10)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_dm10_EraDown", "taubyIsoIdWeight", Weight("(((decayMode_1==10)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=10)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==10)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=10)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_dm11_EraUp", "taubyIsoIdWeight", Weight("(((decayMode_1==11)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=11)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==11)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=11)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_dm11_EraDown", "taubyIsoIdWeight", Weight("(((decayMode_1==11)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=11)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==11)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=11)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ]

emb_tau_id_eff_tt = [
        ReplaceWeight("CMS_eff_t_emb_dm0_EraUp", "taubyIsoIdWeight", Weight("(((decayMode_1==0)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=0)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==0)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=0)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_dm0_EraDown", "taubyIsoIdWeight", Weight("(((decayMode_1==0)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=0)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==0)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=0)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_dm1_EraUp", "taubyIsoIdWeight", Weight("(((decayMode_1==1)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=1)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==1)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=1)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_dm1_EraDown", "taubyIsoIdWeight", Weight("(((decayMode_1==1)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=1)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==1)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=1)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_dm10_EraUp", "taubyIsoIdWeight", Weight("(((decayMode_1==10)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=10)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==10)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=10)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_dm10_EraDown", "taubyIsoIdWeight", Weight("(((decayMode_1==10)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=10)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==10)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=10)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_dm11_EraUp", "taubyIsoIdWeight", Weight("(((decayMode_1==11)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=11)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==11)*tauIDScaleFactorWeightUp_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=11)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ReplaceWeight("CMS_eff_t_emb_dm11_EraDown", "taubyIsoIdWeight", Weight("(((decayMode_1==11)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_1)+((decayMode_1!=11)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_1))*(((decayMode_2==11)*tauIDScaleFactorWeightDown_tight_DeepTau2017v2p1VSjet_2)+((decayMode_2!=11)*tauIDScaleFactorWeight_tight_DeepTau2017v2p1VSjet_2))", "taubyIsoIdWeight")),
        ]

# Jet to tau fake rate.
jet_to_tau_fake = [
        AddWeight("CMS_htt_fake_j_EraUp", Weight("max(1.0-pt_2*0.002, 0.6)", "jetToTauFake_weight")),
        AddWeight("CMS_htt_fake_j_EraDown", Weight("min(1.0+pt_2*0.002, 1.4)", "jetToTauFake_weight"))
        ]

_efake_dict = {
    "2016" : {
        "BA" : "0.31*(abs(eta_1)<1.448)",
        "EC" : "0.22*(abs(eta_1)>1.558)"
    },
    "2017" : {
        "BA" : "0.26*(abs(eta_1)<1.448)",
        "EC" : "0.41*(abs(eta_1)>1.558)"
    },
    "2018" : {
        "BA" : "0.18*(abs(eta_1)<1.448)",
        "EC" : "0.30*(abs(eta_1)>1.558)"
    }
}

_mfake_dict = {
    "2016" : {
        "WH1" : "0.09*((abs(eta_1)<0.4))",
        "WH2" : "0.42*((abs(eta_1)>=0.4)*((abs(eta_1)<0.8)))",
        "WH3" : "0.20*((abs(eta_1)>=0.8)*((abs(eta_1)<1.2)))",
        "WH4" : "0.63*((abs(eta_1)>=1.2)*((abs(eta_1)<1.7)))",
        "WH5" : "0.17*((abs(eta_1)>=1.7))"
    },
    "2017" : {
        "WH1" : "0.18*((abs(eta_1)<0.4))",
        "WH2" : "0.32*((abs(eta_1)>=0.4)*((abs(eta_1)<0.8)))",
        "WH3" : "0.39*((abs(eta_1)>=0.8)*((abs(eta_1)<1.2)))",
        "WH4" : "0.42*((abs(eta_1)>=1.2)*((abs(eta_1)<1.7)))",
        "WH5" : "0.21*((abs(eta_1)>=1.7))"
    },
    "2018" : {
        "WH1" : "0.19*((abs(eta_1)<0.4))",
        "WH2" : "0.34*((abs(eta_1)>=0.4)*((abs(eta_1)<0.8)))",
        "WH3" : "0.24*((abs(eta_1)>=0.8)*((abs(eta_1)<1.2)))",
        "WH4" : "0.57*((abs(eta_1)>=1.2)*((abs(eta_1)<1.7)))",
        "WH5" : "0.20*((abs(eta_1)>=1.7))"
    }
}

zll_et_fake_rate_2016 = [
        AddWeight("CMS_fake_e_BA_2016Up", Weight("(1.0+{})".format(_efake_dict["2016"]["BA"]), "eFakeTau_reweight")),
        AddWeight("CMS_fake_e_BA_2016Down", Weight("(1.0-{})".format(_efake_dict["2016"]["BA"]), "eFakeTau_reweight")),
        AddWeight("CMS_fake_e_EC_2016Up", Weight("(1.0+{})".format(_efake_dict["2016"]["EC"]), "eFakeTau_reweight")),
        AddWeight("CMS_fake_e_EC_2016Down", Weight("(1.0-{})".format(_efake_dict["2016"]["EC"]), "eFakeTau_reweight")),
        ]
zll_et_fake_rate_2017 = [
        AddWeight("CMS_fake_e_BA_2017Up", Weight("(1.0+{})".format(_efake_dict["2017"]["BA"]), "eFakeTau_reweight")),
        AddWeight("CMS_fake_e_BA_2017Down", Weight("(1.0-{})".format(_efake_dict["2017"]["BA"]), "eFakeTau_reweight")),
        AddWeight("CMS_fake_e_EC_2017Up", Weight("(1.0+{})".format(_efake_dict["2017"]["EC"]), "eFakeTau_reweight")),
        AddWeight("CMS_fake_e_EC_2017Down", Weight("(1.0-{})".format(_efake_dict["2017"]["EC"]), "eFakeTau_reweight")),
        ]
zll_et_fake_rate_2018 = [
        AddWeight("CMS_fake_e_BA_2018Up", Weight("(1.0+{})".format(_efake_dict["2018"]["BA"]), "eFakeTau_reweight")),
        AddWeight("CMS_fake_e_BA_2018Down", Weight("(1.0-{})".format(_efake_dict["2018"]["BA"]), "eFakeTau_reweight")),
        AddWeight("CMS_fake_e_EC_2018Up", Weight("(1.0+{})".format(_efake_dict["2018"]["EC"]), "eFakeTau_reweight")),
        AddWeight("CMS_fake_e_EC_2018Down", Weight("(1.0-{})".format(_efake_dict["2018"]["EC"]), "eFakeTau_reweight")),
        ]

zll_mt_fake_rate_2016 = [*[AddWeight("CMS_fake_m_{}_2016Up".format(region), Weight("(1.0+{})".format(_mfake_dict["2016"][region]), "mFakeTau_reweight")) for region in _mfake_dict["2016"].keys()],
                         *[AddWeight("CMS_fake_m_{}_2016Down".format(region), Weight("(1.0+{})".format(_mfake_dict["2016"][region]), "mFakeTau_reweight")) for region in _mfake_dict["2016"].keys()],
                         ]
zll_mt_fake_rate_2017 = [*[AddWeight("CMS_fake_m_{}_2017Up".format(region), Weight("(1.0+{})".format(_mfake_dict["2017"][region]), "mFakeTau_reweight")) for region in _mfake_dict["2017"].keys()],
                         *[AddWeight("CMS_fake_m_{}_2017Down".format(region), Weight("(1.0+{})".format(_mfake_dict["2017"][region]), "mFakeTau_reweight")) for region in _mfake_dict["2017"].keys()],
                         ]
zll_mt_fake_rate_2018 = [*[AddWeight("CMS_fake_m_{}_2018Up".format(region), Weight("(1.0+{})".format(_mfake_dict["2018"][region]), "mFakeTau_reweight")) for region in _mfake_dict["2018"].keys()],
                         *[AddWeight("CMS_fake_m_{}_2018Down".format(region), Weight("(1.0+{})".format(_mfake_dict["2018"][region]), "mFakeTau_reweight")) for region in _mfake_dict["2018"].keys()],
                         ]

_lteffCutDEra = {
    "2016": {
        "mt": "23",
        "et": "26"},
    "2017": {
        "mt": "25",
        "et": "28"},
    "2018": {
        "mt": "25",
        "et": "33"},
}

# Trigger efficiency uncertainties.
lep_trigger_eff_mt_2016 = [
        AddWeight("CMS_eff_trigger_mt_2016Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_trigger_mt_2016Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_mt_2016Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["mt"]), "xtrg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_mt_2016Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["mt"]), "xtrg_mt_eff_weight"))
        ]
lep_trigger_eff_mt_2017 = [
        AddWeight("CMS_eff_trigger_mt_2017Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_trigger_mt_2017Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_mt_2017Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["mt"]), "xtrg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_mt_2017Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["mt"]), "xtrg_mt_eff_weight"))
        ]
lep_trigger_eff_mt_2018 = [
        AddWeight("CMS_eff_trigger_mt_2018Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_trigger_mt_2018Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_mt_2018Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["mt"]), "xtrg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_mt_2018Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["mt"]), "xtrg_mt_eff_weight"))
        ]

lep_trigger_eff_mt_emb_2016 = [
        AddWeight("CMS_eff_trigger_emb_mt_2016Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_trigger_emb_mt_2016Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_mt_2016Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["mt"]), "xtrg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_mt_2016Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["mt"]), "xtrg_mt_eff_weight"))
        ]
lep_trigger_eff_mt_emb_2017 = [
        AddWeight("CMS_eff_trigger_emb_mt_2017Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_trigger_emb_mt_2017Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_mt_2017Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["mt"]), "xtrg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_mt_2017Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["mt"]), "xtrg_mt_eff_weight"))
        ]
lep_trigger_eff_mt_emb_2018 = [
        AddWeight("CMS_eff_trigger_emb_mt_2018Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_trigger_emb_mt_2018Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["mt"]), "trg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_mt_2018Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["mt"]), "xtrg_mt_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_mt_2018Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["mt"]), "xtrg_mt_eff_weight"))
        ]

lep_trigger_eff_et_2016 = [
        AddWeight("CMS_eff_trigger_et_2016Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_trigger_et_2016Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_et_2016Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["et"]), "xtrg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_et_2016Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["et"]), "xtrg_et_eff_weight"))
        ]
lep_trigger_eff_et_2017 = [
        AddWeight("CMS_eff_trigger_et_2017Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_trigger_et_2017Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_et_2017Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["et"]), "xtrg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_et_2017Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["et"]), "xtrg_et_eff_weight"))
        ]
lep_trigger_eff_et_2018 = [
        AddWeight("CMS_eff_trigger_et_2018Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_trigger_et_2018Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_et_2018Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["et"]), "xtrg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_et_2018Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["et"]), "xtrg_et_eff_weight"))
        ]

lep_trigger_eff_et_emb_2016 = [
        AddWeight("CMS_eff_trigger_emb_et_2016Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_trigger_emb_et_2016Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_et_2016Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["et"]), "xtrg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_et_2016Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2016"]["et"]), "xtrg_et_eff_weight"))
        ]
lep_trigger_eff_et_emb_2017 = [
        AddWeight("CMS_eff_trigger_emb_et_2017Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_trigger_emb_et_2017Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_et_2017Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["et"]), "xtrg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_et_2017Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2017"]["et"]), "xtrg_et_eff_weight"))
        ]
lep_trigger_eff_et_emb_2018 = [
        AddWeight("CMS_eff_trigger_emb_et_2018Up", Weight("(1.0*(pt_1<={pt})+1.02*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_trigger_emb_et_2018Down", Weight("(1.0*(pt_1<={pt})+0.98*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["et"]), "trg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_et_2018Up", Weight("(1.02*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["et"]), "xtrg_et_eff_weight")),
        AddWeight("CMS_eff_xtrigger_l_emb_et_2018Down", Weight("(0.98*(pt_1<={pt})+1.0*(pt_1>{pt}))".format(pt=_lteffCutDEra["2018"]["et"]), "xtrg_et_eff_weight"))
        ]

_lteff_exp = {
    "2016": {
        "et": "(pt_1>=26)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerMCEfficiencyWeightKIT_1)",
        "mt": "(pt_1>=23)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerMCEfficiencyWeightKIT_1)"},
    "2017": {
        "et": "(pt_1>=28)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerMCEfficiencyWeightKIT_1)",
        "mt": "(pt_1>=25)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerMCEfficiencyWeightKIT_1)"},
    "2018": {
        "et": "(pt_1>=36)*trigger_32_35_Weight_1+(pt_1>=33)*(pt_1<36)*(trigger_32_Weight_1)",
        "mt": "(pt_1>=25)*(pt_1<28)*(trigger_24_Weight_1)+(pt_1>=28)*(trigger_24_27_Weight_1)"},
}
_xtrg_lep_weight = {
    "2016": {
        "et": "(crossTriggerDataEfficiencyWeightKIT_1/crossTriggerMCEfficiencyWeightKIT_1)",
        "mt": "(crossTriggerDataEfficiencyWeightKIT_1/crossTriggerMCEfficiencyWeightKIT_1)"},
    "2017": {
        "et": "(crossTriggerDataEfficiencyWeight_1/crossTriggerMCEfficiencyWeight_1)",
        "mt": "(crossTriggerDataEfficiencyWeight_1/crossTriggerMCEfficiencyWeight_1)"},
    "2018": {
        "et": "(crossTriggerDataEfficiencyWeight_1/crossTriggerMCEfficiencyWeight_1)",
        "mt": "(crossTriggerDataEfficiencyWeight_1/crossTriggerMCEfficiencyWeight_1)"}
}
_tau_trigger_wstring = "({lt_eff}+(pt_1<{ptcut})*(abs(eta_2)<2.1)*{xtrigger_leptonweight}*(((decayMode_2=={dm})*((crossTriggerDataEfficiencyWeight_tight_DeepTau_2/(crossTriggerMCEfficiencyWeight_tight_DeepTau_2*((pt_1<{ptcut})*(abs(eta_2)<2.1))+1.0*((pt_1>={ptcut})+(abs(eta_2)>=2.1))))*(1{operator}TMath::Sqrt(TMath::Power((crossTriggerDataEfficiencyWeight_tight_DeepTau_2-crossTriggerDataEfficiencyWeightDown_tight_DeepTau_2)/(crossTriggerDataEfficiencyWeight_tight_DeepTau_2*((pt_1<{ptcut})*(abs(eta_2)<2.1))+1.0*((pt_1>={ptcut})+(abs(eta_2)>=2.1))),2)+TMath::Power((crossTriggerMCEfficiencyWeight_tight_DeepTau_2-crossTriggerMCEfficiencyWeightDown_tight_DeepTau_2)/(crossTriggerMCEfficiencyWeight_tight_DeepTau_2*((pt_1<{ptcut})*(abs(eta_2)<2.1))+1.0*((pt_1>={ptcut})+(abs(eta_2)>=2.1))),2)))))+((decayMode_2!={dm})*(crossTriggerDataEfficiencyWeight_tight_DeepTau_2/(crossTriggerMCEfficiencyWeight_tight_DeepTau_2*((pt_1<{ptcut})*(abs(eta_2)<2.1))+1.0*((pt_1>={ptcut})+(abs(eta_2)>=2.1)))))))"
tau_trigger_eff_et_2016 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2016Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["et"],
                                                           ptcut=_lteffCutDEra["2016"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["et"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2016Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["et"],
                                                           ptcut=_lteffCutDEra["2016"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["et"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
]
tau_trigger_eff_et_2017 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2017Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2017"]["et"],
                                                           ptcut=_lteffCutDEra["2017"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2017"]["et"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2017Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2017"]["et"],
                                                           ptcut=_lteffCutDEra["2017"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2017"]["et"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
]
tau_trigger_eff_et_2018 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2018Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["et"],
                                                           ptcut=_lteffCutDEra["2018"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["et"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2018Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["et"],
                                                           ptcut=_lteffCutDEra["2018"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["et"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
]
tau_trigger_eff_mt_2016 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2016Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["mt"],
                                                           ptcut=_lteffCutDEra["2016"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["mt"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2016Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["mt"],
                                                           ptcut=_lteffCutDEra["2016"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["mt"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
]
tau_trigger_eff_mt_2017 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2017Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2017"]["mt"],
                                                           ptcut=_lteffCutDEra["2017"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2017"]["mt"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2017Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2017"]["mt"],
                                                           ptcut=_lteffCutDEra["2017"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2017"]["mt"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
]
tau_trigger_eff_mt_2018 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2018Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["mt"],
                                                           ptcut=_lteffCutDEra["2018"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["mt"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2018Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["mt"],
                                                           ptcut=_lteffCutDEra["2018"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["mt"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
]

_lteff_exp = {
    "2016": {
        "et": "(pt_1>=26)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerEmbeddedEfficiencyWeightKIT_1)",
        "mt": "(pt_1>=23)*(singleTriggerDataEfficiencyWeightKIT_1/singleTriggerEmbeddedEfficiencyWeightKIT_1)"},
    "2017": {
        "et": "((pt_1>=28)*(((pt_1<33)*trigger_27_Weight_1+(pt_1>=33)*(pt_1<36)*trigger_27_32_Weight_1+(pt_1>=36)*trigger_27_32_35_Weight_1)*(abs(eta_1) < 1.5||pt_1>=40) + singleTriggerDataEfficiencyWeightKIT_1*(abs(eta_1)>=1.5)*(pt_1<40)))",
        "mt": "(pt_1>=25 && pt_1<28)*(trigger_24_Weight_1)+(pt_1>=28)*(trigger_24_27_Weight_1)"},
    "2018": {
        "et": "(pt_1>=36)*trigger_32_35_Weight_1+(pt_1>=33)*(pt_1<36)*(trigger_32_Weight_1)",
        "mt": "(pt_1>=25)*(pt_1<28)*(trigger_24_Weight_1)+(pt_1>=28)*(trigger_24_27_Weight_1)"},
}
_xtrg_lep_weight = {
    "2016": {
        "et": "(crossTriggerDataEfficiencyWeightKIT_1/crossTriggerEmbeddedEfficiencyWeightKIT_1)",
        "mt": "(crossTriggerDataEfficiencyWeightKIT_1/crossTriggerEmbeddedEfficiencyWeightKIT_1)"},
    "2017": {
        "et": "crossTriggerEmbeddedWeight_1",
        "mt": "crossTriggerEmbeddedWeight_1"},
    "2018": {
        "et": "crossTriggerEmbeddedWeight_1",
        "mt": "crossTriggerEmbeddedWeight_1"}
}
_tau_trigger_wstring = "({lt_eff}+(pt_1<{ptcut})*(abs(eta_2)<2.1)*{xtrigger_leptonweight}*(((decayMode_2=={dm})*((crossTriggerDataEfficiencyWeight_tight_DeepTau_2/(crossTriggerEMBEfficiencyWeight_tight_DeepTau_2*((pt_1<{ptcut})*(abs(eta_2)<2.1))+1.0*((pt_1>={ptcut})+(abs(eta_2)>=2.1)))*(1{operator}TMath::Sqrt(TMath::Power((crossTriggerDataEfficiencyWeight_tight_DeepTau_2-crossTriggerDataEfficiencyWeightDown_tight_DeepTau_2)/(crossTriggerDataEfficiencyWeight_tight_DeepTau_2*(pt_1<{ptcut})*(abs(eta_2)<2.1)+1.0*((pt_1>={ptcut})+(abs(eta_2)>=2.1))),2)+TMath::Power((crossTriggerEMBEfficiencyWeight_tight_DeepTau_2-crossTriggerEMBEfficiencyWeightDown_tight_DeepTau_2)/(crossTriggerEMBEfficiencyWeight_tight_DeepTau_2*(pt_1<{ptcut})*(abs(eta_2)<2.1)+1.0*((pt_1>{ptcut})+(abs(eta_2)>=2.1))),2)))))+((decayMode_2!={dm})*(crossTriggerDataEfficiencyWeight_tight_DeepTau_2/(crossTriggerEMBEfficiencyWeight_tight_DeepTau_2*(pt_1<{ptcut})*(abs(eta_2)<2.1)+1.0*((pt_1>{ptcut})+(abs(eta_2)>=2.1))))))))"
_tau_trigger_wstring_2017et = "{lt_eff}+(pt_1<{ptcut})*((abs(eta_1)>=1.5)*crossTriggerDataEfficiencyWeight_1*(((decayMode_2=={dm})*(crossTriggerDataEfficiencyWeight_tight_DeepTau_2{operator}(crossTriggerDataEfficiencyWeight_tight_DeepTau_2-crossTriggerDataEfficiencyWeightDown_tight_DeepTau_2)))+((decayMode_2!={dm})*crossTriggerDataEfficiencyWeight_tight_DeepTau_2))+(abs(eta_1)<1.5)*{xtrigger_leptonweight}*(((decayMode_2=={dm})*((crossTriggerDataEfficiencyWeight_tight_DeepTau_2/(crossTriggerEMBEfficiencyWeight_tight_DeepTau_2*(pt_1<{ptcut})*(abs(eta_1)<1.5)+1.0*((pt_1>={ptcut})+(abs(eta_1)>=1.5))))*(1{operator}TMath::Sqrt(TMath::Power((crossTriggerDataEfficiencyWeight_tight_DeepTau_2-crossTriggerDataEfficiencyWeightDown_tight_DeepTau_2)/(crossTriggerDataEfficiencyWeight_tight_DeepTau_2*(pt_1<{ptcut})*(abs(eta_1)<1.5)+1.0*((pt_1>={ptcut})+(abs(eta_1)>=1.5))),2)+TMath::Power((crossTriggerEMBEfficiencyWeight_tight_DeepTau_2-crossTriggerEMBEfficiencyWeightDown_tight_DeepTau_2)/(crossTriggerEMBEfficiencyWeight_tight_DeepTau_2*(pt_1<{ptcut})*(abs(eta_1)<1.5)+1.0*((pt_1>={ptcut})+(abs(eta_1)>=1.5))),2)))))+((decayMode_2!={dm})*(crossTriggerDataEfficiencyWeight_tight_DeepTau_2/(crossTriggerEMBEfficiencyWeight_tight_DeepTau_2*(pt_1<{ptcut})*(abs(eta_1)<1.5)+1.0*((pt_1>={ptcut})+(abs(eta_1)>=1.5)))))))"

tau_trigger_eff_et_emb_2016 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2016Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["et"],
                                                           ptcut=_lteffCutDEra["2016"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["et"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2016Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["et"],
                                                           ptcut=_lteffCutDEra["2016"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["et"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_et_dm{dm}_2016Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["et"],
                                                           ptcut=_lteffCutDEra["2016"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["et"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_et_dm{dm}_2016Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["et"],
                                                           ptcut=_lteffCutDEra["2016"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["et"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        ]
tau_trigger_eff_et_emb_2017 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2017Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring_2017et.format(dm=dm,
                                                                  lt_eff=_lteff_exp["2017"]["et"],
                                                                  ptcut=_lteffCutDEra["2017"]["et"],
                                                                  xtrigger_leptonweight=_xtrg_lep_weight["2017"]["et"],
                                                                  operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2017Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring_2017et.format(dm=dm,
                                                                  lt_eff=_lteff_exp["2017"]["et"],
                                                                  ptcut=_lteffCutDEra["2017"]["et"],
                                                                  xtrigger_leptonweight=_xtrg_lep_weight["2017"]["et"],
                                                                  operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_et_dm{dm}_2017Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring_2017et.format(dm=dm,
                                                                  lt_eff=_lteff_exp["2017"]["et"],
                                                                  ptcut=_lteffCutDEra["2017"]["et"],
                                                                  xtrigger_leptonweight=_xtrg_lep_weight["2017"]["et"],
                                                                  operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_et_dm{dm}_2017Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring_2017et.format(dm=dm,
                                                                  lt_eff=_lteff_exp["2017"]["et"],
                                                                  ptcut=_lteffCutDEra["2017"]["et"],
                                                                  xtrigger_leptonweight=_xtrg_lep_weight["2017"]["et"],
                                                                  operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        ]
tau_trigger_eff_et_emb_2018 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2018Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["et"],
                                                           ptcut=_lteffCutDEra["2018"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["et"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_et_dm{dm}_2018Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["et"],
                                                           ptcut=_lteffCutDEra["2018"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["et"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_et_dm{dm}_2018Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["et"],
                                                           ptcut=_lteffCutDEra["2018"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["et"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_et_dm{dm}_2018Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["et"],
                                                           ptcut=_lteffCutDEra["2018"]["et"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["et"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        ]
tau_trigger_eff_mt_emb_2016 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2016Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["mt"],
                                                           ptcut=_lteffCutDEra["2016"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["mt"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2016Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["mt"],
                                                           ptcut=_lteffCutDEra["2016"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["mt"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_mt_dm{dm}_2016Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["mt"],
                                                           ptcut=_lteffCutDEra["2016"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["mt"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_mt_dm{dm}_2016Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2016"]["mt"],
                                                           ptcut=_lteffCutDEra["2016"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2016"]["mt"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        ]
tau_trigger_eff_mt_emb_2017 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2017Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2017"]["mt"],
                                                           ptcut=_lteffCutDEra["2017"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2017"]["mt"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2017Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2017"]["mt"],
                                                           ptcut=_lteffCutDEra["2017"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2017"]["mt"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_mt_dm{dm}_2017Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2017"]["mt"],
                                                           ptcut=_lteffCutDEra["2017"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2017"]["mt"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_mt_dm{dm}_2017Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2017"]["mt"],
                                                           ptcut=_lteffCutDEra["2017"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2017"]["mt"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        ]
tau_trigger_eff_mt_emb_2018 = [
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2018Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["mt"],
                                                           ptcut=_lteffCutDEra["2018"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["mt"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_mt_dm{dm}_2018Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["mt"],
                                                           ptcut=_lteffCutDEra["2018"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["mt"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_mt_dm{dm}_2018Up".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["mt"],
                                                           ptcut=_lteffCutDEra["2018"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["mt"],
                                                           operator="+"), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_xtrigger_t_emb_mt_dm{dm}_2018Down".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_trigger_wstring.format(dm=dm,
                                                           lt_eff=_lteff_exp["2018"]["mt"],
                                                           ptcut=_lteffCutDEra["2018"]["mt"],
                                                           xtrigger_leptonweight=_xtrg_lep_weight["2018"]["mt"],
                                                           operator="-"), "triggerweight")) for dm in [0, 1, 10, 11]],
        ]

_tau_tt_wstring = "(((decayMode_1=={dm})*((crossTriggerDataEfficiencyWeight_tight_DeepTau_1/crossTriggerMCEfficiencyWeight_tight_DeepTau_1)*(1{operator}TMath::Sqrt(TMath::Power((crossTriggerDataEfficiencyWeight_tight_DeepTau_1-crossTriggerDataEfficiencyWeightDown_tight_DeepTau_1)/crossTriggerDataEfficiencyWeight_tight_DeepTau_1,2)+TMath::Power((crossTriggerMCEfficiencyWeight_tight_DeepTau_1-crossTriggerMCEfficiencyWeightDown_tight_DeepTau_1)/crossTriggerMCEfficiencyWeight_tight_DeepTau_1,2))))+((decayMode_1!={dm})*(crossTriggerDataEfficiencyWeight_tight_DeepTau_1/crossTriggerMCEfficiencyWeight_tight_DeepTau_1)))*(((decayMode_2=={dm})*((crossTriggerDataEfficiencyWeight_tight_DeepTau_2/crossTriggerMCEfficiencyWeight_tight_DeepTau_2)*(1{operator}TMath::Sqrt(TMath::Power((crossTriggerDataEfficiencyWeight_tight_DeepTau_2-crossTriggerDataEfficiencyWeightDown_tight_DeepTau_2)/crossTriggerDataEfficiencyWeight_tight_DeepTau_2,2)+TMath::Power((crossTriggerMCEfficiencyWeight_tight_DeepTau_2-crossTriggerMCEfficiencyWeightDown_tight_DeepTau_2)/crossTriggerMCEfficiencyWeight_tight_DeepTau_2,2)))))+((decayMode_2!={dm})*(crossTriggerDataEfficiencyWeight_tight_DeepTau_2/crossTriggerMCEfficiencyWeight_tight_DeepTau_2))))"
tau_trigger_eff_tt = [
        *[ReplaceWeight("CMS_eff_trigger_tt_dm{dm}_EraUp".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_tt_wstring.format(operator="+", dm=dm), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_trigger_tt_dm{dm}_EraDown".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_tt_wstring.format(operator="-", dm=dm), "triggerweight")) for dm in [0, 1, 10, 11]],
        ]
tau_trigger_eff_emb_tt = [
        *[ReplaceWeight("CMS_eff_trigger_emb_tt_dm{dm}_EraUp".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_tt_wstring.replace("MC", "EMB").format(operator="+", dm=dm), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_trigger_emb_tt_dm{dm}_EraDown".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_tt_wstring.replace("MC", "EMB").format(operator="-", dm=dm), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_trigger_tt_dm{dm}_EraUp".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_tt_wstring.replace("MC", "EMB").format(operator="+", dm=dm), "triggerweight")) for dm in [0, 1, 10, 11]],
        *[ReplaceWeight("CMS_eff_trigger_tt_dm{dm}_EraDown".format(dm=dm),
                        "triggerweight",
                        Weight(_tau_tt_wstring.replace("MC", "EMB").format(operator="-", dm=dm), "triggerweight")) for dm in [0, 1, 10, 11]],
        ]

# Embedding specific variations.
emb_e_es = [
        ChangeDataset("CMS_scale_e_embUp", "eleEsUp"),
        ChangeDataset("CMS_scale_e_embDown", "eleEsDown"),
]

emb_decay_mode_eff = [
        ReplaceWeight("CMS_3ProngEff_EraUp",   "decayMode_SF", Weight("embeddedDecayModeWeight_effUp_pi0Nom", "decayMode_SF")),
        ReplaceWeight("CMS_3ProngEff_EraDown", "decayMode_SF", Weight("embeddedDecayModeWeight_effDown_pi0Nom", "decayMode_SF")),
        ReplaceWeight("CMS_1ProngPi0Eff_EraUp",   "decayMode_SF", Weight("embeddedDecayModeWeight_effNom_pi0Up", "decayMode_SF")),
        ReplaceWeight("CMS_1ProngPi0Eff_EraDown", "decayMode_SF", Weight("embeddedDecayModeWeight_effNom_pi0Down", "decayMode_SF")),
        ]

ggh_acceptance = []
for unc in [
        "THU_ggH_Mig01", "THU_ggH_Mig12", "THU_ggH_Mu", "THU_ggH_PT120",
        "THU_ggH_PT60", "THU_ggH_Res", "THU_ggH_VBF2j", "THU_ggH_VBF3j",
        "THU_ggH_qmtop"]:
    ggh_acceptance.append(AddWeight(unc + "Up", Weight("({})".format(unc), "{}_weight".format(unc))))
    ggh_acceptance.append(AddWeight(unc + "Down", Weight("(2.0-{})".format(unc), "{}_weight".format(unc))))

qqh_acceptance = []
for unc in ["THU_qqH_25", "THU_qqH_JET01", "THU_qqH_Mjj1000", "THU_qqH_Mjj120",
            "THU_qqH_Mjj1500", "THU_qqH_Mjj350", "THU_qqH_Mjj60", "THU_qqH_Mjj700",
            "THU_qqH_PTH200", "THU_qqH_TOT"]:
    qqh_acceptance.append(AddWeight(unc + "Up", Weight("({})".format(unc), "{}_weight".format(unc))))
    qqh_acceptance.append(AddWeight(unc + "Down", Weight("(2.0-{})".format(unc), "{}_weight".format(unc))))


prefiring = [
        ReplaceWeight("CMS_prefiringUp", "prefireWeight", Weight("prefiringweightup", "prefireWeight")),
        ReplaceWeight("CMS_prefiringDown", "prefireWeight", Weight("prefiringweightdown", "prefireWeight")),
]

zpt = [
        SquareWeight("CMS_htt_dyShape_EraUp", "zPtReweightWeight"),
        RemoveWeight("CMS_htt_dyShape_EraDown", "zPtReweightWeight")
        ]

top_pt = [
        SquareWeight("CMS_htt_ttbarShapeUp", "topPtReweightWeight"),
        RemoveWeight("CMS_htt_ttbarShapeDown", "topPtReweightWeight")
        ]

_ff_variations_lt = [
                     "ff_qcd_mvis_{ch}{era}{shift}",
                     "ff_qcd_mvis_osss_{ch}{era}{shift}",
                     "ff_corr_qcd_mvis_{ch}{era}{shift}",
                     "ff_corr_qcd_mvis_osss_{ch}{era}{shift}",

                     "ff_qcd_muiso_{ch}{era}{shift}",
                     "ff_corr_qcd_muiso_{ch}{era}{shift}",

                     "ff_qcd_dr0_njet0_morphed_stat_{ch}{era}{shift}",
                     "ff_qcd_dr0_njet1_morphed_stat_{ch}{era}{shift}",
                     "ff_qcd_dr0_njet2_morphed_stat_{ch}{era}{shift}",

                     "ff_qcd_dr0_njet0_stat_{ch}{era}{shift}",
                     "ff_qcd_dr0_njet1_stat_{ch}{era}{shift}",
                     "ff_qcd_dr0_njet2_stat_{ch}{era}{shift}",

                     "ff_qcd_mc_{ch}{era}{shift}",

                     "ff_qcd_syst_{ch}{era}{shift}",

                     "ff_w_lepPt_{ch}{era}{shift}",
                     "ff_corr_w_lepPt_{ch}{era}{shift}",

                     "ff_corr_w_mt_{ch}{era}{shift}",
                     "ff_w_mt_{ch}{era}{shift}",

                     "ff_w_syst_{ch}{era}{shift}",

                     "ff_w_dr0_njet0_morphed_stat_{ch}{era}{shift}",
                     "ff_w_dr0_njet1_morphed_stat_{ch}{era}{shift}",
                     "ff_w_dr0_njet2_morphed_stat_{ch}{era}{shift}",
                     "ff_w_dr1_njet0_morphed_stat_{ch}{era}{shift}",
                     "ff_w_dr1_njet1_morphed_stat_{ch}{era}{shift}",
                     "ff_w_dr1_njet2_morphed_stat_{ch}{era}{shift}",

                     "ff_w_dr0_njet0_stat_{ch}{era}{shift}",
                     "ff_w_dr0_njet1_stat_{ch}{era}{shift}",
                     "ff_w_dr0_njet2_stat_{ch}{era}{shift}",
                     "ff_w_dr1_njet0_stat_{ch}{era}{shift}",
                     "ff_w_dr1_njet1_stat_{ch}{era}{shift}",
                     "ff_w_dr1_njet2_stat_{ch}{era}{shift}",

                     "ff_w_mc_{ch}{era}{shift}",

                     "ff_frac_w_{ch}{era}{shift}",

                     "ff_corr_tt_syst_{ch}{era}{shift}",
                     "ff_tt_morphed_{ch}{era}{shift}",
                     "ff_tt_sf_{ch}{era}{shift}",

                     "ff_tt_dr0_njet0_morphed_stat_{ch}{era}{shift}",
                     "ff_tt_dr0_njet1_morphed_stat_{ch}{era}{shift}",

                     "ff_tt_stat_{ch}{era}{shift}",
]
#  Variations on the jet backgrounds estimated with the fake factor method.
ff_variations_lt = [
        ReplaceCutAndAddWeight("anti_iso_CMS_{syst}".format(syst=syst.format(shift=shift.capitalize(), era="Era", ch="Channel_").replace("w_dr0", "w_lowdR").replace("w_dr1", "w_highdR").replace("_dr0", "")), "tau_iso",
                               Cut("byTightDeepTau2017v2p1VSjet_2<0.5&&byVLooseDeepTau2017v2p1VSjet_2>0.5", "tau_anti_iso"),
                               Weight("ff2_{syst}".format(syst=syst.format(shift=shift, era="", ch="")), "fake_factor")
                               ) for shift in ["up", "down"] for syst in _ff_variations_lt
        ]

ff_variations_tt = [
        ReplaceCutAndAddWeight("anti_iso_CMS_{syst}".format(syst=syst.format(shift=shift.capitalize(), era="_Era", ch="_tt").replace("dr0_", "")), "tau_iso",
                               Cut("(byTightDeepTau2017v2p1VSjet_2>0.5&&byTightDeepTau2017v2p1VSjet_1<0.5&&byVLooseDeepTau2017v2p1VSjet_1>0.5)||(byTightDeepTau2017v2p1VSjet_1>0.5&&byTightDeepTau2017v2p1VSjet_2<0.5&&byVLooseDeepTau2017v2p1VSjet_2>0.5)", "tau_anti_iso"),
                               Weight("(0.5*ff1_{syst}*(byTightDeepTau2017v2p1VSjet_1<0.5)+0.5*ff2_{syst}*(byTightDeepTau2017v2p1VSjet_2<0.5))".format(syst=syst.format(shift="_"+shift, era="", ch="")), "fake_factor")
                               ) for shift in ["up", "down"] for syst in ["ff_qcd_dr0_njet0_morphed_stat{ch}{era}{shift}",
                                                                          "ff_qcd_dr0_njet1_morphed_stat{ch}{era}{shift}",
                                                                          "ff_qcd_dr0_njet2_morphed_stat{ch}{era}{shift}",

                                                                          "ff_qcd_dr0_njet0_stat{ch}{era}{shift}",
                                                                          "ff_qcd_dr0_njet1_stat{ch}{era}{shift}",
                                                                          "ff_qcd_dr0_njet2_stat{ch}{era}{shift}",

                                                                          "ff_qcd_syst{ch}{era}{shift}",

                                                                          "ff_qcd_mvis{ch}{era}{shift}",
                                                                          "ff_qcd_mvis_osss{ch}{era}{shift}",
                                                                          "ff_corr_qcd_mvis{ch}{era}{shift}",
                                                                          "ff_corr_qcd_mvis_osss{ch}{era}{shift}",

                                                                          "ff_qcd_tau2_pt{ch}{era}{shift}",
                                                                          "ff_corr_qcd_tau2_pt{ch}{era}{shift}",

                                                                          "ff_qcd_mc{ch}{era}{shift}",

                                                                          "ff_w_syst{ch}{era}{shift}",
                                                                          "ff_tt_syst{ch}{era}{shift}",
                                                                          ]
        ]

qcd_variations_em = [
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_0jet_rate_EraUp",    "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_0jet_rateup_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_0jet_rate_EraDown",  "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_0jet_ratedown_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_0jet_shape_EraUp",   "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_0jet_shapeup_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_0jet_shape_EraDown", "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_0jet_shapedown_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_0jet_shape2_EraUp",   "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_0jet_shape2up_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_0jet_shape2_EraDown", "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_0jet_shape2down_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_1jet_rate_EraUp",    "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_1jet_rateup_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_1jet_rate_EraDown",  "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_1jet_ratedown_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_1jet_shape_EraUp",   "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_1jet_shapeup_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_1jet_shape_EraDown", "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_1jet_shapedown_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_1jet_shape2_EraUp",   "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_1jet_shape2up_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_1jet_shape2_EraDown", "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_1jet_shape2down_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_2jet_rate_EraUp",    "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_2jet_rateup_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_2jet_rate_EraDown",  "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_2jet_ratedown_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_2jet_shape_EraUp",   "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_2jet_shapeup_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_2jet_shape_EraDown", "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_2jet_shapedown_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_2jet_shape2_EraUp",   "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_2jet_shape2up_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_2jet_shape2_EraDown", "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_osss_stat_2jet_shape2down_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_iso_EraUp",               "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_extrap_up_Weight", "qcd_weight")),
        ReplaceCutAndAddWeight("same_sign_CMS_htt_qcd_iso_EraDown",             "os", Cut("q_1*q_2>0", "ss"), Weight("em_qcd_extrap_down_Weight", "qcd_weight")),
        ]
