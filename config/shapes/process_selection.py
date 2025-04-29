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


def triggerweight(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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


def lumi_weight(era, **kwargs):
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


def prefiring_weight(era, **kwargs):
    if era in ["2016postVFP", "2016preVFP", "2017"]:
        weight = ("prefiring_wgt", "prefireWeight")
    else:
        weight = ("1.0", "prefireWeight")
    return weight


def MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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
        raise ValueError("Given vs electron working point {} not defined.".format(vs_ele_wp))
    if vs_jet_wp not in wps_dict:
        print("This vs jet working point doen't exist. Please specify the correct vsJet discriminator ")
        raise ValueError("Given vs jet working point {} not defined.".format(vs_jet_wp))

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
    MC_base_process_weights.append(("btag_weight", "btagWeight"))
    return Selection(
        name="MC base",
        weights=[weight for weight in MC_base_process_weights if weight is not None],
    )


def HH2B2Tau_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    HH2B2Tau_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    HH2B2Tau_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight * 0.1", "crossSectionPerEventWeight"),
        ]
    )
    return Selection(name="HH2B2Tau", weights=[weight for weight in HH2B2Tau_weights if weight is not None])


def QCD_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    QCD_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    QCD_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight * 0.1", "crossSectionPerEventWeight"),
        ]
    )
    return Selection(name="QCDMC", weights=[weight for weight in QCD_weights if weight is not None])

def dy_stitching_weight(era, **kwargs):
    if era == "2017":
        weight = (
            # TODO update me
            "((genbosonmass >= 50.0)*0.0000298298*((npartons == 0 || npartons >= 5)*1.0 + (npartons == 1)*0.3478960398 + (npartons == 2)*0.2909516577 + (npartons == 3)*0.1397995594 + (npartons == 4)*0.1257217076) + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)",
            "dy_stitching_weight",
        )
        # xsec_NNLO [pb] = , N_inclusive = 203,729,540, xsec_NNLO/N_inclusive = 0.0000298298 [pb], weights: [1.0, 0.3478960398, 0.2909516577, 0.1397995594, 0.1257217076]
    elif era == "2018":
        weight = (
            """(
                (genbosonmass >= 50.0) * 0.0000631493 * (
                    ( (npartons <= 0) || (npartons >= 5) ) * 1.0 +
                    (npartons == 1) * 0.2056921342 +
                    (npartons == 2) * 0.1664121306 +
                    (npartons == 3) * 0.0891121485 +
                    (npartons == 4) * 0.0843396952
                ) +
                (genbosonmass < 50.0) * numberGeneratedEventsWeight * crossSectionPerEventWeight * (
                    (1.0 / negative_events_fraction) * (
                        ((genWeight < 0) * (-1)) +
                        ((genWeight >= 0) * 1)
                    )
                )
            )""",
            "dy_stitching_weight",
        )
        # xsec_NNLO [pb] = 2025.74*3, N_inclusive = 100194597,  xsec_NNLO/N_inclusive = 0.0000606542 [pb] weights: [1.0, 0.194267667208, 0.21727746547, 0.26760465744, 0.294078683662]
    else:
        raise ValueError("DY stitching weight not defined for era {}".format(era))

    return weight


def DY_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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
                """(
                    crossSectionPerEventWeight * (
                        (1.0 / negative_events_fraction) * (
                            ((genWeight < 0) * (-1)) +
                            ((genWeight >= 0) * 1)
                        )
                    )
                )""",
                "crossSectionPerEventWeight",
            ),
            # dy_stitching_weight(era),  # TODO add stitching weight
            ("ZPtMassReweightWeight", "zPtReweightWeight"),
        ]
    )
    return Selection(name="DY", weights=DY_process_weights)


def DY_NLO_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    DY_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    DY_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                """(
                    (1.0 / negative_events_fraction) * (
                        ((genWeight < 0) * (-1)) +
                        ((genWeight >= 0) * 1)
                    )
                ) * crossSectionPerEventWeight
                """,
                "crossSectionPerEventWeight",
            ),
            # dy_stitching_weight(era),  # TODO add stitching weight
        ]
    )
    return Selection(name="DY_NLO", weights=DY_process_weights)


def TT_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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


def TTV_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    TTV_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    TTV_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
            # ("topPtReweightWeight", "topPtReweightWeight"),
        ]
    )
    return Selection(name="TTV", weights=TTV_process_weights)


def VV_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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


def VVV_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    VVV_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    VVV_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                "crossSectionPerEventWeight",
            ),
        ]
    )
    return Selection(name="VVV", weights=VVV_process_weights)


