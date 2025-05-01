#!/usr/bin/env python
import argparse
import logging
import os
import pickle
from functools import partial
from itertools import combinations
from typing import Union

import yaml

import config.shapes.process_selection as selection
import config.shapes.signal_variations as signal_variations  # TODO: Unify this?
import config.shapes.variations as variations
import shapes.utils as shape_utils
import config.shapes.ntuple_processor_config_helper as ntuple_processor_config_helper
from config.helper_collection import PreserveROOTPathsAsStrings
from config.logging_setup_configs import setup_logging
from config.shapes.category_selection import categorization as default_categorization
from config.shapes.channel_selection import channel_selection
from config.shapes.control_binning import control_binning as default_control_binning
from config.shapes.file_names import files
from config.shapes.gof_binning import load_gof_binning
from ntuple_processor import GraphManager, RunManager, UnitManager


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
        default=1,
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
        "--collect-config-only",
        action="store_true",
        help="Only collect cuts/weights/datasets/variations into a YAML file, skip histogram production.",
    )
    parser.add_argument(
        "--config-output-file",
        default="tmp_config.yaml",
        type=str,
        help="YAML file where configuration data will be stored. Required if --collect-config-only is set.",
    )
    parser.add_argument(
        "--enable-booking-check",
        action="store_true",
        help="Enables check for double actions during booking. Takes long for all variations.",
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
    channel: str,
    era: str,
    datasets: dict,
    categorization: dict,
    apply_tauid: bool,
    vs_jet_wp: str,
    vs_ele_wp: str,
    selection_option: str = "CR",
) -> dict:

    _selection_kwargs = dict(
        channel=channel,
        era=era,
        special=None,
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
        special=None,
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


def collect_config(
    graphs: list,
    era: str,
    channel: str,
    filename: str,
) -> None:

    r_manager = RunManager(
        graphs,
        create_histograms=False,
        create_config=True,
        config_formatter=ntuple_processor_config_helper.get_config_formatter(era=era),
    )
    r_manager.nthreads = 1

    for _graph in graphs:
        logger.info(f"Creating config for graph {_graph.name}")
        r_manager.node_to_root(_graph)

        ntuple_processor_config_helper.add_paths(
            graph=_graph,
            channel=channel,
            era=era,
            r_manager=r_manager,
        )

    _path, _basename = os.path.split(filename)
    _path = os.path.join(_path, f"{era}__{channel}__{_basename}")
    with open(_path, "w") as config_file:
        yaml.dump(
            r_manager.config.regular,
            config_file,
            default_flow_style=False,
            Dumper=PreserveROOTPathsAsStrings,
        )
    logger.info("Configuration written to %s", args.config_output_file)
    logger.info("Due to a bug in ROOT/xrd the script won't exit properly. Please kill it manually. (i.e. Ctrl+z && kill %1)")


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
    unit_manager = UnitManager()
    logger.info(f"Apply tau ID: {args.apply_tauid}")

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
                categorization=default_categorization,
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

    def _book(processes, variations):  # helper wrapper
        shape_utils.book_histograms(
            processes=processes,
            variations=variations,
            manager=unit_manager,
            datasets=nominals[args.era]["units"][channel],
            enable_check=args.enable_booking_check,
        )

    for channel in args.channels:
        _book(signalsS, [])
        if channel in ["mt", "et"]:
            for procs in [embS, dataS | trueTauBkgS | leptonFakesS, jetFakesDS[channel]]:
                _book(procs, variations.SemiLeptonicFFEstimations.unrolled())
        elif channel == "tt":
            for procs in [dataS | embS | trueTauBkgS, leptonFakesS, jetFakesDS[channel]]:
                _book(procs, variations.FullyHadronicFFEstimations.unrolled())
        elif channel == "em":
            _book((dataS | embS | simulatedProcsDS[channel]) - signalsS, [variations.same_sign_em])
        elif channel == "mm":
            _book(procS, [variations.same_sign])
            # _book_histogram(processes=embS, variations=[trigger_eff_mt_emb])
        elif channel == "ee":
            _book(procS, [variations.same_sign])
        ##################################
        # SYSTEMATICS
        ############################
        if not args.skip_systematic_variations:
            # Book variations common to all channels.
            _book({"ggh"} & procS, [signal_variations.ggh_acceptance])  # TODO add signal uncertainties
            _book({"qqh"} & procS, [signal_variations.qqh_acceptance])  # TODO add signal uncertainties
            _book(simulatedProcsDS[channel], [variations.jet_es])
            _book(signalsS, variations.LHE_scale.unrolled())

            _book({"ztt", "zj", "zl", "w"} & procS | signalsS, variations.Recoil.unrolled())
            _book(simulatedProcsDS[channel], [variations.met_unclustered, variations.pileup_reweighting])
            _book({"ztt", "zl", "zj"} & procS, [variations.zpt])
            _book({"ttt", "ttl", "ttj"} & procS, [variations.top_pt])

            if channel in ["et", "mt", "tt"]:
                _book(jetFakesDS[channel], [variations.jet_to_tau_fake])
                _book((trueTauBkgS | leptonFakesS | signalsS) - {"zl"}, variations.TauEnergyScale.unrolled())
                _book(embS, (variations.TauEnergyScale + variations.TauEmbeddingEnergyScale).unrolled())

            if channel in ["et", "mt"]:
                _book((trueTauBkgS | leptonFakesS | signalsS) - {"zl"}, [variations.tau_id_eff_lt])
                _book(dataS | embS | leptonFakesS | trueTauBkgS, variations.FakeFactorLT.unrolled())
                _book(leptonFakesS | trueTauBkgS | embS, [variations.ff_variations_tau_es_lt])
                _book(embS, [variations.ff_variations_tau_es_emb_lt])
                _book(embS, [variations.emb_tau_id_eff_lt, variations.emb_tau_id_eff_lt_corr])

            # TODO btag uncertainties?

            if channel in ["et", "em"]:
                _book(simulatedProcsDS[channel], [variations.ele_res, variations.ele_es])
                _book(embS, [variations.emb_e_es])

            if channel == "mt":
                _book({"zl"} & procS, [variations.mu_fake_es_inc])
                _book(simulatedProcsDS[channel], [variations.trigger_eff_mt])
                _book(embS, [variations.trigger_eff_mt_emb])
                _book({"zl"} & procS, [variations.zll_mt_fake_rate])

            if channel == "et":
                _book({"zl"} & procS, [variations.ele_fake_es])
                _book(simulatedProcsDS[channel], [variations.trigger_eff_et])
                _book(embS, [variations.trigger_eff_et_emb])
                _book({"zl"} & procS, [variations.zll_et_fake_rate])
            if channel == "tt":
                _book(trueTauBkgS | leptonFakesS | signalsS, [variations.tau_id_eff_tt])
                # _book(simulatedProcsDS[channel], [variations.tau_trigger_eff_tt])  # TODO
                # _book(embS, variations.TauIDAndTriggerEfficiency.unrolled())  # TODO
                # _book(dataS | embS | trueTauBkgS, [variations.FakeFactorTT.unrolled()])  # TODO

            if channel == "em":
                _book(dataS | embS | simulatedProcsDS[channel] - signalsS, [variations.qcd_variations_em])  # TODO

            if "2016" in args.era or "2017" in args.era:
                _book(simulatedProcsDS[channel], [variations.prefiring])

            if "2018" in args.era:
                _book(simulatedProcsDS[channel], [variations.jet_es_hem])


    # Step 2: convert units to graphs and merge them
    g_manager = GraphManager(unit_manager.booked_units, True)
    g_manager.optimize(args.optimization_level)
    graphs = g_manager.graphs
    for graph in graphs:
        print("%s" % graph)

    if args.collect_config_only:
        if len(args.channels) > 1:
            raise NotImplementedError("Collecting config for multiple channels is not implemented yet.")
        collect_config(
            graphs=graphs,
            era=args.era,
            channel=args.channels[0],
            filename=args.config_output_file,
        )
        return

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
        with open(graph_file, "wb") as _friend:
            pickle.dump(graphs, _friend)
    else:
        r_manager = RunManager(graphs)
        r_manager.run_locally(output_file, args.num_processes, args.num_threads)


if __name__ == "__main__":
    args = parse_arguments()
    if ".root" in args.output_file:
        log_file = args.output_file.replace(".root", ".log")
    else:
        log_file = "{}.log".format(args.output_file)
    logger = setup_logging(logger=logging.getLogger(__name__))
    variations.set_ff_type(args.ff_type)
    main(args)
