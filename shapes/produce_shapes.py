#!/usr/bin/env python
import argparse
import logging
import os
import pickle
import re

from ntuple_processor import Histogram
from ntuple_processor import dataset_from_artusoutput, Unit, UnitManager, GraphManager, RunManager

from config.shapes.channel_selection import channel_selection
from config.shapes.file_names import files
from config.shapes.process_selection import DY_process_selection, TT_process_selection, VV_process_selection, W_process_selection, ZTT_process_selection, ZL_process_selection, ZJ_process_selection, TTT_process_selection, TTL_process_selection, TTJ_process_selection, VVT_process_selection, VVJ_process_selection, VVL_process_selection, ggH125_process_selection, qqH125_process_selection, ZTT_embedded_process_selection, ZH_process_selection, WH_process_selection, ggHWW_process_selection, qqHWW_process_selection, ZHWW_process_selection, WHWW_process_selection, ttH_process_selection
from config.shapes.process_selection import SUSYbbH_process_selection, SUSYggH_process_selection, SUSYggH_Ai_contribution_selection, SUSYggH_At_contribution_selection, SUSYggH_Ab_contribution_selection, SUSYggH_Hi_contribution_selection, SUSYggH_Ht_contribution_selection, SUSYggH_Hb_contribution_selection, SUSYggH_hi_contribution_selection, SUSYggH_ht_contribution_selection, SUSYggH_hb_contribution_selection
# from config.shapes.category_selection import categorization
from config.shapes.category_selection import categorization
# Variations for estimation of fake processes
from config.shapes.variations import same_sign, same_sign_em, anti_iso_lt, anti_iso_tt, anti_iso_tt_mcl, abcd_method
# Energy scale uncertainties
from config.shapes.variations import tau_es_3prong, tau_es_3prong1pizero, tau_es_1prong, tau_es_1prong1pizero, emb_tau_es_3prong, emb_tau_es_3prong1pizero, emb_tau_es_1prong, emb_tau_es_1prong1pizero, jet_es, mu_fake_es_1prong, mu_fake_es_1prong1pizero, ele_es, ele_res, emb_e_es, ele_fake_es_1prong, ele_fake_es_1prong1pizero
# MET related uncertainties.
from config.shapes.variations import met_unclustered, recoil_resolution, recoil_response
# efficiency uncertainties
from config.shapes.variations import tau_id_eff_lt, tau_id_eff_tt, emb_tau_id_eff_lt, emb_tau_id_eff_tt
# fake rate uncertainties
from config.shapes.variations import jet_to_tau_fake, zll_et_fake_rate_2016, zll_et_fake_rate_2017, zll_et_fake_rate_2018, zll_mt_fake_rate_2016, zll_mt_fake_rate_2017, zll_mt_fake_rate_2018
# trigger efficiencies
from config.shapes.variations import tau_trigger_eff_tt, tau_trigger_eff_tt_emb, trigger_eff_mt, trigger_eff_et, trigger_eff_et_emb, trigger_eff_mt_emb
from config.shapes.variations import prefiring, btag_eff, mistag_eff, ggh_acceptance, qqh_acceptance, zpt, top_pt, emb_decay_mode_eff_lt, emb_decay_mode_eff_tt
from config.shapes.variations import ff_variations_lt, ff_variations_tt, qcd_variations_em, wfakes_tt, wfakes_w_tt
from config.shapes.control_binning import control_binning, minimal_control_plot_set