def EWK_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    EWK_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    veto = __get_ZL_cut(channel)
    EWK_process_weights.extend(
        [
            (veto[0], "emb_veto"),
            (veto[1], "ff_veto"),
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
        ]
    )
    return Selection(name="EWK", weights=EWK_process_weights)


def W_stitching_weight(era, **kwargs):
    if era == "2018":
        weight = (
            """(
                0.0007590865 * (
                    ((npartons <= 0) || (npartons >= 5)) * 1.0 +
                    (npartons == 1) * 0.2191273680 +
                    (npartons == 2) * 0.1335837379 +
                    (npartons == 3) * 0.0636217909 +
                    (npartons == 4) * 0.0823135765
                )
            )""",
            "wj_stitching_weight",
        )
        # xsec_NNLO [pb] = 61526.7, N_inclusive = 71026861, xsec_NNLO/N_inclusive = 0.0008662455 [pb] weights: [1.0, 0.1741017559343336, 0.13621263074538312, 0.08156674151214884, 0.06721295702670023]
    else:
        raise NotImplementedError("W stitching weight not defined for era {}".format(era))
    return weight


def W_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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
    # W_process_weights.append(W_stitching_weight(era))  # TODO add W stitching weight in when npartons is available
    return Selection(name="W", weights=W_process_weights)


def HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    return Selection(
        name="HTT_base", weights=MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    )


def HTT_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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
def HWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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


def HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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
    - STT_process_selection
    - STL_process_selection
    - STJ_process_selection
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


def ZTT_process_selection(channel, **kwargs):
    tt_cut = __get_ZTT_cut(channel)
    return Selection(name="ZTT", cuts=[(tt_cut, "ztt_cut")])


def ZTT_nlo_process_selection(channel, **kwargs):
    tt_cut = __get_ZTT_cut(channel)
    return Selection(name="ZTT_nlo", cuts=[(tt_cut, "ztt_cut")])


def __get_ZTT_cut(channel, **kwargs):
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


def ZTT_embedded_process_selection(channel, era, apply_wps, vs_jet_wp, **kwargs):
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
                    ("(trg_wgt_single_mu24ormu27)", "trgweight"),
                    (f"((gen_match_2==5)*id_wgt_tau_vsJet_{vs_jet_discr}_2 + (gen_match_2!=5))", "taubyIsoIdWeight"),
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


def ZL_process_selection(channel, **kwargs):
    veto = __get_ZL_cut(channel)
    return Selection(
        name="ZL",
        cuts=[("{}".format(veto[0]), "dy_emb_veto"), ("{}".format(veto[1]), "ff_veto")],
    )


def ZL_nlo_process_selection(channel, **kwargs):
    veto = __get_ZL_cut(channel)
    return Selection(
        name="ZL_nlo",
        cuts=[("{}".format(veto[0]), "dy_emb_veto"), ("{}".format(veto[1]), "ff_veto")],
    )


def __get_ZL_cut(channel, **kwargs):
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


def ZJ_process_selection(channel, **kwargs):
    veto = __get_ZJ_cut(channel)
    return Selection(name="ZJ", cuts=[(__get_ZJ_cut(channel), "dy_fakes")])


def ZJ_nlo_process_selection(channel, **kwargs):
    veto = __get_ZJ_cut(channel)
    return Selection(name="ZJ_nlo", cuts=[(__get_ZJ_cut(channel), "dy_fakes")])


def __get_ZJ_cut(channel, **kwargs):
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


def TTT_process_selection(channel, **kwargs):
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


def TTL_process_selection(channel, **kwargs):
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


def TTJ_process_selection(channel, **kwargs):
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


def TTVT_process_selection(channel, **kwargs):
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
    return Selection(name="TTVT", cuts=[(tt_cut, "ttvt_cut")])


def TTVL_process_selection(channel, **kwargs):
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
        name="TTVL",
        cuts=[
            ("{}".format(emb_veto), "ttv_emb_veto"),
            ("{}".format(ff_veto), "ff_veto"),
        ],
    )


def TTVJ_process_selection(channel, **kwargs):
    ct = ""
    if "mt" in channel or "et" in channel:
        ct = "(gen_match_2 == 6 && gen_match_2 == 6)"
    elif "tt" in channel:
        ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        ct = "0 == 1"
    elif "mm" in channel or "ee" in channel:
        ct = "0 == 1"
    return Selection(name="TTVJ", cuts=[(ct, "ttv_fakes")])


def ST_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    ST_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    ST_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
        ]
    )
    return Selection(name="ST", weights=ST_process_weights)


