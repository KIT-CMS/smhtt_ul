#!/usr/bin/env python3

import argparse
import logging
import os
import resource
import shlex
import shutil
import subprocess
from pathlib import Path

from config.logging_setup_configs import LogContext, setup_logging

DEFAULT_VARIABLES_LIST = [
    "pt_1", "eta_1", "phi_1", "tau_decaymode_1", "mt_1", "iso_1", "mass_1",
    "pt_2", "eta_2", "phi_2", "tau_decaymode_2", "mt_2", "iso_2", "mass_2",
    "jpt_1", "jeta_1", "jphi_1", "jpt_2", "jeta_2", "jphi_2",
    "bpt_1", "beta_1", "bphi_1", "btag_value_1",
    "bpt_2", "beta_2", "bphi_2", "btag_value_2",
    "pt_tt", "pt_vis", "pt_dijet", "pt_ttjj",
    "mjj", "mt_tot", "m_vis",
    "met", "metphi", "nbtag", "njets", "q_1", "pzetamissvis", "jet_hemisphere",
    "deltaR_ditaupair", "deltaEta_ditaupair",
    "deltaR_jj", "deltaEta_jj",
    "deltaR_1j1", "deltaR_1j2", "deltaR_2j1", "deltaR_2j2", "deltaR_12j1", "deltaR_12j2",
    "deltaEta_1j1", "deltaEta_1j2", "deltaEta_2j1", "deltaEta_2j2", "deltaEta_12j1", "deltaEta_12j2",
    "eta_fastmtt", "m_fastmtt", "phi_fastmtt", "pt_fastmtt",
]

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UL control plots workflow", allow_abbrev=False)
    parser.add_argument("-c", "--channel", required=True)
    parser.add_argument("-e", "--era", required=True)
    parser.add_argument("-n", "--ntupletag", required=True)
    parser.add_argument("-t", "--tag", required=True)
    parser.add_argument("-m", "--mode", required=True, choices=["XSEC", "SHAPES", "PLOT"])
    parser.add_argument("-f", "--additional-friends", dest="additional_friends", default="xsec")
    parser.add_argument("-M", "--additional-multifriends", dest="additional_multifriends", default="")
    parser.add_argument("-s", "--selection-option", dest="selection_option", default="CR")
    parser.add_argument("-S", "--selection-option-estimation", dest="selection_option_estimation", default="CR")
    parser.add_argument("-F", "--ff_type", "--ff-type", dest="ff_type", default="fake_factor")
    parser.add_argument("-p", "--plotversion", default="all", choices=["all", "emb+ff", "emb+classic", "classic+ff", "classic+classic"])
    parser.add_argument("-v", "--variables", default="")
    parser.add_argument("-N", "--nanoaodversion", default="v9")
    parser.add_argument("-L", "--locally", dest="local_cache", action="store_true", default=True)
    parser.add_argument("-W", "--local-cache-workers", dest="local_cache_workers", type=int, default=10)
    parser.add_argument(
        "--control-plots-njet-split",
        dest="control_plots_njet_split",
        action="store_true",
        help="Enable njets split categories for control-shape production.",
    )
    parser.add_argument(
        "--control-plots-dnn-split",
        dest="control_plots_dnn_split",
        action="store_true",
        help="Split control plots into DNN categories and bins.",
    )
    parser.add_argument(
        "--analysis-units",
        dest="analysis_units",
        action="store_true",
        help="Produce analysis units instead of control-plot units.",
    )
    parser.add_argument(
        "--plotcategory",
        "--category",
        dest="plotcategory",
        default="Nominal",
        help="Category passed to plotting. Use Nominal for unsplit plotting.",
    )

    parser.set_defaults(skip_systematic_variations=True)
    systematic_group = parser.add_mutually_exclusive_group()
    systematic_group.add_argument(
        "--skip-systematic-variations", dest="skip_systematic_variations", action="store_true",
        help="Skip shape systematic variations (default)."
    )
    systematic_group.add_argument(
        "--with-systematic-variations", dest="skip_systematic_variations", action="store_false",
        help="Enable shape systematic variations."
    )

    parser.set_defaults(shape_meta_mode=None)
    meta_group = parser.add_mutually_exclusive_group()
    meta_group.add_argument("--only-create-graphs", dest="shape_meta_mode", action="store_const", const="only_create_graphs")
    meta_group.add_argument("--gof-inputs", dest="shape_meta_mode", action="store_const", const="gof_inputs")
    meta_group.add_argument("--collect-config-only", dest="shape_meta_mode", action="store_const", const="collect_config_only")
    meta_group.add_argument("--run-splitted", dest="shape_meta_mode", action="store_const", const="run_splitted")

    parser.add_argument("--graph-filename", default=None, help="Override graph filename used with --only-create-graphs.")
    parser.add_argument("--config-output-file", default=None, help="Override config output filename used with --collect-config-only.")
    parser.add_argument(
        "--discover-cut-ordering",
        dest="discover_cut_ordering",
        action="store_true",
        help="Discover per-dataset cut ordering and write it to the cache file during this shapes run.",
    )
    parser.add_argument(
        "--cut-order-cache-file",
        dest="cut_order_cache_file",
        default="",
        help="Path to the cut-order cache file used by shapes/produce_shapes.py.",
    )
    parser.add_argument(
        "--enable-cut-ordering",
        dest="enable_cut_ordering",
        action="store_true",
        help="Enable applying cut ordering in shapes/produce_shapes.py.",
    )

    arguments = parser.parse_args()

    if arguments.graph_filename and arguments.shape_meta_mode != "only_create_graphs":
        parser.error("--graph-filename requires --only-create-graphs")
    if arguments.config_output_file and arguments.shape_meta_mode != "collect_config_only":
        parser.error("--config-output-file requires --collect-config-only")
    if arguments.analysis_units and arguments.control_plots_njet_split:
        parser.error("--control-plots-njet-split is only valid for control-plot unit production")
    if arguments.analysis_units and arguments.control_plots_dnn_split:
        parser.error("--control-plots-dnn-split is only valid for control-plot unit production")

    return arguments