logger = logging.getLogger("")


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
            description="Produce shapes for the legacy MSSM analysis.")
    parser.add_argument(
        "--era",
        required=True,
        type=str,
        help="Experiment era."
    )
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist: [channel for channel in channellist.split(',')],
        help="Channels to be considered, seperated by a comma without space"
    )
    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs."
    )
    parser.add_argument(
        "--et-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help=
        "Directories arranged as Artus output and containing a friend tree for et."
    )
    parser.add_argument(
        "--mt-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help=
        "Directories arranged as Artus output and containing a friend tree for mt."
    )
    parser.add_argument(
        "--tt-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help=
        "Directories arranged as Artus output and containing a friend tree for tt."
    )
    parser.add_argument(
        "--em-friend-directory",
        type=str,
        default=[],
        nargs='+',
        help=
        "Directories arranged as Artus output and containing a friend tree for em."
    )
    parser.add_argument(
        "--optimization-level",
        default=2,
        type=int,
        help="Level of optimization for graph merging."
    )
    parser.add_argument(
        "--num-processes",
        default=1,
        type=int,
        help="Number of processes to be used."
    )
    parser.add_argument(
        "--num-threads",
        default=1,
        type=int,
        help="Number of threads to be used."
    )
    parser.add_argument(
        "--skip-systematic-variations",
        action="store_true",
        help="Do not produce the systematic variations."
    )
    parser.add_argument(
        "--output-file",
        required=True,
        type=str,
        help="ROOT file where shapes will be stored."
    )
    parser.add_argument(
        "--control-plots",
        action="store_true",
        help="Produce shapes for control plots. Default is production of analysis shapes."
    )
    parser.add_argument(
        "--control-plots-full-samples",
        action="store_true",
        help="Produce shapes for control plots. Default is production of analysis shapes."
    )
    parser.add_argument(
        "--control-plot-set",
        default=minimal_control_plot_set,
        type=lambda varlist: [variable for variable in varlist.split(',')],
        help="Variables the shapes should be produced for."
    )
    parser.add_argument(
        "--only-create-graphs",
        action="store_true",
        help="Create and optimise graphs and create a pkl file containing the graphs to be processed."
    )
    parser.add_argument(
        "--process-selection",
        default=None,
        type=lambda proclist: set([process.lower() for process in proclist.split(',')]),
        help="Subset of processes to be processed."
    )
    parser.add_argument(
        "--graph-dir",
        default=None,
        type=str,
        help="Directory the graph file is written to."
    )
    parser.add_argument(
        "--enable-booking-check",
        action="store_true",
        help="Enables check for double actions during booking. Takes long for all variations."
    )
    return parser.parse_args()


