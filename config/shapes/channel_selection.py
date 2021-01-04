from ntuple_processor.utils import Selection

def channel_selection(channel, era):
    # Specify general channel and era independent cuts.
    cuts = [
        ("flagMETFilter == 1", "METFilter"),
        ("extraelec_veto<0.5", "extraelec_veto"),
        ("extramuon_veto<0.5", "extramuon_veto"),
        ("dilepton_veto<0.5", "dilepton_veto"),
        ("q_1*q_2<0", "os"),
    ]
    if "mt" in channel:
        #  Add channel specific cuts to the list of cuts.
        cuts.extend([
            ("byTightDeepTau2017v2p1VSmu_2>0.5", "againstMuonDiscriminator"),
            ("byVVLooseDeepTau2017v2p1VSe_2>0.5", "againstElectronDiscriminator"),
            ("byTightDeepTau2017v2p1VSjet_2>0.5", "tau_iso"),
            ("iso_1<0.15", "muon_iso"),
        ])
        #  Add era specific cuts. This is basically restricted to trigger selections.
        if era == "2016":
            cuts.append(
                ("pt_2>30 && ((pt_1 >= 23 && trg_singlemuon == 1) || (trg_mutaucross == 1 && pt_1 < 23 && abs(eta_2)<2.1))","trg_selection")
            )
        elif era == "2017":
            cuts.append(
                ("pt_2>30"
                 "&& (((isSingleMuon||isMC||isEmbedded) && ((pt_2>32 && pt_2<180 && fabs(eta_2)<2.1 && pt_1<25 && (trg_crossmuon_mu20tau27==1)) || (pt_1>=25 && ((trg_singlemuon_27==1) || (trg_singlemuon_24==1)))))"
                     "|| ((isMC||isEmbedded) && (trg_singletau_trailing==1) && pt_2>180 && fabs(eta_2)<2.1)"
                     "|| ((isTau) && !(pt_1>=25 && ((trg_singlemuon_27==1) || (trg_singlemuon_24==1))) && (trg_singletau_trailing==1) && pt_2>180 && fabs(eta_2)<2.1))", "trg_selection"),
            )
        elif era == "2018":
            cuts.append(
                ("pt_2>30 && ((trg_singlemuon_27 == 1) || (trg_singlemuon_24 == 1)) || (pt_1 < 25 && (trg_crossmuon_mu20tau27_hps == 1 || trg_crossmuon_mu20tau27 == 1))", "trg_selection"),
            )
        else:
            raise ValueError("Given era does not exist")
        return Selection(name="mt", cuts=cuts)
    if "et" in channel:
        #  Add channel specific cuts to the list of cuts.
        cuts.extend([
            ("byVLooseDeepTau2017v2p1VSmu_2>0.5", "againstMuonDiscriminator"),
            ("byTightDeepTau2017v2p1VSe_2>0.5", "againstElectronDiscriminator"),
            ("byTightDeepTau2017v2p1VSjet_2>0.5", "tau_iso"),
            ("iso_1<0.15", "ele_iso"),
        ])
        if era == "2016":
            cuts.append(
                ("pt_2>30 && ((pt_1>26 && (trg_singleelectron==1)) || (pt_1<26 && pt_1>25 && (trg_eletaucross==1)))", "trg_selection"),
            )
        elif era == "2017":
            cuts.append(
                ("pt_2>30"
                 "&& (((isSingleElectron||isMC||isEmbedded) && ((pt_2>35 && pt_2<180 && fabs(eta_2)<2.1 && pt_1<28 && (trg_crossele_ele24tau30==1)) || (pt_1>=28 && ((trg_singleelectron_27==1) || (trg_singleelectron_32==1) || (trg_singleelectron_35==1)))))"
                     "|| ((isMC||isEmbedded) && (trg_singletau_trailing==1) && pt_2>180 && fabs(eta_2)<2.1)"
                     "|| ((isTau) && !(pt_1>=28 && ((trg_singleelectron_27==1) || (trg_singleelectron_32==1) || (trg_singleelectron_35==1))) && (trg_singletau_trailing==1) && pt_2>180 && fabs(eta_2)<2.1))", "trg_selection"),
            )
        elif era == "2018":
            cuts.append(
                ("pt_2>30 && ((trg_singleelectron_35 == 1) || (trg_singleelectron_32 == 1) || (pt_1>25 && pt_1<33 && pt_2>35 && (trg_crossele_ele24tau30_hps == 1 || trg_crossele_ele24tau30 == 1)))", "trg_selection"),
            )
        else:
            raise ValueError("Given era does not exist")
        return Selection(name="et", cuts=cuts)
    if "tt" in channel:
        #  Add channel specific cuts to the list of cuts.
        cuts.extend([
            ("byVLooseDeepTau2017v2p1VSmu_1>0.5 && byVLooseDeepTau2017v2p1VSmu_2>0.5", "againstMuonDiscriminator"),
            ("byVVLooseDeepTau2017v2p1VSe_1>0.5 && byVVLooseDeepTau2017v2p1VSe_2>0.5", "againstElectronDiscriminator"),
            ("byTightDeepTau2017v2p1VSjet_1>0.5 && byTightDeepTau2017v2p1VSjet_2>0.5", "tau_iso"),
        ])
        if era == "2016":
            cuts.append(
                ("trg_doubletau==1", "trg_doubletau"),
            )
        elif era == "2017":
            cuts.append(
                ("((trg_doubletau_35_tightiso_tightid == 1) || (trg_doubletau_40_mediso_tightid == 1) || (trg_doubletau_40_tightiso == 1)) || ((pt_1>180)&&((trg_singletau_leading == 1))) || ((pt_2>180)&&(trg_singletau_trailing == 1))", "trg_selection"),
            )
        elif era == "2018":
            cuts.append(
                ("(((!(isMC||isEmbedded) && run>=317509) || (isMC||isEmbedded)) && (trg_doubletau_35_mediso_hps == 1)) || (!(isMC||isEmbedded) && (run<317509) && ((trg_doubletau_35_tightiso_tightid == 1) || (trg_doubletau_40_mediso_tightid == 1) || (trg_doubletau_40_tightiso == 1)))", "trg_selection"),
            )
        else:
                raise ValueError("Given era does not exist")
        return Selection(name="tt", cuts=cuts)
    if "em" in channel:
        #  Add channel specific cuts to the list of cuts.
        cuts.extend([
            ("iso_1<0.15", "ele_iso"),
            ("iso_2<0.2", "muon_iso"),
            ("abs(eta_1)<2.4", "electron_eta"),
        ])
        if era == "2016":
            cuts.append(
                ("pt_1>15 && pt_2>15 && ((pt_1>15 && pt_2>24 && trg_muonelectron_mu23ele12 == 1) || (pt_1>24 && pt_2>15 && trg_muonelectron_mu8ele23 == 1))","trg_selection"),
            )
        elif era == "2017":
            cuts.append(
               ("pt_1>15 && pt_2>15 && ((trg_muonelectron_mu23ele12 == 1) || (trg_muonelectron_mu8ele23 == 1))", "trg_selection"),
            )
        elif era == "2018":
            cuts.append(
                ("(trg_muonelectron_mu23ele12 == 1 && pt_1>15 && pt_2 > 24) || (trg_muonelectron_mu8ele23 == 1 && pt_1>24 && pt_2>15)", "trg_selection"),
            )
        else:
            raise ValueError("Given era does not exist")
        return Selection(name="em", cuts=cuts)
