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


def lumi_weight(era):
    if era == "2016":
        lumi = "36.33"  # "36.326450080"
    elif era == "2017":
        lumi = "41.529"
    elif era == "2018":
        lumi = "59.83"
    else:
        raise ValueError("Given era {} not defined.".format(era))
    return ("{} * 1000.0".format(lumi), "lumi")



def MC_base_process_selection(channel, era, boosted_tau=False):
    if channel == "et":
        if not boosted_tau:
            isoweight = ("iso_wgt_ele_1", "isoweight")
            idweight = ("id_wgt_ele_1", "idweight")
            tauidweight = (
                "((gen_match_2==5)*id_wgt_tau_vsJet_Medium_2 + (gen_match_2!=5))",
                "taubyIsoIdWeight",
            )
            vsmu_weight = ("((gen_match_2==5)*id_wgt_tau_vsMu_VLoose_2 + (gen_match_2!=5))", "vsmuweight")
            vsele_weight = ("((gen_match_2==5)*id_wgt_tau_vsEle_Tight_2 + (gen_match_2!=5))", "vseleweight")
            if era == "2017":
                trgweight = ("((pt_1>=33&&pt_1<36)*trg_wgt_single_ele32)+((pt_1>=36)*trg_wgt_single_ele35)", "trgweight")
            elif era == "2018":
                trgweight = ("trg_wgt_single_ele32orele35", "trgweight")
        elif boosted_tau:
            isoweight = ("iso_wgt_ele_boosted_1", "isoweight")
            idweight = ("id_wgt_ele_boosted_1", "idweight")
            tauidweight = (
                "((boosted_gen_match_2==5)*id_wgt_boostedtau_iso_Loose_2 + (boosted_gen_match_2!=5))",
                "taubyIsoIdWeight",
            )
            vsmu_weight = None # ("((boosted_gen_match_2==5)*id_wgt_tau_antiMu_Loose_2 + (boosted_gen_match_2!=5))", "vsmuweight")
            vsele_weight = ("((boosted_gen_match_2==5)*id_wgt_tau_antiEle_Loose_2 + (boosted_gen_match_2!=5))", "vseleweight")
            trgweight = None
    elif channel == "mt":
        if not boosted_tau:
            isoweight = ("iso_wgt_mu_1", "isoweight")
            idweight = ("id_wgt_mu_1", "idweight")
            tauidweight = (
                "((gen_match_2==5)*id_wgt_tau_vsJet_Medium_2 + (gen_match_2!=5))",
                "taubyIsoIdWeight",
            )
            vsmu_weight = ("((gen_match_2==5)*id_wgt_tau_vsMu_Tight_2 + (gen_match_2!=5))", "vsmuweight")
            vsele_weight = ("((gen_match_2==5)*id_wgt_tau_vsEle_VVLoose_2 + (gen_match_2!=5))", "vseleweight")
            if era == "2017":
                trgweight = ("((pt_1>28)* trg_wgt_single_mu27)", "trgweight")
            elif era == "2018":
                trgweight = ("trg_wgt_single_mu24ormu27", "trgweight")
        elif boosted_tau:
            isoweight = ("iso_wgt_mu_boosted_1", "isoweight")
            idweight = ("id_wgt_mu_boosted_1", "idweight")
            tauidweight = (
                "((boosted_gen_match_2==5)*id_wgt_boostedtau_iso_Loose_2 + (boosted_gen_match_2!=5))",
                "taubyIsoIdWeight",
            )
            vsmu_weight = ("((boosted_gen_match_2==5)*id_wgt_tau_antiMu_Loose_2 + (boosted_gen_match_2!=5))", "vsmuweight")
            vsele_weight = ("((boosted_gen_match_2==5)*id_wgt_tau_antiEle_VLoose_2 + (boosted_gen_match_2!=5))", "vseleweight")
            trgweight = None
    elif channel == "tt":
        if not boosted_tau:
            isoweight = None
            idweight = None
            tauidweight = (
                "((gen_match_1==5)*id_wgt_tau_vsJet_Medium_1 + (gen_match_1!=5)) * ((gen_match_2==5)*id_wgt_tau_vsJet_Medium_2 + (gen_match_2!=5))",
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
        elif boosted_tau:
            isoweight = None
            idweight = None
            tauidweight = (
                "((boosted_gen_match_1==5)*id_wgt_boostedtau_iso_Loose_1 + (boosted_gen_match_1!=5)) * ((boosted_gen_match_2==5)*id_wgt_boostedtau_iso_Loose_2 + (boosted_gen_match_2!=5))",
                "taubyIsoIdWeight",
            )
            vsmu_weight = None # (
            #     "((boosted_gen_match_1==5)*id_wgt_tau_antiMu_Loose_1 + (boosted_gen_match_1!=5)) * ((boosted_gen_match_2==5)*id_wgt_tau_antiMu_Loose_2 + (boosted_gen_match_2!=5))",
            #     "vsmuweight",
            # )
            vsele_weight = None # (
            #     "((boosted_gen_match_1==5)*id_wgt_tau_antiEle_VLoose_1 + (boosted_gen_match_1!=5)) * ((boosted_gen_match_2==5)*id_wgt_tau_antiEle_VLoose_2 + (boosted_gen_match_2!=5))",
            #     "vseleweight",
            # )
            trgweight = None
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
    ]
    return Selection(name="MC base", weights=[weight for weight in MC_base_process_weights if weight is not None])