def main(args):
    # Parse given arguments.
    friend_directories = {
        "et": args.et_friend_directory,
        "mt": args.mt_friend_directory,
        "tt": args.tt_friend_directory,
        "em": args.em_friend_directory,
    }
    if ".root" in args.output_file:
        output_file = args.output_file
        log_file = args.output_file.replace(".root", ".log")
    else:
        output_file = "{}.root".format(args.output_file)
        log_file = "{}.log".format(args.output_file)

    nominals = {}
    nominals[args.era] = {}
    nominals[args.era]['datasets'] = {}
    nominals[args.era]['units'] = {}

    susy_masses = {
        "2016": {
            "bbH": [ 80, 90, 110, 120, 130, 140, 160, 180, 200, 250, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "ggH": [ 80, 90, 100, 110, 120, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
        },
        "2017": {
            "bbH": [  80,   90,  110,  120,  125,  130,  140,  160,  180,  200, 250,  300,  350,  400,  500,  600,  700,  800,  900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "ggH": [  80,   90,  100,  110,  120,  130,  140,  180,  200, 250,  300,  350,  400,  450,  600,  700,  800,  900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
        },
        "2018": {
            "bbH": [  80,   90,  100,  110,  120,  125,  130,  140,  160,  180,  200, 250,  300,  350,  400,  450,  500,  600,  700,  800,  900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200, 3500],
            "ggH": [  80,   90,  100,  110,  120,  130,  140,  160,  180,  200, 250,  300,  350,  400,  450,  600,  700,  800,  900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
        },
    }

    def get_nominal_datasets(era, channel):
        datasets = dict()
        def filter_friends(dataset, friend):
            # Add fake factor friends only for backgrounds.
            if re.match("(gg|qq|susybb|susygg|tt|w|z|v)h", dataset.lower()):
                if "FakeFactors" in friend or "EMQCDWeights" in friend:
                    return False
            # Add NLOReweighting friends only for ggh signals.
            if "NLOReweighting" in friend:
                if re.match("(susygg)h", dataset.lower()):
                    pass
                else:
                    return False
            return True
        for key, names in files[era][channel].items():
            datasets[key] = dataset_from_artusoutput(
                    key, names, channel + '_nominal', args.directory,
                    [fdir for fdir in friend_directories[channel] if filter_friends(key, fdir)])
        return datasets

    def get_analysis_units(channel, era, datasets, nn_shapes=False):
        return {
                "data" : [Unit(
                            datasets["data"], [
                                channel_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "emb": [Unit(
                            datasets["EMB"], [
                                channel_selection(channel, era),
                                ZTT_embedded_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "ztt" : [Unit(
                            datasets["DY"], [
                                channel_selection(channel, era),
                                DY_process_selection(channel, era),
                                ZTT_process_selection(channel),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "zl" :  [Unit(
                            datasets["DY"], [
                                channel_selection(channel, era),
                                DY_process_selection(channel, era),
                                ZL_process_selection(channel),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "zj" :  [Unit(
                            datasets["DY"], [
                                channel_selection(channel, era),
                                DY_process_selection(channel, era),
                                ZJ_process_selection(channel),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "ttt" : [Unit(
                            datasets["TT"], [
                                channel_selection(channel, era),
                                TT_process_selection(channel, era),
                                TTT_process_selection(channel),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "ttl" : [Unit(
                            datasets["TT"], [
                                channel_selection(channel, era),
                                TT_process_selection(channel, era),
                                TTL_process_selection(channel),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "ttj" : [Unit(
                            datasets["TT"], [
                                channel_selection(channel, era),
                                TT_process_selection(channel, era),
                                TTJ_process_selection(channel),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "vvt" : [Unit(
                            datasets["VV"], [
                                channel_selection(channel, era),
                                VV_process_selection(channel, era),
                                VVT_process_selection(channel),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "vvl" : [Unit(
                            datasets["VV"], [
                                channel_selection(channel, era),
                                VV_process_selection(channel, era),
                                VVL_process_selection(channel),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "vvj" : [Unit(
                            datasets["VV"], [
                                channel_selection(channel, era),
                                VV_process_selection(channel, era),
                                VVJ_process_selection(channel),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "w"   : [Unit(
                            datasets["W"], [
                                channel_selection(channel, era),
                                W_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "ggh" : [Unit(
                            datasets["ggH"], [
                                channel_selection(channel, era),
                                ggH125_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "qqh" : [Unit(
                            datasets["qqH"], [
                                channel_selection(channel, era),
                                qqH125_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "wh"  : [Unit(
                            datasets["WH"], [
                                channel_selection(channel, era),
                                WH_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "zh"  : [Unit(
                            datasets["ZH"], [
                                channel_selection(channel, era),
                                ZH_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "tth"  : [Unit(
                            datasets["ttH"], [
                                channel_selection(channel, era),
                                ttH_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "gghww"  : [Unit(
                            datasets["ggHWW"], [
                                channel_selection(channel, era),
                                ggHWW_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "qqhww"  : [Unit(
                            datasets["qqHWW"], [
                                channel_selection(channel, era),
                                qqHWW_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "zhww"  : [Unit(
                            datasets["ZHWW"], [
                                channel_selection(channel, era),
                                ZHWW_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                "whww"  : [Unit(
                            datasets["WHWW"], [
                                channel_selection(channel, era),
                                WHWW_process_selection(channel, era),
                                category_selection], actions) for category_selection, actions in categorization[channel]],
                **{"ggh{}".format(mass): [Unit(
                                            datasets["susyggH_{}".format(mass)], [
                                                channel_selection(channel, era),
                                                SUSYggH_process_selection(channel, era),
                                                contribution_selection(channel),
                                                category_selection], actions) for category_selection, actions in categorization[channel]
                                                                                               for contribution_selection in [
                                                                                                                              SUSYggH_Ai_contribution_selection,
                                                                                                                              SUSYggH_At_contribution_selection,
                                                                                                                              SUSYggH_Ab_contribution_selection,
                                                                                                                              SUSYggH_Hi_contribution_selection,
                                                                                                                              SUSYggH_Ht_contribution_selection,
                                                                                                                              SUSYggH_Hb_contribution_selection,
                                                                                                                              SUSYggH_hi_contribution_selection,
                                                                                                                              SUSYggH_ht_contribution_selection,
                                                                                                                              SUSYggH_hb_contribution_selection]]
                                            for mass in susy_masses[era]["ggH"]},
                **{"bbh{}".format(mass): [Unit(
                                                datasets["susybbH_{}".format(mass)], [
                                                    channel_selection(channel, era),
                                                    SUSYbbH_process_selection(channel, era),
                                                    category_selection], actions) for category_selection, actions in categorization[channel]]
                                            for mass in susy_masses[era]["bbH"]},
        }

    def get_control_units(channel, era, datasets):
        return {
               'data' : [Unit(
                   datasets['data'],[
                       channel_selection(channel, era)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'emb' : [Unit(
                   datasets['EMB'],[
                       channel_selection(channel, era),
                       ZTT_embedded_process_selection(channel, era)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'ztt' : [Unit(
                   datasets['DY'], [
                       channel_selection(channel, era),
                       DY_process_selection(channel, era),
                       ZTT_process_selection(channel)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'zl' : [Unit(
                   datasets['DY'], [
                      channel_selection(channel, era),
                      DY_process_selection(channel, era),
                      ZL_process_selection(channel)],
                      [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'zj' : [Unit(
                   datasets['DY'], [
                       channel_selection(channel, era),
                       DY_process_selection(channel, era),
                       ZJ_process_selection(channel)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'ttl' : [Unit(
                   datasets['TT'], [
                       channel_selection(channel, era),
                       TT_process_selection(channel, era),
                       TTL_process_selection(channel)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'ttt' : [Unit(
                   datasets['TT'], [
                       channel_selection(channel, era),
                       TT_process_selection(channel, era),
                       TTT_process_selection(channel)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'ttj' : [Unit(
                   datasets['TT'], [
                       channel_selection(channel, era),
                       TT_process_selection(channel, era),
                       TTJ_process_selection(channel)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'vvl' : [Unit(
                   datasets['VV'], [
                       channel_selection(channel, era),
                       VV_process_selection(channel, era),
                       VVL_process_selection(channel)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'vvt' : [Unit(
                   datasets['VV'], [
                       channel_selection(channel, era),
                       VV_process_selection(channel, era),
                       VVT_process_selection(channel)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'vvj' : [Unit(
                   datasets['VV'], [
                       channel_selection(channel, era),
                       VV_process_selection(channel, era),
                       VVJ_process_selection(channel)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'w' :   [Unit(
                   datasets['W'], [
                       channel_selection(channel, era),
                       W_process_selection(channel, era)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'ggh' : [Unit(
                   datasets['ggH'], [
                       channel_selection(channel, era),
                       ggH125_process_selection(channel, era)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
               'qqh' : [Unit(
                   datasets['qqH'], [
                       channel_selection(channel, era),
                       qqH125_process_selection(channel, era)],
                       [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])],
                **{"ggh{}".format(mass): [Unit(
                                            datasets["susyggH_{}".format(mass)], [
                                                channel_selection(channel, era),
                                                SUSYggH_process_selection(channel, era),
                                                contribution_selection(channel),
                                                ], [control_binning[channel][v] for v in set(control_binning[channel].keys()) & set(args.control_plot_set)])
                                                                                               for contribution_selection in [
                                                                                                                              SUSYggH_Ai_contribution_selection,
                                                                                                                              SUSYggH_At_contribution_selection,
                                                                                                                              SUSYggH_Ab_contribution_selection,
                                                                                                                              SUSYggH_Hi_contribution_selection,
                                                                                                                              SUSYggH_Ht_contribution_selection,
                                                                                                                              SUSYggH_Hb_contribution_selection,
                                                                                                                              SUSYggH_hi_contribution_selection,
                                                                                                                              SUSYggH_ht_contribution_selection,
                                                                                                                              SUSYggH_hb_contribution_selection]]
                                            for mass in susy_masses[era]["ggH"]},
                }
    # Step 1: create units and book actions
    for channel in args.channels:
        nominals[args.era]['datasets'][channel] = get_nominal_datasets(args.era, channel)
        if args.control_plots:
            nominals[args.era]['units'][channel] = get_control_units(channel, args.era, nominals[args.era]['datasets'][channel])
        else:
            nominals[args.era]['units'][channel] = get_analysis_units(channel, args.era, nominals[args.era]['datasets'][channel])

    um = UnitManager()

    if args.process_selection is None:
        procS = {"data", "emb", "ztt", "zl", "zj", "ttt", "ttl", "ttj", "vvt", "vvl", "vvj", "w",
                 "ggh", "qqh", "tth", "zh", "wh", "gghww", "qqhww", "zhww", "whww"} \
                | set("ggh{}".format(mass) for mass in susy_masses[args.era]["ggH"]) \
                | set("bbh{}".format(mass) for mass in susy_masses[args.era]["bbH"])
    else:
        procS = args.process_selection

    print("Processes to be computed: ", procS)
    dataS = {"data"} & procS
    embS = {"emb"} & procS
    jetFakesDS = {
        "et": {"zj", "ttj", "vvj", "w"} & procS,
        "mt": {"zj", "ttj", "vvj", "w"} & procS,
        "tt": {"zj", "ttj", "vvj", "w"} & procS,
        "em": {"w"} & procS
    }
    leptonFakesS = {"zl", "ttl", "vvl"} & procS
    trueTauBkgS = {"ztt", "ttt", "vvt"} & procS
    sm_signalsS = {"ggh", "qqh", "tth", "zh", "wh", "gghww", "qqhww", "zhww", "whww"} & procS
    mssm_signalsS = (set("ggh{}".format(mass) for mass in susy_masses[args.era]["ggH"]) \
                    | set("bbh{}".format(mass) for mass in susy_masses[args.era]["bbH"]) ) & procS
    signalsS = sm_signalsS | mssm_signalsS
    if args.control_plots and not args.control_plots_full_samples:
        signalsS = signalsS & {"ggh", "qqh"}

    simulatedProcsDS = {
        chname_: jetFakesDS[chname_] | leptonFakesS | trueTauBkgS | signalsS for chname_ in ["et", "mt", "tt", "em"]
    }

    for ch_ in args.channels:
        um.book([unit for d in signalsS for unit in nominals[args.era]['units'][ch_][d]], enable_check=args.enable_booking_check)
        if ch_ in ['mt', 'et']:
            um.book([unit for d in dataS | embS | trueTauBkgS | leptonFakesS for unit in nominals[args.era]['units'][ch_][d]], [same_sign, anti_iso_lt], enable_check=args.enable_booking_check)
            um.book([unit for d in jetFakesDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [same_sign], enable_check=args.enable_booking_check)
        elif ch_ == 'tt':
            um.book([unit for d in dataS | embS | trueTauBkgS for unit in nominals[args.era]['units'][ch_][d]], [anti_iso_tt, *abcd_method], enable_check=args.enable_booking_check)
            um.book([unit for d in jetFakesDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [*abcd_method], enable_check=args.enable_booking_check)
            um.book([unit for d in leptonFakesS for unit in nominals[args.era]['units'][ch_][d]], [wfakes_tt, anti_iso_tt_mcl, *abcd_method], enable_check=args.enable_booking_check)
            um.book([unit for d in {'w'} & procS for unit in nominals[args.era]['units'][ch_][d]], [wfakes_w_tt], enable_check=args.enable_booking_check)
        elif ch_ == 'em':
            um.book([unit for d in dataS | embS | simulatedProcsDS[ch_] - signalsS for unit in nominals[args.era]['units'][ch_][d]], [same_sign_em], enable_check=args.enable_booking_check)
        if args.skip_systematic_variations:
            pass
        else:
            # Book variations common to all channels.
            um.book([unit for d in {"ggh"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*ggh_acceptance], enable_check=args.enable_booking_check)
            um.book([unit for d in {"qqh"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*qqh_acceptance], enable_check=args.enable_booking_check)
            um.book([unit for d in simulatedProcsDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [*jet_es, *met_unclustered, *btag_eff, *mistag_eff], enable_check=args.enable_booking_check)
            um.book([unit for d in {'ztt', 'zj', 'zl', 'w'} & procS | signalsS for unit in nominals[args.era]['units'][ch_][d]], [*recoil_resolution, *recoil_response], enable_check=args.enable_booking_check)
            um.book([unit for d in {'ztt', 'zl', 'zj'} & procS for unit in nominals[args.era]['units'][ch_][d]], [*zpt], enable_check=args.enable_booking_check)
            um.book([unit for d in {'ttt', 'ttl', 'ttj'} & procS for unit in nominals[args.era]['units'][ch_][d]], [*top_pt], enable_check=args.enable_booking_check)
            # Book variations common to multiple channels.
            if ch_ in ["et", "mt", "tt"]:
                um.book([unit for d in (trueTauBkgS | leptonFakesS | signalsS) - {"zl"} for unit in nominals[args.era]['units'][ch_][d]], [*tau_es_3prong, *tau_es_3prong1pizero, *tau_es_1prong, *tau_es_1prong1pizero], enable_check=args.enable_booking_check)
                um.book([unit for d in jetFakesDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [*jet_to_tau_fake], enable_check=args.enable_booking_check)
                um.book([unit for d in embS for unit in nominals[args.era]['units'][ch_][d]], [*emb_tau_es_3prong, *emb_tau_es_3prong1pizero, *emb_tau_es_1prong, *emb_tau_es_1prong1pizero,
                                                                                               *tau_es_3prong, *tau_es_3prong1pizero, *tau_es_1prong, *tau_es_1prong1pizero],
                                                                                            enable_check=args.enable_booking_check)
            if ch_ in ["et", "mt"]:
                um.book([unit for d in (trueTauBkgS | leptonFakesS | signalsS) - {"zl"} for unit in nominals[args.era]['units'][ch_][d]], [*tau_id_eff_lt], enable_check=args.enable_booking_check)
                um.book([unit for d in dataS | embS | leptonFakesS | trueTauBkgS for unit in nominals[args.era]['units'][ch_][d]], [*ff_variations_lt], enable_check=args.enable_booking_check)
                um.book([unit for d in embS for unit in nominals[args.era]['units'][ch_][d]], [*emb_tau_id_eff_lt, *tau_id_eff_lt, *emb_decay_mode_eff_lt], enable_check=args.enable_booking_check)
            if ch_ in ["et", "em"]:
                um.book([unit for d in simulatedProcsDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [*ele_es, *ele_res], enable_check=args.enable_booking_check)
                um.book([unit for d in embS for unit in nominals[args.era]['units'][ch_][d]], [*emb_e_es], enable_check=args.enable_booking_check)
            # Book channel independent variables.
            if ch_ == "mt":
                um.book([unit for d in {"zl"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*mu_fake_es_1prong, *mu_fake_es_1prong1pizero], enable_check=args.enable_booking_check)
                um.book([unit for d in simulatedProcsDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [*trigger_eff_mt], enable_check=args.enable_booking_check)
                um.book([unit for d in embS for unit in nominals[args.era]['units'][ch_][d]], [*trigger_eff_mt_emb, *trigger_eff_mt], enable_check=args.enable_booking_check)
            if ch_ == "et":
                um.book([unit for d in {"zl"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*ele_fake_es_1prong, *ele_fake_es_1prong1pizero], enable_check=args.enable_booking_check)
                um.book([unit for d in simulatedProcsDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [*trigger_eff_et], enable_check=args.enable_booking_check)
                um.book([unit for d in embS for unit in nominals[args.era]['units'][ch_][d]], [*trigger_eff_et_emb, *trigger_eff_et], enable_check=args.enable_booking_check)
            if ch_ == "tt":
                um.book([unit for d in trueTauBkgS | leptonFakesS | signalsS for unit in nominals[args.era]['units'][ch_][d]], [*tau_id_eff_tt], enable_check=args.enable_booking_check)
                um.book([unit for d in simulatedProcsDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [*tau_trigger_eff_tt], enable_check=args.enable_booking_check)
                um.book([unit for d in embS for unit in nominals[args.era]['units'][ch_][d]], [*emb_tau_id_eff_tt, *tau_id_eff_tt, *tau_trigger_eff_tt_emb, *tau_trigger_eff_tt, *emb_decay_mode_eff_tt], enable_check=args.enable_booking_check)
                um.book([unit for d in dataS | embS | trueTauBkgS | leptonFakesS for unit in nominals[args.era]['units'][ch_][d]], [*ff_variations_tt], enable_check=args.enable_booking_check)
            if ch_ == "em":
                um.book([unit for d in dataS | embS | simulatedProcsDS[ch_] - signalsS for unit in nominals[args.era]['units'][ch_][d]], [*qcd_variations_em], enable_check=args.enable_booking_check)
            # Book era dependent uncertainty shapes
            if "2016" in args.era:
                um.book([unit for d in simulatedProcsDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [*prefiring], enable_check=args.enable_booking_check)
                if ch_ == "mt":
                    um.book([unit for d in {"zl"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*zll_mt_fake_rate_2016], enable_check=args.enable_booking_check)
                elif ch_ == "et":
                    um.book([unit for d in {"zl"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*zll_et_fake_rate_2016], enable_check=args.enable_booking_check)
            elif "2017" in args.era:
                um.book([unit for d in simulatedProcsDS[ch_] for unit in nominals[args.era]['units'][ch_][d]], [*prefiring], enable_check=args.enable_booking_check)
                if ch_ == "mt":
                    um.book([unit for d in {"zl"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*zll_mt_fake_rate_2017], enable_check=args.enable_booking_check)
                elif ch_ == "et":
                    um.book([unit for d in {"zl"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*zll_et_fake_rate_2017], enable_check=args.enable_booking_check)
            elif "2018" in args.era:
                if ch_ == "mt":
                    um.book([unit for d in {"zl"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*zll_mt_fake_rate_2018], enable_check=args.enable_booking_check)
                elif ch_ == "et":
                    um.book([unit for d in {"zl"} & procS for unit in nominals[args.era]['units'][ch_][d]], [*zll_et_fake_rate_2018], enable_check=args.enable_booking_check)


    # Step 2: convert units to graphs and merge them
    g_manager = GraphManager(um.booked_units, True)
    g_manager.optimize(args.optimization_level)
    graphs = g_manager.graphs
    for graph in graphs:
        print("%s" % graph)

    if args.only_create_graphs:
        if args.control_plots:
            graph_file_name = "control_unit_graphs-{}-{}-{}.pkl".format(args.era, ",".join(args.channels), ",".join(sorted(procS)))
        else:
            graph_file_name = "analysis_unit_graphs-{}-{}-{}.pkl".format(args.era, ",".join(args.channels), ",".join(sorted(procS)))
        if args.graph_dir is not None:
            graph_file = os.path.join(args.graph_dir, graph_file_name)
        else:
            graph_file = graph_file_name
        logger.info("Writing created graphs to file %s.", graph_file)
        with open(graph_file, 'wb') as f:
            pickle.dump(graphs, f)
    else:
        # Step 3: convert to RDataFrame and run the event loop
        r_manager = RunManager(graphs)
        r_manager.run_locally(output_file, args.num_processes, args.num_threads)
    return


if __name__ == "__main__":
    args = parse_arguments()
    if ".root" in args.output_file:
        log_file = args.output_file.replace(".root", ".log")
    else:
        log_file = "{}.log".format(args.output_file)
    setup_logging(log_file, logging.INFO)
    main(args)
