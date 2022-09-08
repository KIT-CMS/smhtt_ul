from ntuple_processor.utils import Selection


def channel_selection(channel, era, special=None):
    # Specify general channel and era independent cuts.
    cuts = [
        ("extraelec_veto<0.5", "extraelec_veto"),
        ("extramuon_veto<0.5", "extramuon_veto"),
        ("dimuon_veto<0.5", "dilepton_veto"),
        ("q_1*q_2<0", "os"),
    ]
    if special is None:
        if "mt" in channel:
            #  Add channel specific cuts to the list of cuts.
            cuts.extend(
                [
                    ("id_tau_vsMu_Tight_2>0.5", "againstMuonDiscriminator"),
                    ("id_tau_vsEle_VVLoose_2>0.5", "againstElectronDiscriminator"),
                    ("id_tau_vsJet_Tight_2>0.5", "tau_iso"),
                    ("iso_1<0.15", "muon_iso"),
                    ("mt_1 < 70", "mt_cut"),
                ]
            )
            #  Add era specific cuts. This is basically restricted to trigger selections.
            # TODO add 2017 and 2016
            if era == "2018":
                # cuts.append(
                #     (
                #         "pt_2>30 && ((pt_1<25 && (trg_cross_mu20tau27_hps == 1 )) || (pt_1>=25 && ((trg_single_mu27 == 1) || (trg_single_mu24 == 1))))",
                #         "trg_selection",
                #     ),  # TODO add nonHPS Triggerflag for also MC
                # )
                cuts.append(
                    (
                        "pt_2>30 && pt_1>=25 && ((trg_single_mu27 == 1) || (trg_single_mu24 == 1))",
                        "trg_selection",
                    ),  # TODO add nonHPS Triggerflag for also MC
                )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="mt", cuts=cuts)
        if "et" in channel:
            #  Add channel specific cuts to the list of cuts.
            cuts.extend(
                [
                    ("id_tau_vsMu_VLoose_2>0.5", "againstMuonDiscriminator"),
                    ("id_tau_vsEle_Tight_2>0.5", "againstElectronDiscriminator"),
                    ("id_tau_vsJet_Tight_2>0.5", "tau_iso"),
                    ("iso_1<0.15", "ele_iso"),
                    ("mt_1 < 70", "mt_cut"),
                ]
            )
            if era == "2018":
                cuts.append(
                    # (
                    #     "pt_2>30 && ((pt_1>25 && pt_1<33 && ((trg_cross_ele24tau30_hps==1) || (trg_cross_ele24tau30_hps==1))) || (pt_1 >=33 && ((trg_single_ele35==1) || (trg_single_ele32==1))))",
                    #     "trg_selection",
                    # ),
                    (
                        "pt_2>30 && (pt_1 >=33 && ((trg_single_ele35==1) || (trg_single_ele32==1)))",
                        "trg_selection",
                    ),
                )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="et", cuts=cuts)
        if "tt" in channel:
            #  Add channel specific cuts to the list of cuts.
            cuts.extend(
                [
                    (
                        "id_tau_vsMu_VLoose_1>0.5 && id_tau_vsMu_VLoose_2>0.5",
                        "againstMuonDiscriminator",
                    ),
                    (
                        "id_tau_vsEle_VVLoose_1>0.5 && id_tau_vsEle_VVLoose_1>0.5",
                        "againstElectronDiscriminator",
                    ),
                    (
                        "id_tau_vsJet_Tight_1>0.5 && id_tau_vsJet_Tight_2>0.5",
                        "tau_iso",
                    ),
                ]
            )
            if era == "2018":
                cuts.append(
                    ("pt_1 > 40 && pt_2 > 40", "pt_selection"),
                )
                cuts.append(
                    (
                        "((trg_double_tau35_mediumiso_hps==1) || (trg_double_tau40_tightiso==1))",
                        "trg_selection",
                    ),
                )
                print("No triggers atm ...")
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="tt", cuts=cuts)
        if "em" in channel:
            #  Add channel specific cuts to the list of cuts.
            cuts.extend(
                [
                    ("iso_1<0.15", "ele_iso"),
                    ("iso_2<0.2", "muon_iso"),
                    ("abs(eta_1)<2.4", "electron_eta"),
                ]
            )
            if era == "2018":
                cuts.append(
                    (
                        "(trg_cross_mu23ele12 == 1 && pt_1>15 && pt_2 > 24) || (trg_cross_mu8ele23 == 1 && pt_1>24 && pt_2>15)",
                        "trg_selection",
                    ),
                )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="em", cuts=cuts)
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
                        "pt_2>28 && pt_1>=28 && ((trg_single_mu27 == 1) || (trg_single_mu24 == 1))",
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
