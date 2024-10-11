#!/usr/bin/env python
import argparse
import logging
import os
import pickle
import re
import yaml
from itertools import combinations

from shapes.utils import (
    add_process,
    book_histograms,
    add_control_process,
    get_nominal_datasets,
    filter_friends,
    add_tauES_datasets,
    book_tauES_histograms,
)
from ntuple_processor.variations import ReplaceVariable
from ntuple_processor import Histogram
from ntuple_processor import (
    Unit,
    UnitManager,
    GraphManager,
    RunManager,
)
from ntuple_processor.utils import Selection

from config.shapes.channel_selection import channel_selection
from config.shapes.file_names import files
from config.shapes.process_selection import (
    # Data_base_process_selection,
    DY_process_selection,
    DY_NLO_process_selection,
    TT_process_selection,
    ST_process_selection,
    VV_process_selection,
    W_process_selection,
    ZTT_process_selection,
    ZL_process_selection,
    ZJ_process_selection,
    TTT_process_selection,
    TTL_process_selection,
    TTJ_process_selection,
    STT_process_selection,
    STL_process_selection,
    STJ_process_selection,
    VVT_process_selection,
    VVJ_process_selection,
    VVL_process_selection,
    EWK_process_selection,
    ggH125_process_selection,
    qqH125_process_selection,
    ZTT_embedded_process_selection,
    VH_process_selection,
    ZH_process_selection,
    WH_process_selection,
    ggHWW_process_selection,
    qqHWW_process_selection,
    ZHWW_process_selection,
    WHWW_process_selection,
    ttH_process_selection,
    NMSSM_Ybb_process_selection,
    NMSSM_Ytt_process_selection,
)

import config.shapes.category_selection as cat_sel
# from config.shapes.category_selection import categorization as default_categorization
# from config.shapes.category_selection import boosted_categorization as default_boosted_categorization
from config.shapes.tauid_measurement_binning import (
    categorization as tauid_categorization,
)
from config.shapes.taues_measurement_binning import (
    categorization as taues_categorization,
)

# Variations for estimation of fake processes
from config.shapes.variations import (
    same_sign,
    anti_iso_lt,
    boosted_same_sign,
    boosted_anti_iso_lt,
    anti_iso_tt,
    boosted_anti_iso_tt,
    # abcd_method,
)

# Energy scale uncertainties
from config.shapes.variations import (
    tau_es_3prong,
    tau_es_3prong1pizero,
    tau_es_1prong,
    tau_es_1prong1pizero,
    mu_fake_es_inc,
    ele_fake_es,
    emb_tau_es_3prong,
    emb_tau_es_3prong1pizero,
    emb_tau_es_1prong,
    emb_tau_es_1prong1pizero,
    jet_es,
    jet_es_hem,
    # TODO add missing ES
    # mu_fake_es_1prong,
    # mu_fake_es_1prong1pizero,
    ele_es,
    ele_res,
    emb_e_es,
    # ele_fake_es_1prong,
    # ele_fake_es_1prong1pizero,
    # ele_fake_es,
)
# Uncertainties (boosted tau)
from config.shapes.variations import (
    boosted_tau_es_3prong,
    boosted_tau_es_1prong,
    boosted_tau_es_1prong1pizero,
    boosted_tau_id_eff_lt,
    boosted_tau_id_eff_tt,
    ff_variations_boosted_lt,
    ff_variations_boosted_tt,
    trigger_eff_boosted_tt,
    trigger_eff_boosted_mt,
    trigger_eff_boosted_et,
    boosted_zll_mt_fake_rate,
    boosted_zll_et_fake_rate,
)

# MET related uncertainties.
from config.shapes.variations import (
    met_unclustered,
    recoil_resolution,
    recoil_response,
)

# efficiency uncertainties
from config.shapes.variations import (
    tau_id_eff_lt,
    emb_tau_id_eff_lt,
    emb_tau_id_eff_lt_corr,
    tau_id_eff_tt,
    emb_tau_id_eff_tt,
)

# fake rate uncertainties
from config.shapes.variations import jet_to_tau_fake, jet_to_tau_fake_boosted, zll_et_fake_rate, zll_mt_fake_rate

