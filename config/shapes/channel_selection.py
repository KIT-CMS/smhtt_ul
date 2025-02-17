from ntuple_processor.utils import Selection, WarnDict


def modify_for_ff_DR(channel=None, region=None):
    cuts = WarnDict()

    if region is None:
        return cuts

    # general DR cuts
    if channel is None:
        if region == "wjets_dr":
            pass
        elif region == "qcd_dr":
            cuts["os"] = "((q_1 * q_2) > 0)"  # fake ss
        elif region == "ttbar_dr":
            cuts.pop("extraelec_veto")
            cuts.pop("extramuon_veto")
            cuts.pop("dimuon_veto")
            cuts["lepton_veto"] = """(
                !(
                    (extramuon_veto < 0.5) &&
                    (extraelec_veto < 0.5) &&
                    (dimuon_veto < 0.5)
                )
            )"""
        else:
            raise ValueError("Given ff_tests does not exist")

    # channel specific DR cuts
    if channel == "mt":
        if region == "wjets_dr":
            cuts["nbtag"] = "(nbtag == 0)"
            cuts["mt_cut"] = "(mt_1 > 70)"
        elif region == "qcd_dr":
            cuts["muon_iso"] = "((iso_1 > 0.05) && (iso_1 < 0.15))"
            cuts["mt_cut"] = "(mt_1 < 50)"
            cuts["btag_veto"] = "(nbtag >= 0)"
        elif region == "ttbar_dr":
            cuts["btag_veto"] = "(nbtag >= 0)"
        else:
            raise ValueError("Given ff_tests does not exist")
    elif channel == "et":
        raise NotImplementedError("Not implemented yet")
    elif channel == "tt":
        raise NotImplementedError("Not implemented yet")
    else:
        raise ValueError("Given channel does not exist")

    return cuts


