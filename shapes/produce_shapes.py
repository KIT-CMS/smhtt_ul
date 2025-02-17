#!/usr/bin/env python
import argparse
import logging
import os
import pickle
import re
import yaml
from itertools import combinations
from functools import partial

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
import config.shapes.process_selection as selection

# from config.shapes.category_selection import categorization
from config.shapes.category_selection import categorization as default_categorization
from config.shapes.tauid_measurement_binning import (
    categorization as tauid_categorization,
)
from config.shapes.taues_measurement_binning import (
    categorization as taues_categorization,
)

# Variations for estimation of fake processes
from config.shapes.variations import (
    same_sign,
    same_sign_em,
    anti_iso_lt,
    anti_iso_lt_no_ff,
    anti_iso_tt,
    anti_iso_tt_mcl,
    abcd_method,
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
    # TODO add missing ES
    # mu_fake_es_1prong,
    # mu_fake_es_1prong1pizero,
    # ele_es,
    # ele_res,
    emb_e_es,
    # ele_fake_es_1prong,
    # ele_fake_es_1prong1pizero,
    # ele_fake_es,
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
    tau_id_eff_tt,
    emb_tau_id_eff_lt,
    emb_tau_id_eff_tt,
    emb_tau_id_eff_lt_corr,
)

# fake rate uncertainties
from config.shapes.variations import jet_to_tau_fake, zll_et_fake_rate, zll_mt_fake_rate

# TODO add trigger efficiency uncertainties
# # trigger efficiencies
from config.shapes.variations import (
    # tau_trigger_eff_tt,
    # tau_trigger_eff_tt_emb,
    trigger_eff_mt,
    trigger_eff_et,
    trigger_eff_et_emb,
    trigger_eff_mt_emb,
)

# Additional uncertainties
from config.shapes.variations import (
    prefiring,
    zpt,
    top_pt,
    pileup_reweighting,
)

# TODO add missing uncertainties
# Additional uncertainties
# from config.shapes.variations import (
#     btag_eff,
#     mistag_eff,
#     emb_decay_mode_eff_lt,
#     emb_decay_mode_eff_tt,
# )
from config.shapes.signal_variations import (
    ggh_acceptance,
    qqh_acceptance,
)

# jet fake uncertainties
from config.shapes.variations import (
    wfakes_tt,
    wfakes_w_tt,
)

# TODO add jetfake uncertainties
# # jet fake uncertainties
from config.shapes.variations import (
    ff_variations_lt,
    # ff_variations_tt,
    # ff_variations_tt_mcl,
    # qcd_variations_em,
    wfakes_tt,
    wfakes_w_tt,
    ff_variations_tau_es_lt,
    ff_variations_tau_es_emb_lt,
    # ff_variations_tau_es_tt,
    # ff_variations_tau_es_tt_mcl,
)

