import logging

from ntuple_processor.utils import Selection, WarnDict
from config.logging_setup_configs import setup_logging

logger = setup_logging(logger=logging.getLogger(__name__))


def channel_selection(channel, era, special=None, vs_jet_wp="Tight", vs_ele_wp="VVLoose", selection_option="CR", **kwargs):

    cuts = WarnDict()
    cuts["extraelec_veto"] = "(extraelec_veto < 0.5)"
    cuts["extramuon_veto"] = "(extramuon_veto < 0.5)"
    cuts["dilepton_veto"] = "(dilepton_veto < 0.5)"
    cuts["os"] = "((q_1 * q_2) < 0)"
    cuts["b_tagging"] = "(nbtag >= 1) && (bpair_pt_2 > 0)"

    if "DR;ff" in selection_option:
        modify_for_ff_DR(obj=cuts, region=selection_option.split(";")[-1], channel=None)

    wps_dict = {"VVTight", "VVTight", "Tight", "Medium", "Loose", "VLoose", "VVLoose", "VVVLoose"}
    try:
        assert vs_ele_wp in wps_dict, f"{vs_ele_wp} is not a valid vsEle discriminator"
    except AssertionError as e:
        logger.error(e)
        raise e

    try:
        assert vs_jet_wp in wps_dict, f"{vs_jet_wp} is not a valid vsJet discriminator"
    except AssertionError as e:
        logger.error(e)
        raise e

    if special is None:
        if "mt" in channel:
            cuts["againstMuonDiscriminator"] = "(id_tau_vsMu_Tight_2 > 0.5)"
            cuts["againstElectronDiscriminator"] = "(id_tau_vsEle_VVLoose_2 > 0.5)"
            cuts["tau_iso"] = "(id_tau_vsJet_Medium_2 > 0.5)"
            cuts["muon_iso"] = "(iso_1 < 0.15)"
            cuts["mt_cut"] = "(mt_1 < 70)"

            if "DR;ff" in selection_option:
                modify_for_ff_DR(obj=cuts, region=selection_option.split(";")[-1], channel=channel)

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
                logger.error(f"Given era {era} does not exist")
                raise ValueError(f"Given era {era} does not exist")

            return Selection(name="mt", cuts=cuts)
        if "et" in channel:
            cuts["againstMuonDiscriminator"] = "(id_tau_vsMu_VLoose_2 > 0.5)"
            cuts["againstElectronDiscriminator"] = "(id_tau_vsEle_Tight_2 > 0.5)"
            cuts["tau_iso"] = "(id_tau_vsJet_Medium_2 > 0.5)"
            cuts["ele_iso"] = "(iso_1 < 0.15)"
            cuts["mt_cut"] = "(mt_1 < 70)"

            if "DR;ff" in selection_option:
                modify_for_ff_DR(obj=cuts, region=selection_option.split(";")[-1], channel=channel)

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
                logger.error(f"Given era {era} does not exist")
                raise ValueError(f"Given era {era} does not exist")

            return Selection(name="et", cuts=cuts)
        if "tt" in channel:
            cuts["againstMuonDiscriminator"] = "(id_tau_vsMu_VLoose_1 > 0.5) && (id_tau_vsMu_VLoose_2 > 0.5)"
            cuts["againstElectronDiscriminator"] = "(id_tau_vsEle_VVLoose_1 > 0.5) && (id_tau_vsEle_VVLoose_2 > 0.5)"
            cuts["tau_iso"] = "(id_tau_vsJet_Medium_1 > 0.5) && (id_tau_vsJet_Medium_2 > 0.5)"

            if "DR;ff" in selection_option:
                modify_for_ff_DR(obj=cuts, region=selection_option.split(";")[-1], channel=channel)

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
                logger.error(f"Given era {era} does not exist")
                raise ValueError(f"Given era {era} does not exist")

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
                logger.error(f"Given era {era} does not exist")
                raise ValueError(f"Given era {era} does not exist")

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
                logger.error(f"Given era {era} does not exist")
                raise ValueError(f"Given era {era} does not exist")

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
                logger.error(f"Given era {era} does not exist")
                raise ValueError(f"Given era {era} does not exist")

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
                logger.error(f"Given era {era} does not exist")
                raise ValueError(f"Given era {era} does not exist")

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
                logger.error(f"Given era {era} does not exist")
                raise ValueError(f"Given era {era} does not exist")

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
            logger.error(f"Given era {era} does not exist")
            raise ValueError(f"Given era {era} does not exist")

        return Selection(name="mt", cuts=cuts)
    elif special == "EleES":
        assert channel == "ee", "EleES measurement is done in the ee channel only"

        cuts.pop("extramuon_veto")

        cuts["extraelec_veto"] = "(extraelec_veto > 0.5)"
        # cuts["extramuon_veto"] = "(extramuon_veto < 0.5)"
        cuts["dilepton_veto"] = "(dilepton_veto < 0.5)"
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
            logger.error(f"Given era {era} does not exist")
            raise ValueError(f"Given era {era} does not exist")

        return Selection(name="ee", cuts=cuts)
    else:
        logger.error(f"Given special selection: {special} does not exist")
        raise ValueError(f"Given special selection: {special} does not exist")


def modify_for_ff_DR(obj, region, channel=None):
    # general DR cuts
    if channel is None:
        logger.info("No channel specified, applying general DR cuts")
        if region == "wjet":
            logger.info(f"{region}: no additional cuts")
        elif region == "qcd":
            obj["os"] = "((q_1 * q_2) > 0)"  # fake ss
            logger.info(f"{region}: os cut changed {obj['os']}")
        elif region == "ttbar":
            obj.pop("extraelec_veto")
            obj.pop("extramuon_veto")
            obj.pop("dilepton_veto")
            obj["lepton_veto"] = """(
                !(
                    (extramuon_veto < 0.5) &&
                    (extraelec_veto < 0.5) &&
                    (dilepton_veto < 0.5)
                )
            )"""
            logger.info(f"{region}: extra lepton veto cut changed to {obj['lepton_veto']}")
        else:
            logger.error(f"{region} does not exist")
            raise ValueError(f"{region} does not exist")

    # channel specific DR cuts
    elif channel == "mt":
        logger.info(f"Applying DR cuts for {channel}")
        if region == "wjet":
            obj["btag_veto"] = "(nbtag == 0)"
            obj["mt_cut"] = "(mt_1 > 70)"
            logger.info(f"{region}: nbtag cut changed to {obj['btag_veto']}, mt cut changed to {obj['mt_cut']}")
        elif region == "qcd":
            obj["muon_iso"] = "((iso_1 > 0.05) && (iso_1 < 0.15))"
            obj["mt_cut"] = "(mt_1 < 50)"
            obj["btag_veto"] = "(nbtag >= 0)"
            logger.info(
                f"{region}: muon iso cut changed to {obj['muon_iso']}, mt cut changed to "
                f"{obj['mt_cut']}, btag veto cut changed to {obj['btag_veto']}",
            )
        elif region == "ttbar":
            obj["btag_veto"] = "(nbtag >= 0)"
            logger.info(f"{region}: btag veto cut changed to {obj['btag_veto']}")
        else:
            logger.error(f"{region} does not exist")
            raise ValueError(f"{region} does not exist")
    elif channel == "et":
        logger.error(f"{channel} not implemented yet")
        raise NotImplementedError(f"{channel} not implemented yet")
    elif channel == "tt":
        logger.error(f"{channel} not implemented yet")
        raise NotImplementedError(f"{channel} not implemented yet")
    else:
        logger.error(f"{channel} does not exist")
        raise ValueError(f"{channel} does not exist")