# trigger efficiencies
from config.shapes.variations import (
    trigger_eff_tt,
    trigger_eff_tt_emb,
    trigger_eff_mt,
    trigger_eff_mt_emb,
    trigger_eff_et,
    trigger_eff_et_emb,
)

# Additional uncertainties
from config.shapes.variations import (
    prefiring,
    zpt,
    top_pt,
    pileup_reweighting,
)

# Additional uncertainties
from config.shapes.variations import (
    btagging,
    particleNet_Xbb,
    LHE_scale_norm,
)
from config.shapes.signal_variations import (
    ggh_acceptance,
    qqh_acceptance,
)

# jet fake uncertainties
from config.shapes.variations import (
    ff_variations_lt,
    ff_variations_tt,
    # ff_variations_tau_es_lt,
    # ff_variations_tau_es_emb_lt,
)

from config.shapes.control_binning import control_binning as default_control_binning
from config.shapes.gof_binning import load_gof_binning

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
        description="Produce shapes for the legacy NMSSM analysis."
    )
    parser.add_argument("--era", required=True, type=str, help="Experiment era.")
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist: [channel for channel in channellist.split(",")],
        help="Channels to be considered, seperated by a comma without space",
    )
    parser.add_argument(
        "--directory", required=True, type=str, help="Directory with Artus outputs."
    )
    parser.add_argument(
        "--et-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for et.",
    )
    parser.add_argument(
        "--mt-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for mt.",
    )
    parser.add_argument(
        "--tt-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for tt.",
    )
    parser.add_argument(
        "--em-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for em.",
    )
    parser.add_argument(
        "--mm-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for mm.",
    )
    parser.add_argument(
        "--ee-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for ee.",
    )
    parser.add_argument(
        "--optimization-level",
        default=2,
        type=int,
        help="Level of optimization for graph merging.",
    )
    parser.add_argument(
        "--num-processes", default=1, type=int, help="Number of processes to be used."
    )
    parser.add_argument(
        "--num-threads", default=1, type=int, help="Number of threads to be used."
    )
    parser.add_argument(
        "--skip-systematic-variations",
        action="store_true",
        help="Do not produce the systematic variations.",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        type=str,
        help="ROOT file where shapes will be stored.",
    )
    parser.add_argument(
        "--control-plots",
        action="store_true",
        help="Produce shapes for control plots. Default is production of analysis shapes.",
    )
    parser.add_argument(
        "--gof-inputs",
        action="store_true",
        help="Produce shapes for control plots. Default is production of analysis shapes.",
    )
    parser.add_argument(
        "--do-2dGofs",
        action="store_true",
        help="It set, run the 2D gof Tests as well",
    )
    parser.add_argument(
        "--control-plots-full-samples",
        action="store_true",
        help="Produce shapes for control plots. Default is production of analysis shapes.",
    )
    parser.add_argument(
        "--control-plot-set",
        default=[],
        type=lambda varlist: [variable for variable in varlist.split(",")],
        help="Variables the shapes should be produced for.",
    )
    parser.add_argument(
        "--only-create-graphs",
        action="store_true",
        help="Create and optimise graphs and create a pkl file containing the graphs to be processed.",
    )
    parser.add_argument(
        "--process-selection",
        default=None,
        type=lambda proclist: set([process.lower() for process in proclist.split(",")]),
        help="Subset of processes to be processed.",
    )
    parser.add_argument(
        "--graph-dir",
        default=None,
        type=str,
        help="Directory the graph file is written to.",
    )
    parser.add_argument(
        "--enable-booking-check",
        action="store_true",
        help="Enables check for double actions during booking. Takes long for all variations.",
    )
    parser.add_argument(
        "--special-analysis",
        help="Can be set to a special analysis name to only run that analysis.",
        choices=["TauID", "TauES"],
        default=None,
    )
    parser.add_argument(
        "--boosted-tau-analysis",
        action="store_true",
        help="Can be set to a switch to a boosted tau analysis selection.",
    )
    parser.add_argument(
        "--boosted-b-analysis",
        action="store_true",
        help="Can be set to a switch to a boosted bjet analysis selection.",
    )
    parser.add_argument(
        "--massX",
        required=True,
        type=str,
        help="Mass value of X to be used for NMSSM samples.",
    )
    parser.add_argument(
        "--massY",
        required=True,
        type=str,
        help="Mass value of Y to be used for NMSSM samples.",
    )
    parser.add_argument(
        "--xrootd",
        action="store_true",
        help="Read input ntuples and friends via xrootd from gridka dCache",
    )
    parser.add_argument(
        "--validation-tag",
        default="default",
        type=str,
        help="Tag to be used for the validation of the input samples",
    )
    return parser.parse_args()