from config.shapes.control_binning import control_binning as default_control_binning
from config.shapes.gof_binning import load_gof_binning
from config.logging_setup_configs import setup_logging


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for the legacy MSSM analysis."
    )
    parser.add_argument("--era", required=True, type=str, help="Experiment era.")
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist: [channel for channel in channellist.split(",")],
        help="Channels to be considered, seperated by a comma without space",
    )
    parser.add_argument(
        "--vs-jet-wp", required=True, type=str, help="Tau ID WP."
    )
    parser.add_argument(
        "--vs-ele-wp", required=True, type=str, help="Vs Mu Fake rate WP."
    )
    parser.add_argument(
        "--apply-tauid", action="store_true", help="Flag that specifies if we apply tau id scale factors or not"
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
    parser.add_argument(
        "--es",
        action="store_true",
        help="Add tau ES variations.",
    )
    parser.add_argument(
        "--ff-DR",
        help="Set to the DR used for the fake factor estimation.",
        choices=["wjet", "qcd", "ttbar"],
        default=None,
    )
    return parser.parse_args()


def add_processes(
    add_fn: callable,
    datasets: dict,
    select_fn: callable,
    channel: str,
) -> None:

    add_fn(name="data", dataset=datasets["data"], selections=select_fn())
    add_fn(name="emb", dataset=datasets["EMB"], selections=select_fn(selection.ZTT_embedded))
    add_fn(name="ztt", dataset=datasets["DY"], selections=select_fn(selection.DY, selection.ZTT))
    add_fn(name="zl", dataset=datasets["DY"], selections=select_fn(selection.DY, selection.ZL))
    add_fn(name="zj", dataset=datasets["DY"], selections=select_fn(selection.DY, selection.ZJ))
    add_fn(name="ztt_nlo", dataset=datasets["DYNLO"], selections=select_fn(selection.DY_NLO, selection.ZTT))
    add_fn(name="zl_nlo", dataset=datasets["DYNLO"], selections=select_fn(selection.DY_NLO, selection.ZL))
    add_fn(name="zj_nlo", dataset=datasets["DYNLO"], selections=select_fn(selection.DY_NLO, selection.ZJ))
    add_fn(name="ttl", dataset=datasets["TT"], selections=select_fn(selection.TT, selection.TTL))
    add_fn(name="ttt", dataset=datasets["TT"], selections=select_fn(selection.TT, selection.TTT))
    add_fn(name="ttj", dataset=datasets["TT"], selections=select_fn(selection.TT, selection.TTJ))
    add_fn(name="vvl", dataset=datasets["VV"], selections=select_fn(selection.VV, selection.VVL))
    add_fn(name="vvt", dataset=datasets["VV"], selections=select_fn(selection.VV, selection.VVT))
    add_fn(name="vvj", dataset=datasets["VV"], selections=select_fn(selection.VV, selection.VVJ))
    if channel != "mm":
        add_fn(name="qqh", dataset=datasets["qqH"], selections=select_fn(selection.qqH125))
        add_fn(name="ggh", dataset=datasets["ggH"], selections=select_fn(selection.ggH125))
        # add_fn(name="w_nlo", dataset=datasets["WNLO"], selections=select_fn(selection.W))
    add_fn(name="w", dataset=datasets["W"], selections=select_fn(selection.W))


def get_analysis_units(
    channel,
    era,
    datasets,
    categorization,
    special_analysis,
    apply_tauid,
    vs_jet_wp,
    vs_ele_wp,
    nn_shapes=False,
    ff_DR=None,
):

    _selection_kwargs = dict(
        channel=channel,
        era=era,
        special=special_analysis,
        vs_jet_wp=vs_jet_wp,
        vs_ele_wp=vs_ele_wp,
        ff_DR=ff_DR,
        apply_wps=apply_tauid,  # for ZTT_embedded
    )
    _selection_memo = {}
    _channel_selection = channel_selection(**_selection_kwargs)

    def select(*args):
        _selection = [_channel_selection]
        for _process in args:
            if _process.__name__ not in _selection_memo:
                _selection_memo[_process.__name__] = _process(**_selection_kwargs)
            _selection.append(_selection_memo[_process.__name__])
        return _selection

    analysis_units = {}

    add_processes(
        add_fn=partial(
            add_process,
            analysis_unit=analysis_units,
            categorization=categorization,
            channel=channel,
        ),
        datasets=datasets,
        select_fn=select,
        channel=channel,
    )

    return analysis_units


def get_control_units(
    channel,
    era,
    datasets,
    special_analysis,
    variables,
    apply_tauid,
    vs_jet_wp,
    vs_ele_wp,
    do_gofs=False,
    do_2dGofs=False,
    ff_DR=None,
):
    control_units = {}
    control_binning = default_control_binning
    if do_gofs:
        # in this case we have to load the binning from the gof yaml file
        control_binning = load_gof_binning(era, channel)
        # also build all aviailable 2D variables from the 1D variables
        if do_2dGofs:
            variables_2d = []
            for var1, var2 in combinations(variables, 2):
                if f"{var1}_{var2}" in control_binning[channel]:
                    variables_2d.append(f"{var1}_{var2}")
                elif f"{var2}_{var1}" in control_binning[channel]:
                    variables_2d.append(f"{var2}_{var1}")
                else:
                    raise ValueError(
                        f"No binning found for 2D variable from {var1} and {var2}"
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

    _selection_kwargs = dict(
        channel=channel,
        era=era,
        special=special_analysis,
        vs_jet_wp=vs_jet_wp,
        vs_ele_wp=vs_ele_wp,
        ff_DR=ff_DR,
        apply_wps=apply_tauid,  # for ZTT_embedded
    )
    _selection_memo = {}
    _channel_selection = channel_selection(**_selection_kwargs)

    def select(*args):
        _selection = [_channel_selection]
        for _process in args:
            if _process.__name__ not in _selection_memo:
                _selection_memo[_process.__name__] = _process(**_selection_kwargs)
            _selection.append(_selection_memo[_process.__name__])
        return _selection

    add_processes(
        add_fn=partial(
            add_control_process,
            analysis_unit=control_units,
            channel=channel,
            binning=control_binning,
            variables=variable_set,
        ),
        datasets=datasets,
        select_fn=select,
        channel=channel,
    )

    return control_units


def prepare_special_analysis(special):
    if special is None:
        return default_categorization
    elif special == "TauID":
        return tauid_categorization
    elif special == "TauES":
        return taues_categorization
    else:
        raise ValueError("Unknown special analysis: {}".format(special))


def main(args):
    # Parse given arguments.
    friend_directories = {
        "et": args.et_friend_directory,
        "mt": args.mt_friend_directory,
        "tt": args.tt_friend_directory,
        "em": args.em_friend_directory,
        "mm": args.mm_friend_directory,
        "ee": args.ee_friend_directory,
    }
    if ".root" in args.output_file:
        output_file = args.output_file
    else:
        output_file = "{}.root".format(args.output_file)
    # setup categories depending on the selected anayses
    special_analysis = args.special_analysis
    categorization = prepare_special_analysis(special_analysis)
    um = UnitManager()
    do_check = args.enable_booking_check
    era = args.era
    apply_tauid = args.apply_tauid
    print("#### Apply tau ID", apply_tauid)
    vs_jet_wp = args.vs_jet_wp
    vs_ele_wp = args.vs_ele_wp

    nominals = {}
    nominals[era] = {}
    nominals[era]["datasets"] = {}
    nominals[era]["units"] = {}

    # Step 1: create units and book actions
    for channel in args.channels:
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
                apply_tauid,
                vs_jet_wp,
                vs_ele_wp,
                do_gofs=False,
            )
        elif args.gof_inputs:
            nominals[era]["units"][channel] = get_control_units(
                channel,
                era,
                nominals[era]["datasets"][channel],
                special_analysis,
                args.control_plot_set,
                apply_tauid,
                vs_jet_wp,
                vs_ele_wp,
                do_gofs=True,
                do_2dGofs=args.do_2dGofs,
            )
        else:
            nominals[era]["units"][channel] = get_analysis_units(
                channel,
                era,
                nominals[era]["datasets"][channel],
                categorization,
                special_analysis,
                apply_tauid,
                vs_jet_wp,
                vs_ele_wp,
            )
        if special_analysis == "TauES":
            additional_emb_procS = set()
            tauESvariations = [-2.5 + 0.1 * i for i in range(0, 51)]
            add_tauES_datasets(
                era,
                channel,
                friend_directories,
                files,
                args.directory,
                nominals,
                tauESvariations,
                [
                    channel_selection(channel, era, special_analysis,  vs_jet_wp, vs_ele_wp),
                    selection.ZTT_embedded(channel, era, apply_tauid, vs_jet_wp),
                ],
                categorization,
                additional_emb_procS,
                xrootd=args.xrootd,
                validation_tag=args.validation_tag,
            )
        if special_analysis == "TauID" and args.es:
            additional_emb_procS = set()
            tauESvariations = [-4.0 + 0.1 * i for i in range(0, 81)]
            add_tauES_datasets(
                era,
                channel,
                friend_directories,
                files,
                args.directory,
                nominals,
                tauESvariations,
                [
                    channel_selection(channel, era, special_analysis,  vs_jet_wp, vs_ele_wp),
                    selection.ZTT_embedded(channel, era, apply_tauid, vs_jet_wp),
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
            "ztt",
            "zl",
            "zj",
            "ztt_nlo",
            "zl_nlo",
            "zj_nlo",
            "ttt",
            "ttl",
            "ttj",
            "vvt",
            "vvl",
            "vvj",
            "w",
            # "w_nlo",
            "ggh",
            "qqh",
            # "zh",
            # "wh",
        }
        # if "et" in args.channels:
        #     procS = procS - {"w"}
        # procS = {"data", "emb", "ztt", "zl", "zj", "ttt", "ttl", "ttj", "vvt", "vvl", "vvj", "w",
        #          "ggh", "qqh", "tth", "zh", "wh", "gghww", "qqhww", "zhww", "whww"} \
        #         | set("ggh{}".format(mass) for mass in susy_masses[era]["ggH"]) \
        #         | set("bbh{}".format(mass) for mass in susy_masses[era]["bbH"])
    else:
        procS = args.process_selection
    if "mm" in args.channels or "ee" in args.channels:
        procS = {
            "data",
            "zl",
            "zl_nlo",
            "ttl",
            "vvl",
            "w",
            # "w_nlo",
            "emb",
        } & procS

    dataS = {"data"} & procS
    embS = {"emb"} & procS
    jetFakesDS = {
        "et": {"zj", "ttj", "vvj", "w", "zj_nlo", "w_nlo"} & procS,
        "mt": {"zj", "ttj", "vvj", "w", "zj_nlo", "w_nlo"} & procS,
        "tt": {"zj", "ttj", "vvj", "w", "zj_nlo", "w_nlo"} & procS,
        "em": {"w", "w_nlo"} & procS,
    }
    leptonFakesS = {"zl", "ttl", "vvl", "zl_nlo"} & procS
    trueTauBkgS = {"ztt", "ttt", "vvt", "ztt_nlo"} & procS
    sm_signalsS = {
        "ggh",
        "qqh",
        "tth",
        "zh",
        "wh",
        "gghww",
        "qqhww",
        "zhww",
        "whww",
    } & procS
    signalsS = sm_signalsS
    if args.control_plots or args.gof_inputs and not args.control_plots_full_samples:
        signalsS = signalsS & {"ggh", "qqh"}

    simulatedProcsDS = {
        chname_: jetFakesDS[chname_] | leptonFakesS | trueTauBkgS | signalsS
        for chname_ in ["et", "mt", "tt", "em"]
    }
    logger.info(f"Processes to be computed: {procS}")
    logger.info(f"Simulated processes: {simulatedProcsDS}")
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
                [same_sign, anti_iso_lt],
                do_check,
            )
        if channel == "mt" and args.es and special_analysis == "TauID":
            logger.info("Booking TauES")
            book_tauES_histograms(
                um,
                additional_emb_procS,
                nominals[era]["units"][channel],
                [same_sign, anti_iso_lt_no_ff],
                do_check,
            )
            # book_tauES_histograms(
            #     um,
            #     additional_emb_procS,
            #     nominals[era]["units"][channel],
            #     [trigger_eff_mt_emb],
            #     do_check,
            # )
            # book_histograms(
            #     um,
            #     additional_emb_procS,
            #     datasets=nominals[era]["units"][channel],
            #     variations=[trigger_eff_mt_emb],
            #     enable_check=do_check,
            # )
        elif channel in ["mt", "et"] and special_analysis != "TauID":
            book_histograms(
                um,
                processes=embS,
                datasets=nominals[era]["units"][channel],
                variations=[same_sign, anti_iso_lt],  # this
                enable_check=do_check,
            )
        if channel in ["mt", "et"]:
            book_histograms(
                um,
                processes=dataS | trueTauBkgS | leptonFakesS,
                datasets=nominals[era]["units"][channel],
                variations=[same_sign, anti_iso_lt],  # this
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=jetFakesDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[same_sign],
                enable_check=do_check,
            )
            # book_histograms(
            #     um,
            #     processes=embS,
            #     datasets=nominals[era]["units"][channel],
            #     variations=[same_sign],
            #     enable_check=do_check,
            # )  ' DUPLICATE
        elif channel == "tt":
            # TODO add anti_iso_tt
            book_histograms(
                um,
                processes=dataS | embS | trueTauBkgS,
                datasets=nominals[era]["units"][channel],
                variations=[abcd_method, same_sign, anti_iso_tt],
                enable_check=do_check,
            )

            book_histograms(
                um,
                processes=jetFakesDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[abcd_method, same_sign, anti_iso_tt],
                enable_check=do_check,
            )
            # TODO add anti_iso_tt_mcl
            book_histograms(
                um,
                processes=leptonFakesS,
                datasets=nominals[era]["units"][channel],
                variations=[wfakes_tt, abcd_method, same_sign, anti_iso_tt],
                enable_check=do_check,
            )

            book_histograms(
                um,
                processes={"w"} & procS,
                datasets=nominals[era]["units"][channel],
                variations=[wfakes_w_tt],
                enable_check=do_check,
            )

        elif channel == "em":
            book_histograms(
                um,
                processes=dataS | embS | simulatedProcsDS[channel] - signalsS,
                datasets=nominals[era]["units"][channel],
                variations=[same_sign_em],
                enable_check=do_check,
            )
        elif channel == "mm" and special_analysis == "TauES":
            book_histograms(
                um,
                processes={"data", "zl", "w", "ttl"},
                datasets=nominals[era]["units"][channel],
                variations=[],
                enable_check=do_check,
            )
        elif channel == "mm":
            book_histograms(
                um,
                processes=procS,
                datasets=nominals[era]["units"][channel],
                variations=[same_sign],
                enable_check=do_check,
            )
            # book_histograms(
            #     um,
            #     processes=embS,
            #     datasets=nominals[era]["units"][channel],
            #     variations=[trigger_eff_mt_emb],
            #     enable_check=do_check,
            # )
        elif channel == "ee":
            book_histograms(
                um,
                processes=procS,
                datasets=nominals[era]["units"][channel],
                variations=[same_sign],
                enable_check=do_check,
            )
        ##################################
        # SYSTEMATICS
        ############################
        if args.skip_systematic_variations:
            pass
        else:
            # Book variations common to all channels.
            # um.book([unit for d in {"ggh"} & procS for unit in nominals[era]['units'][channel][d]], [*ggh_acceptance], enable_check=args.enable_booking_check)
            # um.book([unit for d in {"qqh"} & procS for unit in nominals[era]['units'][channel][d]], [*qqh_acceptance], enable_check=args.enable_booking_check)
            # TODO add signal uncertainties
            book_histograms(
                um,
                processes={"ggh"} & procS,
                datasets=nominals[era]["units"][channel],
                variations=[ggh_acceptance],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes={"qqh"} & procS,
                datasets=nominals[era]["units"][channel],
                variations=[qqh_acceptance],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=simulatedProcsDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[jet_es],
                enable_check=do_check,
            )
            # TODO add btag stuff
            # book_histograms(
            #     um,
            #     processes=simulatedProcsDS[channel],
            #     datasets=nominals[era]["units"][channel],
            #     variations=[mistag_eff, btag_eff],
            #     enable_check=do_check,
            # )
            book_histograms(
                um,
                processes={"ztt", "zj", "zl", "w"} & procS | signalsS,
                datasets=nominals[era]["units"][channel],
                variations=[recoil_resolution, recoil_response],
                enable_check=do_check,
            )
            book_histograms(
                um,
                processes=simulatedProcsDS[channel],
                datasets=nominals[era]["units"][channel],
                variations=[met_unclustered, pileup_reweighting],
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
                if not args.es and special_analysis != "TauID":
                    book_histograms(
                        um,
                        processes=(trueTauBkgS | leptonFakesS | signalsS) - {"zl"},
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
                book_histograms(
                    um,
                    processes=jetFakesDS[channel],
                    datasets=nominals[era]["units"][channel],
                    variations=[
                        jet_to_tau_fake,
                    ],
                    enable_check=do_check,
                )
            if channel in ["et", "mt"]:
                if not args.es and special_analysis != "TauID":
                    book_histograms(
                        um,
                        processes=(trueTauBkgS | leptonFakesS | signalsS) - {"zl"},
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

                    book_histograms(
                        um,
                        processes=leptonFakesS | trueTauBkgS | embS,
                        datasets=nominals[era]["units"][channel],
                        variations=[
                            ff_variations_tau_es_lt,
                        ],
                        enable_check=do_check,
                    )
                    book_histograms(
                        um,
                        processes=embS,
                        datasets=nominals[era]["units"][channel],
                        variations=[
                            ff_variations_tau_es_emb_lt,
                        ],
                        enable_check=do_check,
                    )
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
            if channel in ["et", "em"]:
                # TODO add eleES
                # book_histograms(
                #     um,
                #     processes=simulatedProcsDS[channel],
                #     datasets=nominals[era]["units"][channel],
                #     variations=[
                #         ele_res,
                #         ele_es
                #     ],
                #     enable_check=do_check,
                # )
                # TODO add emb ele ES
                book_histograms(
                    um,
                    processes=embS,
                    datasets=nominals[era]["units"][channel],
                    variations=[emb_e_es],
                    enable_check=do_check,
                )
            # Book channel independent variables.
            if channel == "mt":
                book_histograms(
                    um,
                    processes={"zl"} & procS,
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
                # book_histograms(
                #     um,
                #     processes=embS,
                #     datasets=nominals[era]["units"][channel],
                #     variations=[trigger_eff_mt_emb],
                #     enable_check=do_check,
                # )
                book_histograms(
                    um,
                    processes=embS,
                    datasets=nominals[era]["units"][channel],
                    variations=[same_sign, anti_iso_lt_no_ff],
                    enable_check=do_check,
                )
                book_histograms(
                    um,
                    processes={"zl"} & procS,
                    datasets=nominals[era]["units"][channel],
                    variations=[zll_mt_fake_rate],
                    enable_check=do_check,
                )
            if channel == "et":
                book_histograms(
                    um,
                    processes={"zl"} & procS,
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
                    processes={"zl"} & procS,
                    datasets=nominals[era]["units"][channel],
                    variations=[zll_et_fake_rate],
                    enable_check=do_check,
                )
            if channel == "tt":
                book_histograms(
                    um,
                    processes=trueTauBkgS | leptonFakesS | signalsS,
                    datasets=nominals[era]["units"][channel],
                    variations=[tau_id_eff_tt],
                    enable_check=do_check,
                )
                # Todo add trigger efficiency
                # book_histograms(
                #     um,
                #     processes=simulatedProcsDS[channel],
                #     datasets=nominals[era]["units"][channel],
                #     variations=[tau_trigger_eff_tt],
                #     enable_check=do_check,
                # )
                # TODO add trigger efficiency for emb
                # book_histograms(
                #     um,
                #     processes=embS,
                #     datasets=nominals[era]["units"][channel],
                #     variations=[emb_tau_id_eff_tt, tau_id_eff_tt, tau_trigger_eff_tt_emb, tau_trigger_eff_tt, emb_decay_mode_eff_tt],
                #     enable_check=do_check,
                # )
                # TODO add fake factor variations
                # book_histograms(
                #     um,
                #     processes=dataS | embS | trueTauBkgS,
                #     datasets=nominals[era]["units"][channel],
                #     variations=[ff_variations_tt],
                #     enable_check=do_check,
                # )
                # TODO add fake factor variations for lepton fakes
                # book_histograms(
                #     um,
                #     processes=leptonFakesS,
                #     datasets=nominals[era]["units"][channel],
                #     variations=[ff_variations_tt_mcl],
                #     enable_check=do_check,
                # )
            # if channel == "em":
            # TODO add QCD variations ?
            # book_histograms(
            #     um,
            #     processes=dataS | embS | simulatedProcsDS[channel] - signalsS,
            #     datasets=nominals[era]["units"][channel],
            #     variations=[qcd_variations_em],
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

    # Step 2: convert units to graphs and merge them
    g_manager = GraphManager(um.booked_units, True)
    g_manager.optimize(args.optimization_level)
    graphs = g_manager.graphs
    for graph in graphs:
        print("%s" % graph)

    if args.only_create_graphs:
        if args.control_plots or args.gof_inputs:
            graph_file_name = "control_unit_graphs-{}-{}-{}.pkl".format(
                era, ",".join(args.channels), ",".join(sorted(procS))
            )
        else:
            graph_file_name = "analysis_unit_graphs-{}-{}-{}.pkl".format(
                era, ",".join(args.channels), ",".join(sorted(procS))
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
    logger = logging.getLogger(__name__)
    logger = setup_logging(log_file, logger, logging.DEBUG)
    main(args)