def STT_process_selection(channel, **kwargs):
    tt_cut = ""
    btag_weight = ""
    if "mt" in channel:
        tt_cut = "gen_match_1==4 && gen_match_2==5"
        btag_weight = ("1.002108*btag_weight*(bpair_pt_1>=0)+(bpair_pt_1<0)", "btagging_weight")
    elif "et" in channel:
        tt_cut = "gen_match_1==3 && gen_match_2==5"
        btag_weight = ("0.996391*btag_weight*(bpair_pt_1>=0)+(bpair_pt_1<0)", "btagging_weight")
    elif "tt" in channel:
        tt_cut = "gen_match_1==5 && gen_match_2==5"
        btag_weight = ("0.999864*btag_weight*(bpair_pt_1>=0)+(bpair_pt_1<0)", "btagging_weight")
    return Selection(name="STT", cuts=[(tt_cut, "stt_cut")], weights=[btag_weight])


def STL_process_selection(channel, **kwargs):
    emb_veto = ""
    ff_veto = ""
    btag_weight = ""
    if "mt" in channel:
        emb_veto = "!(gen_match_1==4 && gen_match_2==5)"
        ff_veto = "!(gen_match_2 == 6)"
        btag_weight = ("1.002703*btag_weight*(bpair_pt_1>=0)+(bpair_pt_1<0)", "btagging_weight")
    elif "et" in channel:
        emb_veto = "!(gen_match_1==3 && gen_match_2==5)"
        ff_veto = "!(gen_match_2 == 6)"
        btag_weight = ("1.002547*btag_weight*(bpair_pt_1>=0)+(bpair_pt_1<0)", "btagging_weight")
    elif "tt" in channel:
        emb_veto = "!(gen_match_1==5 && gen_match_2==5)"
        ff_veto = "!(gen_match_1 == 6 || gen_match_2 == 6)"
        btag_weight = ("1.017508*btag_weight*(bpair_pt_1>=0)+(bpair_pt_1<0)", "btagging_weight")
    return Selection(
        name="STL",
        cuts=[
            ("{}".format(emb_veto), "st_emb_veto"),
            ("{}".format(ff_veto), "ff_veto"),
        ],
        weights=[btag_weight],
    )


def STJ_process_selection(channel, **kwargs):
    ct = ""
    btag_weight = ""
    if "mt" in channel:
        ct = "(gen_match_2 == 6)"
        btag_weight = ("1.004332*btag_weight*(bpair_pt_1>=0)+(bpair_pt_1<0)", "btagging_weight")
    elif "et" in channel:
        ct = "(gen_match_2 == 6)"
        btag_weight = ("1.000362*btag_weight*(bpair_pt_1>=0)+(bpair_pt_1<0)", "btagging_weight")
    elif "tt" in channel:
        ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
        btag_weight = ("1.005110*btag_weight*(bpair_pt_1>=0)+(bpair_pt_1<0)", "btagging_weight")
    return Selection(name="STJ", cuts=[(ct, "st_fakes")], weights=[btag_weight])


def VVT_process_selection(channel, **kwargs):
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


def VVJ_process_selection(channel, **kwargs):
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


def VVL_process_selection(channel, **kwargs):
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


def VVVT_process_selection(channel, **kwargs):
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
    return Selection(name="VVVT", cuts=[(tt_cut, "vvt_cut")])


def VVVJ_process_selection(channel, **kwargs):
    ct = ""
    if "mt" in channel or "et" in channel:
        ct = "(gen_match_2 == 6 && gen_match_2 == 6)"
    elif "tt" in channel:
        ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        ct = "0.0 == 1.0"
    elif "mm" in channel or "ee" in channel:
        ct = "0.0 == 1.0"
    return Selection(name="VVVJ", cuts=[(ct, "vv_fakes")])


def VVVL_process_selection(channel, **kwargs):
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
        name="VVVL",
        cuts=[
            ("{}".format(emb_veto), "tt_emb_veto"),
            ("{}".format(ff_veto), "ff_veto"),
        ],
    )


def VH_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    return Selection(
        name="VH125",
        weights=HTT_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights,
        # cuts=[
        #     (
        #         "(HTXS_stage1_2_cat_pTjet30GeV>=300)&&(HTXS_stage1_2_cat_pTjet30GeV<=505)",
        #         "htxs_match",
        #     )
        # ],
    )


def WH_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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
        # cuts=[
        #     (
        #         "(HTXS_stage1_2_cat_pTjet30GeV>=300)&&(HTXS_stage1_2_cat_pTjet30GeV<=305)",
        #         "htxs_match",
        #     )
        # ],
    )


def ZH_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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
        # cuts=[
        #     (
        #         "(HTXS_stage1_2_cat_pTjet30GeV>=400)&&(HTXS_stage1_2_cat_pTjet30GeV<=405)",
        #         "htxs_match",
        #     )
        # ],
    )


