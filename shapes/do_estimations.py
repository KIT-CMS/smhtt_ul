#!/usr/bin/env python3
import argparse
import logging
import json
import multiprocessing as mp
import os
import tempfile

import ROOT
from functools import partial

# import the estimation functions
from shapes.estimations.additionals import qqH_merge_estimation
from shapes.estimations.fakefactors import fake_factor_estimation
from shapes.estimations.qcd import qcd_estimation, abcd_estimation
from shapes.estimations.ttbar_emb import emb_ttbar_contamination_estimation
from config.logging_setup_configs import setup_logging, LogContext


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Input root file.")
    parser.add_argument("-e", "--era", required=True, help="Experiment era.")
    parser.add_argument(
        "--do-emb-tt",
        action="store_true",
        help="Add embedded ttbar contamination variation to file.",
    )
    parser.add_argument(
        "--do-ff",
        action="store_true",
        help="Add fake factor estimations to file.",
    )
    parser.add_argument(
        "--do-qcd",
        action="store_true",
        help="Add qcd estimations to file.",
    )
    parser.add_argument(
        "--do-qqh-procs",
        action="store_true",
        help="Add qqh procs estimations to file.",
    )
    parser.add_argument(
        "--selection-option",
        help="Set to the DR used for the fake factor estimation.",
        choices=["CR", "DR;ff;wjet", "DR;ff;qcd", "DR;ff;ttbar"],
        default="CR",
    )
    parser.add_argument("-s", "--special", help="Special selection.", default="")
    parser.add_argument(
            "--num-processes",
            type=int,
            default=max(1, min(8, os.cpu_count() or 1)),
            help="Number of worker processes used for per-variable estimation tasks.",
        )
    return parser.parse_args()


def _extract_data_categories(inputfile):
    categories = set()
    for key in inputfile.GetListOfKeys():
        dataset, selection, variation, _variable = key.GetName().split("#")
        if "data" not in dataset:
            continue
        sel_split = selection.split("-", maxsplit=1)
        if len(sel_split) > 1 and sel_split[1]:
            categories.add(sel_split[1])
    return sorted(categories, key=len, reverse=True)


def _split_selection(selection, known_categories):
    sel_split = selection.split("-", maxsplit=1)
    channel = sel_split[0]
    if len(sel_split) == 1:
        return channel, "", ""

    process_and_maybe_category = sel_split[1]
    for category in known_categories:
        if process_and_maybe_category == category:
            return channel, "", category
        category_suffix = f"-{category}"
        if process_and_maybe_category.endswith(category_suffix):
            process = process_and_maybe_category[: -len(category_suffix)]
            return channel, process, category

    return channel, process_and_maybe_category, ""


def parse_process_name(name, variation_key, known_categories=None):
    logger.debug("Processing histogram %s", name.GetName())
    dataset, selection, variation, variable = name.GetName().split("#")
    if variation_key not in variation:
        return None, None, None, None, None

    if known_categories is None:
        known_categories = []

    channel, process, category = _split_selection(selection, known_categories)

    # Data selections are channel[-category] only.
    if "data" in dataset:
        process = "data"
    elif process == "" and category != "":
        # Conservative fallback: avoid dropping process information when category matching is ambiguous.
        process = category
        category = ""

    return channel, category, variable, variation, process

def add_input_to_inputdict(input_dict, channel, category, variable, variation, process):
    if channel not in input_dict:
        input_dict[channel] = {category: {variable: {variation: [process]}}}
    if category not in input_dict[channel]:
        input_dict[channel][category] = {variable: {variation: [process]}}
    if variable not in input_dict[channel][category]:
        input_dict[channel][category][variable] = {variation: [process]}
    if variation not in input_dict[channel][category][variable]:
        input_dict[channel][category][variable][variation] = [process]
    if variation in input_dict[channel][category][variable]:
        input_dict[channel][category][variable][variation].append(process)


def parse_histograms_for_ff(inputfile):
    ff_inputs = {}
    available_variations = set()
    known_categories = _extract_data_categories(inputfile)
    for key in inputfile.GetListOfKeys():
        channel, category, variable, variation, process = parse_process_name(
            key, "anti_iso", known_categories=known_categories
        )
        if variation is not None:
            available_variations.add(variation)
        if channel is not None:
            if not variation.startswith("abcd"):
                add_input_to_inputdict(
                    ff_inputs, channel, category, variable, variation, process
                )
    logger.debug(available_variations)
    return ff_inputs


