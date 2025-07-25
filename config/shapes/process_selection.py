import logging

from ntuple_processor.utils import Selection
from config.logging_setup_configs import setup_logging, LogContext

logger = setup_logging(logger=logging.getLogger(__name__))


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
    if channel != "mm" and channel != "mt":
        MC_base_process_weights.append(("btag_weight", "btagWeight"))
    return Selection(
        name="MC base",
        weights=[weight for weight in MC_base_process_weights if weight is not None],
    )


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


def DY_process_selection(channel, era, vs_jet_wp, vs_ele_wp, weight_stitching_DY=True, **kwargs):
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

    if weight_stitching_DY:
        DY_process_weights.append(dy_stitching_weight(era))
    else:
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
            ]
        )
    DY_process_weights.append(("ZPtMassReweightWeight", "zPtReweightWeight"))
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


def EWK_process_selection(channel, era, **kwargs):
    EWK_process_weights = MC_base_process_selection(channel, era).weights
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


def W_process_selection(channel, era, vs_jet_wp, vs_ele_wp, weight_stitching_W=True, **kwargs):
    W_process_weights = MC_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    if weight_stitching_W:
        W_process_weights.append(W_stitching_weight(era))
    else:
        W_process_weights.extend(
            [
                ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
                (
                    "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                    "crossSectionPerEventWeight",
                ),
            ]
        )
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
    return Selection(name="ZTT", cuts=[(f"({tt_cut})", "ztt_cut")])


def ZTT_nlo_process_selection(channel, **kwargs):
    tt_cut = __get_ZTT_cut(channel)
    return Selection(name="ZTT_nlo", cuts=[(f"({tt_cut})", "ztt_cut")])