def dy_stitching_weight(era):
    if era == "2017":
        weight = (
            "((genbosonmass >= 50.0)*0.0000298298*((npartons == 0 || npartons >= 5)*1.0 + (npartons == 1)*0.3478960398 + (npartons == 2)*0.2909516577 + (npartons == 3)*0.1397995594 + (npartons == 4)*0.1257217076) + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)",
            "dy_stitching_weight",
            )
        # xsec_NNLO [pb] = , N_inclusive = 203,729,540, xsec_NNLO/N_inclusive = 0.0000298298 [pb], weights: [1.0, 0.3478960398, 0.2909516577, 0.1397995594, 0.1257217076]
    elif era == "2018":
        weight = (
            "( (genbosonmass>=50.0)*0.0000631493*( ((npartons<=0) || (npartons>=5))*1.0 + (npartons==1)*0.2056921342 + (npartons==2)*0.1664121306 + (npartons==3)*0.0891121485 + (npartons==4)*0.0843396952 ) + (genbosonmass<50.0) * numberGeneratedEventsWeight * crossSectionPerEventWeight * (( 1.0 / negative_events_fraction) * ( ((genWeight<0) * -1) + ((genWeight>=0) * 1))))",
            "dy_stitching_weight",
        )
        # xsec_NNLO [pb] = 2025.74*3, N_inclusive = 100194597,  xsec_NNLO/N_inclusive = 0.0000606542 [pb] weights: [1.0, 0.194267667208, 0.21727746547, 0.26760465744, 0.294078683662]
    else:
        raise ValueError("DY stitching weight not defined for era {}".format(era))

    return weight


def DY_process_selection(channel, era):
    DY_process_weights = MC_base_process_selection(channel, era).weights
    if era == "2017":
        gen_events_weight = ("(1./203729540)*(genbosonmass >= 50.0) + (genbosonmass < 50.0)*numberGeneratedEventsWeight", "numberGeneratedEventsWeight")
    elif era == "2018":
        gen_events_weight = ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight")
        xsec_events_weight = ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight")
    DY_process_weights.extend(
        [
            # gen_events_weight,
            # xsec_events_weight,
            dy_stitching_weight(era), 
            ("ZPtMassReweightWeight", "zPtReweightWeight"),
        ]
    )
    return Selection(name="DY", weights=DY_process_weights)


def DY_NLO_process_selection(channel, era):
    DY_process_weights = MC_base_process_selection(channel, era).weights
    DY_process_weights.extend(
        [
            # ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            # ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
            dy_stitching_weight(era),  
            ("ZPtMassReweightWeight", "zPtReweightWeight"),
        ]
    )
    return Selection(name="DY_NLO", weights=DY_process_weights)


def TT_process_selection(channel, era):
    TT_process_weights = MC_base_process_selection(channel, era).weights
    TT_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
            ("topPtReweightWeight", "topPtReweightWeight"),
        ]
    )
    return Selection(name="TT", weights=TT_process_weights)


def ST_process_selection(channel, era):
    ST_process_weights = MC_base_process_selection(channel, era).weights
    ST_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
        ]
    )
    return Selection(name="ST", weights=ST_process_weights)


def VV_process_selection(channel, era):
    VV_process_weights = MC_base_process_selection(channel, era).weights
    VV_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
        ]
    )
    return Selection(name="VV", weights=VV_process_weights)


def W_stitching_weight(era):
    if era == "2018":
        weight = (
            "(0.0007590865*( ((npartons<=0) || (npartons>=5))*1.0 + (npartons==1)*0.2191273680 + (npartons==2)*0.1335837379 + (npartons==3)*0.0636217909 + (npartons==4)*0.0823135765 ))",
            "wj_stitching_weight",
        )
        # xsec_NNLO [pb] = 61526.7, N_inclusive = 71026861, xsec_NNLO/N_inclusive = 0.0008662455 [pb] weights: [1.0, 0.1741017559343336, 0.13621263074538312, 0.08156674151214884, 0.06721295702670023]
    else:
        raise ValueError("W stitching weight not defined for era {}".format(era))
    return weight