def parse_histograms_for_qcd(inputfile):
    qcd_inputs = {}
    known_categories = _extract_data_categories(inputfile)
    for key in inputfile.GetListOfKeys():
        channel, category, variable, variation, process = parse_process_name(
            key, "same_sign", known_categories=known_categories
        )
        if channel is not None:
            if (
                channel in ["et", "mt", "em", "tt", "mm", "ee"]
                or "abcd_same_sign_anti_iso" in variation
            ):
                add_input_to_inputdict(
                    qcd_inputs, channel, category, variable, variation, process
                )
    return qcd_inputs


def parse_histograms_for_emb_estimation(inputfile):
    emb_categories = {}
    for key in inputfile.GetListOfKeys():
        dataset, selection, variation, variable = key.GetName().split("#")
        if "Nominal" in variation:
            sel_split = selection.split("-", maxsplit=1)
            if "EMB" in dataset or ("emb" in dataset and "jetFakes" not in dataset):
                channel = sel_split[0]
                category = sel_split[1].replace("Embedded", "").strip("-")
                if channel in emb_categories:
                    if category in emb_categories[channel]:
                        emb_categories[channel][category].append(variable)
                    else:
                        emb_categories[channel][category] = [variable]
                else:
                    emb_categories[channel] = {category: [variable]}
    return emb_categories


def parse_histograms_for_qqh(inputfile):
    qqh_procs = {}
    known_categories = _extract_data_categories(inputfile)
    for key in inputfile.GetListOfKeys():
        dataset, selection, variation, variable = key.GetName().split("#")
        if dataset in ["qqH", "ZH", "WH"] and not variation.startswith("THU"):
            channel, process, category = _split_selection(selection, known_categories)

            if "data" in dataset:
                process = "data"

            if category == "":
                continue
            add_input_to_inputdict(
                qqh_procs, channel, category, variable, variation, process
            )
    return qqh_procs

def _open_root_file(path, mode):
    root_file = ROOT.TFile(path, mode)
    if root_file is None or root_file.IsZombie():
        raise OSError(f"Failed to open ROOT file {path} with mode {mode}")
    return root_file


def _qcd_extrapolation_factor(channel, category, era):
    extrapolation_factor = 1.0
    if channel in ["et", "mt"] and era == "2016":
        extrapolation_factor = 1.17
    elif channel in ["em"]:
        if "NbtagGt1" in category:
            if "2016" in era:
                extrapolation_factor = 0.71
            elif era == "2017":
                extrapolation_factor = 0.69
            elif era == "2018":
                extrapolation_factor = 0.67
            else:
                logger.warning(
                    "No correction for given era %s available. Setting extrapolation factor to 1.0",
                    era,
                )
                extrapolation_factor = 1.0
    elif channel in ["tt"]:
        extrapolation_factor = 1.5  # 1.37
    return extrapolation_factor


def _build_qcd_tasks(qcd_inputs, era):
    tasks = []
    for channel in qcd_inputs:
        for category in qcd_inputs[channel]:
            logger.info("Do estimation for category %s", category)
            extrapolation_factor = _qcd_extrapolation_factor(channel, category, era)
            for var in qcd_inputs[channel][category]:
                tasks.append(
                    {
                        "channel": channel,
                        "category": category,
                        "variable": var,
                        "variations": list(qcd_inputs[channel][category][var].keys()),
                        "extrapolation_factor": extrapolation_factor,
                    }
                )
    return tasks


def _build_emb_tt_tasks(emb_categories, special, eleES_names):
    tasks = []
    for channel in emb_categories:
        for category in emb_categories[channel]:
            logger.info("Do estimation for category %s", category)
            variables = emb_categories[channel][category]
            if special == "EleES":
                if not variables:
                    continue
                tasks.append(
                    {
                        "channel": channel,
                        "category": category,
                        "variable": variables[0],
                        "emb_signals": list(eleES_names),
                        "special": special,
                    }
                )
            else:
                for var in variables:
                    tasks.append(
                        {
                            "channel": channel,
                            "category": category,
                            "variable": var,
                            "special": special,
                        }
                    )
    return tasks


def _build_ff_tasks(ff_inputs, selection_option):
    tasks = []
    for channel in ff_inputs:
        for category in ff_inputs[channel]:
            logger.info("Do estimation for category %s", category)
            for variable in ff_inputs[channel][category]:
                tasks.append(
                    {
                        "channel": channel,
                        "category": category,
                        "variable": variable,
                        "variations": list(ff_inputs[channel][category][variable].keys()),
                        "selection_option": selection_option,
                    }
                )
    return tasks


def _write_histograms_to_temp_file(output_file, histograms):
    out_file = _open_root_file(output_file, "RECREATE")
    try:
        out_file.cd()
        for histogram in histograms:
            histogram.Write()
    finally:
        out_file.Close()


