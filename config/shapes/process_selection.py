from ntuple_processor.utils import Selection


"""Base processes

List of base processes, mostly containing only weights:
    - triggerweight
    - triggerweight_emb
    - tau_by_iso_id_weight
    - ele_hlt_Z_vtx_weight
    - ele_reco_weight
    - aiso_muon_correction
    - lumi_weight
    - MC_base_process_selection
    - DY_base_process_selection
    - TT_process_selection
    - VV_process_selection
    - W_process_selection
    - HTT_base_process_selection
    - HTT_process_selection
    - HWW_process_selection
"""
def triggerweight(channel, era, vs_jet_wp, vs_ele_wp):
    weight = ("1.0", "triggerweight")

    # General definitions of weights valid for all eras and channels
    if "mt" in channel:
        weight = ("mtau_triggerweight_ic", "triggerweight")
    elif "et" in channel:
        weight = ("etau_triggerweight_ic", "triggerweight")
    elif "tt" in channel:
        weight = ("tautau_triggerweight_ic", "triggerweight")
    elif "em" in channel:
        ElMuData = "(trigger_23_data_Weight_2*trigger_12_data_Weight_1*(trg_muonelectron_mu23ele12==1)+trigger_23_data_Weight_1*trigger_8_data_Weight_2*(trg_muonelectron_mu8ele23==1) - trigger_23_data_Weight_2*trigger_23_data_Weight_1*(trg_muonelectron_mu8ele23==1 && trg_muonelectron_mu23ele12==1))"
        ElMuEmb = ElMuData.replace("data", "mc")
        ElMu = "(" + ElMuData + ")/(" + ElMuEmb + ")"
        weight = (ElMu, "triggerweight")

    # In previous software only used in 2017 and 2018. Before usage in 2016 check if the weight is valid.
    elif "mm" in channel:
        weight = (
            "singleTriggerDataEfficiencyWeightKIT_1/singleTriggerMCEfficiencyWeightKIT_1",
            "trigger_lepton_sf",
        )

    return weight


def triggerweight_emb(channel, era, vs_jet_wp, vs_ele_wp):
    weight = ("1.0", "triggerweight")
    if "mt" in channel:
        weight = ("mtau_triggerweight_ic", "triggerweight")
    elif "et" in channel:
        weight = ("etau_triggerweight_ic", "triggerweight")
    elif "tt" in channel:
        weight = ("tautau_triggerweight_ic", "triggerweight")
    elif "em" in channel:
        ElMuData = "(trigger_23_data_Weight_2*trigger_12_data_Weight_1*(trg_muonelectron_mu23ele12==1)+trigger_23_data_Weight_1*trigger_8_data_Weight_2*(trg_muonelectron_mu8ele23==1) - trigger_23_data_Weight_2*trigger_23_data_Weight_1*(trg_muonelectron_mu8ele23==1 && trg_muonelectron_mu23ele12==1))"
        ElMuEmb = ElMuData.replace("data", "embed")
        ElMu = "(" + ElMuData + ")/(" + ElMuEmb + ")"
        weight = (ElMu, "triggerweight")
    return weight


def fakemetweight_emb(channel, era, vs_jet_wp, vs_ele_wp):
    weightmap = {
        "2016": {
            "et": "1.005",
            "mt": "1.005",
            "tt": "1.008",
        },
        "2017": {
            "et": "1.005",
            "mt": "1.005",
            "tt": "1.010",
        },
        "2018": {
            "et": "1.005",
            "mt": "1.005",
            "tt": "1.010",
        },
    }
    weight = (weightmap[era][channel], "fakemetweight")
    return weight


def tau_by_iso_id_weight(channel):
    weight = ("1.0", "taubyIsoIdWeight")
    if "mt" in channel or "et" in channel:
        weight = (
            "((pt_2<100)*((gen_match_2==5)*tauIDScaleFactorWeight_medium_DeepTau2017v2p1VSjet_2 + (gen_match_2!=5))"
            "+ (pt_2>=100)*((gen_match_2==5)*tauIDScaleFactorWeight_highpt_deeptauid_2 + (gen_match_2!=5)))",
            "taubyIsoIdWeight",
        )
    elif "tt" in channel:
        weight = (
            "((pt_1<100)*(((gen_match_1==5)*tauIDScaleFactorWeight_medium_DeepTau2017v2p1VSjet_1 + (gen_match_1!=5))*((gen_match_2==5)*tauIDScaleFactorWeight_medium_DeepTau2017v2p1VSjet_2 + (gen_match_2!=5)))"
            "+ (pt_1>=100)*(pt_2<100)*(((gen_match_1==5)*tauIDScaleFactorWeight_highpt_deeptauid_1 + (gen_match_1!=5))*((gen_match_2==5)*tauIDScaleFactorWeight_medium_DeepTau2017v2p1VSjet_2 + (gen_match_2!=5)))"
            "+ (pt_2>=100)*(((gen_match_1==5)*tauIDScaleFactorWeight_highpt_deeptauid_1 + (gen_match_1!=5))*((gen_match_2==5)*tauIDScaleFactorWeight_highpt_deeptauid_2 + (gen_match_2!=5))))",
            "taubyIsoIdWeight",
        )
    return weight


def ele_hlt_Z_vtx_weight(channel, era, vs_jet_wp, vs_ele_wp):
    weight = ("1.0", "eleHLTZvtxWeight")
    if "et" in channel and era == "2017":
        weight = (
            "(trg_singleelectron_35 || trg_singleelectron_32 || trg_singleelectron_27 || trg_crossele_ele24tau30)*0.991 + (!(trg_singleelectron_35 || trg_singleelectron_32 || trg_singleelectron_27 || trg_crossele_ele24tau30))*1.0",
            "eleHLTZvtxWeight",
        )
    return weight


def ele_reco_weight(channel, era, vs_jet_wp, vs_ele_wp):
    if channel in ["et", "em"] and era == "2016":
        weight = ("eleRecoWeight_1", "eleRecoWeight")
    else:
        weight = ("1.0", "eleRecoWeight")
    return weight