def setup_environment(repository_root: Path, ntupletag: str, era: str) -> str:
    dumbledraw_path = str(repository_root / "Dumbledraw")
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = f"{current_pythonpath}:{dumbledraw_path}" if current_pythonpath else dumbledraw_path

    with LogContext(logger).log_and_suppress(OSError, ValueError, msg="Failed to set unlimited stack size"):
        resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

    os.environ["COLUMNS"] = str(shutil.get_terminal_size(fallback=(120, 24)).columns)

    source_command = (
        f"get_conda && conda activate SANNT.dev && "
        f"set -a && "
        f"source {shlex.quote(str(repository_root / 'utils/setup_root.sh'))} && "
        f"source {shlex.quote(str(repository_root / 'utils/setup_ul_samples.sh'))} {shlex.quote(ntupletag)} {shlex.quote(era)} && "
        f"set +a && env -0"
    )
    process_result = subprocess.run(["bash", "-lc", source_command], cwd=str(repository_root), capture_output=True, text=True, check=False)

    if process_result.returncode != 0:
        with LogContext(logger).logging_raised_Error():
            raise RuntimeError(f"Failed to source setup scripts.\n{process_result.stderr}")

    for environment_entry in process_result.stdout.split("\0"):
        if "=" in environment_entry:
            environment_key, environment_value = environment_entry.split("=", 1)
            os.environ[environment_key] = environment_value

    # Setup Fallback Variables
    user_name = os.environ.get("USER", "")
    os.environ.setdefault("KINGMAKER_BASEDIR", f"/store/user/{user_name}/CROWN/ntuples/{ntupletag}/CROWNRun/")
    os.environ.setdefault("KINGMAKER_BASEDIR_XROOTD", f"root://cmsdcache-kit-disk.gridka.de/{os.environ['KINGMAKER_BASEDIR']}")
    os.environ.setdefault("XSEC_FRIENDS", f"/store/user/{user_name}/CROWN/ntuples/{ntupletag}/CROWNFriends/xsec/")
    os.environ.setdefault("NTUPLES", os.environ["KINGMAKER_BASEDIR"])

    return user_name


def get_plot_variables(variables_arg: str) -> str:
    if not variables_arg or variables_arg == "default":
        logger.info("Using the default variable list defined in the script.")
        used_variables = ",".join(DEFAULT_VARIABLES_LIST)
    else:
        logger.info("Using custom variable list provided via --variables.")
        used_variables = variables_arg

    if not used_variables:
        with LogContext(logger).logging_raised_Error():
            raise ValueError("The final variable list to be plotted is empty. Exiting.")

    return used_variables