def _run_qcd_task(task):
    input_file = _open_root_file(task["input_file"], "READ")
    histograms = []
    try:
        common_kwargs = dict(
            rootfile=input_file,
            channel=task["channel"],
            selection=task["category"],
            variable=task["variable"],
        )
        for variation in task["variations"]:
            if task["channel"] in ["et", "mt", "em", "mm", "ee", "tt"]:
                for use_emb in [False, False]:
                    for use_nlo in [False]:
                        histograms.append(
                            qcd_estimation(
                                **common_kwargs,
                                variation=variation,
                                is_embedding=use_emb,
                                is_nlo=use_nlo,
                                extrapolation_factor=task["extrapolation_factor"],
                            )
                        )
            else:
                for use_emb in [False, False]:
                    histograms.append(
                        abcd_estimation(
                            **common_kwargs,
                            variation=variation,
                            is_embedding=use_emb,
                        )
                    )
        if task["channel"] in ["em"]:
            for variation, scale in zip(["subtrMCUp", "subtrMCDown"], [0.8, 1.2]):
                for use_emb in [False, False]:
                    histograms.append(
                        qcd_estimation(
                            **common_kwargs,
                            variation=variation,
                            is_embedding=use_emb,
                            extrapolation_factor=task["extrapolation_factor"],
                            sub_scale=scale,
                        )
                    )

        _write_histograms_to_temp_file(task["temp_output"], histograms)
        return {
            "task_index": task["task_index"],
            "temp_output": task["temp_output"],
            "hist_count": len(histograms),
        }
    finally:
        input_file.Close()


def _run_emb_tt_task(task):
    input_file = _open_root_file(task["input_file"], "READ")
    histograms = []
    try:
        if task["special"] == "EleES":
            for emb_signal in task["emb_signals"]:
                histograms.append(
                    emb_ttbar_contamination_estimation(
                        input_file,
                        task["channel"],
                        task["category"],
                        task["variable"],
                        sub_scale=0.1,
                        embname=emb_signal,
                    )
                )
                histograms.append(
                    emb_ttbar_contamination_estimation(
                        input_file,
                        task["channel"],
                        task["category"],
                        task["variable"],
                        sub_scale=-0.1,
                        embname=emb_signal,
                    )
                )
        else:
            histograms.append(
                emb_ttbar_contamination_estimation(
                    input_file,
                    task["channel"],
                    task["category"],
                    task["variable"],
                    sub_scale=0.1,
                    embname="EMB",
                )
            )
            histograms.append(
                emb_ttbar_contamination_estimation(
                    input_file,
                    task["channel"],
                    task["category"],
                    task["variable"],
                    sub_scale=-0.1,
                    embname="EMB",
                )
            )

        _write_histograms_to_temp_file(task["temp_output"], histograms)
        return {
            "task_index": task["task_index"],
            "temp_output": task["temp_output"],
            "hist_count": len(histograms),
        }
    finally:
        input_file.Close()


def _run_ff_task(task):
    input_file = _open_root_file(task["input_file"], "READ")
    histograms = []
    try:
        _fake_factor_estimation = partial(
            fake_factor_estimation,
            rootfile=input_file,
            channel=task["channel"],
            selection=task["category"],
            variable=task["variable"],
            selection_option=task["selection_option"],
        )

        for variation in task["variations"]:
            if "same_sign_anti_iso" in variation:
                continue

            histograms.append(_fake_factor_estimation(variation=variation))
            histograms.append(_fake_factor_estimation(variation=variation, is_embedding=False))

            for ff_variation, scale in zip(
                [
                    "CMS_ff_total_sub_syst_Channel_EraUp",
                    "CMS_ff_total_sub_syst_Channel_EraDown",
                ],
                [0.9, 1.1],
            ):
                histograms.append(
                    _fake_factor_estimation(
                        variation=ff_variation,
                        sub_scale=scale,
                    )
                )
                histograms.append(
                    _fake_factor_estimation(
                        variation=ff_variation,
                        is_embedding=False,
                        sub_scale=scale,
                    )
                )

        _write_histograms_to_temp_file(task["temp_output"], histograms)
        return {
            "task_index": task["task_index"],
            "temp_output": task["temp_output"],
            "hist_count": len(histograms),
        }
    finally:
        input_file.Close()


def _merge_temp_outputs(target_file, stage_results):
    output_file = _open_root_file(target_file, "UPDATE")
    try:
        for result in sorted(stage_results, key=lambda item: item["task_index"]):
            temp_file = _open_root_file(result["temp_output"], "READ")
            try:
                for key in temp_file.GetListOfKeys():
                    obj = key.ReadObj()
                    output_file.cd()
                    obj.Write(obj.GetName(), ROOT.TObject.kOverwrite)
            finally:
                temp_file.Close()
    finally:
        output_file.Close()