def W_process_selection(channel, era, boosted_tau=False):
    W_process_weights = MC_base_process_selection(channel, era).weights
    # W_process_weights.extend(
    #     [
    #         ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
    #         ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
    #     ]
    # )
    W_process_weights.append(W_stitching_weight(era)) 
    btag_weight = ""
    if not boosted_tau:
        if "et" in channel:
            btag_weight = ("0.995256*btag_weight", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("0.995653*btag_weight", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("0.996317*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "et" in channel:
            btag_weight = ("0.988039*btag_weight_boosted", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    W_process_weights.append(btag_weight)

    return Selection(name="W", weights=W_process_weights)


def HTT_base_process_selection(channel, era):
    return Selection(
        name="HTT_base", weights=MC_base_process_selection(channel, era).weights
    )


def HTT_process_selection(channel, era):
    HTT_weights = HTT_base_process_selection(channel, era).weights + [
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
    ]
    return Selection(name="HTT", weights=HTT_weights)


# This could eventually be used for all HWW estimations if necessary. At the moment this is not possible due to wrong cross section weights in 2018.
# If the additional processes are required new functions would need to be implemented.
def HWW_process_selection(channel, era):
    HWW_process_weights = MC_base_process_selection(channel, era).weights
    HWW_process_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
        ]
    )
    return Selection(name="HWW", weights=HWW_process_weights)


def HWW_base_process_selection(channel, era):
    HWW_base_process_weights = MC_base_process_selection(channel, era).weights + [
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
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


# def DY_process_selection(channel, era):
#     DY_process_weights = DY_base_process_selection(channel, era).weights
#     DY_process_weights.append((
#         "((genbosonmass >= 50.0)*6.2139e-05*((npartons == 0 || npartons >= 5)*1.0 + (npartons == 1)*0.1743 + (npartons == 2)*0.3556 + (npartons == 3)*0.2273 + (npartons == 4)*0.2104) + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)","z_stitching_weight"))
#     return Selection(name = "DY",
#                      weights = DY_process_weights)


# def DY_nlo_process_selection(channel, era):
#     DY_nlo_process_weights = DY_base_process_selection(channel, era).weights
#     DY_nlo_process_weights.append(
#         (
#             "((genbosonmass >= 50.0) * 2.8982e-05 + (genbosonmass < 50.0)*numberGeneratedEventsWeight*crossSectionPerEventWeight)",
#             "z_stitching_weight",
#         )
#     )
#     return Selection(name="DY_nlo", weights=DY_nlo_process_weights)


def ZTT_process_selection(channel, boosted_tau=False):
    tt_cut = __get_ZTT_cut(channel, boosted_tau=False)
    btag_weight = ""
    if not boosted_tau:
        if "et" in channel:
            btag_weight = ("0.995725*btag_weight", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("0.996964*btag_weight", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("0.993891*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "et" in channel:
            btag_weight = ("0.946104*btag_weight_boosted", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(name="ZTT", cuts=[(tt_cut, "ztt_cut")], weights=[btag_weight])


def ZTT_nlo_process_selection(channel, boosted_tau=False):
    tt_cut = __get_ZTT_cut(channel, boosted_tau=False)
    return Selection(name="ZTT_nlo", cuts=[(tt_cut, "ztt_cut")])


def __get_ZTT_cut(channel, boosted_tau=False):
    if not boosted_tau:
        if "mt" in channel:
            return "gen_match_1==4 && gen_match_2==5"
        elif "et" in channel:
            return "gen_match_1==3 && gen_match_2==5"
        elif "tt" in channel:
            return "gen_match_1==5 && gen_match_2==5"
    elif boosted_tau:
        if "mt" in channel:
            return "boosted_gen_match_1==4 && boosted_gen_match_2==5"
        elif "et" in channel:
            return "boosted_gen_match_1==3 && boosted_gen_match_2==5"
        elif "tt" in channel:
            return "boosted_gen_match_1==5 && boosted_gen_match_2==5"

def ZTT_embedded_process_selection(channel, era, boosted_tau=False):
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
                    # ("((gen_match_2==5)*id_wgt_tau_vsJet_Tight_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                ]
            )
        elif era == "2018":
            if not boosted_tau:
                ztt_embedded_weights.extend(
                    [
                        ("gen_match_1==4 && gen_match_2==5", "emb_veto"),
                        ("iso_wgt_mu_1", "isoweight"),
                        ("id_wgt_mu_1", "idweight"),
                        ("trg_wgt_single_mu24ormu27", "trgweight"),
                        ("((gen_match_2==5)*id_wgt_tau_vsJet_Medium_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                    ]
                )
            elif boosted_tau:
                ztt_embedded_weights.extend(
                    [
                        ("boosted_gen_match_1==4 && boosted_gen_match_2==5", "emb_veto"),
                        ("iso_wgt_mu_boosted_1", "isoweight"),
                        ("id_wgt_mu_boosted_1", "idweight"),
                        # ("((boosted_gen_match_2==5)*id_wgt_boostedtau_iso_Loose_2 + (boosted_gen_match_2!=5))", "taubyIsoIdWeight")
                    ]
                )
        else:
            raise ValueError(f"Embedded process selection for given era {era} not yet implemented")
    elif "et" in channel:
        if era == "2017":
            ztt_embedded_weights.extend(
                [
                    ("gen_match_1==3 && gen_match_2==5", "emb_veto"),
                    ("iso_wgt_ele_1", "isoweight"),
                    ("id_wgt_ele_1", "idweight"),
                    #("trg_wgt_single_ele35", "trgweight"),
                    ("((pt_1>=33&&pt_1<36)*trg_wgt_single_ele32)+((pt_1>=36)*trg_wgt_single_ele35)", "trgweight"),
                    # ("((gen_match_2==5)*id_wgt_tau_vsJet_Tight_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                ]
            )
        elif era == "2018":
            if not boosted_tau:
                ztt_embedded_weights.extend(
                    [
                        ("gen_match_1==3 && gen_match_2==5", "emb_veto"),
                        ("iso_wgt_ele_1", "isoweight"),
                        ("id_wgt_ele_1", "idweight"),
                        ("trg_wgt_single_ele32orele35", "trgweight"),
                        ("((gen_match_2==5)*id_wgt_tau_vsJet_Medium_2 + (gen_match_2!=5))", "taubyIsoIdWeight")
                    ]
                )
            elif boosted_tau:
                ztt_embedded_weights.extend(
                    [
                        ("boosted_gen_match_1==3 && boosted_gen_match_2==5", "emb_veto"),
                        ("iso_wgt_ele_boosted_1", "isoweight"),
                        ("id_wgt_ele_boosted_1", "idweight"),
                        # ("((boosted_gen_match_2==5)*id_wgt_boostedtau_iso_Loose_2 + (boosted_gen_match_2!=5))", "taubyIsoIdWeight")
                    ]
                )
        else:
            raise ValueError(f"Embedded process selection for given era {era} not yet implemented")
    elif "tt" in channel:
        if not boosted_tau:
            ztt_embedded_weights.extend(
                [
                    ("gen_match_1==5 && gen_match_2==5", "emb_veto"),
                    ("emb_trg_wgt_1 * emb_trg_wgt_2", "trgweight"),
                    (
                        "((gen_match_1==5)*id_wgt_tau_vsJet_Medium_1 + (gen_match_1!=5)) * ((gen_match_2==5)*id_wgt_tau_vsJet_Medium_2 + (gen_match_2!=5))",
                        "taubyIsoIdWeight",
                    ), 
                ]
            )
        elif boosted_tau:
            ztt_embedded_weights.extend(
                [
                    ("boosted_gen_match_1==5 && boosted_gen_match_2==5", "emb_veto"),
                    # (
                    #     "((boosted_gen_match_1==5)*id_wgt_boostedtau_iso_Loose_1 + (boosted_gen_match_1!=5)) * ((boosted_gen_match_2==5)*id_wgt_boostedtau_iso_Loose_2 + (boosted_gen_match_2!=5))",
                    #     "taubyIsoIdWeight",
                    # ), 
                ]
            )

    if not boosted_tau:
        ztt_embedded_cuts = [
            (
                "((gen_match_1>2 && gen_match_1<6) && (gen_match_2>2 && gen_match_2<6))",
                "dy_genuine_tau",
            )
        ]
    elif boosted_tau:
        ztt_embedded_cuts = [
            (
                "((boosted_gen_match_1>2 && boosted_gen_match_1<6) && (boosted_gen_match_2>2 && boosted_gen_match_2<6))",
                "dy_genuine_tau",
            )
        ]
    return Selection(
        name="Embedded", cuts=ztt_embedded_cuts if channel not in ["mm", "ee"] else [], weights=ztt_embedded_weights
    )


def ZL_process_selection(channel, boosted_tau=False):
    veto = __get_ZL_cut(channel, boosted_tau=False)
    btag_weight = ""
    if not boosted_tau:
        if "et" in channel:
            btag_weight = ("0.996615*btag_weight", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("0.994832*btag_weight", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("0.996646*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "et" in channel:
            btag_weight = ("0.962257*btag_weight_boosted", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(
        name="ZL",
        cuts=[("{}".format(veto[0]), "dy_emb_veto"), ("{}".format(veto[1]), "ff_veto")],
        weights=[btag_weight],
    )


def ZL_nlo_process_selection(channel, boosted_tau=False):
    veto = __get_ZL_cut(channel, boosted_tau=False)
    return Selection(
        name="ZL_nlo",
        cuts=[("{}".format(veto[0]), "dy_emb_veto"), ("{}".format(veto[1]), "ff_veto")],
    )


def __get_ZL_cut(channel, boosted_tau=False):
    emb_veto = ""
    ff_veto = ""
    if not boosted_tau:
        if "mt" in channel:
            emb_veto = "!(gen_match_1==4 && gen_match_2==5)"
            ff_veto = "!(gen_match_2 == 6)"
        elif "et" in channel:
            emb_veto = "!(gen_match_1==3 && gen_match_2==5)"
            ff_veto = "!(gen_match_2 == 6)"
        elif "tt" in channel:
            emb_veto = "!(gen_match_1==5 && gen_match_2==5)"
            ff_veto = "!(gen_match_1 == 6 || gen_match_2 == 6)"
    elif boosted_tau:
        if "mt" in channel:
            emb_veto = "!(boosted_gen_match_1==4 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_2 == 6)"
        elif "et" in channel:
            emb_veto = "!(boosted_gen_match_1==3 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_2 == 6)"
        elif "tt" in channel:
            emb_veto = "!(boosted_gen_match_1==5 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_1 == 6 || boosted_gen_match_2 == 6)"
    return (emb_veto, ff_veto)


def ZJ_process_selection(channel, boosted_tau=False):
    veto = __get_ZJ_cut(channel, boosted_tau=False)
    btag_weight = ""
    if not boosted_tau:
        if "et" in channel:
            btag_weight = ("0.971493*btag_weight", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("0.988512*btag_weight", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("0.964894*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "et" in channel:
            btag_weight = ("0.928060*btag_weight_boosted", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(name="ZJ", cuts=[(__get_ZJ_cut(channel), "dy_fakes")], weights=[btag_weight])


def ZJ_nlo_process_selection(channel, boosted_tau=False):
    veto = __get_ZJ_cut(channel, boosted_tau=False)
    return Selection(name="ZJ_nlo", cuts=[(__get_ZJ_cut(channel), "dy_fakes")])


def __get_ZJ_cut(channel, boosted_tau=False):
    if not boosted_tau:
        if "mt" in channel or "et" in channel:
            return "gen_match_2 == 6"
        elif "tt" in channel:
            return "(gen_match_1 == 6 || gen_match_2 == 6)"
        else:
            return ""
    elif boosted_tau:
        if "mt" in channel or "et" in channel:
            return "boosted_gen_match_2 == 6"
        elif "tt" in channel:
            return "(boosted_gen_match_1 == 6 || boosted_gen_match_2 == 6)"
        else:
            return ""

def TTT_process_selection(channel, boosted_tau=False):
    tt_cut = ""
    btag_weight = ""
    if not boosted_tau:
        if "mt" in channel:
            tt_cut = "gen_match_1==4 && gen_match_2==5"
            btag_weight = ("1.003354*btag_weight", "btagging_weight")
        elif "et" in channel:
            tt_cut = "gen_match_1==3 && gen_match_2==5"
            btag_weight = ("1.001670*btag_weight", "btagging_weight")
        elif "tt" in channel:
            tt_cut = "gen_match_1==5 && gen_match_2==5"
            btag_weight = ("1.004327*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "mt" in channel:
            tt_cut = "boosted_gen_match_1==4 && boosted_gen_match_2==5"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "et" in channel:
            tt_cut = "boosted_gen_match_1==3 && boosted_gen_match_2==5"
            btag_weight = ("0.964945*btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            tt_cut = "boosted_gen_match_1==5 && boosted_gen_match_2==5"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(name="TTT", cuts=[(tt_cut, "ttt_cut")], weights=[btag_weight])


def TTL_process_selection(channel, boosted_tau=False):
    emb_veto = ""
    ff_veto = ""
    btag_weight = ""
    if not boosted_tau:
        if "mt" in channel:
            emb_veto = "!(gen_match_1==4 && gen_match_2==5)"
            ff_veto = "!(gen_match_2 == 6)"
            btag_weight = ("1.003343*btag_weight", "btagging_weight")
        elif "et" in channel:
            emb_veto = "!(gen_match_1==3 && gen_match_2==5)"
            ff_veto = "!(gen_match_2 == 6)"
            btag_weight = ("1.002875*btag_weight", "btagging_weight")
        elif "tt" in channel:
            emb_veto = "!(gen_match_1==5 && gen_match_2==5)"
            ff_veto = "!(gen_match_1 == 6 || gen_match_2 == 6)"
            btag_weight = ("1.006854*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "mt" in channel:
            emb_veto = "!(boosted_gen_match_1==4 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "et" in channel:
            emb_veto = "!(boosted_gen_match_1==3 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_2 == 6)"
            btag_weight = ("0.985751*btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            emb_veto = "!(boosted_gen_match_1==5 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_1 == 6 || boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(
        name="TTL",
        cuts=[
            ("{}".format(emb_veto), "tt_emb_veto"),
            ("{}".format(ff_veto), "ff_veto"),
        ],
        weights=[btag_weight],
    )


def TTJ_process_selection(channel, boosted_tau=False):
    ct = ""
    btag_weight = ""
    if not boosted_tau:
        if "mt" in channel:
            ct = "(gen_match_2 == 6)"
            btag_weight = ("0.996539*btag_weight", "btagging_weight")
        elif "et" in channel:
            ct = "(gen_match_2 == 6)"
            btag_weight = ("0.997063*btag_weight", "btagging_weight")
        elif "tt" in channel:
            ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
            btag_weight = ("0.999434*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "mt" in channel:
            ct = "(boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "et" in channel:
            ct = "(boosted_gen_match_2 == 6)"
            btag_weight = ("0.981112*btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            ct = "(boosted_gen_match_1 == 6 || boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(name="TTJ", cuts=[(ct, "tt_fakes")], weights=[btag_weight])


def STT_process_selection(channel, boosted_tau=False):
    tt_cut = ""
    btag_weight = ""
    if not boosted_tau:
        if "mt" in channel:
            tt_cut = "gen_match_1==4 && gen_match_2==5"
            btag_weight = ("1.002667*btag_weight", "btagging_weight")
        elif "et" in channel:
            tt_cut = "gen_match_1==3 && gen_match_2==5"
            btag_weight = ("0.996035*btag_weight", "btagging_weight")
        elif "tt" in channel:
            tt_cut = "gen_match_1==5 && gen_match_2==5"
            btag_weight = ("0.999741*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "mt" in channel:
            tt_cut = "boosted_gen_match_1==4 && boosted_gen_match_2==5"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "et" in channel:
            tt_cut = "boosted_gen_match_1==3 && boosted_gen_match_2==5"
            btag_weight = ("1.111998*btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            tt_cut = "boosted_gen_match_1==5 && boosted_gen_match_2==5"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(name="STT", cuts=[(tt_cut, "stt_cut")], weights=[btag_weight])


def STL_process_selection(channel, boosted_tau=False):
    emb_veto = ""
    ff_veto = ""
    btag_weight = ""
    if not boosted_tau:
        if "mt" in channel:
            emb_veto = "!(gen_match_1==4 && gen_match_2==5)"
            ff_veto = "!(gen_match_2 == 6)"
            btag_weight = ("1.002659*btag_weight", "btagging_weight")
        elif "et" in channel:
            emb_veto = "!(gen_match_1==3 && gen_match_2==5)"
            ff_veto = "!(gen_match_2 == 6)"
            btag_weight = ("1.002656*btag_weight", "btagging_weight")
        elif "tt" in channel:
            emb_veto = "!(gen_match_1==5 && gen_match_2==5)"
            ff_veto = "!(gen_match_1 == 6 || gen_match_2 == 6)"
            btag_weight = ("1.018794*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "mt" in channel:
            emb_veto = "!(boosted_gen_match_1==4 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "et" in channel:
            emb_veto = "!(boosted_gen_match_1==3 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_2 == 6)"
            btag_weight = ("0.995524*btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            emb_veto = "!(boosted_gen_match_1==5 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_1 == 6 || boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(
        name="STL",
        cuts=[
            ("{}".format(emb_veto), "st_emb_veto"),
            ("{}".format(ff_veto), "ff_veto"),
        ],
        weights=[btag_weight],
    )


def STJ_process_selection(channel, boosted_tau=False):
    ct = ""
    btag_weight = ""
    if not boosted_tau:
        if "mt" in channel:
            ct = "(gen_match_2 == 6)"
            btag_weight = ("1.003108*btag_weight", "btagging_weight")
        elif "et" in channel:
            ct = "(gen_match_2 == 6)"
            btag_weight = ("1.000190*btag_weight", "btagging_weight")
        elif "tt" in channel:
            ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
            btag_weight = ("1.004701*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "mt" in channel:
            ct = "(boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "et" in channel:
            ct = "(boosted_gen_match_2 == 6)"
            btag_weight = ("0.980138*btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            ct = "(boosted_gen_match_1 == 6 || boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(name="STJ", cuts=[(ct, "st_fakes")], weights=[btag_weight])


def VVT_process_selection(channel, boosted_tau=False):
    tt_cut = ""
    btag_weight = ""
    if not boosted_tau:
        if "mt" in channel:
            tt_cut = "gen_match_1==4 && gen_match_2==5"
            btag_weight = ("0.988705*btag_weight", "btagging_weight")
        elif "et" in channel:
            tt_cut = "gen_match_1==3 && gen_match_2==5"
            btag_weight = ("0.989048*btag_weight", "btagging_weight")
        elif "tt" in channel:
            tt_cut = "gen_match_1==5 && gen_match_2==5"
            btag_weight = ("0.983496*btag_weight", "btagging_weight")
    if boosted_tau:
        if "mt" in channel:
            tt_cut = "boosted_gen_match_1==4 && boosted_gen_match_2==5"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "et" in channel:
            tt_cut = "boosted_gen_match_1==3 && boosted_gen_match_2==5"
            btag_weight = ("0.937946*btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            tt_cut = "boosted_gen_match_1==5 && boosted_gen_match_2==5"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(name="VVT", cuts=[(tt_cut, "vvt_cut")], weights=[btag_weight])


def VVJ_process_selection(channel, boosted_tau=False):
    ct = ""
    btag_weight = ""
    if not boosted_tau:
        if "mt" in channel:
            ct = "(gen_match_2 == 6)"
            btag_weight = ("0.998744*btag_weight", "btagging_weight")
        elif "et" in channel:
            ct = "(gen_match_2 == 6)"
            btag_weight = ("0.994748*btag_weight", "btagging_weight")
        elif "tt" in channel:
            ct = "(gen_match_1 == 6 || gen_match_2 == 6)"
            btag_weight = ("0.987639*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "mt" in channel:
            ct = "(boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "et" in channel:
            ct = "(boosted_gen_match_2 == 6)"
            btag_weight = ("0.940127*btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            ct = "(boosted_gen_match_1 == 6 || boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(name="VVJ", cuts=[(ct, "vv_fakes")], weights=[btag_weight])


def VVL_process_selection(channel, boosted_tau=False):
    emb_veto = ""
    ff_veto = ""
    btag_weight = ""
    if not boosted_tau:
        if "mt" in channel:
            emb_veto = "!(gen_match_1==4 && gen_match_2==5)"
            ff_veto = "!(gen_match_2 == 6)"
            btag_weight = ("0.993716*btag_weight", "btagging_weight")
        elif "et" in channel:
            emb_veto = "!(gen_match_1==3 && gen_match_2==5)"
            ff_veto = "!(gen_match_2 == 6)"
            btag_weight = ("0.993561*btag_weight", "btagging_weight")
        elif "tt" in channel:
            emb_veto = "!(gen_match_1==5 && gen_match_2==5)"
            ff_veto = "!(gen_match_1 == 6 || gen_match_2 == 6)"
            btag_weight = ("0.995844*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "mt" in channel:
            emb_veto = "!(boosted_gen_match_1==4 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "et" in channel:
            emb_veto = "!(boosted_gen_match_1==3 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_2 == 6)"
            btag_weight = ("0.947681*btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            emb_veto = "!(boosted_gen_match_1==5 && boosted_gen_match_2==5)"
            ff_veto = "!(boosted_gen_match_1 == 6 || boosted_gen_match_2 == 6)"
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    return Selection(
        name="VVL",
        cuts=[
            ("{}".format(emb_veto), "vv_emb_veto"),
            ("{}".format(ff_veto), "ff_veto"),
        ],
        weights=[btag_weight],
    )


def VH_process_selection(channel, era):
    return Selection(
        name="VH125",
        weights=HTT_process_selection(channel, era).weights,
        cuts=[
            # (
            #     "(HTXS_stage1_2_cat_pTjet30GeV>=300)&&(HTXS_stage1_2_cat_pTjet30GeV<=505)",
            #     "htxs_match",
            # )
        ],
    )


def WH_process_selection(channel, era):
    return Selection(
        name="WH125",
        weights=HTT_base_process_selection(channel, era).weights
        + [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            (
                "(abs(crossSectionPerEventWeight - 0.052685) < 0.001)*0.051607+"
                "(abs(crossSectionPerEventWeight - 0.03342) < 0.001)*0.032728576",
                "crossSectionPerEventWeight",
            ),
        ],
        cuts=[
            # (
            #     "(HTXS_stage1_2_cat_pTjet30GeV>=300)&&(HTXS_stage1_2_cat_pTjet30GeV<=305)",
            #     "htxs_match",
            # )
        ],
    )


def ZH_process_selection(channel, era):
    return Selection(
        name="ZH125",
        weights=HTT_base_process_selection(channel, era).weights
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
            # (
            #     "(HTXS_stage1_2_cat_pTjet30GeV>=400)&&(HTXS_stage1_2_cat_pTjet30GeV<=405)",
            #     "htxs_match",
            # )
        ],
    )


def ttH_process_selection(channel, era):
    ttH_weights = HTT_process_selection(channel, era).weights
    return Selection(name="ttH125", weights=ttH_weights)


def ggHWW_process_selection(channel, era):
    if era in ["2016", "2017"]:
        ggHWW_weights = HWW_base_process_selection(channel, era).weights
    else:
        ggHWW_weights = MC_base_process_selection(channel, era).weights + [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("1.1019558", "crossSectionPerEventWeight"),
        ]
    return Selection(name="ggHWW125", weights=ggHWW_weights)


def qqHWW_process_selection(channel, era):
    if era in ["2016", "2017"]:
        qqHWW_weights = HWW_base_process_selection(channel, era).weights
    else:
        qqHWW_weights = MC_base_process_selection(channel, era).weights + [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("0.0857883", "crossSectionPerEventWeight"),
        ]
    return Selection(name="qqHWW125", weights=qqHWW_weights)


def WHWW_process_selection(channel, era):
    WHWW_weights = HWW_base_process_selection(channel, era).weights
    return Selection(name="WHWW125", weights=WHWW_weights)


def ZHWW_process_selection(channel, era):
    ZHWW_weights = HWW_base_process_selection(channel, era).weights
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


def ggH125_process_selection(channel, era, boosted_tau=False):
    ggH125_weights = HTT_base_process_selection(channel, era).weights + [
        # ("ggh_NNLO_weight", "gghNNLO"),
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
        # ggh_stitching_weight(era),
    ]
    btag_weight = ""
    if not boosted_tau:
        if "et" in channel:
            btag_weight = ("0.994928*btag_weight", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("0.995716*btag_weight", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("0.993979*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "et" in channel:
            btag_weight = ("0.925884*btag_weight_boosted", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    ggH125_weights.append(btag_weight)
    ggH125_cuts = [
        # (
        #     "(HTXS_stage1_2_cat_pTjet30GeV>=100)&&(HTXS_stage1_2_cat_pTjet30GeV<=113)",
        #     "htxs",
        # )
    ]
    return Selection(name="ggH125", weights=ggH125_weights, cuts=ggH125_cuts)


def qqH125_process_selection(channel, era, boosted_tau=False):
    qqH125_weights = HTT_base_process_selection(channel, era).weights + [
        # qqh_stitching_weight(era)
        ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
        ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
    ]
    btag_weight = ""
    if not boosted_tau:
        if "et" in channel:
            btag_weight = ("0.986513*btag_weight", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("0.987531*btag_weight", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("0.982555*btag_weight", "btagging_weight")
    elif boosted_tau:
        if "et" in channel:
            btag_weight = ("0.921058*btag_weight_boosted", "btagging_weight")
        elif "mt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
        elif "tt" in channel:
            btag_weight = ("btag_weight_boosted", "btagging_weight")
    qqH125_weights.append(btag_weight)
    qqH125_cuts = [
        # (
        #     "(HTXS_stage1_2_cat_pTjet30GeV>=200)&&(HTXS_stage1_2_cat_pTjet30GeV<=210)",
        #     "qqH125",
        # )
    ]
    return Selection(name="qqH125", weights=qqH125_weights, cuts=qqH125_cuts)


def NMSSM_process_selection(channel,era):
    NMSSM_weights = MC_base_process_selection(channel, era).weights
    NMSSM_weights.extend(
        [
            ("numberGeneratedEventsWeight", "numberGeneratedEventsWeight"),
            ("(( 1.0 / negative_events_fraction) * (((genWeight<0) * -1) + ((genWeight > 0 * 1)))) * crossSectionPerEventWeight", "crossSectionPerEventWeight"),
            ("btag_weight", "btagging_weight"),
        ]
    )
    return Selection(name="NMSSM", weights=NMSSM_weights)


def FF_training_process_selection(channel, era):
    cuts = []
    weights = []
    if channel == "et" or channel == "mt":
        cuts = [
            ("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        ]
        weights = [
            ("ff2_nom", "fake_factor")
        ]
    elif channel == "tt":
        raise NotImplementedError("FF training not implemented for tt")
    elif channel == "em":
        raise NotImplementedError("FF training not implemented for em")
    else:
        raise ValueError("Invalid channel: {}".format(channel))
    print("FF training cuts:", cuts)
    print("FF training weights:", weights)
    return Selection(name="jetFakes", cuts=cuts, weights=weights)