def channel_selection(channel, era, special=None, vs_jet_wp="Tight", vs_ele_wp="VVLoose", ff_DR=None):

    cuts = WarnDict()
    cuts["extraelec_veto"] = "(extraelec_veto < 0.5)"
    cuts["extramuon_veto"] = "(extramuon_veto < 0.5)"
    cuts["dilepton_veto"] = "(dimuon_veto < 0.5)"
    cuts["os"] = "((q_1 * q_2) < 0)"

    cuts.update(modify_for_ff_DR(None, ff_DR))

    wps_dict = {"VVTight", "VVTight", "Tight", "Medium", "Loose", "VLoose", "VVLoose", "VVVLoose"}
    assert vs_ele_wp in wps_dict, f"{vs_ele_wp} is not a valid vsEle discriminator"
    assert vs_jet_wp in wps_dict, f"{vs_jet_wp} is not a valid vsJet discriminator"

    if special is None:
        if "mt" in channel:
            cuts["againstMuonDiscriminator"] = "(id_tau_vsMu_Tight_2 > 0.5)"
            cuts["againstElectronDiscriminator"] = "(id_tau_vsEle_VVLoose_2 > 0.5)"
            cuts["tau_iso"] = "(id_tau_vsJet_Tight_2 > 0.5)"
            cuts["muon_iso"] = "(iso_1 < 0.15)"
            cuts["mt_cut"] = "(mt_1 < 70)"

            cuts.update(modify_for_ff_DR(channel, ff_DR))

            if era == "2016preVFP" or era == "2016postVFP":
                cuts["trg_selection"] = """(
                    (pt_2 > 20) &&
                    (pt_1 >= 23) &&
                    (
                        (trg_single_mu22 == 1) ||
                        (trg_single_mu22_tk == 1) ||
                        (trg_single_mu22_eta2p1 == 1) ||
                        (trg_single_mu22_tk_eta2p1 == 1)
                    )
                )"""
            elif era == "2017":
                cuts["trg_selection"] = """(
                    (pt_2 > 30) &&
                    (
                        (pt_1 >= 28) &&
                        (trg_single_mu27 == 1)
                    )
                )"""
            elif era == "2018":
                cuts["trg_selection"] = """(
                    (pt_2 > 30) &&
                    (
                        (pt_1 > 25) &&
                        (
                            (trg_single_mu27 > 0.5) ||
                            (trg_single_mu24 > 0.5)
                        )
                    )
                )"""
            else:
                raise ValueError("Given era does not exist")

            return Selection(name="mt", cuts=cuts)
        if "et" in channel:
            cuts["againstMuonDiscriminator"] = "(id_tau_vsMu_VLoose_2 > 0.5)"
            cuts["againstElectronDiscriminator"] = "(id_tau_vsEle_Tight_2 > 0.5)"
            cuts["tau_iso"] = "(id_tau_vsJet_Tight_2 > 0.5)"
            cuts["ele_iso"] = "(iso_1 < 0.15)"
            cuts["mt_cut"] = "(mt_1 < 70)"

            cuts.update(modify_for_ff_DR(channel, ff_DR))

            if era == "2016preVFP" or era == "2016postVFP":
                print(f" *** No triggers for {era} implemented yet ***")
            elif era == "2017":
                cuts["trg_selection"] = """(
                    (pt_2 > 30) &&
                    (
                        (
                            (pt_1 >= 33) &&
                            (pt_1 < 36) &&
                            (trg_single_ele32==1)
                        ) ||
                        (
                            (pt_1 >=36) &&
                            (trg_single_ele35 == 1)
                        )
                    )
                )"""
            elif era == "2018":
                cuts["trg_selection"] = """(
                    (pt_2 > 30) &&
                    (
                        (pt_1 > 33) &&
                        (
                            (trg_single_ele35 > 0.5) ||
                            (trg_single_ele32 > 0.5)
                        )
                    )
                )"""
            else:
                raise ValueError("Given era does not exist")

            return Selection(name="et", cuts=cuts)
        if "tt" in channel:
            cuts["againstMuonDiscriminator"] = "(id_tau_vsMu_VLoose_1 > 0.5) && (id_tau_vsMu_VLoose_2 > 0.5)"
            cuts["againstElectronDiscriminator"] = "(id_tau_vsEle_VVLoose_1 > 0.5) && (id_tau_vsEle_VVLoose_2 > 0.5)"
            cuts["tau_iso"] = "(id_tau_vsJet_Tight_1 > 0.5) && (id_tau_vsJet_Tight_2 > 0.5)"

            cuts.update(modify_for_ff_DR(channel, ff_DR))

            if era == "2016preVFP" or era == "2016postVFP":
                print(f" *** No triggers for {era} implemented yet ***")
            elif era == "2017":
                print(f" *** No triggers for {era} implemented yet ***")        
            elif era == "2018":
                cuts["pt_selection"] = "(pt_1 > 40) && (pt_2 > 40)"
                cuts["trg_selection"] = """(
                    (trg_double_tau35_tightiso_tightid > 0.5) ||
                    (trg_double_tau35_mediumiso_hps > 0.5) ||
                    (trg_double_tau40_mediumiso_tightid > 0.5) ||
                    (trg_double_tau40_tightiso > 0.5)
                )"""
            else:
                raise ValueError("Given era does not exist")

            return Selection(name="tt", cuts=cuts)
        if "em" in channel:
            cuts["ele_iso"] = "(iso_1 < 0.15)"
            cuts["muon_iso"] = "(iso_2 < 0.2)"
            cuts["electron_eta"] = "(abs(eta_1) < 2.4)"

            if era == "2016preVFP" or era == "2016postVFP":
                print(f" *** No triggers for {era} implemented yet ***")
            elif era == "2017":
                print(f" *** No triggers for {era} implemented yet ***")
            elif era == "2018":
                cuts["trg_selection"] = """(
                    (
                        (trg_cross_mu23ele12 == 1) &&
                        (pt_1 > 15) &&
                        (pt_2 > 24)
                    ) ||
                    (
                        (trg_cross_mu8ele23 == 1) &&
                        (pt_1 > 24) &&
                        (pt_2 > 15)
                    )
                )"""
            else:
                raise ValueError("Given era does not exist")

            return Selection(name="em", cuts=cuts)
        if "mm" in channel:
            cuts.pop("extraelec_veto")
            cuts.pop("extramuon_veto")
            cuts.pop("dilepton_veto")

            cuts["os"] = "((q_1 * q_2) < 0)"
            cuts["muon_iso"] = "(iso_1 < 0.15)"
            cuts["muon2_iso"] = "(iso_2 < 0.15)"

            #  Add era specific cuts. This is basically restricted to trigger selections.
            if era == "2016preVFP" or era == "2016postVFP":
                cuts["trg_selection"] = """(
                    (pt_2 > 10) &&
                    (pt_1 >= 23) &&
                    (
                        (trg_single_mu22 == 1) ||
                        (trg_single_mu22_tk == 1) ||
                        (trg_single_mu22_eta2p1 == 1) ||
                        (trg_single_mu22_tk_eta2p1 == 1)
                    )
                )"""
            elif era == "2017":
                cuts["trg_selection"] = """(
                    (pt_2 > 20) &&
                    (
                        (pt_1 >= 28) &&
                        (trg_single_mu27 == 1)
                    )
                )"""
            elif era == "2018":
                cuts["trg_selection"] = """(
                    (pt_2 > 20) &&
                    (pt_1 >= 28) &&
                    (trg_single_mu27 == 1)
                )"""
            else:
                raise ValueError("Given era does not exist")

            return Selection(name="mm", cuts=cuts)
        if "ee" in channel:
            cuts.pop("extraelec_veto")
            cuts.pop("extramuon_veto")
            cuts.pop("dilepton_veto")

            cuts["os"] = "((q_1 * q_2) < 0)"
            cuts["ele_iso"] = "(iso_1 < 0.15)"
            cuts["ele2_iso"] = "(iso_2 < 0.15)"

            #  Add era specific cuts. This is basically restricted to trigger selections.
            if era == "2016preVFP" or era == "2016postVFP":
                cuts["trg_selection"] = """(
                    (pt_2 > 20) &&
                    (
                        (
                            (pt_1 >= 26) &&
                            (trg_single_ele25 == 1)
                        )
                    )
                )"""
            elif era == "2017":
                cuts["trg_selection"] = """(
                    (pt_2 > 20) &&
                    (
                        (pt_1 >= 36) &&
                        (trg_single_ele35 == 1)
                    )
                )"""
            elif era == "2018":
                cuts["trg_selection"] = """(
                    (pt_2 > 20) &&
                    (
                        (pt_1 >= 33) &&
                        (
                            (trg_single_ele35 == 1) ||
                            (trg_single_ele32 == 1)
                        )
                    )
                )"""
            else:
                raise ValueError("Given era does not exist")

            return Selection(name="ee", cuts=cuts)
    # Special selection for TauID measurement
    if special == "TauID":
        assert channel in {"mt", "mm"}, "TauID measurement is only available for mt (with mm control region)"
        if channel == "mt":
            cuts["againstMuonDiscriminator"] = "(id_tau_vsMu_Tight_2 > 0.5)"
            cuts["againstElectronDiscriminator"] = f"(id_tau_vsEle_{vs_ele_wp}_2 > 0.5)"
            cuts["tau_iso"] = f"(id_tau_vsJet_{vs_jet_wp}_2 > 0.5)"
            cuts["muon_iso"] = "(iso_1 < 0.15)"
            cuts["mt_1"] = "(mt_1 < 60)"

            if era == "2016preVFP" or era == "2016postVFP":
                cuts["trg_selection"] = """(
                    (pt_2 > 20) &&
                    (pt_1 >= 23) &&
                    (
                        (trg_single_mu22 == 1) ||
                        (trg_single_mu22_tk == 1) ||
                        (trg_single_mu22_eta2p1 == 1) ||
                        (trg_single_mu22_tk_eta2p1 == 1)
                    )
                )"""
            elif era == "2017":
                print(f" *** No triggers for {era} implemented yet ***")
            elif era == "2018":
                cuts["trg_selection"] = """(
                    (pt_2 > 20) &&
                    (pt_1 >= 28) &&
                    (
                        (trg_single_mu27 == 1) ||
                        (trg_single_mu24 == 1)
                    )
                )"""
            else:
                raise ValueError("Given era does not exist")

            return Selection(name="mt", cuts=cuts)
        if channel == "mm":
            cuts.pop("extraelec_veto")
            cuts.pop("extramuon_veto")
            cuts.pop("dilepton_veto")

            # for mm we just need the control region between 60 and 120 GeV as a single bin
            cuts["os"] = "((q_1 * q_2) < 0)"
            cuts["m_vis"] = "(m_vis > 50)"
            cuts["muon_iso"] = "((iso_1 < 0.15) && (iso_2 < 0.15))"

            if era == "2016preVFP" or era == "2016postVFP":
                cuts["trg_selection"] = """(
                    (pt_2 > 23) &&
                    (pt_1 >= 23) &&
                    (
                        (trg_single_mu22 == 1) ||
                        (trg_single_mu22_tk == 1) ||
                        (trg_single_mu22_eta2p1 == 1) ||
                        (trg_single_mu22_tk_eta2p1 == 1)
                    )
                )"""
            elif era == "2017":
                print(f" *** No triggers for {era} implemented yet ***")
            elif era == "2018":
                cuts["trg_selection"] = """(
                    (pt_2 > 20) &&
                    (pt_1 >= 28) &&
                    (
                        (trg_single_mu27 == 1) ||
                        (trg_single_mu24 == 1)
                    )
                )"""
            else:
                raise ValueError("Given era does not exist")

            return Selection(name="mm", cuts=cuts)
    # Special selection for TauES measurement
    elif special == "TauES":
        assert channel == "mt", "TauID measurement is only available for mt"

        cuts["againstMuonDiscriminator"] = "(id_tau_vsMu_Tight_2 > 0.5)"
        cuts["againstElectronDiscriminator"] = f"(id_tau_vsEle_{vs_ele_wp}_2 > 0.5)"
        cuts["tau_iso"] = f"(id_tau_vsJet_{vs_jet_wp}_2 > 0.5)"
        cuts["muon_iso"] = "(iso_1 < 0.15)"
        cuts["pzetamissvis"] = "(pzetamissvis > -25)"
        cuts["mt_1"] = "(mt_1 < 60)"

        if era == "2016preVFP" or era == "2016postVFP":
            print(f" *** No triggers for {era} implemented yet ***")
        elif era == "2017":
            print(f" *** No triggers for {era} implemented yet ***")
        elif era == "2018":
            cuts["trg_selection"] = """(
                (pt_2 > 20) &&
                (pt_1 >= 28) &&
                (
                    (trg_single_mu27 == 1) ||
                    (trg_single_mu24 == 1)
                )
            )"""
        else:
            raise ValueError("Given era does not exist")

        return Selection(name="mt", cuts=cuts)
    elif special == "EleES":
        assert channel == "ee", "EleES measurement is done in the ee channel only"

        cuts.pop("extramuon_veto")

        cuts["extraelec_veto"] = "(extraelec_veto > 0.5)"
        # cuts["extramuon_veto"] = "(extramuon_veto < 0.5)"
        cuts["dilepton_veto"] = "(dimuon_veto < 0.5)"
        cuts["os"] = "((q_1 * q_2) < 0)"
        cuts["ele_iso"] = "((iso_1 < 0.1) && (iso_2 < 0.1))"
        cuts["electron_eta"] = "((abs(eta_1) < 2.1) && (abs(eta_2) < 2.1))"
        # cuts["met"] = "(met < 100)"

        if era == "2016preVFP" or era == "2016postVFP":
            cuts["trg_selection"] = """(
                (pt_2 > 20) &&
                (
                    (
                        (pt_1 >= 26) &&
                        (trg_single_ele25 == 1)
                    )
                )
            )"""
        elif era == "2017":
            cuts["trg_selection"] = """(
                (pt_2 > 20) &&
                (
                    (pt_1 >= 36) &&
                    (trg_single_ele35 == 1)
                )
            )"""
        elif era == "2018":
            cuts["trg_selection"] = """(
                (pt_2 > 33) &&
                (pt_1 >= 33) &&
                (trg_single_ele32 == 1)
            )"""
        else:
            raise ValueError(f"Given era {era} does not exist")

        return Selection(name="ee", cuts=cuts)
    else:
        raise ValueError("Given special selection does not exist")


