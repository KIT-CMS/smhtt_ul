from ntuple_processor.utils import Selection


def channel_selection(channel, era, special=None, boosted_tau=False, boosted_b=False):
    # Specify general channel and era independent cuts.
    if not boosted_tau:
        cuts = [
            ("q_1*q_2<0", "os"),
            ("((boosted_deltaR_ditaupair > 0.8) || (boosted_deltaR_ditaupair < 0.1))", "boosted_tau_restriction"),
            ("(tau_decaymode_2==0 || tau_decaymode_2==1 || tau_decaymode_2==10 || tau_decaymode_2==11)", "tau_decay_mode"),
        ]
    elif boosted_tau:
        cuts = [
            ("boosted_q_1*boosted_q_2<0", "os"),
            ("(boosted_tau_decaymode_2==0 || boosted_tau_decaymode_2==1 || boosted_tau_decaymode_2==10)", "tau_decay_mode"),
            ("boosted_deltaR_ditaupair<=0.8", "boosted_deltaR"),
        ]
    
    if not boosted_b:
        if not boosted_tau:
            cuts.extend(
                [
                    ("(bpair_pt_1>=20 && bpair_pt_2>=20 && nbtag>=1)", "bjet_pair"),
                    ("(bpair_btag_value_2>=0.049 && abs(bpair_eta_2)<=2.5)", "second_bjet_restriction"),
                    # ("((bpair_pt_1>=20 && bpair_pt_2>=20 && nbtag>=1 && bpair_btag_value_2>=0.049 && abs(bpair_eta_2)<=2.5) || (fj_Xbb_particleNet_XbbvsQCD>=0.0 && abs(fj_Xbb_eta)<=2.5 && fj_Xbb_pt>=200 && ((bpair_btag_value_2<0.049 && nbtag==1) || (nbtag==0))))", "bb incl"),
                ]
            )
        if boosted_tau:
            cuts.extend(
                [
                    ("(bpair_pt_1_boosted>=20 && bpair_pt_2_boosted>=20 && nbtag_boosted>=1)", "bjet_pair"),
                    ("(bpair_btag_value_2_boosted>=0.049 && abs(bpair_eta_2_boosted)<=2.5)", "second_bjet_restriction"),
                ]
            )
    elif boosted_b:
        if not boosted_tau:
            cuts.extend(
                [
                    ("(abs(fj_Xbb_eta)<=2.5 && fj_Xbb_pt>=200 && jpt_1<200 &&mt_1<40)", "bb_fatjet"),
                    # ("((bpair_btag_value_2<0.049 && nbtag==1) || (nbtag==0))", "resolved_bb_restriction"),
                    ("nbtag==0", "btag"),
                ]
            )
        if boosted_tau:
            cuts.extend(
                [
                    ("(fj_Xbb_particleNet_XbbvsQCD_boosted>=0.0 && abs(fj_Xbb_eta_boosted)<=2.5 && fj_Xbb_pt_boosted>=200)", "bb_fatjet"), 
                    ("((bpair_btag_value_2_boosted<0.049 && nbtag_boosted==1) || (nbtag_boosted==0))", "resolved_bb_restriction"),
                ]
            )

    if special is None:
        if "mt" in channel:
            #  Add channel specific cuts to the list of cuts.
            if not boosted_tau:
                cuts.extend(
                    [   
                        ("extraelec_veto<0.5", "extraelec_veto"),
                        ("extramuon_veto<0.5", "extramuon_veto"),
                        ("dilepton_veto<0.5", "dilepton_veto"),
                        ("id_tau_vsMu_Tight_2>0.5", "againstMuonDiscriminator"),
                        ("id_tau_vsEle_VVLoose_2>0.5", "againstElectronDiscriminator"),
                        ("id_tau_vsJet_Medium_2>0.5", "tau_iso"),
                        ("iso_1<0.15", "muon_iso"),
                        ("abs(eta_1)<=2.1", "muon_eta"),
                    ]
                )
            elif boosted_tau:
                cuts.extend(
                    [   
                        ("extraelec_veto<0.5", "extraelec_veto"),
                        ("boosted_extramuon_veto<0.5", "extramuon_veto"),
                        ("dilepton_veto<0.5", "dilepton_veto"),
                        ("id_boostedtau_antiMu_Loose_2>0.5", "againstMuonDiscriminator"),
                        ("id_boostedtau_antiEle_VLoose_2>0.5", "againstElectronDiscriminator"),
                        ("id_boostedtau_iso_Loose_2>0.5", "tau_iso"),
                    ]
                )
            #  Add era specific cuts. This is basically restricted to trigger selections.
            # TODO add 2017 and 2016
            if era == "2017":
                cuts.append(
                        (
                            "pt_2>30 && (pt_1>=28 && (trg_single_mu27 == 1))",
                            "trg_selection",
                        ),
                        )
            elif era == "2018":
                if not boosted_tau:
                    cuts.append(
                        (
                            "pt_2>30 && ( (pt_1>=25 && (trg_single_mu27 == 1)) || (pt_1>=25 && (trg_single_mu24 == 1)) )",
                            "trg_selection",
                        ),  # TODO add nonHPS Triggerflag for also MC
                    )
                elif boosted_tau:
                    cuts.append(
                        (
                            "boosted_pt_2>40 && (((trg_single_mu50_boosted > 0.5) && (boosted_pt_1 >= 55)) || ((trg_single_mu27_boosted > 0.5) && (boosted_iso_1 < 0.3) && (boosted_pt_1 > 28) && (boosted_pt_1 < 55)))",
                            "trg_selection",
                        ),  # TODO add nonHPS Triggerflag for also MC
                    )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="mt", cuts=cuts)
        if "et" in channel:
            #  Add channel specific cuts to the list of cuts.
            if not boosted_tau:
                cuts.extend(
                    [
                        ("extraelec_veto<0.5", "extraelec_veto"),
                        ("extramuon_veto<0.5", "extramuon_veto"),
                        ("dilepton_veto<0.5", "dilepton_veto"),
                        ("id_tau_vsMu_VLoose_2>0.5", "againstMuonDiscriminator"),
                        ("id_tau_vsEle_Tight_2>0.5", "againstElectronDiscriminator"),
                        ("id_tau_vsJet_Medium_2>0.5", "tau_iso"),
                        ("iso_1<0.15", "ele_iso"),
                        ("abs(eta_1)<=2.1", "muon_eta"),
                    ]
                )
            elif boosted_tau:
                cuts.extend(
                    [
                        ("boosted_extraelec_veto<0.5", "extraelec_veto"),
                        ("extramuon_veto<0.5", "extramuon_veto"),
                        ("dilepton_veto<0.5", "dilepton_veto"),
                        # ("id_boostedtau_antiMu_Loose_2>0.5", "againstMuonDiscriminator"),
                        ("id_boostedtau_antiEle_Loose_2>0.5", "againstElectronDiscriminator"),
                        ("id_boostedtau_iso_Loose_2>0.5", "tau_iso"),
                    ]
                )
            if era == "2017":
                cuts.append(
                    (
                        "pt_2>30 && ((pt_1>=33 && pt_1 < 36 && (trg_single_ele32==1)) || (pt_1 >=36 && (trg_single_ele35==1)))",
                        "trg_selection",
                    ),
                )
            elif era == "2018":
                if not boosted_tau:
                    cuts.append(
                        (
                            "pt_2>30 && ( (pt_1>=33 && (trg_single_ele35 == 1)) || (pt_1>=33 && (trg_single_ele32 == 1)) )",
                            "trg_selection",
                        ),
                    )
                elif boosted_tau:
                    cuts.append(
                        (
                            "boosted_pt_2>40 && (((trg_single_ele115_boosted > 0.5) && (boosted_pt_1 >= 120)) || ((trg_single_ele35_boosted > 0.5) && (boosted_iso_1 < 0.3) && (boosted_pt_1 > 38) && (boosted_pt_1 < 120)))", # || (boosted_pt_1<118 && boosted_pt_1>=35 && boosted_iso_1<0.3 && met>30&& trg_single_ele32_boosted==1))",
                            "trg_selection",
                        ),
                    )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="et", cuts=cuts)
        if "tt" in channel:
            #  Add channel specific cuts to the list of cuts.
            if not boosted_tau:
                cuts.extend(
                    [
                        ("extraelec_veto<0.5", "extraelec_veto"),
                        ("extramuon_veto<0.5", "extramuon_veto"),
                        (
                            "id_tau_vsMu_VLoose_1>0.5 && id_tau_vsMu_VLoose_2>0.5",
                            "againstMuonDiscriminator",
                        ),
                        (
                            "id_tau_vsEle_VVLoose_1>0.5 && id_tau_vsEle_VVLoose_2>0.5",
                            "againstElectronDiscriminator",
                        ),
                        (
                            "id_tau_vsJet_Medium_1>0.5 && id_tau_vsJet_Medium_2>0.5",
                            "tau_iso",
                        ),
                        ("m_fastmtt>60 && m_fastmtt<140", "mvis_veto"),
                    ]
                )
            elif boosted_tau:
                cuts.extend(
                    [
                        ("extraelec_veto<0.5", "extraelec_veto"),
                        ("extramuon_veto<0.5", "extramuon_veto"),
                        # (
                        #     "id_boostedtau_antiMu_Loose_1>0.5 && id_boostedtau_antiMu_Loose_2>0.5",
                        #     "againstMuonDiscriminator",
                        # ),
                        # (
                        #     "id_boostedtau_antiEle_VLoose_1>0.5 && id_boostedtau_antiEle_VLoose_2>0.5",
                        #     "againstElectronDiscriminator",
                        # ),
                        (
                            "id_boostedtau_iso_Loose_1>0.5 && id_boostedtau_iso_Loose_2>0.5",
                            "tau_iso",
                        ),
                    ]
                )
            if era == "2018":
                if not boosted_tau:
                    cuts.extend(
                        [
                            ("pt_1 > 40 && pt_2 > 40", "pt_selection"),
                            (
                                "((trg_double_tau35_tightiso_tightid > 0.5) || (trg_double_tau35_mediumiso_hps > 0.5) || (trg_double_tau40_mediumiso_tightid > 0.5) || (trg_double_tau40_tightiso > 0.5))",
                                "trg_selection",
                            ),
                        ]
                    )
                elif boosted_tau:
                    cuts.extend(
                        [
                            ("boosted_pt_1 > 40 && boosted_pt_2 > 40", "pt_selection"),
                            (
                                "((trg_ak8jet400_trimmass30 > 0.5) || (trg_ht500_met100_mht100_tightid > 0.5))", 
                                "trg_selection",
                            ),
                        ]
                    )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="tt", cuts=cuts)
        
        
    # Special selection for TauID measurement
    if special == "TauID":
        if channel != "mt" and channel != "mm":
            raise ValueError("TauID measurement is only available for mt (with mm control region)")
        if channel == "mt":
            cuts.extend(
                [
                    ("id_tau_vsMu_Tight_2>0.5", "againstMuonDiscriminator"),
                    ("id_tau_vsEle_VLoose_2>0.5", "againstElectronDiscriminator"),
                    ("id_tau_vsJet_Tight_2>0.5", "tau_iso"),
                    ("iso_1<0.15", "muon_iso"),
                    ("pzetamissvis > -25", "pzetamissvis"),
                    ("mt_1 < 60", "mt_1"),
                ]
            )
            if era == "2018":
                cuts.append(
                    (
                        "pt_2>20 && pt_1>=28 && ((trg_single_mu27 == 1) || (trg_single_mu24 == 1))",
                        "trg_selection",
                    ),
                )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="mt", cuts=cuts)
        # for mm we just need the control region between 60 and 120 GeV as a single bin
        if channel == "mm":
            cuts = [
                    ("q_1*q_2<0", "os"),
                    ("m_vis>50", "m_vis"),
                    ("iso_1<0.15 && iso_2<0.15", "muon_iso"),
                ]
            if era == "2018":
                cuts.append(
                    (
                        "pt_2>20 && pt_1>=28 && ((trg_single_mu27 == 1) || (trg_single_mu24 == 1))",
                        "trg_selection",
                    ),
                )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="mm", cuts=cuts)
    # Special selection for TauES measurement
    elif special == "TauES":
        if channel != "mt":
            raise ValueError("TauID measurement is only available for mt")
        cuts.extend(
            [
                ("id_tau_vsMu_Tight_2>0.5", "againstMuonDiscriminator"),
                ("id_tau_vsEle_VLoose_2>0.5", "againstElectronDiscriminator"),
                ("id_tau_vsJet_Tight_2>0.5", "tau_iso"),
                ("iso_1<0.15", "muon_iso"),
                ("pzetamissvis > -25", "pzetamissvis"),
                ("mt_1 < 60", "mt_1"),
            ]
        )
        if era == "2018":
            cuts.append(
                (
                    "pt_2>20 && pt_1>=28 && ((trg_single_mu27 == 1) || (trg_single_mu24 == 1))",
                    "trg_selection",
                ),
            )
        else:
            raise ValueError("Given era does not exist")
        return Selection(name="mt", cuts=cuts)
    else:
        raise ValueError("Given special selection does not exist")