def __get_ZTT_cut(channel, **kwargs):
    if "mt" in channel:
        return "(gen_match_1==4 && gen_match_2==5)"
    elif "et" in channel:
        return "(gen_match_1==3 && gen_match_2==5)"
    elif "tt" in channel:
        return "(gen_match_1==5 && gen_match_2==5)"
    elif "em" in channel:
        return "(gen_match_1==3 && gen_match_2==4)"
    elif "mm" in channel:
        return "(gen_match_1==4 && gen_match_2==4)"
    elif "ee" in channel:
        return "(gen_match_1==3 && gen_match_2==3)"


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
                ]
            )
            if apply_wps:
                ztt_embedded_weights.extend(
                    [
                        (f"((gen_match_2==5)*id_wgt_tau_vsJet_{vs_jet_discr}_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
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
        emb_veto = "(!(gen_match_1==4 && gen_match_2==5))"
        ff_veto = "(!(gen_match_2 == 6))"
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
        return "(gen_match_2 == 6)"
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
        tt_cut = "(gen_match_1==4 && gen_match_2==5)"
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
    return Selection(name="TTT", cuts=[(f"({tt_cut})", "ttt_cut")])


def TTL_process_selection(channel, **kwargs):
    emb_veto = ""
    ff_veto = ""
    if "mt" in channel:
        emb_veto = "(!(gen_match_1==4 && gen_match_2==5))"
        ff_veto = "(!(gen_match_2 == 6))"
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
        cuts=[(f"({emb_veto})", "tt_emb_veto"), (f"({ff_veto})", "ff_veto")],
    )


def TTJ_process_selection(channel, **kwargs):
    ct = ""
    if "mt" in channel or "et" in channel:
        ct = "(gen_match_2 == 6)"
    elif "tt" in channel:
        ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        ct = "0 == 1"
    elif "mm" in channel or "ee" in channel:
        ct = "0 == 1"
    return Selection(name="TTJ", cuts=[(f"({ct})", "tt_fakes")])


def VVT_process_selection(channel, **kwargs):
    tt_cut = ""
    if "mt" in channel:
        tt_cut = "(gen_match_1==4 && gen_match_2==5)"
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
    return Selection(name="VVT", cuts=[(f"({tt_cut})", "vvt_cut")])


def VVJ_process_selection(channel, **kwargs):
    ct = ""
    if "mt" in channel or "et" in channel:
        ct = "(gen_match_2 == 6)"
    elif "tt" in channel:
        ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
    elif "em" in channel:
        ct = "0.0 == 1.0"
    elif "mm" in channel or "ee" in channel:
        ct = "0.0 == 1.0"
    return Selection(name="VVJ", cuts=[(f"({ct})", "vv_fakes")])


def VVL_process_selection(channel, **kwargs):
    emb_veto = ""
    ff_veto = ""
    if "mt" in channel:
        emb_veto = "(!(gen_match_1==4 && gen_match_2==5))"
        ff_veto = "(!(gen_match_2 == 6))"
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
        cuts=[(f"({emb_veto})", "tt_emb_veto"), (f"({ff_veto})", "ff_veto")],
    )


def VH_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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
        cuts=[
            (
                "(HTXS_stage1_2_cat_pTjet30GeV>=300)&&(HTXS_stage1_2_cat_pTjet30GeV<=305)",
                "htxs_match",
            )
        ],
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
        cuts=[
            (
                "(HTXS_stage1_2_cat_pTjet30GeV>=400)&&(HTXS_stage1_2_cat_pTjet30GeV<=405)",
                "htxs_match",
            )
        ],
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


def _stxs_bin_or_range(*bins):
    if len(bins) == 1:
        return f"(HTXS_stage1_2_cat_pTjet30GeV == {bins[0]})"
    elif len(bins) == 2:
        return f"((HTXS_stage1_2_cat_pTjet30GeV >= {bins[0]}) && (HTXS_stage1_2_cat_pTjet30GeV <= {bins[1]}))"


def ggh_stitching_weight(era, **kwargs):
    xsec_inclusive = 48.58 * 0.06272  # N3LO * BR(tau tau)

    # fraction determined from N3LO cross section in each bin of inclusive sample pre-selection
    xsec_fractions = {
        "bin100": 0.08318797823593468,
        "bin101": 0.01042200334575194,
        "bin102": 0.00298337083653306,
        "bin103": 0.0005678862986734344,
        "bin104to105": 0.00010037567623046294 + 0.12614697523978313,
        "bin106": 0.44989430160739785,
        "bin107to109": 0.140926124593334 + 0.08157534324506752 + 0.014167855250793428,
        "bin110to113": 0.01976800749762655 + 0.0371421174622971 + 0.01734075531449457 + 0.005172074925766409,
        "bin114": 0.005839791380690793,
        "bin115": 0.0023501000717436656,
        "bin116": 0.0024149390178801132,
    }

    N = {
        '2016preVFP': {
            'inclusive': 6134000,
            'bin101': 1373032,
            'bin101_ext1': 5232863,
            'bin104to105': 6952512,
            'bin104to105_ext1': 33418400,
            'bin106': 1978107,
            'bin106_ext1': 9825511,
            'bin107to109': 2017851,
            'bin107to109_ext1': 10165655,
            'bin110to113': 3094573,
            'bin110to113_ext1': 14530099,
        },
        '2016postVFP': {
            'inclusive': 6439000,
            'bin101': 1093494,
            'bin101_ext1': 6340339,
            'bin104to105': 6557985,
            'bin104to105_ext1': 35814651,
            'bin106': 2001772,
            'bin106_ext1': 9948089,
            'bin107to109': 2017124,
            'bin107to109_ext1': 10122661,
            'bin110to113': 3049031,
            'bin110to113_ext1': 15992787,
        },
        '2018': {
            'inclusive': 12966000,
            'bin101': 2228950,
            'bin101_ext1': 9732154,
            'bin104to105': 13615355,
            'bin104to105_ext1': 68079587,
            'bin106': 3917850,
            'bin106_ext1': 20141681,
            'bin107to109': 4012248,
            'bin107to109_ext1': 20518986,
            'bin110to113': 6122208,
            'bin110to113_ext1': 29718881,
        },
        '2017': {
            'inclusive': 12974000,
            'bin101': 2230442,
            'bin101_ext1': 12316040,
            'bin104to105_ext1': 69394908,
            'bin107to109': 4037059,
            'bin104to105': 13502118,
            'bin110to113': 6037239,
            'bin106_ext1': 19755954,
            'bin106': 3945057,
            'bin110to113_ext1': 30074010,
            'bin107to109_ext1': 19863603,
        },
    }

    negative_fraction = {
        '2016preVFP': {
            'inclusive': 0.9897538311053147,
            'bin101': 0.9993459729999009,
            'bin101_ext1': 0.9992803174858581,
            'bin104to105': 0.9930312957388638,
            'bin104to105_ext1': 0.9930483805328801,
            'bin106': 0.9933694183378351,
            'bin106_ext1': 0.9934517400672596,
            'bin107to109': 0.9951314542054889,
            'bin107to109_ext1': 0.9950293414443043,
            'bin110to113': 0.9960065572859325,
            'bin110to113_ext1': 0.9960758698202951,
        },
        '2016postVFP': {
            'inclusive': 0.9896303773877931,
            'bin101': 0.9992647421933728,
            'bin101_ext1': 0.9992669161696244,
            'bin104to105': 0.9929676569861017,
            'bin104to105_ext1': 0.9930765763988598,
            'bin106': 0.9933418990774174,
            'bin106_ext1': 0.9934184344349956,
            'bin107to109': 0.995108877788376,
            'bin107to109_ext1': 0.9950321363127739,
            'bin110to113': 0.9961259823202847,
            'bin110to113_ext1': 0.996109871281347,
        },
        '2018': {
            'inclusive': 0.9896493907141756,
            'bin101': 0.9992812759371005,
            'bin101_ext1': 0.9993010796993143,
            'bin104to105': 0.9930831035988411,
            'bin104to105_ext1': 0.9930390294523966,
            'bin106': 0.993488265247521,
            'bin106_ext1': 0.99343758845153,
            'bin107to109': 0.9950102785271498,
            'bin107to109_ext1': 0.9950589176287756,
            'bin110to113': 0.996042277557378,
            'bin110to113_ext1': 0.9960882780209659,
        },
        '2017': {
            'inclusive': 0.9897097271466009,
            'bin101': 0.9992862401263964,
            'bin101_ext1': 0.9992996125377962,
            'bin104to105': 0.9930560523911878,
            'bin104to105_ext1': 0.9930626898446209,
            'bin106': 0.9934439477046846,
            'bin106_ext1': 0.9933888285020304,
            'bin107to109': 0.9950944487063479,
            'bin107to109_ext1': 0.9950293005755301,
            'bin110to113': 0.9961280313732818,
            'bin110to113_ext1': 0.9960913094063611,
        },
    }

    def inclusive_and_extended(*bins):
        _bin = f"bin{bins[0]}" if len(bins) == 1 else f"bin{bins[0]}to{bins[-1]}"
        _bin_ext1 = f"{_bin}_ext1"

        _frac = xsec_fractions[_bin]

        return (_frac * xsec_inclusive)  / sum(
            [
                N[era][_bin] * negative_fraction[era][_bin],
                N[era][_bin_ext1] * negative_fraction[era][_bin_ext1],
                _frac * N[era]["inclusive"] * negative_fraction[era]["inclusive"],
            ]
        )

    sign = "(((genWeight < 0) * (-1)) + ((genWeight >= 0) * (1)))"
    inclusive = xsec_inclusive * (N[era]["inclusive"] * negative_fraction[era]["inclusive"]) ** (-1)
    category_wise_reweighting = " + ".join(
        [
            f"(({_stxs_bin_or_range(100)}) * ({inclusive}))",
            f"(({_stxs_bin_or_range(101)}) * ({inclusive_and_extended(101)}))",
            f"(({_stxs_bin_or_range(102)}) * ({inclusive}))",
            f"(({_stxs_bin_or_range(103)}) * ({inclusive}))",
            f"(({_stxs_bin_or_range(104, 105)}) * ({inclusive_and_extended(104, 105)}))",
            f"(({_stxs_bin_or_range(106)}) * ({inclusive_and_extended(106)}))",
            f"(({_stxs_bin_or_range(107, 109)}) * ({inclusive_and_extended(107, 109)}))",
            f"(({_stxs_bin_or_range(110, 113)}) * ({inclusive_and_extended(110, 113)}))",
            f"(({_stxs_bin_or_range(114)}) * ({inclusive}))",
            f"(({_stxs_bin_or_range(115)}) * ({inclusive}))",
            f"(({_stxs_bin_or_range(116)}) * ({inclusive}))",
        ]
    )

    return (f"(({sign}) * ({category_wise_reweighting}))", "ggh_stitching_weight")


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


def ggH125_process_selection(channel, era, vs_jet_wp, vs_ele_wp, weight_stitching_ggH125=True, **kwargs):
    ggH125_weights = HTT_base_process_selection(channel, era, vs_jet_wp, vs_ele_wp).weights
    
    if weight_stitching_ggH125:
        ggH125_weights.append(ggh_stitching_weight(era))
    else:
        ggH125_weights.extend(
            [
                ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
                (
                    "(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight",
                    "crossSectionPerEventWeight",
                ),
            ]
        )
    
    ggH125_weights.append(("ggh_NNLO_weight", "gghNNLO"))

    ggH125_cuts = [
        (
            "(HTXS_stage1_2_cat_pTjet30GeV>=100)&&(HTXS_stage1_2_cat_pTjet30GeV<=116)",
            "htxs",
        )
    ]
    return Selection(name="ggH125", weights=ggH125_weights, cuts=ggH125_cuts)


def _get_ggH125_bin_selection(*bins):
    _bin = f"bin{bins[0]}" if len(bins) == 1 else f"bin{bins[0]}to{bins[-1]}"
    with LogContext(logger).suppress_logging():
        def _selection(**kwargs):
            return Selection(name=f"ggH125_{_bin}_selection", cuts=[(_stxs_bin_or_range(*bins), f"ggH125_{_bin}_selection")])
        _selection.__name__ = f"ggH125_{_bin}_selection"
    return _selection


def qqH125_process_selection(channel, era, vs_jet_wp, vs_ele_wp, **kwargs):
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
DY = DY_process_selection
DY_NLO = DY_NLO_process_selection
TT = TT_process_selection
VV = VV_process_selection
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
VVT = VVT_process_selection
VVL = VVL_process_selection
VVJ = VVJ_process_selection
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

ggH125_inclusive = _get_ggH125_bin_selection(100, 116)
ggH125_100 = _get_ggH125_bin_selection(100)
ggH125_101 = _get_ggH125_bin_selection(101)
ggH125_102 = _get_ggH125_bin_selection(102)
ggH125_103 = _get_ggH125_bin_selection(103)
ggH125_104 = _get_ggH125_bin_selection(104)
ggH125_105 = _get_ggH125_bin_selection(105)
ggH125_106 = _get_ggH125_bin_selection(106)
ggH125_107 = _get_ggH125_bin_selection(107)
ggH125_108 = _get_ggH125_bin_selection(108)
ggH125_109 = _get_ggH125_bin_selection(109)
ggH125_110 = _get_ggH125_bin_selection(110)
ggH125_111 = _get_ggH125_bin_selection(111)
ggH125_112 = _get_ggH125_bin_selection(112)
ggH125_113 = _get_ggH125_bin_selection(113)
ggH125_114 = _get_ggH125_bin_selection(114)
ggH125_115 = _get_ggH125_bin_selection(115)
ggH125_116 = _get_ggH125_bin_selection(116)

