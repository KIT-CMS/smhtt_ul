#!/usr/bin/env python3
import argparse
import logging
import json

import ROOT

# import the estimation functions
from shapes.estimations.additionals import qqH_merge_estimation
from shapes.estimations.fakefactors import fake_factor_estimation
from shapes.estimations.qcd import qcd_estimation, abcd_estimation
from shapes.estimations.ttbar_emb import emb_ttbar_contamination_estimation
from shapes.estimations.wfakes import wfakes_estimation


logger = logging.getLogger("")


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
        "--do-wfakes",
        action="store_true",
        help="Add wfakes estimations to file.",
    )
    parser.add_argument(
        "--do-qqh-procs",
        action="store_true",
        help="Add qqh procs estimations to file.",
    )
    parser.add_argument("-s", "--special", help="Special selection.", default="")
    return parser.parse_args()


def setup_logging(output_file, level=logging.INFO):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return


def parse_process_name(name, variation_key):
    logger.debug("Processing histogram %s", name.GetName())
    dataset, selection, variation, variable = name.GetName().split("#")
    if variation_key in variation:
        sel_split = selection.split("-", maxsplit=1)
        # Set category to default since not present in control plots.
        category = ""
        # Treat data hists seperately because only channel selection is applied to data.
        if "data" in dataset:
            channel = sel_split[0]
            # Set category label for analysis categories.
            if len(sel_split) > 1:
                category = sel_split[1]
            process = "data"
        else:
            channel = sel_split[0]
            #  Check if analysis category present in root file.
            if (
                len(sel_split[1].split("-")) > 2
                or ("Embedded" in sel_split[1] and len(sel_split[1].split("-")) > 1)
                or ("W" in sel_split[1] and len(sel_split[1].split("-")) > 1)
                or ("H125" in sel_split[1] and len(sel_split[1].split("-")) > 1)
                or ("qqHComb125" in sel_split[1])
            ):
                process = "-".join(sel_split[1].split("-")[:-1])
                category = sel_split[1].split("-")[-1]
            else:
                # Set only process if no categorization applied.
                process = sel_split[1]
        return channel, category, variable, variation, process
    else:
        return None, None, None, None, None


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
    for key in inputfile.GetListOfKeys():
        channel, category, variable, variation, process = parse_process_name(
            key, "anti_iso"
        )
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
    for key in inputfile.GetListOfKeys():
        channel, category, variable, variation, process = parse_process_name(
            key, "same_sign"
        )
        if channel is not None:
            if (
                channel in ["et", "mt", "em", "mm", "ee"]
                or "abcd_same_sign_anti_iso" in variation
            ):
                add_input_to_inputdict(
                    qcd_inputs, channel, category, variable, variation, process
                )
    return qcd_inputs


def parse_histograms_for_wfakes(inputfile):
    wfakes_inputs = {}
    for key in inputfile.GetListOfKeys():
        channel, category, variable, variation, process = parse_process_name(
            key, "wfakes"
        )
        if channel is not None:
            add_input_to_inputdict(
                wfakes_inputs, channel, category, variable, variation, process
            )
    return wfakes_inputs


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
    for key in inputfile.GetListOfKeys():
        dataset, selection, variation, variable = key.GetName().split("#")
        if dataset in ["qqH", "ZH", "WH"] and not variation.startswith("THU"):
            sel_split = selection.split("-", maxsplit=1)
            # Set category to default since not present in control plots.
            category = ""
            # Treat data hists seperately because only channel selection is applied to data.
            if "data" in dataset:
                channel = sel_split[0]
                # Set category label for analysis categories.
                if len(sel_split) > 1:
                    category = sel_split[1]
                process = "data"
            else:
                channel = sel_split[0]
                #  Check if analysis category present in root file.
                if (
                    len(sel_split[1].split("-")) > 2
                    or ("Embedded" in sel_split[1] and len(sel_split[1].split("-")) > 1)
                    or ("W" in sel_split[1] and len(sel_split[1].split("-")) > 1)
                    or ("H125" in sel_split[1] and len(sel_split[1].split("-")) > 1)
                    or ("qqHComb125" in sel_split[1])
                ):
                    process = "-".join(sel_split[1].split("-")[:-1])
                    category = sel_split[1].split("-")[-1]
                else:
                    # Set only process if no categorization applied.
                    process = sel_split[1]
            if category == "":
                continue
            add_input_to_inputdict(
                qqh_procs, channel, category, variable, variation, process
            )
    return qqh_procs