def aiso_muon_correction(channel, era, vs_jet_wp, vs_ele_wp):
    if "em" in channel and "2016" in era:
        weight = (
            "(iso_2 <= 0.15)*1.0+((iso_2 > 0.15 && iso_2 < 0.20)*(((abs(eta_2) > 0 && abs(eta_2) < 0.9)*(((pt_2 > 10.0 && pt_2 < 15.0)*0.9327831343)+((pt_2 > 15.0 && pt_2 < 20.0)*0.953716709495)+((pt_2 > 20.0 && pt_2 < 22.0)*0.970107931338)+((pt_2 > 22.0 && pt_2 < 24.0)*0.975194707069)+((pt_2 > 24.0 && pt_2 < 26.0)*0.987926954702)+((pt_2 > 26.0 && pt_2 < 28.0)*0.984899759186)+((pt_2 > 28.0 && pt_2 < 30.0)*0.98461236424)+((pt_2 > 30.0 && pt_2 < 32.0)*0.982678110647)+((pt_2 > 32.0 && pt_2 < 34.0)*0.969564600424)+((pt_2 > 34.0 && pt_2 < 36.0)*0.952545963996)+((pt_2 > 36.0 && pt_2 < 38.0)*0.93801027736)+((pt_2 > 38.0 && pt_2 < 40.0)*0.928180181431)+((pt_2 > 40.0 && pt_2 < 45.0)*0.936587036212)+((pt_2 > 45.0 && pt_2 < 50.0)*0.937996645301)+((pt_2 > 50.0 && pt_2 < 60.0)*0.906087339587)+((pt_2 > 60.0 && pt_2 < 80.0)*0.887611582681)+((pt_2 > 80.0 && pt_2 < 100.0)*0.8834356199)+((pt_2 > 100.0 && pt_2 < 200.0)*1.17717912783)+((pt_2 > 200.0)*0.782070939337)))+((abs(eta_2) > 0.9 && abs(eta_2) < 1.2)*(((pt_2 > 10.0 && pt_2 < 15.0)*0.886291162409)+((pt_2 > 15.0 && pt_2 < 20.0)*0.915805873893)+((pt_2 > 20.0 && pt_2 < 22.0)*0.928213984488)+((pt_2 > 22.0 && pt_2 < 24.0)*0.968808738285)+((pt_2 > 24.0 && pt_2 < 26.0)*1.00847685497)+((pt_2 > 26.0 && pt_2 < 28.0)*1.01823133239)+((pt_2 > 28.0 && pt_2 < 30.0)*0.992528525978)+((pt_2 > 30.0 && pt_2 < 32.0)*0.978795541905)+((pt_2 > 32.0 && pt_2 < 34.0)*0.942964386045)+((pt_2 > 34.0 && pt_2 < 36.0)*0.938710844744)+((pt_2 > 36.0 && pt_2 < 38.0)*0.922702562159)+((pt_2 > 38.0 && pt_2 < 40.0)*0.897758415445)+((pt_2 > 40.0 && pt_2 < 45.0)*0.909162491)+((pt_2 > 45.0 && pt_2 < 50.0)*0.90265167858)+((pt_2 > 50.0 && pt_2 < 60.0)*0.912325787246)+((pt_2 > 60.0 && pt_2 < 80.0)*0.897018870572)+((pt_2 > 80.0 && pt_2 < 100.0)*0.972647372742)+((pt_2 > 100.0 && pt_2 < 200.0)*1.38562213225)+((pt_2 > 200.0)*0.738304282781)))+((abs(eta_2) > 1.2 && abs(eta_2) < 2.1)*(((pt_2 > 10.0 && pt_2 < 15.0)*0.88678133381)+((pt_2 > 15.0 && pt_2 < 20.0)*0.855042730357)+((pt_2 > 20.0 && pt_2 < 22.0)*0.897842682768)+((pt_2 > 22.0 && pt_2 < 24.0)*0.905849165918)+((pt_2 > 24.0 && pt_2 < 26.0)*0.910626040493)+((pt_2 > 26.0 && pt_2 < 28.0)*0.952076550342)+((pt_2 > 28.0 && pt_2 < 30.0)*0.968869527514)+((pt_2 > 30.0 && pt_2 < 32.0)*0.942569376345)+((pt_2 > 32.0 && pt_2 < 34.0)*0.941205386066)+((pt_2 > 34.0 && pt_2 < 36.0)*0.925500794627)+((pt_2 > 36.0 && pt_2 < 38.0)*0.907300484346)+((pt_2 > 38.0 && pt_2 < 40.0)*0.87984390364)+((pt_2 > 40.0 && pt_2 < 45.0)*0.87339713294)+((pt_2 > 45.0 && pt_2 < 50.0)*0.87980130335)+((pt_2 > 50.0 && pt_2 < 60.0)*0.860066115116)+((pt_2 > 60.0 && pt_2 < 80.0)*0.857712710727)+((pt_2 > 80.0 && pt_2 < 100.0)*1.0645948221)+((pt_2 > 100.0 && pt_2 < 200.0)*1.18849162977)+((pt_2 > 200.0)*1.28784467602)))+((abs(eta_2) > 2.1 && abs(eta_2) < 2.4)*(((pt_2 > 10.0 && pt_2 < 15.0)*0.776167258269)+((pt_2 > 15.0 && pt_2 < 20.0)*0.770868349402)+((pt_2 > 20.0 && pt_2 < 22.0)*0.808779663589)+((pt_2 > 22.0 && pt_2 < 24.0)*0.812754474056)+((pt_2 > 24.0 && pt_2 < 26.0)*0.84667222665)+((pt_2 > 26.0 && pt_2 < 28.0)*0.837142139899)+((pt_2 > 28.0 && pt_2 < 30.0)*0.8356560823)+((pt_2 > 30.0 && pt_2 < 32.0)*0.888386540505)+((pt_2 > 32.0 && pt_2 < 34.0)*0.881083238091)+((pt_2 > 34.0 && pt_2 < 36.0)*0.872500048844)+((pt_2 > 36.0 && pt_2 < 38.0)*0.861737355714)+((pt_2 > 38.0 && pt_2 < 40.0)*0.872186406375)+((pt_2 > 40.0 && pt_2 < 45.0)*0.853060222605)+((pt_2 > 45.0 && pt_2 < 50.0)*0.927735148085)+((pt_2 > 50.0 && pt_2 < 60.0)*0.82749753618)+((pt_2 > 60.0 && pt_2 < 80.0)*0.924329437022)+((pt_2 > 80.0 && pt_2 < 100.0)*0.887073323216)+((pt_2 > 100.0 && pt_2 < 200.0)*1.15559449916)+((pt_2 > 200.0)*0.37887229649)))))",
            "m_aiso_correction",
        )
    else:
        weight = ("1.0", "m_aiso_correction")
    return weight


def lumi_weight(era):
    if era == "2016preVFP":
        lumi = "19.5"  # "36.326450080"
    elif era == "2016postVFP":
        lumi = "16.8"
    elif era == "2017":
        lumi = "41.529"
    elif era == "2018":
        lumi = "59.83"
    else:
        raise ValueError("Given era {} not defined.".format(era))
    return ("{} * 1000.0".format(lumi), "lumi")


def prefiring_weight(era):
    if era in ["2016postVFP", "2016preVFP", "2017"]:
        weight = ("prefiring_wgt", "prefireWeight")
    else:
        weight = ("1.0", "prefireWeight")
    return weight


def MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    wps_dict = [

        "VVTight",
        "VVTight",
        "Tight",
        "Medium",
        "Loose",
        "VLoose",
        "VVLoose",
        "VVVLoose",
    ]

    if vs_ele_wp not in wps_dict:
        print("This vs electron working point doen't exist. Please specify the correct vsEle discriminator ")
    if vs_jet_wp not in wps_dict:
        print("This vs jet working point doen't exist. Please specify the correct vsJet discriminator ")
    vs_ele_discr = vs_ele_wp
    vs_jet_discr = vs_jet_wp
    if channel == "em":
        isoweight = ("iso_wgt_ele_1 * iso_wgt_ele_2", "isoweight")
        idweight = ("id_wgt_ele_1 * id_wgt_ele_2", "idweight")
        tauidweight = None
        vsmu_weight = None
        vsele_weight = None
        trgweight = None
    elif channel == "et":
        isoweight = ("iso_wgt_ele_1", "isoweight")
        idweight = ("id_wgt_ele_1", "idweight")
        tauidweight = (
            "((gen_match_2==5)*id_wgt_tau_vsJet_Tight_2 + (gen_match_2!=5))",
            "taubyIsoIdWeight",
        )
        vsmu_weight = ("id_wgt_tau_vsMu_VLoose_2", "vsmuweight")
        vsele_weight = ("id_wgt_tau_vsEle_Tight_2", "vseleweight")
        if era == "2017":
            trgweight = (
                "((pt_1>=33&&pt_1<36)*trg_wgt_single_ele32)+((pt_1>=36)*trg_wgt_single_ele35)",
                "trgweight",
            )
        else:
            trgweight = ("trg_wgt_single_ele32orele35", "trgweight")
    elif channel == "mt":
        isoweight = ("iso_wgt_mu_1", "isoweight")
        idweight = ("id_wgt_mu_1", "idweight")
        tauidweight = (
            "((gen_match_2==5)*id_wgt_tau_vsJet_"+vs_jet_discr+"_2 + (gen_match_2!=5))",
            "taubyIsoIdWeight",
        )
        # tauidweight = None
        vsmu_weight = ("id_wgt_tau_vsMu_Tight_2", "vsmuweight")
        vsele_weight = ("id_wgt_tau_vsEle_"+vs_ele_discr+"_2", "vseleweight")
        if era == "2016preVFP" or era == "2016postVFP":
            trgweight = ("((pt_1>23)* trg_wgt_single_mu22)", "trgweight")
        elif era == "2017":
            trgweight = ("((pt_1>28)* trg_wgt_single_mu27)", "trgweight")
        else:
            trgweight = (
                "((pt_1>=25 && pt_1<28)* trg_wgt_single_mu24) + ((pt_1>28)* trg_wgt_single_mu27)",
                "trgweight",
            )
    elif channel == "tt":
        isoweight = None
        idweight = None
        tauidweight = (
            "((gen_match_1==5)*id_wgt_tau_vsJet_Tight_1 + (gen_match_1!=5)) * ((gen_match_2==5)*id_wgt_tau_vsJet_Tight_2 + (gen_match_2!=5))",
            "taubyIsoIdWeight",
        )
        vsmu_weight = (
            "((gen_match_1==5)*id_wgt_tau_vsMu_VLoose_1 + (gen_match_1!=5)) * ((gen_match_2==5)*id_wgt_tau_vsMu_VLoose_1 + (gen_match_2!=5))",
            "vsmuweight",
        )
        vsele_weight = (
            "((gen_match_1==5)*id_wgt_tau_vsEle_VVLoose_1 + (gen_match_1!=5)) * ((gen_match_2==5)*id_wgt_tau_vsEle_VVLoose_1 + (gen_match_2!=5))",
            "vseleweight",
        )
        trgweight = None
    elif channel == "mm":
        isoweight = ("iso_wgt_mu_1 * iso_wgt_mu_2", "isoweight")
        idweight = ("id_wgt_mu_1 * id_wgt_mu_2", "idweight")
        tauidweight = None
        vsmu_weight = None
        vsele_weight = None
        if era == "2017":
            trgweight = ("trg_wgt_single_mu27", "trgweight")
        elif era == "2018":
            trgweight = ("1", "trgweight")
        elif era == "2016postVFP" or era == "2016preVFP":
            trgweight = ("trg_wgt_single_mu22", "trgweight")
    elif channel == "ee":
        isoweight = ("iso_wgt_ele_1 * iso_wgt_ele_2", "isoweight")
        idweight = ("id_wgt_ele_1 * id_wgt_ele_2", "idweight")
        tauidweight = None
        vsmu_weight = None
        vsele_weight = None
        if era == "2017":
            trgweight = ("trg_wgt_single_ele35", "trgweight")
        elif era == "2018":
            trgweight = ("trg_wgt_single_ele35", "trgweight")
        elif era in ["2016postVFP", "2016preVFP"]:
            trgweight = ("trg_wgt_single_ele25", "trgweight")
    else:
        raise ValueError("Given channel {} not defined.".format(channel))
    MC_base_process_weights = [
        ("puweight", "puweight"),
        isoweight,
        idweight,
        tauidweight,
        vsmu_weight,
        vsele_weight,
        trgweight,
        lumi_weight(era),
        prefiring_weight(era),
    ]
    if channel != "mm" and channel != "mt":
        MC_base_process_weights.append(("btag_weight", "btagWeight"))
    return Selection(
        name="MC base",
        weights=[weight for weight in MC_base_process_weights if weight is not None],
    )


def dy_stitching_weight(era):
    if era == "2017":
        weight = (
            "((genbosonmass >= 50.0)*0.0000298298*((npartons == 0 || npartons >= 5)*1.0 + (npartons == 1)*0.3478960398 + (npartons == 2)*0.2909516577 + (npartons == 3)*0.1397995594 + (npartons == 4)*0.1257217076) + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)",
            "dy_stitching_weight",
        )
        # xsec_NNLO [pb] = , N_inclusive = 203,729,540, xsec_NNLO/N_inclusive = 0.0000298298 [pb], weights: [1.0, 0.3478960398, 0.2909516577, 0.1397995594, 0.1257217076]
    elif era == "2018":
        weight = (
            "((genbosonmass >= 50.0)*0.0000606542*((npartons == 0 || npartons >= 5)*1.0 + (npartons == 1)*0.194267667208 + (npartons == 2)*0.21727746547 + (npartons == 3)*0.26760465744 + (npartons == 4)*0.294078683662) + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)",
            "dy_stitching_weight",
        )
        # xsec_NNLO [pb] = 2025.74*3, N_inclusive = 100194597,  xsec_NNLO/N_inclusive = 0.0000606542 [pb] weights: [1.0, 0.194267667208, 0.21727746547, 0.26760465744, 0.294078683662]
    else:
        raise ValueError("DY stitching weight not defined for era {}".format(era))

    return weight


