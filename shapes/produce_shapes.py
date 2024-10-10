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

# TODO adjust analysis units for boosted selection
def get_analysis_units(
    channel, era, datasets, categorization, special_analysis, boosted_tau=False, boosted_b=False, nn_shapes=False
):
    analysis_units = {}

    add_process(
        analysis_units,
        name="data",
        dataset=datasets["data"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            # Data_base_process_selection(era, channel),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="zl_nlo",
        dataset=datasets["DYNLO"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            DY_NLO_process_selection(channel, era, boosted_tau),
            ZL_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="ttl",
        dataset=datasets["TT"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            TT_process_selection(channel, era, boosted_tau),
            TTL_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="vvl",
        dataset=datasets["VV"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VV_process_selection(channel, era, boosted_tau),
            VVL_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    # if channel != "mm":
    # Embedding
    add_process(
        analysis_units,
        name="emb",
        dataset=datasets["EMB"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ZTT_embedded_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )

    add_process(
        analysis_units,
        name="ztt_nlo",
        dataset=datasets["DYNLO"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            DY_NLO_process_selection(channel, era, boosted_tau),
            ZTT_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="vvt",
        dataset=datasets["VV"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VV_process_selection(channel, era, boosted_tau),
            VVT_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="ttt",
        dataset=datasets["TT"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            TT_process_selection(channel, era, boosted_tau),
            TTT_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="zj_nlo",
        dataset=datasets["DYNLO"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            DY_NLO_process_selection(channel, era, boosted_tau),
            ZJ_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="vvj",
        dataset=datasets["VV"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VV_process_selection(channel, era, boosted_tau),
            VVJ_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="ttj",
        dataset=datasets["TT"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            TT_process_selection(channel, era, boosted_tau),
            TTJ_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="ggh_tt",
        dataset=datasets["ggH_tt"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ggH125_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="qqh_tt",
        dataset=datasets["qqH_tt"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            qqH125_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="ggh_bb",
        dataset=datasets["ggH_bb"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ggH125_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="qqh_bb",
        dataset=datasets["qqH_bb"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            qqH125_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    # add_process(
    #     analysis_units,
    #     name="wh",
    #     dataset=datasets["WH"],
    #     selections=[
    #         channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
    #         WH_process_selection(channel, era),
    #     ],
    #     categorization=categorization,
    #     channel=channel,
    # )
    # add_process(
    #     analysis_units,
    #     name="zh",
    #     dataset=datasets["ZH"],
    #     selections=[
    #         channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
    #         ZH_process_selection(channel, era),
    #     ],
    #     categorization=categorization,
    #     channel=channel,
    # )
    # add_process(
    #     analysis_units,
    #     name="tth",
    #     dataset=datasets["ttH"],
    #     selections=[
    #         channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
    #         ttH_process_selection(channel, era),
    #     ],
    #     categorization=categorization,
    #     channel=channel,
    # )
    # "gghww"  : [Unit(
    #             datasets["ggHWW"], [
    #                 channel_selection(channel, era, special_analysis),
    #                 ggHWW_process_selection(channel, era),
    #                 category_selection], actions) for category_selection, actions in categorization[channel]],
    # "qqhww"  : [Unit(
    #             datasets["qqHWW"], [
    #                 channel_selection(channel, era, special_analysis),
    #                 qqHWW_process_selection(channel, era),
    #                 category_selection], actions) for category_selection, actions in categorization[channel]],
    # "zhww"  : [Unit(
    #             datasets["ZHWW"], [
    #                 channel_selection(channel, era, special_analysis),
    #                 ZHWW_process_selection(channel, era),
    #                 category_selection], actions) for category_selection, actions in categorization[channel]],
    # "whww"  : [Unit(
    #             datasets["WHWW"], [
    #                 channel_selection(channel, era, special_analysis),
    #                 WHWW_process_selection(channel, era),
    #                 category_selection], actions) for category_selection, actions in categorization[channel]],

    add_process(
        analysis_units,
        name="w",
        dataset=datasets["W"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            W_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="vh_tt",
        dataset=datasets["VH_tt"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VH_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="vh_bb",
        dataset=datasets["VH_bb"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VH_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="stt",
        dataset=datasets["ST"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ST_process_selection(channel, era, boosted_tau),
            STT_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="stl",
        dataset=datasets["ST"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ST_process_selection(channel, era, boosted_tau),
            STL_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="stj",
        dataset=datasets["ST"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ST_process_selection(channel, era, boosted_tau),
            STJ_process_selection(channel, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="nmssm_Ybb",
        dataset=datasets["nmssm_Ybb"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            NMSSM_Ybb_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    add_process(
        analysis_units,
        name="nmssm_Ytautau",
        dataset=datasets["nmssm_Ytautau"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            NMSSM_Ytt_process_selection(channel, era, boosted_tau),
        ],
        categorization=categorization,
        channel=channel,
    )
    return analysis_units


def get_control_units(
    channel, era, datasets, special_analysis, variables, boosted_tau=False, boosted_b=False, do_gofs=False, do_2dGofs=False
):
    control_units = {}
    control_binning = default_control_binning
    if do_gofs:
        # in this case we have to load the binning from the gof yaml file
        control_binning = load_gof_binning(era, channel, boosted_tau)
        
        # also build all aviailable 2D variables from the 1D variables
        if do_2dGofs:
            variables_2d = []
            for var1 in variables:
                for var2 in variables:
                    if var1 == var2:
                        continue
                    elif f"{var1}_{var2}" in control_binning[channel]:
                        variables_2d.append(f"{var1}_{var2}")
                    elif f"{var2}_{var1}" in control_binning[channel]:
                        variables_2d.append(f"{var2}_{var1}")
                    else:
                        raise ValueError(
                            "No binning found for 2D variable from {} and {}".format(
                                var1, var2
                            )
                        )
            variables.extend(variables_2d)
            logger.info(
                "Will run GoFs for {} variables, indluding {} 2D variables".format(
                    len(variables) - len(variables_2d), len(variables_2d)
                )
            )
        logger.debug("Variables: {}".format(variables))
    # check that all variables are available
    variable_set = set()
    for variable in set(variables):
        if variable not in control_binning[channel]:
            raise Exception("Variable %s not available in control_binning" % variable)
        else:
            variable_set.add(variable)
    # variable_set = set(control_binning[channel].keys()) & set(args.control_plot_set)
    logger.info("[INFO] Running control plots for variables: {}".format(variable_set))
    add_control_process(
        control_units,
        name="data",
        dataset=datasets["data"],
        selections=channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="emb",
        dataset=datasets["EMB"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ZTT_embedded_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    # add_control_process(
    #     control_units,
    #     name="ztt",
    #     dataset=datasets["DY"],
    #     selections=[
    #         channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
    #         DY_process_selection(channel, era, boosted_tau),
    #         ZTT_process_selection(channel, boosted_tau),
    #     ],
    #     channel=channel,
    #     binning=control_binning,
    #     variables=variable_set,
    # )
    # add_control_process(
    #     control_units,
    #     name="zl",
    #     dataset=datasets["DY"],
    #     selections=[
    #         channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
    #         DY_process_selection(channel, era, boosted_tau),
    #         ZL_process_selection(channel, boosted_tau),
    #     ],
    #     channel=channel,
    #     binning=control_binning,
    #     variables=variable_set,
    # )
    # add_control_process(
    #     control_units,
    #     name="zj",
    #     dataset=datasets["DY"],
    #     selections=[
    #         channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
    #         DY_process_selection(channel, era, boosted_tau),
    #         ZJ_process_selection(channel, boosted_tau),
    #     ],
    #     channel=channel,
    #     binning=control_binning,
    #     variables=variable_set,
    # )
    add_control_process(
        control_units,
        name="ztt_nlo",
        dataset=datasets["DYNLO"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            DY_NLO_process_selection(channel, era, boosted_tau),
            ZTT_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="zl_nlo",
        dataset=datasets["DYNLO"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            DY_NLO_process_selection(channel, era, boosted_tau),
            ZL_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="zj_nlo",
        dataset=datasets["DYNLO"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            DY_NLO_process_selection(channel, era, boosted_tau),
            ZJ_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    # add_control_process(
    #     control_units,
    #     name="ewk",
    #     dataset=datasets["EWK"],
    #     selections=[
    #         channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
    #         EWK_process_selection(channel, era, boosted_tau),
    #     ],
    #     channel=channel,
    #     binning=control_binning,
    #     variables=variable_set,
    # )
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
    add_control_process(
        control_units,
        name="vvl",
        dataset=datasets["VV"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VV_process_selection(channel, era, boosted_tau),
            VVL_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="vvt",
        dataset=datasets["VV"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VV_process_selection(channel, era, boosted_tau),
            VVT_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="vvj",
        dataset=datasets["VV"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VV_process_selection(channel, era, boosted_tau),
            VVJ_process_selection(channel, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="qqh_tt",
        dataset=datasets["qqH_tt"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            qqH125_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="ggh_tt",
        dataset=datasets["ggH_tt"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ggH125_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="vh_tt",
        dataset=datasets["VH_tt"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VH_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="qqh_bb",
        dataset=datasets["qqH_bb"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            qqH125_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="ggh_bb",
        dataset=datasets["ggH_bb"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            ggH125_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    add_control_process(
        control_units,
        name="vh_bb",
        dataset=datasets["VH_bb"],
        selections=[
            channel_selection(channel, era, special_analysis, boosted_tau, boosted_b),
            VH_process_selection(channel, era, boosted_tau),
        ],
        channel=channel,
        binning=control_binning,
        variables=variable_set,
    )
    # add_control_process(
    #     control_units,
    #     name="w_nlo",
    #     dataset=datasets["WNLO"],
    #     selections=[
    #         channel_selection(channel, era, special_analysis),
    #         W_process_selection(channel, era),
    #     ],
    #     channel=channel,
    #     binning=control_binning,
    #     variables=variable_set,
    # )

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


def prepare_special_analysis(special, massX, massY, boosted_tau=False):
    if special is None:
        return cat_sel.get_categorization(massX, massY, boosted_tt=boosted_tau)
    elif special and special == "TauID":
        return tauid_categorization
    elif special and special == "TauES":
        return taues_categorization
    else:
        raise ValueError("Unknown special analysis: {}".format(special))


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
    categorization = prepare_special_analysis(special_analysis, massX, massY, boosted_tau_analysis)
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
                do_gofs=False,
            )
        elif args.gof_inputs:
            nominals[era]["units"][channel] = get_control_units(
                channel,
                era,
                nominals[era]["datasets"][channel],
                special_analysis,
                args.control_plot_set,
                do_gofs=True,
                do_2dGofs=args.do_2dGofs,
                boosted_tau=boosted_tau_analysis,
                boosted_b=boosted_b_analysis,
            )
        else:
            nominals[era]["units"][channel] = get_analysis_units(
                channel,
                era,
                nominals[era]["datasets"][channel],
                categorization,
                special_analysis,
                boosted_tau=boosted_tau_analysis, 
                boosted_b=boosted_b_analysis,
            )
        if special_analysis == "TauES":
            additional_emb_procS = set()
            tauESvariations = [-1.2 + 0.05 * i for i in range(0, 47)]
            add_tauES_datasets(
                era,
                channel,
                friend_directories,
                files,
                args.directory,
                nominals,
                tauESvariations,
                [
                    channel_selection(channel, era, special_analysis),
                    ZTT_embedded_process_selection(channel, era),
                ],
                categorization,
                additional_emb_procS,
                xrootd=args.xrootd,
                validation_tag=args.validation_tag,
            )

    if args.process_selection is None:
        procS = {
            "data",
            "emb",
            # "ztt",
            # "zl",
            # "zj",
            "ztt_nlo",
            "zl_nlo",
            "zj_nlo",
            "ttt",
            "ttl",
            "ttj",
            "vvt",
            "vvl",
            "vvj",
            "stt",
            "stl",
            "stj",
            "w",
            # "w_nlo",
            # "ewk",
            "ggh_tt",
            "qqh_tt",
            "vh_tt",
            "ggh_bb",
            "qqh_bb",
            "vh_bb",
            "nmssm_Ybb",
            "nmssm_Ytautau",
        }
    else:
        procS = args.process_selection

    logger.info(f"Processes to be computed: {procS}")
    dataS = {"data"} & procS
    embS = {"emb"} & procS
    jetFakesDS = {
        "et": {"zj_nlo", "ttj", "vvj", "w", "stj"} & procS,
        "mt": {"zj_nlo", "ttj", "vvj", "w", "stj"} & procS,
        "tt": {"zj_nlo", "ttj", "vvj", "w", "stj"} & procS,
    }
    leptonFakesS = {"zl_nlo", "ttl", "vvl", "stl"} & procS
    trueTauBkgS = {"ztt_nlo", "ttt", "vvt", "stt"} & procS
    smHiggsBkgS = {"ggh_tt", "qqh_tt", "tth_tt", "vh_tt", "ggh_bb", "qqh_bb", "tth_bb", "vh_bb"} & procS
    signalsS = {
        "nmssm_Ybb", 
        "nmssm_Ytautau",
    } & procS

    if args.control_plots or args.gof_inputs and not args.control_plots_full_samples:
        signalsS = signalsS & {"nmssm_Ybb", "nmssm_Ytautau"}

    simulatedProcsDS = {
        chname_: jetFakesDS[chname_] | leptonFakesS | trueTauBkgS | signalsS | smHiggsBkgS
        for chname_ in ["et", "mt", "tt"]
    }
    logger.info(f"Processes to be computed: {procS}")
    logger.info(f"Simulated processes: {simulatedProcsDS}")
    logger.info(f"SM Higgs processes: {smHiggsBkgS}")
    logger.info(f"Data processes: {dataS}")
    logger.info(f"Embedded processes: {embS}")
    logger.info(f"Jet fakes processes: {jetFakesDS}")
    logger.info(f"Lepton fakes processes: {leptonFakesS}")
    logger.info(f"True tau bkg processes: {trueTauBkgS}")
    logger.info(f"signals: {signalsS}")
    for channel in args.channels:
        book_histograms(
            um,
            processes=signalsS,
            datasets=nominals[era]["units"][channel],
            enable_check=do_check,
        )
        if channel == "mt" and special_analysis == "TauES":
            logger.info("Booking TauES")
            book_tauES_histograms(
                um,
                additional_emb_procS,
                nominals[era]["units"][channel],
                [same_sign, anti_iso_lt] if not boosted_tau_analysis else [boosted_same_sign, boosted_anti_iso_lt],
                do_check,
            )
        elif channel in ["mt", "et"]:
            book_histograms(
                um,
                processes=embS,
                datasets=nominals[era]["units"][channel],
                variations=[same_sign, anti_iso_lt] if not boosted_tau_analysis else [boosted_same_sign, boosted_anti_iso_lt],
                enable_check=do_check,
            )
        if channel in ["mt", "et"]:
            book_histograms(
                um,
                processes=dataS | trueTauBkgS | leptonFakesS | smHiggsBkgS,
                datasets=nominals[era]["units"][channel],
                variations=[same_sign, anti_iso_lt] if not boosted_tau_analysis else [boosted_same_sign, boosted_anti_iso_lt],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=jetFakesDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[same_sign] if not boosted_tau_analysis else [boosted_same_sign],
                enable_check=do_check,
            )
        elif channel == "tt":
            # TODO add abcd method
            book_histograms(
                um,
                processes=dataS | leptonFakesS| trueTauBkgS | smHiggsBkgS,
                datasets=nominals[era]["units"][channel],
                variations=[same_sign, anti_iso_tt] if not boosted_tau_analysis else [boosted_same_sign, boosted_anti_iso_tt],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=jetFakesDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[same_sign] if not boosted_tau_analysis else [boosted_same_sign],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=embS,
                datasets=nominals[era]["units"][channel],
                variations=[same_sign, anti_iso_tt] if not boosted_tau_analysis else [boosted_same_sign, boosted_anti_iso_tt],
                enable_check=do_check,
            )

        ##################################
        # SYSTEMATICS
        ############################
        if args.skip_systematic_variations:
            pass
        elif not args.skip_systematic_variations and not boosted_tau_analysis:
            # Book variations common to all channels.
            # um.book([unit for d in {"ggh"} & procS for unit in nominals[era]['units'][channel][d]], [*ggh_acceptance], enable_check=args.enable_booking_check)
            # um.book([unit for d in {"qqh"} & procS for unit in nominals[era]['units'][channel][d]], [*qqh_acceptance], enable_check=args.enable_booking_check)
            # TODO add signal uncertainties
            # book_histograms(
            #     um,
            #     processes={"ggh"} & procS,
            #     datasets=nominals[era]["units"][channel],
            #     variations=[ggh_acceptance],
            #     enable_check=do_check,
            # )
            # book_histograms(
            #     um,
            #     processes={"qqh"} & procS,
            #     datasets=nominals[era]["units"][channel],
            #     variations=[qqh_acceptance],
            #     enable_check=do_check,
            # )
            book_histograms(
                um,
                processes=signalsS,
                datasets=nominals[era]["units"][channel],
                variations=[LHE_scale_norm],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=simulatedProcsDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[jet_es],
                enable_check=do_check,
            )
            if "2018" in era:
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[jet_es_hem],
                    enable_check=do_check,
                )
            book_histograms(
                um,
                processes=simulatedProcsDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[btagging, particleNet_Xbb],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes={"ztt", "zj", "zl", "ztt_nlo", "zj_nlo", "zl_nlo", "w"} & procS | smHiggsBkgS | signalsS,
                datasets=nominals[era]["units"][channel],
                variations=[recoil_resolution, recoil_response],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes={"ttt", "ttl", "ttj", "vvt", "vvl", "vvj", "stt", "stl", "stj"} & procS,
                datasets=nominals[era]["units"][channel],
                variations=[met_unclustered],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=simulatedProcsDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[pileup_reweighting],
                enable_check=do_check,
            )

            book_histograms(
                um,
                processes={"ztt", "zl", "zj"} & procS,
                datasets=nominals[era]["units"][channel],
                variations=[zpt],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes={"ttt", "ttl", "ttj"} & procS,
                datasets=nominals[era]["units"][channel],
                variations=[top_pt],
                enable_check=do_check,
            )
            # Book variations common to multiple channels.
            if channel in ["et", "mt", "tt"]:
                book_histograms(
                    um,
                    processes=(trueTauBkgS | leptonFakesS | smHiggsBkgS | signalsS) - {"zl", "zl_nlo"},
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        tau_es_3prong,
                        tau_es_3prong1pizero,
                        tau_es_1prong,
                        tau_es_1prong1pizero,
                    ],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes=jetFakesDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        jet_to_tau_fake,
                    ],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes=embS,
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        emb_tau_es_3prong,
                        emb_tau_es_3prong1pizero,
                        emb_tau_es_1prong,
                        emb_tau_es_1prong1pizero,
                        tau_es_3prong,
                        tau_es_3prong1pizero,
                        tau_es_1prong,
                        tau_es_1prong1pizero,
                    ],
                    enable_check=do_check,
                )
            if channel in ["et", "mt"]:
                book_histograms(
                    um,
                    processes=(trueTauBkgS | leptonFakesS | smHiggsBkgS | signalsS) - {"zl", "zl_nlo"},
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        tau_id_eff_lt,
                    ],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes=dataS | embS | leptonFakesS | trueTauBkgS,
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        ff_variations_lt,
                    ],
                    enable_check=do_check,
                )

                # book_histograms(
                #     um,
                #     processes=leptonFakesS | trueTauBkgS | embS,
                #     datasets=nominals[era]["units"][channel],
                #     variations=[
                #         ff_variations_tau_es_lt,
                #     ],
                #     enable_check=do_check,
                # )
                # book_histograms(
                #     um,
                #     processes=embS,
                #     datasets=nominals[era]["units"][channel],
                #     variations=[
                #         ff_variations_tau_es_emb_lt,
                #     ],
                #     enable_check=do_check,
                # )
                book_histograms(
                    um,
                    processes=embS,
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        emb_tau_id_eff_lt,
                        emb_tau_id_eff_lt_corr,
                    ],
                    enable_check=do_check,
                )
            # Book channel independent variables.
            if channel == "mt":
                book_histograms(
                    um,
                    processes={"zl", "zl_nlo"} & procS,
                    datasets=nominals[era]["units"][channel],
                    variations=[mu_fake_es_inc],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[trigger_eff_mt],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes=embS,
                    datasets=nominals[era]["units"][channel],
                    variations=[trigger_eff_mt_emb],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes={"zl", "zl_nlo"} & procS,
                    datasets=nominals[era]["units"][channel],
                    variations=[zll_mt_fake_rate],
                    enable_check=do_check,
                )
            if channel == "et":
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        ele_res,
                        ele_es
                    ],
                    enable_check=do_check,
                )
                # TODO add emb ele ES
                book_histograms(
                    um,
                    processes=embS,
                    datasets=nominals[era]["units"][channel],
                    variations=[emb_e_es],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes={"zl", "zl_nlo"} & procS,
                    datasets=nominals[era]["units"][channel],
                    variations=[ele_fake_es],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[trigger_eff_et],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes=embS,
                    datasets=nominals[era]["units"][channel],
                    variations=[trigger_eff_et_emb],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes={"zl", "zl_nlo"} & procS,
                    datasets=nominals[era]["units"][channel],
                    variations=[zll_et_fake_rate],
                    enable_check=do_check,
                )
            if channel == "tt":
                book_histograms(
                    um,
                    processes=trueTauBkgS | leptonFakesS | smHiggsBkgS | signalsS,
                    datasets=nominals[era]["units"][channel],
                    variations=[tau_id_eff_tt],
                    enable_check=do_check,
                )
                # Todo add trigger efficiency
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[trigger_eff_tt],
                    enable_check=do_check,
                )
                # TODO add trigger efficiency for emb
                book_histograms(
                    um,
                    processes=embS,
                    datasets=nominals[era]["units"][channel],
                    variations=[emb_tau_id_eff_tt, tau_id_eff_tt, trigger_eff_tt_emb, trigger_eff_tt],
                    enable_check=do_check,
                )
                # TODO add fake factor variations
                book_histograms(
                    um,
                    processes=dataS | embS | leptonFakesS | trueTauBkgS,
                    datasets=nominals[era]["units"][channel],
                    variations=[ff_variations_tt],
                    enable_check=do_check,
                )
                # TODO add fake factor variations for lepton fakes
                # book_histograms(
                #     um,
                #     processes=leptonFakesS,
                #     datasets=nominals[era]["units"][channel],
                #     variations=[ff_variations_tt_mcl],
                #     enable_check=do_check,
                # )
            # Book era dependent uncertainty shapes
            if "2016" in era or "2017" in era:
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[prefiring],
                    enable_check=do_check,
                )
                
        elif not args.skip_systematic_variations and boosted_tau_analysis:
            # Book variations common to all channels in boosted tau analysis.
            book_histograms(
                um,
                processes=signalsS,
                datasets=nominals[era]["units"][channel],
                variations=[LHE_scale_norm],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=simulatedProcsDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[jet_es],
                enable_check=do_check,
            )
            if "2018" in era:
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[jet_es_hem],
                    enable_check=do_check,
                )
            book_histograms(
                um,
                processes=simulatedProcsDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[btagging, particleNet_Xbb],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes={"ztt", "zj", "zl", "ztt_nlo", "zj_nlo", "zl_nlo", "w"} & procS | smHiggsBkgS | signalsS,
                datasets=nominals[era]["units"][channel],
                variations=[recoil_resolution, recoil_response],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes={"ttt", "ttl", "ttj", "vvt", "vvl", "vvj", "stt", "stl", "stj"} & procS,
                datasets=nominals[era]["units"][channel],
                variations=[met_unclustered],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=simulatedProcsDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[pileup_reweighting],
                enable_check=do_check,
            )

            book_histograms(
                um,
                processes={"ztt", "zl", "zj"} & procS,
                datasets=nominals[era]["units"][channel],
                variations=[zpt],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes={"ttt", "ttl", "ttj"} & procS,
                datasets=nominals[era]["units"][channel],
                variations=[top_pt],
                enable_check=do_check,
            )
            # Book variations common to multiple channels.
            if channel in ["et", "mt", "tt"]:
                book_histograms(
                    um,
                    processes=(trueTauBkgS | leptonFakesS | smHiggsBkgS | signalsS) - {"zl", "zl_nlo"},
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        boosted_tau_es_3prong,
                        boosted_tau_es_1prong,
                        boosted_tau_es_1prong1pizero,
                    ],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes=jetFakesDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        jet_to_tau_fake_boosted,
                    ],
                    enable_check=do_check,
                )
            if channel in ["et", "mt"]:
                book_histograms(
                    um,
                    processes=(trueTauBkgS | leptonFakesS | smHiggsBkgS | signalsS) - {"zl", "zl_nlo"},
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        boosted_tau_id_eff_lt,
                    ],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes=dataS | embS | leptonFakesS | trueTauBkgS,
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        ff_variations_boosted_lt,
                    ],
                    enable_check=do_check,
                )
            # Book channel independent variables.
            if channel == "mt":
                # book_histograms(
                #     um,
                #     processes={"zl", "zl_nlo"} & procS,
                #     datasets=nominals[era]["units"][channel],
                #     variations=[mu_fake_es_inc],
                #     enable_check=do_check,
                # )
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[trigger_eff_boosted_mt],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes={"zl", "zl_nlo"} & procS,
                    datasets=nominals[era]["units"][channel],
                    variations=[boosted_zll_mt_fake_rate],
                    enable_check=do_check,
                )
            if channel == "et":
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        ele_res,
                        ele_es
                    ],
                    enable_check=do_check,
                )
                # book_histograms(
                #     um,
                #     processes={"zl", "zl_nlo"} & procS,
                #     datasets=nominals[era]["units"][channel],
                #     variations=[ele_fake_es],
                #     enable_check=do_check,
                # )
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[trigger_eff_boosted_et],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes={"zl", "zl_nlo"} & procS,
                    datasets=nominals[era]["units"][channel],
                    variations=[boosted_zll_et_fake_rate],
                    enable_check=do_check,
                )
            if channel == "tt":
                book_histograms(
                    um,
                    processes=trueTauBkgS | leptonFakesS | smHiggsBkgS | signalsS,
                    datasets=nominals[era]["units"][channel],
                    variations=[boosted_tau_id_eff_tt],
                    enable_check=do_check,
                )
                # Todo add trigger efficiency
                book_histograms(
                    um,
                    processes=simulatedProcsDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[trigger_eff_boosted_tt],
                    enable_check=do_check,
                )
                # TODO add fake factor variations
                book_histograms(
                    um,
                    processes=dataS | embS | leptonFakesS | trueTauBkgS,
                    datasets=nominals[era]["units"][channel],
                    variations=[ff_variations_boosted_tt],
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
    setup_logging(log_file, logging.INFO)
    main(args)