# old implementation of channel_selection (TODO: remove)


def _channel_selection(channel, era, special=None, vs_jet_wp="Tight", vs_ele_wp="VVLoose", ff_DR=None):

    # Specify general channel and era independent cuts.
    cuts = [
        ("extraelec_veto<0.5", "extraelec_veto"),
        ("extramuon_veto<0.5", "extramuon_veto"),
        ("dimuon_veto<0.5", "dilepton_veto"),
        ("q_1*q_2<0", "os"),
    ]
    if ff_DR is None:
        pass
    elif ff_DR == "wjets_dr":
        pass
    elif ff_DR == "qcd_dr":
        cuts = [
            ("extraelec_veto<0.5", "extraelec_veto"),
            ("extramuon_veto<0.5", "extramuon_veto"),
            ("dimuon_veto<0.5", "dilepton_veto"),
            ("q_1*q_2>0", "os"),
        ]
    elif ff_DR == "ttbar_dr":
        cuts = [
            ('!((extramuon_veto < 0.5) && (extraelec_veto < 0.5) && (dimuon_veto < 0.5))', "lepton_veto"),
            ("q_1*q_2<0", "os"),
        ]
    else:
        raise ValueError("Given ff_tests does not exist")

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

    if special is None:
        if "mt" in channel:
            #  Add channel specific cuts to the list of cuts.
            cuts.extend(
                [
                    ("id_tau_vsMu_Tight_2>0.5", "againstMuonDiscriminator"),
                    ("id_tau_vsEle_VVLoose_2>0.5", "againstElectronDiscriminator"),
                    ("id_tau_vsJet_Tight_2>0.5", "tau_iso"),
                    # ("iso_1<0.15", "muon_iso"),
                    # ("mt_1 < 70", "mt_cut"),
                ]
            )
            if ff_DR is None:
                cuts.extend(
                    [
                        ("iso_1<0.15", "muon_iso"),
                        ("mt_1 < 70", "mt_cut"),
                    ]
                )

            elif ff_DR == "wjets_dr":
                cuts.extend(
                    [
                        ("iso_1<0.15", "muon_iso"),
                        ("nbtag == 0", "btag_veto"),
                        ("mt_1 > 70", "mt_cut"),
                    ]
                )
            elif ff_DR == "qcd_dr":
                cuts.extend(
                    [
                        ("((iso_1 > 0.05) && (iso_1 < 0.15))", "muon_iso"),
                        ("mt_1 < 50", "mt_cut"),
                        ("nbtag >= 0", "btag_veto"),
                    ]
                )
            elif ff_DR == "ttbar_dr":
                cuts.extend(
                    [
                        ("iso_1<0.15", "muon_iso"),
                        ("mt_1 < 70", "mt_cut"),
                        ("nbtag >= 0", "btag_veto"),
                    ]
                )
            else:
                raise ValueError("Given ff_tests does not exist")
            #  Add era specific cuts. This is basically restricted to trigger selections.
            # TODO add 2017 and 2016
            if era == "2016preVFP" or era == "2016postVFP":
                cuts.append(
                    (
                        "pt_2>20 && pt_1>=23 && ((trg_single_mu22 == 1) || (trg_single_mu22_tk == 1)  || (trg_single_mu22_eta2p1 == 1)  || (trg_single_mu22_tk_eta2p1 == 1))",
                        "trg_selection",
                    ),
                )
            elif era == "2017":
                cuts.append(
                    (
                        "pt_2>30 && (pt_1>=28 && (trg_single_mu27 == 1))",
                        "trg_selection",
                    ),
                )
            elif era == "2018":
                cuts.append(
                    (
                        "(pt_2 > 30) && ((pt_1 > 25) && ((trg_single_mu27 > 0.5) || (trg_single_mu24 > 0.5)))",
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
            if era == "2017":
                cuts.append(
                    (
                        "pt_2>30 && ((pt_1>=33 && pt_1 < 36 && (trg_single_ele32==1)) || (pt_1 >=36 && (trg_single_ele35==1)))",
                        "trg_selection",
                    ),
                )
            elif era == "2018":
                cuts.append(
                    # (
                    #     "pt_2>30 && ((pt_1>25 && pt_1<33 && ((trg_cross_ele24tau30_hps==1) || (trg_cross_ele24tau30_hps==1))) || (pt_1 >=33 && ((trg_single_ele35==1) || (trg_single_ele32==1))))",
                    #     "trg_selection",
                    # ),
                    (
                        "pt_2 > 30 && (pt_1 > 33 && ((trg_single_ele35 > 0.5) || (trg_single_ele32 > 0.5)))",
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
                        "(id_tau_vsMu_VLoose_1 > 0.5) && (id_tau_vsMu_VLoose_2 > 0.5)",
                        "againstMuonDiscriminator",
                    ),
                    (
                        "(id_tau_vsEle_VVLoose_1 > 0.5) && (id_tau_vsEle_VVLoose_2 > 0.5)",  # TODO: possible typo
                        "againstElectronDiscriminator",
                    ),
                    (
                        "(id_tau_vsJet_Tight_1 > 0.5) && (id_tau_vsJet_Tight_2 > 0.5)",
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
                        "((trg_double_tau35_tightiso_tightid > 0.5) || (trg_double_tau35_mediumiso_hps > 0.5) || (trg_double_tau40_mediumiso_tightid > 0.5) || (trg_double_tau40_tightiso > 0.5))",
                        "trg_selection",
                    ),
                )
                # print("No triggers atm ...")
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
        if "mm" in channel:
            #  Add channel specific cuts to the list of cuts.
            cuts = [
                ("q_1*q_2<0", "os"),
                ("iso_1<0.15", "muon_iso"),
                ("iso_2<0.15", "muon2_iso"),
            ]
            #  Add era specific cuts. This is basically restricted to trigger selections.
            # TODO add 2017 and 2016
            if era == "2017":
                cuts.append(
                    (
                        "pt_2>20 && (pt_1>=28 && (trg_single_mu27 == 1))",
                        "trg_selection",
                    ),
                )
            elif era == "2018":
                # cuts.append(
                #     (
                #         "pt_2>30 && ((pt_1<25 && (trg_cross_mu20tau27_hps == 1 )) || (pt_1>=25 && ((trg_single_mu27 == 1) || (trg_single_mu24 == 1))))",
                #         "trg_selection",
                #     ),  # TODO add nonHPS Triggerflag for also MC
                # )
                cuts.append(
                    (
                        # "pt_2>20 && ( (pt_1>=28 && (trg_single_mu27 == 1)) || (pt_1>=25 && pt_1 < 28 && (trg_single_mu24 == 1)))",
                        "pt_2>20 && pt_1>=28 && (trg_single_mu27 == 1)",
                        "trg_selection",
                    ),  # TODO add nonHPS Triggerflag for also MC
                )
            elif era == "2016postVFP" or era == "2016preVFP":
                cuts.extend(
                    [
                        (
                            "pt_2>10 && pt_1>=23 && ((trg_single_mu22 == 1) || (trg_single_mu22_tk == 1)  || (trg_single_mu22_eta2p1 == 1)  || (trg_single_mu22_tk_eta2p1 == 1))",
                            "trg_selection",
                        ),
                        # ("m_vis>60 && m_vis < 120", "m_vis"),
                    ]
                )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="mm", cuts=cuts)
        if "ee" in channel:
            #  Add channel specific cuts to the list of cuts.
            cuts = [
                ("q_1*q_2<0", "os"),
                ("iso_1<0.15", "ele_iso"),
                ("iso_2<0.15", "ele2_iso"),
            ]
            #  Add era specific cuts. This is basically restricted to trigger selections.
            # TODO add 2016
            if era == "2017":
                cuts.append(
                    (
                        "pt_2>20 && (pt_1 >=36 && (trg_single_ele35==1))",
                        "trg_selection",
                    ),
                )
            elif era == "2018":
                cuts.append(
                    (
                        "pt_2>20 && (pt_1 >=33 && ((trg_single_ele35==1) || (trg_single_ele32==1)))",
                        "trg_selection",
                    ),
                )
            elif era in ["2016postVFP", "2016preVFP"]:
                cuts.append(
                    (
                        "pt_2>20 && ((pt_1>=26 && (trg_single_ele25 == 1)))",
                        "trg_selection",
                    ),
                )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="ee", cuts=cuts)
    # Special selection for TauID measurement
    if special == "TauID":
        if channel != "mt" and channel != "mm":
            raise ValueError(
                "TauID measurement is only available for mt (with mm control region)"
            )
        if channel == "mt":
            cuts.extend(
                [
                    ("id_tau_vsMu_Tight_2>0.5", "againstMuonDiscriminator"),
                    (f"id_tau_vsEle_{vs_ele_wp}_2>0.5", "againstElectronDiscriminator"),
                    (f"id_tau_vsJet_{vs_jet_wp}_2>0.5", "tau_iso"),
                    ("iso_1<0.15", "muon_iso"),
                    # ("pzetamissvis > -25", "pzetamissvis"),
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
            elif era == "2016preVFP" or era == "2016postVFP":
                cuts.append(
                    (
                        "pt_2>20 && pt_1>=23 && ((trg_single_mu22 == 1) || (trg_single_mu22_tk == 1)  || (trg_single_mu22_eta2p1 == 1)  || (trg_single_mu22_tk_eta2p1 == 1))",
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
            elif era in ["2016postVFP", "2016preVFP"]:
                cuts.append(
                    (
                        "pt_2>23 && pt_1>=23 && ((trg_single_mu22 == 1) || (trg_single_mu22_tk == 1)  || (trg_single_mu22_eta2p1 == 1)  || (trg_single_mu22_tk_eta2p1 == 1))",
                        "trg_selection",
                    ),
                )
            else:
                raise ValueError("Given era does not exist")
            return Selection(name="mm", cuts=cuts)
    # Special selection for TauES measurement
    elif special == "TauES":
        if channel != "mt":
            raise ValueError("TauES measurement is only available for mt")
        cuts.extend(
            [
                ("id_tau_vsMu_Tight_2>0.5", "againstMuonDiscriminator"),
                (f"id_tau_vsEle_{vs_ele_wp}_2>0.5", "againstElectronDiscriminator"),
                (f"id_tau_vsJet_{vs_jet_wp}_2>0.5", "tau_iso"),
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
    elif special == "EleES":
        if channel != "ee":
            raise ValueError("EleES measurement is done in the ee channel only")
        cuts = [
            ("extraelec_veto>0.5", "extraelec_veto"),
            # ("extramuon_veto<0.5", "extramuon_veto"),
            ("dimuon_veto<0.5", "dilepton_veto"),
            ("q_1*q_2<0", "os"),
            ("iso_1<0.1 && iso_2<0.1", "ele_iso"),
            ("abs(eta_1)<2.1 && abs(eta_2)<2.1", "electron_eta"),
            # ("met < 100", "met"),
        ]
        if era == "2018":
            cuts.append(
                (
                    "pt_2>33 && pt_1>=33 && ( trg_single_ele32 == 1)",
                    "trg_selection",
                ),
            )
        elif era == "2017":
            cuts.append(
                (
                    "pt_2>20 && (pt_1 >=36 && (trg_single_ele35==1))",
                    "trg_selection",
                ),
            )
        elif era in ["2016postVFP", "2016preVFP"]:
            cuts.append(
                (
                    "pt_2>20 && ((pt_1>=26 && (trg_single_ele25 == 1)))",
                    "trg_selection",
                ),
            )
        else:
            raise ValueError(f"Given era {era} does not exist")
        return Selection(name="ee", cuts=cuts)
    else:
        raise ValueError("Given special selection does not exist")

# -----------------------------