def main(args):
    input_file = ROOT.TFile(args.input, "update")
    logger.info("Reading inputs from file {}".format(args.input))
    tauES_names = []
    eleES_names = []
    if args.special == "TauES":
        # we have to extend the _dataset_map and the _process_map to include the TauES variations
        tauESvariations = [-2.5 + 0.1 * i for i in range(0, 52)]
        for variation in tauESvariations:
            name = str(round(variation, 2)).replace("-", "minus").replace(".", "p")
            processname = f"emb{name}"
            tauES_names.append(processname)
    elif args.special == "EleES":
        # we have to extend the _dataset_map and the _process_map to include the TauES variations
        eleESvariations = [-1.5 + 0.05 * i for i in range(0, 51)]
        for variation in eleESvariations:
            name = str(round(variation, 2)).replace("-", "minus").replace(".", "p")
            processname = f"emb{name}"
            eleES_names.append(processname)
    # Loop over available ff inputs and do the estimations
    if args.do_ff:
        logger.info("Starting estimations for fake factors and their variations")
        ff_inputs = parse_histograms_for_ff(input_file)
        logger.debug("%s", json.dumps(ff_inputs, sort_keys=True, indent=4))
        for ch in ff_inputs:
            for cat in ff_inputs[ch]:
                logger.info("Do estimation for category %s", cat)
                for var in ff_inputs[ch][cat]:
                    for variation in ff_inputs[ch][cat][var]:
                        estimated_hist = fake_factor_estimation(
                            input_file, ch, cat, var, variation=variation
                        )
                        estimated_hist.Write()
                        estimated_hist = fake_factor_estimation(
                            input_file,
                            ch,
                            cat,
                            var,
                            variation=variation,
                            is_embedding=False,
                        )
                        estimated_hist.Write()
                        for variation, scale in zip(
                            [
                                "CMS_ff_total_sub_syst_Channel_EraUp",
                                "CMS_ff_total_sub_syst_Channel_EraDown",
                            ],
                            [0.9, 1.1],
                        ):
                            estimated_hist = fake_factor_estimation(
                                input_file,
                                ch,
                                cat,
                                var,
                                variation=variation,
                                sub_scale=scale,
                            )
                            estimated_hist.Write()
                            estimated_hist = fake_factor_estimation(
                                input_file,
                                ch,
                                cat,
                                var,
                                variation=variation,
                                is_embedding=False,
                                sub_scale=scale,
                            )
                            estimated_hist.Write()
    if args.do_qcd:
        qcd_inputs = parse_histograms_for_qcd(input_file)
        logger.info("Starting estimations for the QCD mulitjet process.")
        logger.debug("%s", json.dumps(qcd_inputs, sort_keys=True, indent=4))
        for channel in qcd_inputs:
            for category in qcd_inputs[channel]:
                logger.info("Do estimation for category %s", category)
                extrapolation_factor = 1.25
                if channel in ["et", "mt"] and args.era == "2016":
                    extrapolation_factor = 1.17
                elif channel in ["em"]:
                    if "NbtagGt1" in category:
                        if "2016" in args.era:
                            extrapolation_factor = 0.71
                        elif args.era == "2017":
                            extrapolation_factor = 0.69
                        elif args.era == "2018":
                            extrapolation_factor = 0.67
                        else:
                            logger.warning(
                                "No correction for given era %s available. "
                                "Setting extrapolation factor to 1.0",
                                args.era,
                            )
                            extrapolation_factor = 1.0
                for var in qcd_inputs[channel][category]:
                    for variation in qcd_inputs[channel][category][var]:
                        if channel in ["et", "mt", "em", "mm", "ee"]:
                            for use_emb in [True, False]:
                                for use_nlo in [False]:
                                    estimated_hist = qcd_estimation(
                                        input_file,
                                        channel,
                                        category,
                                        var,
                                        variation=variation,
                                        is_embedding=use_emb,
                                        is_nlo=use_nlo,
                                        extrapolation_factor=extrapolation_factor,
                                    )
                                    estimated_hist.Write()
                        else:
                            for use_emb in [True, False]:
                                estimated_hist = abcd_estimation(
                                    input_file,
                                    channel,
                                    category,
                                    var,
                                    variation=variation,
                                    is_embedding=use_emb,
                                )
                                estimated_hist.Write()
                    if channel in ["em"]:
                        for variation, scale in zip(
                            ["subtrMCUp", "subtrMCDown"], [0.8, 1.2]
                        ):
                            for use_emb in [True, False]:
                                estimated_hist = qcd_estimation(
                                    input_file,
                                    channel,
                                    category,
                                    var,
                                    variation=variation,
                                    is_embedding=use_emb,
                                    extrapolation_factor=extrapolation_factor,
                                    sub_scale=scale,
                                )
                                estimated_hist.Write()
    if args.do_wfakes:
        wfakes_inputs = parse_histograms_for_wfakes(input_file)
        logger.info("Starting estimations for wfakes")
        logger.debug("%s", json.dumps(wfakes_inputs, sort_keys=True, indent=4))
        for channel in wfakes_inputs:
            for category in wfakes_inputs[channel]:
                logger.info("Do estimation for category %s", category)
                for var in wfakes_inputs[channel][category]:
                    for variation in wfakes_inputs[channel][category][var]:
                        estimated_hist = wfakes_estimation(
                            input_file, channel, category, var, variation=variation
                        )
                        estimated_hist.Write()
    if args.do_qqh_procs:
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

    if args.do_emb_tt:
        emb_categories = parse_histograms_for_emb_estimation(input_file)
        logger.info("Producing embedding ttbar variations.")
        logger.debug("%s", json.dumps(emb_categories, sort_keys=True, indent=4))
        for channel in emb_categories:
            for category in emb_categories[channel]:
                logger.info("Do estimation for category %s", category)
                if args.special == "EleES":
                    for embsignal in eleES_names:
                        print(embsignal)
                        var = emb_categories[channel][category][0]
                        estimated_hist = emb_ttbar_contamination_estimation(
                            input_file,
                            channel,
                            category,
                            var,
                            sub_scale=0.1,
                            embname=embsignal,
                        )
                        estimated_hist.Write()
                        estimated_hist = emb_ttbar_contamination_estimation(
                            input_file,
                            channel,
                            category,
                            var,
                            sub_scale=-0.1,
                            embname=embsignal,
                        )
                        estimated_hist.Write()
                else:
                    for var in emb_categories[channel][category]:
                        estimated_hist = emb_ttbar_contamination_estimation(
                            input_file,
                            channel,
                            category,
                            var,
                            sub_scale=0.1,
                            embname="EMB",
                        )
                        estimated_hist.Write()
                        estimated_hist = emb_ttbar_contamination_estimation(
                            input_file,
                            channel,
                            category,
                            var,
                            sub_scale=-0.1,
                            embname="EMB",
                        )
                        estimated_hist.Write()

    logger.info("Successfully finished estimations.")
    # Clean-up.
    input_file.Close()
    return


if __name__ == "__main__":
    args = parse_args()
    setup_logging("do_estimations.log", level=logging.DEBUG)
    main(args)