def DY_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    DY_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    if era == "2017":
        gen_events_weight = (
            "(1./203729540)*(genbosonmass >= 50.0) + (genbosonmass < 50.0)*numberGeneratedEventsWeight",
            "numberGeneratedEventsWeight",
        )
    elif era == "2018":
        gen_events_weight = (
            "numberGeneratedEventsWeight",
            "numberGeneratedEventsWeight",
        )
    elif era in ["2016preVFP", "2016postVFP"]:
        gen_events_weight = (
            "numberGeneratedEventsWeight",
            "numberGeneratedEventsWeight",
        )
    DY_process_weights.extend(
        [
            gen_events_weight,
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
            # dy_stitching_weight(era),  # TODO add stitching weight
            ("ZPtMassReweightWeight", "zPtReweightWeight"),
        ]
    )
    return Selection(name="DY", weights=DY_process_weights)


def DY_NLO_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    DY_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    DY_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
            # dy_stitching_weight(era),  # TODO add stitching weight
            # ("ZPtMassReweightWeight", "zPtReweightWeight"),
        ]
    )
    return Selection(name="DY_NLO", weights=DY_process_weights)


def TT_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    TT_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    TT_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
            ("topPtReweightWeight", "topPtReweightWeight"),
        ]
    )
    return Selection(name="TT", weights=TT_process_weights)


def VV_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    VV_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    VV_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
        ]
    )
    return Selection(name="VV", weights=VV_process_weights)


def W_stitching_weight(era):
    if era == "2018":
        weight = (
            "((0.0008662455*((npartons <= 0 || npartons >= 5)*1.0 + (npartons == 1)*0.174101755934 + (npartons == 2)*0.136212630745 + (npartons == 3)*0.0815667415121 + (npartons == 4)*0.06721295702670023)) * (genbosonmass>=0.0) + numberGeneratedEventsWeight * crossSectionPerEventWeight * (genbosonmass<0.0))",
            "wj_stitching_weight",
        )
        # xsec_NNLO [pb] = 61526.7, N_inclusive = 71026861, xsec_NNLO/N_inclusive = 0.0008662455 [pb] weights: [1.0, 0.1741017559343336, 0.13621263074538312, 0.08156674151214884, 0.06721295702670023]
    else:
        raise ValueError("DY stitching weight not defined for era {}".format(era))
    return weight


def W_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    W_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    W_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
        ]
    )
    # W_process_weights.append(W_stitching_weight(era)) # TODO add W stitching weight in when npartons is available
    return Selection(name="W", weights=W_process_weights)


def HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    return Selection(
        name="HTT_base", weights=MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    )


def HTT_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    HTT_weights = HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        (
            "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
            "crossSectionPerEventWeight",
        ),
    ]
    return Selection(name="HTT", weights=HTT_weights)


# This could eventually be used for all HWW estimations if necessary. At the moment this is not possible due to wrong cross section weights in 2018.
# If the additional processes are required new functions would need to be implemented.
def HWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    HWW_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    HWW_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
        ]
    )
    return Selection(name="HWW", weights=HWW_process_weights)


def HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    HWW_base_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        (
            "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
            "crossSectionPerEventWeight",
        ),
    ]
    return Selection(name="HTT", weights=HWW_base_process_weights)


"""Built-on-top processes

List of other processes meant to be put on top of base processes:
    - DY_process_selection
    - DY_nlo_process_selection
    - ZTT_process_selection
    - ZTT_nlo_process_selection
    - ZTT_embedded_process_selection
    - ZL_process_selection
    - ZL_nlo_process_selection
    - ZJ_process_selection
    - ZJ_nlo_process_selection
    - TTT_process_selection
    - TTL_process_selection
    - TTJ_process_selection
    - VVT_process_selection
    - VVJ_process_selection
    - VVL_process_selection
    - VH_process_selection
    - WH_process_selection
    - ZH_process_selection
    - ttH_process_selection
    - ggH125_process_selection
    - qqH125_process_selection
    - ggHWW_process_selection
    - qqHWW_process_selection
    - ZHWW_process_selection
    - WHWW_process_selection
    - SUSYqqH_process_selection
    - SUSYbbH_process_selection
"""


# def DY_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
#     DY_process_weights = DY_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
#     DY_process_weights.append((
#         "((genbosonmass >= 50.0)*6.2139e-05*((npartons == 0 || npartons >= 5)*1.0 + (npartons == 1)*0.1743 + (npartons == 2)*0.3556 + (npartons == 3)*0.2273 + (npartons == 4)*0.2104) + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)","z_stitching_weight"))
#     return Selection(name = "DY",
#                      weights = DY_process_weights)


def DY_nlo_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    DY_nlo_process_weights = DY_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    DY_nlo_process_weights.append(
        (
            "((genbosonmass >= 50.0) * 2.8982e-05 + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)",
            "z_stitching_weight",
        )
    )
    return Selection(name="DY_nlo", weights=DY_nlo_process_weights)


def ZTT_process_selection(channel):
    tt_cut = __get_ZTT_cut(channel)
    return Selection(name="ZTT", cuts=[(tt_cut, "ztt_cut")])


def ZTT_nlo_process_selection(channel):
    tt_cut = __get_ZTT_cut(channel)
    return Selection(name="ZTT_nlo", cuts=[(tt_cut, "ztt_cut")])


def __get_ZTT_cut(channel):
    if "mt" in channel:
        return "gen_match_1==4 && gen_match_2==5"
    elif "et" in channel:
        return "gen_match_1==3 && gen_match_2==5"
    elif "tt" in channel:
        return "gen_match_1==5 && gen_match_2==5"
    elif "em" in channel:
        return "gen_match_1==3 && gen_match_2==4"
    elif "mm" in channel:
        return "gen_match_1==4 && gen_match_2==4"
    elif "ee" in channel:
        return "gen_match_1==3 && gen_match_2==3"