def get_control_units(
    channel, era, datasets, special_analysis, variables, boosted_tau=False, boosted_b=False
):
    control_units = {}
    control_binning = default_control_binning

    # check that all variables are available
    variable_set = set()
    for variable in set(variables):
        if variable not in control_binning[channel]:
            raise Exception("Variable %s not available in control_binning" % variable)
        else:
            variable_set.add(variable)
    # variable_set = set(control_binning[channel].keys()) & set(args.control_plot_set)
    logger.info("[INFO] Running control plots for variables: {}".format(variable_set))

    # data
    # - channel selection
    add_control_process(
        control_units,
        name="data",
        dataset=datasets["data"],
        selections=channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # Z -> tau tau simulation
    # - channel selection
    # - MC weights for DY samples
    # - generator-level Z -> tau tau selection
    add_control_process(
        control_units,
        name="ztt",
        dataset=datasets["DY"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            DY_process_selection(channel, era, boosted_tau),
            ZTT_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # Z -> ell ell simulation
    # - channel selection
    # - MC weights for DY samples
    # - generator-level Z -> ell ell selection (where ell is an electron or a muon)
    add_control_process(
        control_units,
        name="zl",
        dataset=datasets["DY"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            DY_process_selection(channel, era, boosted_tau),
            ZL_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # ttbar with genuine tau pairs
    # - channel selection
    # - MC weights for TT samples
    # - generator-level ttbar selection for events with genuine di-tau pairs
    add_control_process(
        control_units,
        name="ttt",
        dataset=datasets["TT"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            TT_process_selection(channel, era, boosted_tau),
            TTT_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # ttbar with l -> tau_h fakes
    # - channel selection
    # - MC weights for TT samples
    # - generator-level ttbar selection for l -> tau_h fakes
    add_control_process(
        control_units,
        name="ttl",
        dataset=datasets["TT"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            TT_process_selection(channel, era, boosted_tau),
            TTL_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # ttbar with jet -> tau_h fakes
    # - channel selection
    # - MC weights for TT samples
    # - generator-level ttbar selection for jet -> tau_h fakes
    add_control_process(
        control_units,
        name="ttj",
        dataset=datasets["TT"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            TT_process_selection(channel, era, boosted_tau),
            TTJ_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # W+Jets
    # - channel selection
    # - MC weights for W samples
    add_control_process(
        control_units,
        name="w",
        dataset=datasets["W"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            W_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # single-top with genuine tau pairs
    # - channel selection
    # - MC weights for ST samples
    # - generator-level single-top selection for events with genuine tau pairs
    add_control_process(
        control_units,
        name="stt",
        dataset=datasets["ST"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ST_process_selection(channel, era, boosted_tau),
            STT_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # single-top with l -> tau_h fakes
    # - channel selection
    # - MC weights for ST samples
    # - generator-level single-top selection for l -> tau_h fakes
    add_control_process(
        control_units,
        name="stl",
        dataset=datasets["ST"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ST_process_selection(channel, era, boosted_tau),
            STL_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # single-top with jet -> tau_h fakes
    # - channel selection
    # - MC weights for ST samples
    # - generator-level single-top selection for jet -> tau_h fakes
    add_control_process(
        control_units,
        name="stj",
        dataset=datasets["ST"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ST_process_selection(channel, era, boosted_tau),
            STJ_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # NMSSM Y -> bb, H -> tau tau
    # - channel selection
    # - MC weights for NMSSM_Ybb samples
    add_control_process(
        control_units,
        name="nmssm_Ybb",
        dataset=datasets["nmssm_Ybb"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            NMSSM_Ybb_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    # NMSSM Y -> tau tau, H -> bb
    # - channel selection
    # - MC weights for NMSSM_Ytautau samples
    add_control_process(
        control_units,
        name="nmssm_Ytautau",
        dataset=datasets["nmssm_Ytautau"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            NMSSM_Ytt_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )

    return control_units


def main(args):
    # Parse given arguments.
    friend_directories = {
        "et": args.et_friend_directory,
        "mt": args.mt_friend_directory,
        "tt": args.tt_friend_directory,
    }
    if ".root" in args.output_file:
        output_file = args.output_file
    else:
        output_file = "{}.root".format(args.output_file)
    # setup categories depending on the selected anayses
    special_analysis = args.special_analysis
    boosted_tau_analysis = args.boosted_tau_analysis
    boosted_b_analysis = args.boosted_b_analysis
    logger.info(f"boosted tau analysis: {boosted_tau_analysis}")
    logger.info(f"boosted b analysis: {boosted_b_analysis}")
    massX = args.massX
    massY = args.massY
    um = UnitManager()
    do_check = args.enable_booking_check
    era = args.era

    nominals = {}
    nominals[era] = {}
    nominals[era]["datasets"] = {}
    nominals[era]["units"] = {}

    # Step 1: create units and book actions
    for channel in args.channels:
        for sample in files[era][channel]:
            if "nmssm" in sample:
                files[era][channel][sample][0] = files[era][channel][sample][0].replace("MASSX", massX).replace("MASSY", massY)

        nominals[era]["datasets"][channel] = get_nominal_datasets(
            era, channel, friend_directories, files, args.directory,
            xrootd=args.xrootd, validation_tag=args.validation_tag
        )
        if args.control_plots:
            nominals[era]["units"][channel] = get_control_units(
                channel,
                era,
                nominals[era]["datasets"][channel],
                special_analysis,
                args.control_plot_set,
                boosted_tau=boosted_tau_analysis,
                boosted_b=boosted_b_analysis,
            )
        else:
            raise ValueError("no other options than control_plots implemented")

    if args.process_selection is None:
        procS = {
            "data",
            "ztt",
            "zl",
            "w",
            "ttt",
            "ttl",
            "ttj",
            "stt",
            "stl",
            "stj",
            "nmssm_Ybb",
            "nmssm_Ytautau",
        }
    else:
        procS = args.process_selection

    logger.info(f"Processes to be computed: {procS}")

    for channel in args.channels:
        book_histograms(
            um,
            processes=procS,
            datasets=nominals[era]["units"][channel],
            enable_check=do_check,
        )

    # Step 2: convert units to graphs and merge them
    g_manager = GraphManager(um.booked_units, True)
    g_manager.optimize(args.optimization_level)
    graphs = g_manager.graphs
    for graph in graphs:
        print("%s" % graph)

    if args.only_create_graphs:
        boosted_prefix = ""
        if boosted_tau_analysis:
            boosted_prefix = "boosted_"
        if args.control_plots or args.gof_inputs:
            # graph_file_name = "control_unit_graphs-{}-{}-{}.pkl".format(
            #     era, ",".join(args.channels), ",".join(sorted(procS))
            # )
            graph_file_name = "{}control_unit_graphs-{}-{}-{}-{}.pkl".format(
                boosted_prefix, era, ",".join(args.channels), args.massX, args.massY
            )
        else:
            graph_file_name = "{}analysis_unit_graphs-{}-{}-{}-{}.pkl".format(
                boosted_prefix, era, ",".join(args.channels), args.massX, args.massY
            )
        if args.graph_dir is not None:
            graph_file = os.path.join(args.graph_dir, graph_file_name)
        else:
            graph_file = graph_file_name
        logger.info("Writing created graphs to file %s.", graph_file)
        with open(graph_file, "wb") as f:
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
    setup_logging(log_file, logging.DEBUG)
    main(args)