def ttH_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    ttH_weights = HTT_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    return Selection(name="ttH125", weights=ttH_weights)


def ggHWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    if era in ["2016", "2017"]:
        ggHWW_weights = HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    else:
        ggHWW_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("1.1019558", "crossSectionPerEventWeight"),
        ]
    return Selection(name="ggHWW125", weights=ggHWW_weights)


def qqHWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    if era in ["2016", "2017"]:
        qqHWW_weights = HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    else:
        qqHWW_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("0.0857883", "crossSectionPerEventWeight"),
        ]
    return Selection(name="qqHWW125", weights=qqHWW_weights)


def WHWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    WHWW_weights = HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    return Selection(name="WHWW125", weights=WHWW_weights)


def ZHWW_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    ZHWW_weights = HWW_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    return Selection(name="ZHWW125", weights=ZHWW_weights)


def ggh_stitching_weight(era, **kwargs):
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


def qqh_stitching_weight(era, **kwargs):
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


def ggH125_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    ggH125_weights = HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
        # ("ggh_NNLO_weight", "gghNNLO"),
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        (
            "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
            "crossSectionPerEventWeight",
        ),
        # ggh_stitching_weight(era),
    ]
    # ggH125_cuts = [
    #     (
    #         "(HTXS_stage1_2_cat_pTjet30GeV>=100)&&(HTXS_stage1_2_cat_pTjet30GeV<=113)",
    #         "htxs",
    #     )
    # ]
    return Selection(name="ggH125", weights=ggH125_weights) #, cuts=ggH125_cuts)


def qqH125_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
    qqH125_weights = HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights + [
        # qqh_stitching_weight(era)
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        (
            "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
            "crossSectionPerEventWeight",
        ),
    ]
    # qqH125_cuts = [
    #     (
    #         "(HTXS_stage1_2_cat_pTjet30GeV>=200)&&(HTXS_stage1_2_cat_pTjet30GeV<=210)",
    #         "qqH125",
    #     )
    # ]
    return Selection(name="qqH125", weights=qqH125_weights) #, cuts=qqH125_cuts)


def FF_training_process_selection(channel, era, **kwargs):
    cuts = []
    weights = []
    if channel == "et" or channel == "mt":
        cuts = [
            ("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        ]
        weights = [("fake_factor", "fake_factor")]
    elif channel == "tt":
        # TODO
        raise NotImplementedError("FF training not implemented for tt")
    elif channel == "em":
        raise NotImplementedError("FF training not implemented for em")
    else:
        raise ValueError("Invalid channel: {}".format(channel))
    print("FF training cuts:", cuts)
    print("FF training weights:", weights)
    return Selection(name="jetFakes", cuts=cuts, weights=weights)


# --- Process selections aliases ---
MC_base = MC_base_process_selection
HH2B2Tau = HH2B2Tau_process_selection
DY = DY_process_selection
DY_NLO = DY_NLO_process_selection
TT = TT_process_selection
TTV = TTV_process_selection
VV = VV_process_selection
VVV = VVV_process_selection
EWK = EWK_process_selection
W = W_process_selection
HTT_base = HTT_base_process_selection
HTT = HTT_process_selection
HWW = HWW_process_selection
HWW_base = HWW_base_process_selection
ZTT = ZTT_process_selection
ZTT_nlo = ZTT_nlo_process_selection
ZTT_embedded = ZTT_embedded_process_selection
ZL = ZL_process_selection
ZL_nlo = ZL_nlo_process_selection
ZJ = ZJ_process_selection
ZJ_nlo = ZJ_nlo_process_selection
TTT = TTT_process_selection
TTL = TTL_process_selection
TTJ = TTJ_process_selection
TTVT = TTVT_process_selection
TTVL = TTVL_process_selection
TTVJ = TTVJ_process_selection
ST = ST_process_selection
STT = STT_process_selection
STL = STL_process_selection
STJ = STJ_process_selection
VVT = VVT_process_selection
VVL = VVL_process_selection
VVJ = VVJ_process_selection
VVVT = VVVT_process_selection
VVVL = VVVL_process_selection
VVVJ = VVVJ_process_selection
VH = VH_process_selection
WH = WH_process_selection
ZH = ZH_process_selection
ttH = ttH_process_selection
ggHWW = ggHWW_process_selection
qqHWW = qqHWW_process_selection
WHWW = WHWW_process_selection
ZHWW = ZHWW_process_selection
ggH125 = ggH125_process_selection
qqH125 = qqH125_process_selection
FF_training = FF_training_process_selection
QCD = QCD_process_selection