def _run_parallel_stage(stage_name, tasks, worker_fn, input_file, num_processes):
    if not tasks:
        logger.info("No %s tasks to process.", stage_name)
        return

    if num_processes < 1:
        raise ValueError("--num-processes has to be larger zero")

    nworkers = min(num_processes, len(tasks))
    logger.info(
        "Running %s stage with %d task(s) using %d worker process(es).",
        stage_name,
        len(tasks),
        nworkers,
    )

    with tempfile.TemporaryDirectory(prefix=f"do_estimations_{stage_name}_") as temp_dir:
        stage_tasks = []
        for task_index, task in enumerate(tasks):
            staged = dict(task)
            staged["task_index"] = task_index
            staged["input_file"] = input_file
            staged["temp_output"] = os.path.join(temp_dir, f"{stage_name}_{task_index}.root")
            stage_tasks.append(staged)

        if nworkers == 1:
            stage_results = [worker_fn(task) for task in stage_tasks]
        else:
            with mp.Pool(processes=nworkers) as pool:
                stage_results = list(pool.imap_unordered(worker_fn, stage_tasks))

        _merge_temp_outputs(input_file, stage_results)

    logger.info(
        "Finished %s stage and wrote %d histogram(s).",
        stage_name,
        sum(result["hist_count"] for result in stage_results),
    )

def main(args):
    logger.info("Reading inputs from file {}".format(args.input))
    eleES_names = []
    if args.special == "EleES":
        # we have to extend the _dataset_map and the _process_map to include the TauES variations
        eleESvariations = [-1.5 + 0.05 * i for i in range(0, 51)]
        for variation in eleESvariations:
            name = str(round(variation, 2)).replace("-", "minus").replace(".", "p")
            processname = f"emb{name}"
            eleES_names.append(processname)

    if args.do_qcd:
        input_file = _open_root_file(args.input, "READ")
        try:
            qcd_inputs = parse_histograms_for_qcd(input_file)
        finally:
            input_file.Close()

        logger.info("Starting estimations for the QCD mulitjet process.")
        logger.debug("%s", json.dumps(qcd_inputs, sort_keys=True, indent=4))
        qcd_tasks = _build_qcd_tasks(qcd_inputs, args.era)
        _run_parallel_stage(
            stage_name="qcd",
            tasks=qcd_tasks,
            worker_fn=_run_qcd_task,
            input_file=args.input,
            num_processes=args.num_processes,
        )

    if args.do_qqh_procs:
        input_file = _open_root_file(args.input, "UPDATE")
        try:
            qqh_procs = parse_histograms_for_qqh(input_file)
            logger.info("Starting adding for qqH and VH processes.")
            logger.debug("%s", json.dumps(qqh_procs, sort_keys=True, indent=4))
            for channel in qqh_procs:
                for category in qqh_procs[channel]:
                    if "MTGt70" in category:
                        continue
                    logger.info("Do estimation for category %s", category)
                    for var in qqh_procs[channel][category]:
                        for variation in qqh_procs[channel][category][var]:
                            estimated_hist = qqH_merge_estimation(
                                input_file, channel, category, var, variation=variation
                            )
                            estimated_hist.Write()
        finally:
            input_file.Close()

    if args.do_emb_tt:
        input_file = _open_root_file(args.input, "READ")
        try:
            emb_categories = parse_histograms_for_emb_estimation(input_file)
        finally:
            input_file.Close()

        logger.info("Producing embedding ttbar variations.")
        logger.debug("%s", json.dumps(emb_categories, sort_keys=True, indent=4))
        emb_tasks = _build_emb_tt_tasks(emb_categories, args.special, eleES_names)
        _run_parallel_stage(
            stage_name="emb_tt",
            tasks=emb_tasks,
            worker_fn=_run_emb_tt_task,
            input_file=args.input,
            num_processes=args.num_processes,
        )

    if args.do_ff:
        logger.info("Starting estimations for fake factors and their variations")
        input_file = _open_root_file(args.input, "READ")
        try:
            ff_inputs = parse_histograms_for_ff(input_file)
        finally:
            input_file.Close()

        logger.debug("%s", json.dumps(ff_inputs, sort_keys=True, indent=4))
        ff_tasks = _build_ff_tasks(ff_inputs, args.selection_option)
        with LogContext(logger).duplicate_filter():
            _run_parallel_stage(
                stage_name="ff",
                tasks=ff_tasks,
                worker_fn=_run_ff_task,
                input_file=args.input,
                num_processes=args.num_processes,
            )

    logger.info("Successfully finished estimations.")
    return


if __name__ == "__main__":
    args = parse_args()
    logger = setup_logging(logger=logging.getLogger(__name__))
    main(args)
