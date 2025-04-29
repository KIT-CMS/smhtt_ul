#!/usr/bin/env python
import argparse
import logging
import os
import pickle
from functools import partial
from itertools import combinations
from typing import Union

import config.shapes.process_selection as selection
import config.shapes.signal_variations as signal_variations  # TODO: Unify this?
import config.shapes.variations as variations
from config.logging_setup_configs import setup_logging

from config.shapes.category_selection import categorization as default_categorization
from config.shapes.channel_selection import channel_selection
from config.shapes.control_binning import control_binning as default_control_binning
from config.shapes.file_names import files
from config.shapes.gof_binning import load_gof_binning
from config.shapes.taues_measurement_binning import categorization as taues_categorization
from config.shapes.tauid_measurement_binning import categorization as tauid_categorization
from ntuple_processor import GraphManager, RunManager, UnitManager
import shapes.utils as shape_utils


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
        "--selection-option",
        help="Set to the DR used for the fake factor estimation.",
        choices=["CR", "DR;ff;wjet", "DR;ff;qcd", "DR;ff;ttbar"],
        default="CR",
    )
    parser.add_argument(
        "--ff-type",
        help=f"Set to the type of fake factor used.\n{variations.__FF_OPTION_info__}",
        default="fake_factor"
    )
    return parser.parse_args()


def add_processes(
    add_fn: callable,
    datasets: dict,
    select_fn: callable,
    channel: str,
) -> None:

    add_fn(name="data", dataset=datasets["data"], selections=select_fn())
    add_fn(name="hh2b2tau", dataset=datasets["HH2B2Tau"], selections=select_fn(selection.HH2B2Tau))
    add_fn(name="ztt", dataset=datasets["DY"], selections=select_fn(selection.DY, selection.ZTT))
    add_fn(name="zl", dataset=datasets["DY"], selections=select_fn(selection.DY, selection.ZL))
    add_fn(name="zj", dataset=datasets["DY"], selections=select_fn(selection.DY, selection.ZJ))
    # add_fn(name="ztt_nlo", dataset=datasets["DYNLO"], selections=select_fn(selection.DY_NLO, selection.ZTT))
    # add_fn(name="zl_nlo", dataset=datasets["DYNLO"], selections=select_fn(selection.DY_NLO, selection.ZL))
    # add_fn(name="zj_nlo", dataset=datasets["DYNLO"], selections=select_fn(selection.DY_NLO, selection.ZJ))
    add_fn(name="w", dataset=datasets["W"], selections=select_fn(selection.W))
    add_fn(name="stl", dataset=datasets["ST"], selections=select_fn(selection.ST, selection.STL))
    add_fn(name="stt", dataset=datasets["ST"], selections=select_fn(selection.ST, selection.STT))
    add_fn(name="stj", dataset=datasets["ST"], selections=select_fn(selection.ST, selection.STJ))
    add_fn(name="ggh", dataset=datasets["ggH"], selections=select_fn(selection.ggH125))
    add_fn(name="qqh", dataset=datasets["qqH"], selections=select_fn(selection.qqH125))
    add_fn(name="ttl", dataset=datasets["TT"], selections=select_fn(selection.TT, selection.TTL))
    add_fn(name="ttt", dataset=datasets["TT"], selections=select_fn(selection.TT, selection.TTT))
    add_fn(name="ttj", dataset=datasets["TT"], selections=select_fn(selection.TT, selection.TTJ))
    add_fn(name="tth", dataset=datasets["ttH"], selections=select_fn(selection.ttH))
    add_fn(name="vvl", dataset=datasets["VV"], selections=select_fn(selection.VV, selection.VVL))
    add_fn(name="vvt", dataset=datasets["VV"], selections=select_fn(selection.VV, selection.VVT))
    add_fn(name="vvj", dataset=datasets["VV"], selections=select_fn(selection.VV, selection.VVJ))
    add_fn(name="vvvl", dataset=datasets["VVV"], selections=select_fn(selection.VVV, selection.VVVL))
    add_fn(name="vvvt", dataset=datasets["VVV"], selections=select_fn(selection.VVV, selection.VVVT))
    add_fn(name="vvvj", dataset=datasets["VVV"], selections=select_fn(selection.VVV, selection.VVVJ))
    add_fn(name="vh", dataset=datasets["VH"], selections=select_fn(selection.VH))
    add_fn(name="ewk", dataset=datasets["EWK"], selections=select_fn(selection.EWK))
    add_fn(name="ttvl", dataset=datasets["TTV"], selections=select_fn(selection.TTV, selection.TTVL))
    add_fn(name="ttvt", dataset=datasets["TTV"], selections=select_fn(selection.TTV, selection.TTVT))
    add_fn(name="ttvj", dataset=datasets["TTV"], selections=select_fn(selection.TTV, selection.TTVJ))
    add_fn(name="qcd", dataset=datasets["QCDMC"], selections=select_fn(selection.QCD))