def ZTT_embedded_process_selection(channel, era, apply_wps, vs_jet_wp):
    wps_dict = [

        "VVTight",
        "VVTight",
        "Tight",
        "Medium",
        "Loose",
        "VLoose",
        "VVLoose",
        "VVVLoose",
    ]

    if vs_jet_wp not in wps_dict:
        print("This vs jet working point doen't exist. Please specify the correct vsJet discriminator ")
    vs_jet_discr = vs_jet_wp
    ztt_embedded_weights = [
        ("emb_genweight", "emb_genweight"),
        ("emb_idsel_wgt_1*emb_idsel_wgt_2*emb_triggersel_wgt", "emb_selection_weight"),
    ]
    if "mt" in channel:
        if era == "2017":
            ztt_embedded_weights.extend(
                [
                    ("gen_match_1==4 && gen_match_2==5", "emb_veto"),
                    ("iso_wgt_mu_1", "isoweight"),
                    ("id_wgt_mu_1", "idweight"),
                    ("((pt_1>28)* trg_wgt_single_mu27)", "trgweight"),
                ]
            )
            if apply_wps:
                ztt_embedded_weights.extend(
                [
                    ("((gen_match_2==5)*id_wgt_tau_vsJet_"+vs_jet_discr+"_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                ]
                )
            if not apply_wps:
                pass
        elif era == "2018":
            ztt_embedded_weights.extend(
                [
                    ("gen_match_1==4 && gen_match_2==5", "emb_veto"),
                    ("iso_wgt_mu_1", "isoweight"),
                    ("id_wgt_mu_1", "idweight"),
                    (
                        "((pt_1>=25 && pt_1<28) * trg_wgt_single_mu24) + ((pt_1>28)* trg_wgt_single_mu27)",
                        "trgweight",
                    ),
                ]
            )
            if apply_wps:
                ztt_embedded_weights.extend(
                [
                    ("((gen_match_2==5)*id_wgt_tau_vsJet_"+vs_jet_discr+"_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                ]
                )
            if not apply_wps:
                pass
        elif era == "2016preVFP" or era == "2016postVFP":
            ztt_embedded_weights.extend(
                [
                    ("gen_match_1==4 && gen_match_2==5", "emb_veto"),
                    ("iso_wgt_mu_1", "isoweight"),
                    ("id_wgt_mu_1", "idweight"),
                    (
                        "((pt_1>=23) * trg_wgt_single_mu22)",
                        "trgweight",
                    ),
                ]
            )
            if apply_wps:
                ztt_embedded_weights.extend(
                [
                    ("((gen_match_2==5)*id_wgt_tau_vsJet_"+vs_jet_discr+"_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                ]
                )
            if not apply_wps:
                pass
        else:
            raise ValueError(
                f"Embedded process selection for given era {era} not yet implemented"
            )
    elif "et" in channel:
        if era == "2017":
            ztt_embedded_weights.extend(
                [
                    ("gen_match_1==3 && gen_match_2==5", "emb_veto"),
                    ("iso_wgt_ele_1", "isoweight"),
                    ("id_wgt_ele_1", "idweight"),
                    # ("trg_wgt_single_ele35", "trgweight"),
                    (
                        "((pt_1>=33&&pt_1<36)*trg_wgt_single_ele32)+((pt_1>=36)*trg_wgt_single_ele35)",
                        "trgweight",
                    ),
                    # ("((gen_match_2==5)*id_wgt_tau_vsJet_Tight_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                ]
            )
            if apply_wps:
                ztt_embedded_weights.extend(
                [
                    ("((gen_match_2==5)*id_wgt_tau_vsJet_"+vs_jet_discr+"_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                ]
                )
            if not apply_wps:
                pass
        elif era == "2018":
            ztt_embedded_weights.extend(
                [
                    ("gen_match_1==3 && gen_match_2==5", "emb_veto"),
                    ("iso_wgt_ele_1", "isoweight"),
                    ("id_wgt_ele_1", "idweight"),
                    ("trg_wgt_single_ele32orele35", "trgweight"),
                ]
            )
            if apply_wps:
                ztt_embedded_weights.extend(
                [
                    ("((gen_match_2==5)*id_wgt_tau_vsJet_"+vs_jet_discr+"_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                ]
                )
            if not apply_wps:
                pass
        else:
            raise ValueError(
                f"Embedded process selection for given era {era} not yet implemented"
            )
    elif "tt" in channel:
        ztt_embedded_weights.extend(
            [
                # TODO trigger weights for tt
                # (
                #     "(pt_1<100)*embeddedDecayModeWeight+(pt_1>=100)*(pt_2<100)*((decayMode_2==0)*0.975+(decayMode_2==1)*0.975*1.051+(decayMode_2==10)*0.975*0.975*0.975+(decayMode_2==11)*0.975*0.975*0.975*1.051)+(pt_2>=100)",
                #     "decayMode_SF",
                # ), # TODO check embeddedDecayModeWeight
                ("gen_match_1==5 && gen_match_2==5", "emb_veto"),
                # tau_by_iso_id_weight(channel),
                # triggerweight_emb(channel, era, vs_jet_wp, vs_ele_wp),
                # fakemetweight_emb(channel, era, vs_jet_wp, vs_ele_wp),
            ]
        )
        if apply_wps:
            ztt_embedded_weights.extend(
            [
                (
                    "((gen_match_1==5)*id_wgt_tau_vsJet_"+vs_jet_discr+"_1 + (gen_match_1!=5)) * ((gen_match_2==5)*id_wgt_tau_vsJet_"+vs_jet_discr+"_2 + (gen_match_2!=5))",
                )
            ]
            )
        if not apply_wps:
            pass
    elif "em" in channel:
        ztt_embedded_weights.extend(
            [
                # TODO trigger weights for em
                ("(gen_match_1==3 && gen_match_2==4)", "emb_gen_match"),
                ("iso_wgt_ele_1 * iso_wgt_mu_2", "isoweight"),
                ("id_wgt_ele_1 * id_wgt_mu_2", "idweight"),
                # triggerweight_emb(channel, era, vs_jet_wp, vs_ele_wp),
            ]
        )
    elif "mm" in channel:
        if era == "2017" or era == "2018":
            ztt_embedded_weights.extend(
                [
                    # TODO trigger weights for em
                    ("(gen_match_1==2 && gen_match_2==2)", "emb_gen_match"),
                    ("iso_wgt_mu_1 * iso_wgt_mu_2", "isoweight"),
                    ("id_wgt_mu_1 * id_wgt_mu_2", "idweight"),
                    ("trg_wgt_single_mu27", "trgweight"),
                    # triggerweight_emb(channel, era, vs_jet_wp, vs_ele_wp),
                ]
            )
        if era == "2016postVFP" or era == "2016preVFP":
            ztt_embedded_weights.extend(
                [
                    # TODO trigger weights for em
                    ("(gen_match_1==2 && gen_match_2==2)", "emb_gen_match"),
                    ("iso_wgt_mu_1 * iso_wgt_mu_2", "isoweight"),
                    ("id_wgt_mu_1 * id_wgt_mu_2", "idweight"),
                    ("trg_wgt_single_mu22", "trgweight"),
                    # triggerweight_emb(channel, era, vs_jet_wp, vs_ele_wp),
                ]
            )
    elif "ee" in channel:
        if era in ["2017", "2018"]:
            ztt_embedded_weights.extend(
                [
                    # TODO trigger weights for em
                    ("(gen_match_1==1 && gen_match_2==1)", "emb_gen_match"),
                    ("iso_wgt_ele_1 * iso_wgt_ele_2", "isoweight"),
                    ("id_wgt_ele_1 * id_wgt_ele_2", "idweight"),
                    ("trg_wgt_single_ele35", "trgweight"),
                    # triggerweight_emb(channel, era, vs_jet_wp, vs_ele_wp),
                ]
            )
        elif era in ["2016preVFP", "2016postVFP"]:
            ztt_embedded_weights.extend(
                [
                    # TODO trigger weights for em
                    ("(gen_match_1==1 && gen_match_2==1)", "emb_gen_match"),
                    ("iso_wgt_ele_1 * iso_wgt_ele_2", "isoweight"),
                    ("id_wgt_ele_1 * id_wgt_ele_2", "idweight"),
                    ("trg_wgt_single_ele25", "trgweight"),
                    # triggerweight_emb(channel, era, vs_jet_wp, vs_ele_wp),
                ]
            )

    ztt_embedded_cuts = [
        (
            "((gen_match_1>2 && gen_match_1<6) && (gen_match_2>2 && gen_match_2<6))",
            "dy_genuine_tau",
        )
    ]

    return Selection(
        name="Embedded",
        cuts=ztt_embedded_cuts if channel not in ["mm", "ee"] else [],
        weights=ztt_embedded_weights,
    )


def ZL_process_selection(channel):
    veto = __get_ZL_cut(channel)
    return Selection(
        name="ZL",
        cuts=[("{}".format(veto[0]), "dy_emb_veto"), ("{}".format(veto[1]), "ff_veto")],
    )


def ZL_nlo_process_selection(channel):
    veto = __get_ZL_cut(channel)
    return Selection(
        name="ZL_nlo",
        cuts=[("{}".format(veto[0]), "dy_emb_veto"), ("{}".format(veto[1]), "ff_veto")],
    )


def __get_ZL_cut(channel):
    emb_veto = ""
    ff_veto = ""
    if "mt" in channel:
        emb_veto = "!(gen_match_1==4 && gen_match_2==5)"
        ff_veto = "!(gen_match_2 == 6)"
    elif "et" in channel:
        emb_veto = "!(gen_match_1==3 && gen_match_2==5)"
        ff_veto = "!(gen_match_2 == 6)"
    elif "tt" in channel:
        emb_veto = "!(gen_match_1==5 && gen_match_2==5)"
        ff_veto = "!(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        emb_veto = "!(gen_match_1==3 && gen_match_2==4)"
        ff_veto = "(1.0)"
    elif "mm" in channel:
        emb_veto = "!(gen_match_1==2 && gen_match_2==2) && !(gen_match_1==4 && gen_match_2==4) "
        ff_veto = "(1.0)"
    elif "ee" in channel:
        emb_veto = (
            "!(gen_match_1==1 && gen_match_2==1) && !(gen_match_1==3 && gen_match_2==3)"
        )
        ff_veto = "(1.0)"
    return (emb_veto, ff_veto)


def ZJ_process_selection(channel):
    veto = __get_ZJ_cut(channel)
    return Selection(name="ZJ", cuts=[(__get_ZJ_cut(channel), "dy_fakes")])


def ZJ_nlo_process_selection(channel):
    veto = __get_ZJ_cut(channel)
    return Selection(name="ZJ_nlo", cuts=[(__get_ZJ_cut(channel), "dy_fakes")])


def __get_ZJ_cut(channel):
    if "mt" in channel or "et" in channel:
        return "gen_match_2 == 6"
    elif "tt" in channel:
        return "(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        return "0 == 1"
    elif "mm" in channel:
        return "0 == 1"
    elif "ee" in channel:
        return "0 == 1"
    else:
        return ""


def TTT_process_selection(channel):
    tt_cut = ""
    if "mt" in channel:
        tt_cut = "gen_match_1==4 && gen_match_2==5"
    elif "et" in channel:
        tt_cut = "gen_match_1==3 && gen_match_2==5"
    elif "tt" in channel:
        tt_cut = "gen_match_1==5 && gen_match_2==5"
    elif "em" in channel:
        tt_cut = "gen_match_1==3 && gen_match_2==4"
    elif "mm" in channel:
        tt_cut = "gen_match_1==4 && gen_match_2==4"
    elif "ee" in channel:
        tt_cut = "gen_match_1==3 && gen_match_2==3"
    return Selection(name="TTT", cuts=[(tt_cut, "ttt_cut")])


def TTL_process_selection(channel):
    emb_veto = ""
    ff_veto = ""
    if "mt" in channel:
        emb_veto = "!(gen_match_1==4 && gen_match_2==5)"
        ff_veto = "!(gen_match_2 == 6)"
    elif "et" in channel:
        emb_veto = "!(gen_match_1==3 && gen_match_2==5)"
        ff_veto = "!(gen_match_2 == 6)"
    elif "tt" in channel:
        emb_veto = "!(gen_match_1==5 && gen_match_2==5)"
        ff_veto = "!(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        emb_veto = "!(gen_match_1==3 && gen_match_2==4)"
        ff_veto = "(1.0)"
    elif "mm" in channel:
        emb_veto = "!(gen_match_1==4 && gen_match_2==4)"
        ff_veto = "(1.0)"
    elif "ee" in channel:
        emb_veto = "!(gen_match_1==3 && gen_match_2==3)"
        ff_veto = "(1.0)"
    return Selection(
        name="TTL",
        cuts=[
            ("{}".format(emb_veto), "tt_emb_veto"),
            ("{}".format(ff_veto), "ff_veto"),
        ],
    )


def TTJ_process_selection(channel):
    ct = ""
    if "mt" in channel or "et" in channel:
        ct = "(gen_match_2 == 6 && gen_match_2 == 6)"
    elif "tt" in channel:
        ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        ct = "0 == 1"
    elif "mm" in channel or "ee" in channel:
        ct = "0 == 1"
    return Selection(name="TTJ", cuts=[(ct, "tt_fakes")])


def VVT_process_selection(channel):
    tt_cut = ""
    if "mt" in channel:
        tt_cut = "gen_match_1==4 && gen_match_2==5"
    elif "et" in channel:
        tt_cut = "gen_match_1==3 && gen_match_2==5"
    elif "tt" in channel:
        tt_cut = "gen_match_1==5 && gen_match_2==5"
    elif "em" in channel:
        tt_cut = "gen_match_1==3 && gen_match_2==4"
    elif "mm" in channel:
        tt_cut = "gen_match_1==4 && gen_match_2==4"
    elif "ee" in channel:
        tt_cut = "gen_match_1==3 && gen_match_2==3"
    return Selection(name="VVT", cuts=[(tt_cut, "vvt_cut")])


def VVJ_process_selection(channel):
    ct = ""
    if "mt" in channel or "et" in channel:
        ct = "(gen_match_2 == 6 && gen_match_2 == 6)"
    elif "tt" in channel:
        ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        ct = "0.0 == 1.0"
    elif "mm" in channel or "ee" in channel:
        ct = "0.0 == 1.0"
    return Selection(name="VVJ", cuts=[(ct, "vv_fakes")])


def VVL_process_selection(channel):
    emb_veto = ""
    ff_veto = ""
    if "mt" in channel:
        emb_veto = "!(gen_match_1==4 && gen_match_2==5)"
        ff_veto = "!(gen_match_2 == 6)"
    elif "et" in channel:
        emb_veto = "!(gen_match_1==3 && gen_match_2==5)"
        ff_veto = "!(gen_match_2 == 6)"
    elif "tt" in channel:
        emb_veto = "!(gen_match_1==5 && gen_match_2==5)"
        ff_veto = "!(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        emb_veto = "!(gen_match_1==3 && gen_match_2==4)"
        ff_veto = "(1.0)"
    elif "mm" in channel:
        emb_veto = "!(gen_match_1==4 && gen_match_2==4)"
        ff_veto = "(1.0)"
    elif "ee" in channel:
        emb_veto = "!(gen_match_1==3 && gen_match_2==3)"
        ff_veto = "(1.0)"
    return Selection(
        name="VVL",
        cuts=[
            ("{}".format(emb_veto), "tt_emb_veto"),
            ("{}".format(ff_veto), "ff_veto"),
        ],
    )


def VH_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    return Selection(
        name="VH125",
        weights=HTT_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights,
        cuts=[
            (
                "(HTXS_stage1_2_cat_pTjet30GeV>=300)&&(HTXS_stage1_2_cat_pTjet30GeV<=505)",
                "htxs_match",
            )
        ],
    )


def WH_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    return Selection(
        name="WH125",
        weights=HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
        + [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(abs(crossSectionPerEventWeight - 0.052685) < 0.001)*0.051607+"
                "(abs(crossSectionPerEventWeight - 0.03342) < 0.001)*0.032728576",
                "crossSectionPerEventWeight",
            ),
        ],
        cuts=[
            (
                "(HTXS_stage1_2_cat_pTjet30GeV>=300)&&(HTXS_stage1_2_cat_pTjet30GeV<=305)",
                "htxs_match",
            )
        ],
    )


def ZH_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    return Selection(
        name="ZH125",
        weights=HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
        + [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(abs(crossSectionPerEventWeight - 0.04774) < 0.001)*0.04683+"
                "(abs(crossSectionPerEventWeight - 0.0007771) < 0.00001)*0.0007666+"
                "(abs(crossSectionPerEventWeight - 0.0015391) < 0.0001)*0.00151848",
                "crossSectionPerEventWeight",
            ),
        ],
        cuts=[
            (
                "(HTXS_stage1_2_cat_pTjet30GeV>=400)&&(HTXS_stage1_2_cat_pTjet30GeV<=405)",
                "htxs_match",
            )
        ],
    )


def ttH_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    ttH_weights = HTT_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    return Selection(name="ttH125", weights=ttH_weights)


def ggHWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    if era in ["2016", "2017"]:
        ggHWW_weights = HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    else:
        ggHWW_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("1.1019558", "crossSectionPerEventWeight"),
        ]
    return Selection(name="ggHWW125", weights=ggHWW_weights)


def qqHWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    if era in ["2016", "2017"]:
        qqHWW_weights = HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    else:
        qqHWW_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("0.0857883", "crossSectionPerEventWeight"),
        ]
    return Selection(name="qqHWW125", weights=qqHWW_weights)


def WHWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    WHWW_weights = HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    return Selection(name="WHWW125", weights=WHWW_weights)


def ZHWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    ZHWW_weights = HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    return Selection(name="ZHWW125", weights=ZHWW_weights)


# def ggh_stitching_weight(era):
#     if era == "2016":
#         weight = (
#             "(numberGeneratedEventsWeight*0.005307836*(abs(crossSectionPerEventWeight - 3.0469376) > 1e-5)+1.0/(9673200 + 19939500 + 19977000)*2.998464*(abs(crossSectionPerEventWeight - 3.0469376) < 1e-5))",
#             "ggh_stitching_weight",
#         )
#     elif era == "2017":
#         weight = (
#             "((HTXS_stage1_2_cat_pTjet30GeV==100||HTXS_stage1_2_cat_pTjet30GeV==102||HTXS_stage1_2_cat_pTjet30GeV==103)*crossSectionPerEventWeight*8.210e-8+"
#             "(HTXS_stage1_2_cat_pTjet30GeV==101)*2.08e-8+"
#             "(HTXS_stage1_2_cat_pTjet30GeV==104||HTXS_stage1_2_cat_pTjet30GeV==105)*4.39e-8+"
#             "(HTXS_stage1_2_cat_pTjet30GeV==106)*1.19e-8+"
#             "(HTXS_stage1_2_cat_pTjet30GeV>=107&&HTXS_stage1_2_cat_pTjet30GeV<=109)*4.91e-8+"
#             "(HTXS_stage1_2_cat_pTjet30GeV>=110&&HTXS_stage1_2_cat_pTjet30GeV<=113)*7.90e-9"
#             ")*0.98409104275716*(abs(crossSectionPerEventWeight - 0.00538017) > 1e-5) + numberGeneratedEventsWeight*0.005307836*(abs(crossSectionPerEventWeight - 0.00538017) < 1e-5)",
#             "ggh_stitching_weight",
#         )
#     elif era == "2018":
#         weight = (
#             "(((HTXS_stage1_2_cat_pTjet30GeV==100||HTXS_stage1_2_cat_pTjet30GeV==102||HTXS_stage1_2_cat_pTjet30GeV==103)*crossSectionPerEventWeight*numberGeneratedEventsWeight+"
#             "(HTXS_stage1_2_cat_pTjet30GeV==101)*2.09e-8+"
#             "(HTXS_stage1_2_cat_pTjet30GeV==104||HTXS_stage1_2_cat_pTjet30GeV==105)*4.28e-8+"
#             "(HTXS_stage1_2_cat_pTjet30GeV==106)*1.39e-8+"
#             "(HTXS_stage1_2_cat_pTjet30GeV>=107&&HTXS_stage1_2_cat_pTjet30GeV<=109)*4.90e-8+"
#             "(HTXS_stage1_2_cat_pTjet30GeV>=110&&HTXS_stage1_2_cat_pTjet30GeV<=113)*9.69e-9"
#             ")*0.98409104275716*(abs(crossSectionPerEventWeight - 0.00538017) > 1e-5) + numberGeneratedEventsWeight*0.005307836*(abs(crossSectionPerEventWeight - 0.00538017) < 1e-5))",
#             "ggh_stitching_weight",
#         )
#     return weight


def ggh_stitching_weight(era):
    if era == "2016":
        weight = (
            "(numberGeneratedEventsWeight*0.005307836*(abs(crossSectionPerEventWeight - 3.0469376) > 1e-5)+1.0/(9673200 + 19939500 + 19977000)*2.998464*(abs(crossSectionPerEventWeight - 3.0469376) < 1e-5))",
            "ggh_stitching_weight",
        )
    elif era == "2017":
        weight = (
            "((HTXS_stage1_2_cat_pTjet30GeV==100||HTXS_stage1_2_cat_pTjet30GeV==102||HTXS_stage1_2_cat_pTjet30GeV==103)*crossSectionPerEventWeight*8.210e-8+"
            "(HTXS_stage1_2_cat_pTjet30GeV==101)*2.08e-8+"
            "(HTXS_stage1_2_cat_pTjet30GeV==104||HTXS_stage1_2_cat_pTjet30GeV==105)*4.39e-8+"
            "(HTXS_stage1_2_cat_pTjet30GeV==106)*1.19e-8+"
            "(HTXS_stage1_2_cat_pTjet30GeV>=107&&HTXS_stage1_2_cat_pTjet30GeV<=109)*4.91e-8+"
            "(HTXS_stage1_2_cat_pTjet30GeV>=110&&HTXS_stage1_2_cat_pTjet30GeV<=113)*7.90e-9"
            ")*0.98409104275716*(abs(crossSectionPerEventWeight - 0.00538017) > 1e-5) + numberGeneratedEventsWeight*0.005307836*(abs(crossSectionPerEventWeight - 0.00538017) < 1e-5)",
            "ggh_stitching_weight",
        )
    elif era == "2018":
        weight = (
            "(((HTXS_stage1_2_cat_pTjet30GeV==100||HTXS_stage1_2_cat_pTjet30GeV==102||HTXS_stage1_2_cat_pTjet30GeV==103)*crossSectionPerEventWeight*numberGeneratedEventsWeight+"
            "(HTXS_stage1_2_cat_pTjet30GeV==101)*2.09e-8+"
            "(HTXS_stage1_2_cat_pTjet30GeV==104||HTXS_stage1_2_cat_pTjet30GeV==105)*4.28e-8+"
            "(HTXS_stage1_2_cat_pTjet30GeV==106)*1.39e-8+"
            "(HTXS_stage1_2_cat_pTjet30GeV>=107&&HTXS_stage1_2_cat_pTjet30GeV<=109)*4.90e-8+"
            "(HTXS_stage1_2_cat_pTjet30GeV>=110&&HTXS_stage1_2_cat_pTjet30GeV<=113)*9.69e-9"
            ")*0.98409104275716*(abs(crossSectionPerEventWeight - 0.00538017) > 1e-5) + numberGeneratedEventsWeight*0.005307836*(abs(crossSectionPerEventWeight - 0.00538017) < 1e-5))",
            "ggh_stitching_weight",
        )
    return weight


def qqh_stitching_weight(era):
    if era == "2016":
        weight = (
            "(numberGeneratedEventsWeight*((abs(crossSectionPerEventWeight - 0.04774)<0.001)*0.04683+"
            "(abs(crossSectionPerEventWeight - 0.052685)<0.001)*0.051607+"
            "(abs(crossSectionPerEventWeight - 0.03342)<0.001)*0.032728576)"
            "+1.0/(1499400 + 1999000 + 2997000)*0.2340416*(abs(crossSectionPerEventWeight - 0.2370687)<1e-4))",
            "qqh_stitching_weight",
        )
    elif era == "2017":
        weight = (
            "(((HTXS_stage1_2_cat_pTjet30GeV>=200&&HTXS_stage1_2_cat_pTjet30GeV<=202)*(abs(crossSectionPerEventWeight-0.237207)<1e-4)*0.2340416)+"
            "(abs(crossSectionPerEventWeight-0.04774)<0.001)*0.04683+"
            "(abs(crossSectionPerEventWeight-0.052685)<0.001)*0.051607+"
            "(abs(crossSectionPerEventWeight-0.03342)<0.001)*0.032728576)*numberGeneratedEventsWeight"
            "+0.987231127517045*(abs(crossSectionPerEventWeight-0.04774)>=0.001&&abs(crossSectionPerEventWeight-0.052685)>=0.001&&abs(crossSectionPerEventWeight-0.03342)>=0.001)*("
            "(HTXS_stage1_2_cat_pTjet30GeV>=203&&HTXS_stage1_2_cat_pTjet30GeV<=205)*8.70e-9+"
            "(HTXS_stage1_2_cat_pTjet30GeV==206)*8.61e-9+"
            "(HTXS_stage1_2_cat_pTjet30GeV>=207&&HTXS_stage1_2_cat_pTjet30GeV<=210)*1.79e-8"
            ")",
            "qqh_stitching_weight",
        )
    elif era == "2018":
        weight = (
            "(((HTXS_stage1_2_cat_pTjet30GeV>=200&&HTXS_stage1_2_cat_pTjet30GeV<=202)*(abs(crossSectionPerEventWeight-0.2370687)<1e-4)*0.2340416)+"
            "(abs(crossSectionPerEventWeight-0.04774)<0.001)*0.04683+"
            "(abs(crossSectionPerEventWeight-0.052685)<0.001)*0.051607+"
            "(abs(crossSectionPerEventWeight-0.03342)<0.001)*0.032728576)*numberGeneratedEventsWeight"
            "+0.987231127517045*(abs(crossSectionPerEventWeight-0.04774)>=0.001&&abs(crossSectionPerEventWeight-0.052685)>=0.001&&abs(crossSectionPerEventWeight-0.03342)>=0.001)*("
            "(HTXS_stage1_2_cat_pTjet30GeV>=203&&HTXS_stage1_2_cat_pTjet30GeV<=205)*9.41e-9+"
            "(HTXS_stage1_2_cat_pTjet30GeV==206)*8.52e-9+"
            "(HTXS_stage1_2_cat_pTjet30GeV>=207&&HTXS_stage1_2_cat_pTjet30GeV<=210)*1.79e-8"
            ")",
            "qqh_stitching_weight",
        )
    return weight


def ggH125_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    ggH125_weights = HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
        ("ggh_NNLO_weight", "gghNNLO"),
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        (
            "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
            "crossSectionPerEventWeight",
        ),
        # ggh_stitching_weight(era),
    ]
    ggH125_cuts = [
        (
            "(HTXS_stage1_2_cat_pTjet30GeV>=100)&&(HTXS_stage1_2_cat_pTjet30GeV<=113)",
            "htxs",
        )
    ]
    return Selection(name="ggH125", weights=ggH125_weights, cuts=ggH125_cuts)


def qqH125_process_selection(channel, era, vs_jet_wp, vs_ele_wp):
    qqH125_weights = HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
        # qqh_stitching_weight(era)
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        (
            "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
            "crossSectionPerEventWeight",
        ),
    ]
    qqH125_cuts = [
        (
            "(HTXS_stage1_2_cat_pTjet30GeV>=200)&&(HTXS_stage1_2_cat_pTjet30GeV<=210)",
            "qqH125",
        )
    ]
    return Selection(name="qqH125", weights=qqH125_weights, cuts=qqH125_cuts)


def FF_training_process_selection(channel, era):
    cuts = []
    weights = []
    if channel == "et" or channel == "mt":
        cuts = [
            ("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        ]
        weights = [("ff2_nom", "fake_factor")]
    elif channel == "tt":
        raise NotImplementedError("FF training not implemented for tt")
    elif channel == "em":
        raise NotImplementedError("FF training not implemented for em")
    else:
        raise ValueError("Invalid channel: {}".format(channel))
    print("FF training cuts:", cuts)
    print("FF training weights:", weights)
    return Selection(name="jetFakes", cuts=cuts, weights=weights)