def get_friend_directories(args: argparse.Namespace, user_name: str) -> tuple[str, str]:
    friend_directories = []
    seen_friends = set()
    for tag in args.additional_friends.split():
        if tag == "xsec":
            continue
        if tag not in seen_friends:
            friend_directories.append(f"/store/user/{user_name}/CROWN/ntuples/{args.ntupletag}/CROWNFriends/{tag}/")
            seen_friends.add(tag)

    multifriend_directories = []
    for tag in args.additional_multifriends.split():
        if tag:
            multifriend_directories.append(f"/store/user/{user_name}/CROWN/ntuples/{args.ntupletag}/CROWNMultiFriends/{tag}/")

    return " ".join(friend_directories), " ".join(multifriend_directories)


def execute_bash_string(command_string: str, repository_root: Path) -> None:
    """Parses a multiline string into a command array and runs it cleanly."""
    command_list = shlex.split(command_string)
    logger.info(f"Running command: {shlex.join(command_list)}")
    subprocess.run(command_list, cwd=str(repository_root), env=os.environ.copy(), check=True)


def main() -> None:
    arguments = parse_arguments()
    repository_root = Path(__file__).resolve().parent

    # --- Setup and Resolve Variables ---
    user_name = setup_environment(repository_root, arguments.ntupletag, arguments.era)
    used_variables = get_plot_variables(arguments.variables)
    friends_string, multifriends_string = get_friend_directories(arguments, user_name)

    if arguments.local_cache:
        logger.info(f"Local ntuple cache enabled. Using /ceph/{user_name} when possible with {arguments.local_cache_workers} worker(s).")

    xsec_friend = os.environ["XSEC_FRIENDS"]
    logger.info(f"Using xsec friend directory: {xsec_friend}")

    unit_kind = "analysis" if arguments.analysis_units else "control"
    output_shapes_name = f"{unit_kind}_shapes-{arguments.era}-{arguments.channel}-{arguments.ntupletag}-{arguments.tag}"
    shapes_output_path = Path("output") / f"{arguments.era}-{arguments.channel}-{arguments.ntupletag}-{arguments.tag}" / output_shapes_name
    shape_rootfile = f"{shapes_output_path}.root"

    logger.info(f"KINGMAKER_BASEDIR: {os.environ.get('KINGMAKER_BASEDIR', '')}")
    logger.info(f"BASEDIR: {os.environ.get('BASEDIR', '')}")
    logger.info(f"output_shapes: {output_shapes_name}")

    if arguments.mode == "XSEC":
        logger.info("Checking xsec friends directory", extra={"summary": True})
        logger.info("Running xsec friends script")
        logger.info(f"XSEC_FRIENDS: {xsec_friend}")

        xsec_command = f"""
            nice -n 19 python3 friends/build_friend_tree.py
            --basepath {os.environ['KINGMAKER_BASEDIR_XROOTD']}
            --outputpath root://cmsdcache-kit-disk.gridka.de/{xsec_friend}
            --dataset-config datasets/nanoAOD_{arguments.nanoaodversion}/datasets.json
            --nthreads 20
        """
        execute_bash_string(xsec_command, repository_root)

    elif arguments.mode == "SHAPES":
        logger.info(
            f"Producing {unit_kind} units for {arguments.channel}-{arguments.era}-{arguments.ntupletag}",
            extra={"summary": True},
        )
        (repository_root / shapes_output_path).parent.mkdir(parents=True, exist_ok=True)
        graph_filename = arguments.graph_filename or f"{arguments.channel}_{arguments.era}_{arguments.ntupletag}_{arguments.tag}.pkl"

        skip_sys_flag = "--skip-systematic-variations" if arguments.skip_systematic_variations else ""
        cache_flags = f"--locally --local-cache-workers {arguments.local_cache_workers}" if arguments.local_cache else ""

        cut_order_flags = ""
        if arguments.cut_order_cache_file:
            cut_order_flags += f" --cut-order-cache-file {shlex.quote(arguments.cut_order_cache_file)}"
        if arguments.discover_cut_ordering:
            cut_order_flags += " --discover-cut-ordering"
        if arguments.enable_cut_ordering:
            cut_order_flags += " --enable-cut-ordering"

        meta_flags = ""
        if arguments.shape_meta_mode == "only_create_graphs":
            meta_flags = f"--only-create-graphs --graph-filename {graph_filename}"
        elif arguments.shape_meta_mode == "gof_inputs":
            meta_flags = "--gof-inputs --do-2dGofs"
        elif arguments.shape_meta_mode == "collect_config_only":
            config_file = arguments.config_output_file or f"{arguments.channel}_{arguments.era}_{arguments.ntupletag}_{arguments.tag}.yaml"
            meta_flags = f"--collect-config-only --config-output-file {config_file}"
        elif arguments.shape_meta_mode == "run_splitted":
            meta_flags = "--run-splitted --incremental-hadd"

        control_plots_flag = ""
        if not arguments.analysis_units and not arguments.shape_meta_mode == "gof_inputs":
            control_plots_flag = "--control-plots"
        control_njet_split_flag = "--control-plots-njet-split" if arguments.control_plots_njet_split else ""
        control_dnn_split_flag = "--control-plots-dnn-split" if arguments.control_plots_dnn_split else ""
        control_plot_set_flag = f"--control-plot-set {used_variables}" if not arguments.analysis_units else ""

        shapes_command = f"""
            nice -n 19 python shapes/produce_shapes.py
            --channels {arguments.channel}
            --directory {os.environ['NTUPLES']}
            --{arguments.channel}-friend-directory {xsec_friend} {friends_string} {multifriends_string}
            --era {arguments.era}
            --num-processes 14
            --num-threads 60
            --optimization-level 2
            {control_plots_flag}
            {control_njet_split_flag}
            {control_dnn_split_flag}
            {control_plot_set_flag}
            --output-file {shapes_output_path}
            --xrootd {cache_flags}
            --validation-tag {arguments.tag}
            --vs-jet-wp Tight
            --vs-ele-wp VVLoose
            --apply-tauid
            --selection-option {arguments.selection_option}
            --ff-type {arguments.ff_type}
            {skip_sys_flag}
            {cut_order_flags}
            {meta_flags}
        """
        execute_bash_string(shapes_command, repository_root)

        # Graph Splitting Cleanup
        if arguments.shape_meta_mode == "only_create_graphs":
            logger.info("Graph splitting enabled.")
            execute_bash_string(f"bash split_graph_processing/run_split_graph_processing.sh {graph_filename} {shape_rootfile}", repository_root)

            try:
                user_answer = input("Graph processing finished. Clean up the temporary directories? ('tmp' and 'condor_jobs')? [y/N] ").strip().lower()
            except EOFError:
                user_answer = "n"

            if user_answer in ["y", "yes"]:
                with LogContext(logger).log_and_suppress(OSError, FileNotFoundError, msg="Failed to clean directories"):
                    shutil.rmtree(repository_root / "split_graph_processing/tmp", ignore_errors=True)
                    shutil.rmtree(repository_root / "split_graph_processing/condor_jobs", ignore_errors=True)
                logger.info("Cleanup completed")
            else:
                logger.info("Cleanup skipped")

        if not arguments.shape_meta_mode == "collect_config_only":
            # Estimations
            logger.info("Additional estimations", extra={"summary": True})
            if arguments.channel == "mm":
                execute_bash_string(f"nice -n 19 python shapes/do_estimations.py -e {arguments.era} -i {shape_rootfile} --do-qcd", repository_root)
            else:
                execute_bash_string(f"nice -n 19 python shapes/do_estimations.py -e {arguments.era} -i {shape_rootfile} --do-emb-tt --do-qcd --do-ff --selection-option {arguments.selection_option_estimation}", repository_root)

    elif arguments.mode == "PLOT":
        logger.info("Plotting", extra={"summary": True})

        category_flag = ""
        if arguments.plotcategory and arguments.plotcategory != "Nominal":
            category_flag = f"--category {arguments.plotcategory}"

        nll_path = "/work/amonsch/Documents/_M_Code/nll-training"
        current = os.environ.get("PYTHONPATH", "")
        paths = current.split(":") if current else []
        if nll_path not in paths:
            os.environ["PYTHONPATH"] = f"{current}:{nll_path}" if current else nll_path

        base_plot_cmd = f"""
            python3 plotting/plot_shapes_control_new.py
            --era Run{arguments.era}
            --input {shape_rootfile}
            --variables {used_variables}
            --channels {arguments.channel}
            --tag {arguments.tag}
            --selection-option {arguments.selection_option}
            --add-signals
            {category_flag}
        """

        plot_version = arguments.plotversion
        if plot_version in ["all", "emb+ff"]:
            execute_bash_string(f"{base_plot_cmd} --embedding --fake-factor", repository_root)
        # if plot_version in ["all", "emb+classic"]:
        #     execute_bash_string(f"{base_plot_cmd} --embedding", repository_root)
        # if plot_version in ["all", "classic+ff"]:
        #     execute_bash_string(f"{base_plot_cmd} --fake-factor", repository_root)
        # if plot_version in ["all", "classic+classic"]:
        #     execute_bash_string(base_plot_cmd, repository_root)


if __name__ == "__main__":
    setup_logging(logger=logger)
    main()