def get_analysis_units(
    channel: str,
    era: str,
    datasets: dict,
    categorization: dict,
    special_analysis: Union[str, None],
    apply_tauid: bool,
    vs_jet_wp: str,
    vs_ele_wp: str,
    selection_option: str = "CR",
) -> dict:

    _selection_kwargs = dict(
        channel=channel,
        era=era,
        special=special_analysis,
        vs_jet_wp=vs_jet_wp,
        vs_ele_wp=vs_ele_wp,
        selection_option=selection_option,
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
            shape_utils.add_process,
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
    channel: str,
    era: str,
    datasets: dict,
    special_analysis: Union[str, None],
    variables: list[str],
    apply_tauid: bool,
    vs_jet_wp: str,
    vs_ele_wp: str,
    selection_option: str = "CR",
    do_gofs: bool = False,
    do_2dGofs: bool = False,
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
        selection_option=selection_option,
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
            shape_utils.add_control_process,
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


def TauES_TauID_histogram_booking(
    channel: str,
    processes: str,
    unit_manager: UnitManager,
    args: argparse.Namespace,
    datasets: dict,
):
    if channel == "mt" and args.special_analysis == "TauES":
        logger.info("Booking TauES")
        shape_utils.book_tauES_histograms(
            manager=unit_manager,
            additional_emb_procS=processes,
            datasets=datasets,
            variations=[variations.same_sign], # , variations.anti_iso_lt
            enable_check=args.enable_booking_check,
        )
    elif channel == "mt" and args.es and args.special_analysis == "TauID":
        logger.info("Booking TauES")
        shape_utils.book_tauES_histograms(
            manager=unit_manager,
            additional_emb_procS=processes,
            datasets=datasets,
            variations=[variations.same_sign, variations.anti_iso_lt_no_ff],
            enable_check=args.enable_booking_check,
        )
        # book_tauES_histograms(
        #     um,
        #     additional_emb_procS,
        #     nominals[args.era]["units"][channel],
        #     [trigger_eff_mt_emb],
        #     args.enable_booking_check,
        # )
        # book_histograms(
        #     um,
        #     additional_emb_procS,
        #     datasets=nominals[args.era]["units"][channel],
        #     variations=[trigger_eff_mt_emb],
        #     enable_check=args.enable_booking_check,
        # )
    else:
        raise ValueError("Unknown special analysis: {}".format(args.special_analysis))


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
    categorization = prepare_special_analysis(args.special_analysis)
    unit_manager = UnitManager()
    print("#### Apply tau ID", args.apply_tauid)

    nominals = {}
    nominals[args.era] = {}
    nominals[args.era]["datasets"] = {}
    nominals[args.era]["units"] = {}

    # Step 1: create units and book actions
    for channel in args.channels:
        nominals[args.era]["datasets"][channel] = shape_utils.get_nominal_datasets(
            era=args.era,
            channel=channel,
            friend_directories=friend_directories,
            files=files,
            directory=args.directory,
            xrootd=args.xrootd,
            validation_tag=args.validation_tag,
        )

        common_kwargs = dict(
            era=args.era,
            channel=channel,
            datasets=nominals[args.era]["datasets"][channel],
            special_analysis=args.special_analysis,
            apply_tauid=args.apply_tauid,
            vs_jet_wp=args.vs_jet_wp,
            vs_ele_wp=args.vs_ele_wp,
            selection_option=args.selection_option,
        )

        if args.control_plots:
            nominals[args.era]["units"][channel] = get_control_units(
                **common_kwargs,
                variables=args.control_plot_set,
                do_gofs=False,
            )
        elif args.gof_inputs:
            nominals[args.era]["units"][channel] = get_control_units(
                **common_kwargs,
                variables=args.control_plot_set,
                do_gofs=True,
                do_2dGofs=args.do_2dGofs,
            )
        else:
            nominals[args.era]["units"][channel] = get_analysis_units(
                **common_kwargs,
                categorization=categorization,
            )
        if args.special_analysis == "TauES":
            additional_emb_procS = set()
            tauESvariations = [-2.5 + 0.1 * i for i in range(0, 51)]
            shape_utils.add_tauES_datasets(
                args.era,
                channel,
                friend_directories,
                files,
                args.directory,
                nominals,
                tauESvariations,
                [
                    channel_selection(channel, args.era, args.special_analysis, args.vs_jet_wp, args.vs_ele_wp),
                    selection.ZTT_embedded(channel, args.era, args.apply_tauid, args.vs_jet_wp),
                ],
                categorization,
                additional_emb_procS,
                xrootd=args.xrootd,
                validation_tag=args.validation_tag,
            )
        if args.special_analysis == "TauID" and args.es:
            additional_emb_procS = set()
            tauESvariations = [-4.0 + 0.1 * i for i in range(0, 81)]
            shape_utils.add_tauES_datasets(
                args.era,
                channel,
                friend_directories,
                files,
                args.directory,
                nominals,
                tauESvariations,
                [
                    channel_selection(channel, args.era, args.special_analysis, args.vs_jet_wp, args.vs_ele_wp),
                    selection.ZTT_embedded(channel, args.era, args.apply_tauid, args.vs_jet_wp),
                ],
                categorization,
                additional_emb_procS,
                xrootd=args.xrootd,
                validation_tag=args.validation_tag,
            )

    if args.process_selection is None:
        procS = {
            "data",
            "hh2b2tau",
            "ztt",
            "zl",
            "zj",
            "w",
            "stl",
            "stt",
            "stj",
            "ggh",
            "qqh",
            "ttl",
            "ttt",
            "ttj",
            "tth",
            "vvl",
            "vvt",
            "vvj",
            "vh",
            "vvvl",
            "vvvt",
            "vvvj",
            "ewk",
            "ttvl",
            "ttvt",
            "ttvj",
            "qcd",
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
            "stl",
            "w",
            # "w_nlo",
            # "emb",
        } & procS

    dataS = {"data"} & procS
    # embS = {"emb"} & procS
    qcdS = {"qcd"} & procS
    jetFakesDS = {
        "et": {"zj", "ttj", "ttvj", "vvj", "vvvj", "stj", "w", "zj_nlo", "w_nlo"} & procS,
        "mt": {"zj", "ttj", "ttvj", "vvj", "vvvj", "stj", "w", "zj_nlo", "w_nlo"} & procS,
        "tt": {"zj", "ttj", "ttvj", "vvj", "vvvj", "stj", "w", "zj_nlo", "w_nlo"} & procS,
        "em": {"w", "w_nlo"} & procS,
    }
    leptonFakesS = {"zl", "ttl", "ttvl", "vvl", "vvvl", "stl", "zl_nlo"} & procS
    trueTauBkgS = {"ztt", "ttt", "ttvt", "vvt", "vvvt", "stt", "ztt_nlo"} & procS
    signalsS = {
        "hh2b2tau",
    } & procS
    ewkS = {"ewk"} & procS
    singleHiggsS = {"ggh", "qqh", "tth", "vh"} & procS

    simulatedProcsDS = {
        chname_: jetFakesDS[chname_] | leptonFakesS | trueTauBkgS | signalsS
        for chname_ in ["et", "mt", "tt", "em"]
    }
    logger.info(f"Processes to be computed: {procS}")
    logger.info(f"Simulated processes: {simulatedProcsDS}")
    logger.info(f"Data processes: {dataS}")
    # logger.info(f"Embedded processes: {embS}")
    logger.info(f"Jet fakes processes: {jetFakesDS}")
    logger.info(f"Lepton fakes processes: {leptonFakesS}")
    logger.info(f"True tau bkg processes: {trueTauBkgS}")
    logger.info(f"Single Higgs processes: {singleHiggsS}")
    logger.info(f"signals: {signalsS}")

    _book_histogram = partial(
        shape_utils.book_histograms,
        manager=unit_manager,
        datasets=nominals[args.era]["units"][channel],
        enable_check=args.enable_booking_check,
    )

    for channel in args.channels:
        _book_histogram(processes=signalsS)
        # if channel == "mt" and args.special_analysis in {"TauES", "TauID"}:
        #     TauES_TauID_histogram_booking(
        #         channel=channel,
        #         processes=additional_emb_procS,
        #         unit_manager=unit_manager,
        #         args=args,
        #         datasets=nominals[args.era]["units"][channel],
        #    )
        if channel in ["mt", "et"]:
            for procs in [dataS | trueTauBkgS | leptonFakesS | singleHiggsS | ewkS | qcdS | jetFakesDS[channel]]:
                _book_histogram(
                    processes=procs,
                    variations=[variations.abcd_method_lt, variations.same_sign],
                    # variations=variations.SemiLeptonicFFEstimations.unrolled(),
                )
        elif channel == "tt":
            for procs in [dataS | trueTauBkgS | leptonFakesS  | singleHiggsS | ewkS | qcdS | jetFakesDS[channel]]:
                _book_histogram(
                    processes=procs,
                    # variations=[variations.same_sign],
                    # variations=variations.FullyHadronicFFEstimations.unrolled(),
                    variations=[variations.abcd_method_tt, variations.same_sign],
                )
        elif channel == "em":
            _book_histogram(
                processes=dataS | simulatedProcsDS[channel] - signalsS,
                variations=[variations.same_sign_em],
            )
        elif channel == "mm" and args.special_analysis == "TauES":
            _book_histogram(processes={"data", "zl", "w", "ttl"}, variations=[])
        elif channel == "mm":
            _book_histogram(processes=procS, variations=[variations.same_sign])
            # _book_histogram(processes=embS, variations=[trigger_eff_mt_emb])
        elif channel == "ee":
            _book_histogram(processes=procS, variations=[variations.same_sign])
        ##################################
        # SYSTEMATICS
        ############################
        if not args.skip_systematic_variations:
            # Book variations common to all channels.
            # um.book([unit for d in {"ggh"} & procS for unit in nominals[era]['units'][channel][d]], [*ggh_acceptance], enable_check=args.enable_booking_check)
            # um.book([unit for d in {"qqh"} & procS for unit in nominals[era]['units'][channel][d]], [*qqh_acceptance], enable_check=args.enable_booking_check)
            # TODO add signal uncertainties
            _book_histogram(
                processes={"ggh"} & procS,
                variations=[signal_variations.ggh_acceptance],
            )
            _book_histogram(
                processes={"qqh"} & procS,
                variations=[signal_variations.qqh_acceptance],
            )
            _book_histogram(
                processes=simulatedProcsDS[channel],
                variations=[variations.jet_es],
            )
            # TODO add btag stuff
            # _book_histogram(
            #     processes=simulatedProcsDS[channel],
            #     variations=[mistag_eff, btag_eff],
            # )
            _book_histogram(
                processes={"ztt", "zj", "zl", "w"} & procS | signalsS,
                variations=[variations.recoil_resolution, variations.recoil_response],
            )
            _book_histogram(
                processes=simulatedProcsDS[channel],
                variations=[variations.met_unclustered, variations.pileup_reweighting],
            )
            _book_histogram(
                processes={"ztt", "zl", "zj"} & procS,
                variations=[variations.zpt],
            )
            _book_histogram(
                processes={"ttt", "ttl", "ttj", "ttvt", "ttvl", "ttvj"} & procS,
                variations=[variations.top_pt],
            )
            # Book variations common to multiple channels.
            if channel in ["et", "mt", "tt"]:
                if not args.es and args.special_analysis != "TauID":
                    _book_histogram(
                        processes=(trueTauBkgS | leptonFakesS | signalsS) - {"zl"},
                        variations=[
                            variations.tau_es_3prong,
                            variations.tau_es_3prong1pizero,
                            variations.tau_es_1prong,
                            variations.tau_es_1prong1pizero,
                        ],
                    )
                    # _book_histogram(
                    #     processes=embS,
                    #     variations=[
                    #         variations.emb_tau_es_3prong,
                    #         variations.emb_tau_es_3prong1pizero,
                    #         variations.emb_tau_es_1prong,
                    #         variations.emb_tau_es_1prong1pizero,
                    #         variations.tau_es_3prong,
                    #         variations.tau_es_3prong1pizero,
                    #         variations.tau_es_1prong,
                    #         variations.tau_es_1prong1pizero,
                    #     ],
                    # )
                _book_histogram(
                    processes=jetFakesDS[channel],
                    variations=[variations.jet_to_tau_fake],
                )
            if channel in ["et", "mt"]:
                if not args.es and args.special_analysis != "TauID":
                    _book_histogram(
                        processes=(trueTauBkgS | leptonFakesS | signalsS) - {"zl"},
                        variations=[variations.tau_id_eff_lt],
                    )
                    _book_histogram(
                        processes=dataS | leptonFakesS | trueTauBkgS,
                        variations=[variations.ff_variations_lt],
                    )

                    _book_histogram(
                        processes=leptonFakesS | trueTauBkgS,
                        variations=[variations.ff_variations_tau_es_lt],
                    )
                    # _book_histogram(
                    #     processes=embS,
                    #     variations=[variations.ff_variations_tau_es_emb_lt],
                    # )
                    # _book_histogram(
                    #     processes=embS,
                    #     variations=[variations.emb_tau_id_eff_lt, variations.emb_tau_id_eff_lt_corr],
                    # )
            # if channel in ["et", "em"]:
            #     # TODO add eleES
            #     _book_histogram(
            #         processes=simulatedProcsDS[channel],
            #         variations=[ele_res, ele_es],
            #     )
            #     # TODO add emb ele ES
            #     _book_histogram(
            #         processes=embS,
            #         variations=[variations.emb_e_es],
            #     )
            # Book channel independent variables.
            if channel == "mt":
                _book_histogram(
                    processes={"zl"} & procS,
                    variations=[variations.mu_fake_es_inc],
                )
                _book_histogram(
                    processes=simulatedProcsDS[channel],
                    variations=[variations.trigger_eff_mt],
                )
                # _book_histogram(
                #     processes=embS,
                #     variations=[trigger_eff_mt_emb],
                # )
                # _book_histogram(
                #     processes=embS,
                #     variations=[variations.same_sign, variations.anti_iso_lt_no_ff],
                # )
                _book_histogram(
                    processes={"zl"} & procS,
                    variations=[variations.zll_mt_fake_rate],
                )
            if channel == "et":
                _book_histogram(
                    processes={"zl"} & procS,
                    variations=[variations.ele_fake_es],
                )
                _book_histogram(
                    processes=simulatedProcsDS[channel],
                    variations=[variations.trigger_eff_et],
                )
                # _book_histogram(
                #     processes=embS,
                #     variations=[variations.trigger_eff_et_emb],
                # )
                _book_histogram(
                    processes={"zl"} & procS,
                    variations=[variations.zll_et_fake_rate],
                )
            if channel == "tt":
                _book_histogram(
                    processes=trueTauBkgS | leptonFakesS | signalsS,
                    variations=[variations.tau_id_eff_tt],
                )
                # Todo add trigger efficiency
                # _book_histogram(
                #     processes=simulatedProcsDS[channel],
                #     variations=[tau_trigger_eff_tt],
                # )
                # TODO add trigger efficiency for emb
                # _book_histogram(
                #     processes=embS,
                #     variations=[emb_tau_id_eff_tt, tau_id_eff_tt, tau_trigger_eff_tt_emb, tau_trigger_eff_tt, emb_decay_mode_eff_tt],
                # )
                # TODO add fake factor variations
                # _book_histogram(
                #     processes=dataS | embS | trueTauBkgS,
                #     variations=[ff_variations_tt],
                # )
                # TODO add fake factor variations for lepton fakes
                # _book_histogram(
                #     processes=leptonFakesS,
                #     variations=[ff_variations_tt_mcl],
                # )
            # if channel == "em":
            # TODO add QCD variations ?
            # _book_histogram(
            #     processes=dataS | embS | simulatedProcsDS[channel] - signalsS,
            #     variations=[qcd_variations_em],
            # )
            # Book era dependent uncertainty shapes
            if "2016" in args.era or "2017" in args.era:
                _book_histogram(
                    processes=simulatedProcsDS[channel],
                    variations=[variations.prefiring],
                )

    # Step 2: convert units to graphs and merge them
    g_manager = GraphManager(unit_manager.booked_units, True)
    g_manager.optimize(args.optimization_level)
    graphs = g_manager.graphs
    for graph in graphs:
        print("%s" % graph)

    if args.only_create_graphs:
        _channels = ",".join(args.channels)
        _processes = ",".join(sorted(procS))
        if args.control_plots or args.gof_inputs:
            graph_file_name = f"control_unit_graphs-{args.era}-{_channels}-{_processes}.pkl"
        else:
            graph_file_name = f"analysis_unit_graphs-{args.era}-{_channels}-{_processes}.pkl"
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
    logger = setup_logging(logger=logging.getLogger(__name__))
    variations.set_ff_type(args.ff_type)
    main(args)
