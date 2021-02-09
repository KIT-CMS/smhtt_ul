#!/usr/bin/env python3
import argparse
import logging
import json

import ROOT


logger = logging.getLogger("")

_dataset_map = {
    "data": "data",
    "ZTT": "DY",
    "ZL": "DY",
    "ZJ": "DY",
    "TTT": "TT",
    "TTL": "TT",
    "TTJ": "TT",
    "VVT": "VV",
    "VVL": "VV",
    "VVJ": "VV",
    "EMB": "EMB",
    "W": "W",
}

_process_map = {
    "data": "data",
    "ZTT": "DY-ZTT",
    "ZL": "DY-ZL",
    "ZJ": "DY-ZJ",
    "TTT": "TT-TTT",
    "TTL": "TT-TTL",
    "TTJ": "TT-TTJ",
    "VVT": "VV-VVT",
    "VVL": "VV-VVL",
    "VVJ": "VV-VVJ",
    "EMB": "Embedded",
    "W": "W",
}

_name_string = "{dataset}#{channel}{process}{selection}#{variation}#{variable}"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Input root file.")
    parser.add_argument("-e", "--era", required=True, help="Experiment era.")
    parser.add_argument("--emb-tt", action="store_true",
                        help="Add embedded ttbar contamination variation to file.")
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


def replace_negative_entries_and_renormalize(histogram, tolerance):
    # This function is taken from https://github.com/KIT-CMS/shape-producer/blob/beddc4a43e2e326018d804e58d612d8688ec33b6/shape_producer/histogram.py#L189

    # Find negative entries and calculate norm.
    norm_all = 0.0
    norm_positive = 0.0
    for i_bin in range(1, histogram.GetNbinsX() + 1):
        this_bin = histogram.GetBinContent(i_bin)
        if this_bin < 0.0:
            histogram.SetBinContent(i_bin, 0.0)
        else:
            norm_positive += this_bin
        norm_all += this_bin

    if norm_all == 0.0 and norm_positive != 0.0:
        logger.fatal(
            "Aborted renormalization because initial normalization is zero, but positive normalization not. . Check histogram %s",
            histogram.GetName() )
        raise Exception

    if norm_all < 0.0:
        logger.fatal(
            "Aborted renormalization because initial normalization is negative: %f. Check histogram %s ",
            norm_all, histogram.GetName())
        raise Exception

    if abs(norm_all - norm_positive) > tolerance * norm_all:
        logger.warning(
            "Renormalization failed because the normalization changed by %f, which is above the tolerance %f. Check histogram %s",
            abs(norm_all - norm_positive), tolerance * norm_all, histogram.GetName())

    # Renormalize histogram if negative entries are found
    if norm_all != norm_positive:
        if norm_positive == 0.0:
            logger.fatal(
                "Renormalization failed because all bins have negative entries."
            )
            raise Exception
        for i_bin in range(1, histogram.GetNbinsX() + 1):
            this_bin = histogram.GetBinContent(i_bin)
            histogram.SetBinContent(i_bin,
                                       this_bin * norm_all / norm_positive)

    return histogram


def fake_factor_estimation(rootfile, channel, selection, variable, variation="Nominal", is_embedding=True):
    if is_embedding:
        procs_to_subtract = ["EMB", "ZL", "TTL", "VVL"]
    else:
        procs_to_subtract = ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL"]
    logger.debug("Trying to get object {}".format(
                            _name_string.format(dataset="data",
                                                channel=channel,
                                                process="",
                                                selection="-" + selection if selection != "" else "",
                                                variation=variation,
                                                variable=variable)))
    base_hist = rootfile.Get(_name_string.format(
                                dataset="data",
                                channel=channel,
                                process="",
                                selection="-" + selection if selection != "" else "",
                                variation=variation,
                                variable=variable
        )).Clone()
    for proc in procs_to_subtract:
        logger.debug("Trying to get object {}".format(
                            _name_string.format(dataset=_dataset_map[proc],
                                                channel=channel,
                                                process="-" + _process_map[proc],
                                                selection="-" + selection if selection != "" else "",
                                                variation=variation,
                                                variable=variable)))
        base_hist.Add(rootfile.Get(_name_string.format(
                                        dataset=_dataset_map[proc],
                                        channel=channel,
                                        process="-" + _process_map[proc],
                                        selection="-" + selection if selection !="" else "",
                                        variation=variation,
                                        variable=variable)), -1.0)
    proc_name = "jetFakes" if is_embedding else "jetFakesMC"
    if variation in ["anti_iso"]:
        ff_variation = "Nominal"
    else:
        ff_variation = variation.replace("anti_iso_", "")
    variation_name = base_hist.GetName().replace("data", proc_name) \
                                        .replace(variation, ff_variation) \
                                        .replace("#" + channel, "#" + "-".join([channel, proc_name]), 1)
    base_hist.SetName(variation_name)
    base_hist.SetTitle(variation_name)
    return base_hist


def qcd_estimation(rootfile, channel, selection, variable, variation="Nominal", is_embedding=True,
                   extrapolation_factor=1.):
    if is_embedding:
        procs_to_subtract = ["EMB", "ZL", "ZJ", "TTL", "TTJ", "VVL", "VVJ", "W"]
        if "em" in channel:
            procs_to_subtract = ["EMB", "ZL", "TTL", "VVL", "W"]
    else:
        procs_to_subtract = ["ZTT", "ZL", "ZJ", "TTT", "TTL", "TTJ", "VVT", "VVL", "VVJ", "W"]
        if "em" in channel:
            procs_to_subtract = ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL", "W"]

    logger.debug("Trying to get object {}".format(
                                    _name_string.format(dataset="data",
                                                        channel=channel,
                                                        process="",
                                                        selection="-" + selection if selection != "" else "",
                                                        variation=variation,
                                                        variable=variable)))
    base_hist = rootfile.Get(_name_string.format(
                                dataset="data",
                                channel=channel,
                                process="",
                                selection="-" + selection if selection != "" else "",
                                variation=variation,
                                variable=variable
        )).Clone()
    for proc in procs_to_subtract:
        logger.debug("Trying to get object {}".format(
                                    _name_string.format(dataset=_dataset_map[proc],
                                                        channel=channel,
                                                        process="-" + _process_map[proc],
                                                        selection="-" + selection if selection != "" else "",
                                                        variation=variation,
                                                        variable=variable)))
        base_hist.Add(rootfile.Get(_name_string.format(
                                        dataset=_dataset_map[proc],
                                        channel=channel,
                                        process="-" + _process_map[proc],
                                        selection="-" + selection if selection != "" else "",
                                        variation=variation,
                                        variable=variable)), -1.0)

    proc_name = "QCD" if is_embedding else "QCDMC"
    if variation in ["same_sign"]:
        qcd_variation = "Nominal"
    else:
        qcd_variation = variation.replace("same_sign_", "")
    logger.debug("Use extrapolation_factor factor with value %.2f to scale from ss to os region.",
                  extrapolation_factor)
    if base_hist.Integral() > 0.0:
        base_hist.Scale(extrapolation_factor)
    else:
        logger.warning("No data in same-sign region for histogram %s. Setting extrapolation factor to 0.0",
                       base_hist.GetName())
        base_hist.Scale(0.0)
    variation_name = base_hist.GetName().replace("data", proc_name) \
                                        .replace(variation, qcd_variation) \
                                        .replace(channel, "-".join([channel, proc_name]), 1)
    base_hist.SetName(variation_name)
    base_hist.SetTitle(variation_name)
    replace_negative_entries_and_renormalize(base_hist, tolerance=100.05)
    return base_hist


def abcd_estimation(rootfile, channel, selection, variable,
                    variation="Nominal", is_embedding=True, transposed=False):
    if is_embedding:
        procs_to_subtract = ["EMB", "ZL", "ZJ", "TTL", "TTJ", "VVL", "VVJ", "W"]
        if "em" in channel:
            procs_to_subtract = ["EMB", "ZL", "TTL", "VVL", "W"]
    else:
        procs_to_subtract = ["ZTT", "ZL", "ZJ", "TTT", "TTL", "TTJ", "VVT", "VVL", "VVJ", "W"]
        if "em" in channel:
            procs_to_subtract = ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL", "W"]

    # Get the shapes from region B.
    logger.debug("Trying to get object {}".format(
                                    _name_string.format(dataset="data",
                                                        channel=channel,
                                                        process="",
                                                        selection="-" + selection if selection != "" else "",
                                                        variation=variation.replace("same_sign_anti_iso", "same_sign") if transposed else variation.replace("same_sign_anti_iso", "anti_iso"),
                                                        variable=variable)))
    base_hist = rootfile.Get(_name_string.format(
                                dataset="data",
                                channel=channel,
                                process="",
                                selection="-" + selection if selection != "" else "",
                                variation=variation.replace("same_sign_anti_iso", "same_sign") if transposed else variation.replace("same_sign_anti_iso", "anti_iso"),
                                variable=variable
        )).Clone()
    for proc in procs_to_subtract:
        logger.debug("Trying to get object {}".format(
                                    _name_string.format(dataset=_dataset_map[proc],
                                                        channel=channel,
                                                        process="-" + _process_map[proc],
                                                        selection="-" + selection if selection != "" else "",
                                                        variation=variation.replace("same_sign_anti_iso", "same_sign") if transposed else variation.replace("same_sign_anti_iso", "anti_iso"),
                                                        variable=variable)))
        base_hist.Add(rootfile.Get(_name_string.format(
                                        dataset=_dataset_map[proc],
                                        channel=channel,
                                        process="-" + _process_map[proc],
                                        selection="-" + selection if selection != "" else "",
                                        variation=variation.replace("same_sign_anti_iso", "same_sign") if transposed else variation.replace("same_sign_anti_iso", "anti_iso"),
                                        variable=variable)), -1.0)
    # Calculate extrapolation_factor from regions C and D.
    data_yield_C = rootfile.Get(_name_string.format(
                                dataset="data",
                                channel=channel,
                                process="",
                                selection="-" + selection if selection != "" else "",
                                variation=variation.replace("same_sign_anti_iso", "anti_iso") if transposed else variation.replace("same_sign_anti_iso", "same_sign"),
                                variable=variable
        )).Integral()
    bkg_yield_C = sum(rootfile.Get(_name_string.format(
                                dataset=_dataset_map[proc],
                                channel=channel,
                                process="-" + _process_map[proc],
                                selection="-" + selection if selection != "" else "",
                                variation=variation.replace("same_sign_anti_iso", "anti_iso") if transposed else variation.replace("same_sign_anti_iso", "same_sign"),
                                variable=variable
        )).Integral() for proc in procs_to_subtract)
    data_yield_D = rootfile.Get(_name_string.format(
                                dataset="data",
                                channel=channel,
                                process="",
                                selection="-" + selection if selection != "" else "",
                                variation=variation,
                                variable=variable
        )).Integral()
    bkg_yield_D = sum(rootfile.Get(_name_string.format(
                                dataset=_dataset_map[proc],
                                channel=channel,
                                process="-" + _process_map[proc],
                                selection="-" + selection if selection != "" else "",
                                variation=variation,
                                variable=variable
        )).Integral() for proc in procs_to_subtract)
    if data_yield_C == 0 or data_yield_D == 0:
        logger.warning("No data in region C or region D for shape of variable %s in category %s. Setting extrapolation_factor to zero.",
                       variable, "-" + selection if selection != "" else "")
        extrapolation_factor = 0.0
    elif not data_yield_D - bkg_yield_D > 0:
        logger.warning("Event content in region D for shape of variable %s in category %s is %f.",
                       variable, selection if selection != "" else "inclusive", data_yield_D - bkg_yield_D)
        extrapolation_factor = 0.0
    else:
        extrapolation_factor = (data_yield_C - bkg_yield_C) / (data_yield_D - bkg_yield_D)

    proc_name = "QCD" if is_embedding else "QCDMC"
    if variation in ["abcd_same_sign_anti_iso"]:
        qcd_variation = "Nominal"
    else:
        qcd_variation = variation.replace("abcd_same_sign_anti_iso_", "")
    logger.debug("Use extrapolation_factor factor with value %.2f to scale from region B to region A.",
                  extrapolation_factor)
    base_hist.Scale(extrapolation_factor)
    variation = variation.replace("same_sign_anti_iso", "same_sign") if transposed else variation.replace("same_sign_anti_iso", "anti_iso")
    variation_name = base_hist.GetName().replace("data", proc_name) \
                                        .replace(variation, qcd_variation) \
                                        .replace(channel, "-".join([channel, proc_name]), 1)
    base_hist.SetName(variation_name)
    base_hist.SetTitle(variation_name)
    replace_negative_entries_and_renormalize(base_hist, tolerance=100.05)
    return base_hist


def emb_ttbar_contamination_estimation(rootfile, channel, category, variable, sub_scale=0.1):
    procs_to_subtract = ["TTT"]
    logger.debug("Trying to get object {}".format(
                            _name_string.format(dataset=_dataset_map["EMB"],
                                                channel=channel,
                                                process="-" + _process_map["EMB"],
                                                selection=category,
                                                variation="Nominal",
                                                variable=variable)))
    base_hist = rootfile.Get(_name_string.format(
                            dataset=_dataset_map["EMB"],
                            channel=channel,
                            process="-" + _process_map["EMB"],
                            selection="-" + category if category != "" else "",
                            variation="Nominal",
                            variable=variable)).Clone()
    for proc in procs_to_subtract:
        logger.debug("Trying to fetch root histogram {}".format(
                                        _name_string.format(dataset=_dataset_map[proc],
                                                            channel=channel,
                                                            process="-" + _process_map[proc],
                                                            selection=category,
                                                            variation="Nominal",
                                                            variable=variable)))
        base_hist.Add(rootfile.Get(_name_string.format(
                                        dataset=_dataset_map[proc],
                                        channel=channel,
                                        process="-" + _process_map[proc],
                                        selection="-" + category if category != "" else "",
                                        variation="Nominal",
                                        variable=variable)), -sub_scale)
        if sub_scale > 0:
            variation_name = base_hist.GetName().replace("Nominal", "CMS_htt_emb_ttbar_EraDown")
        else:
            variation_name = base_hist.GetName().replace("Nominal", "CMS_htt_emb_ttbar_EraUp")
        base_hist.SetName(variation_name)
        base_hist.SetTitle(variation_name)
    return base_hist


def wfakes_estimation(rootfile, channel, selection, variable, variation="Nominal", is_embedding=True):
    procs_to_add = ["ZL", "TTL", "VVL", "W"]
    logger.debug("Trying to get object {}".format(
                        _name_string.format(dataset=_dataset_map[procs_to_add[0]],
                                            channel=channel,
                                            process="-" + _process_map[procs_to_add[0]],
                                            selection="-" + selection if selection != "" else "",
                                            variation=variation,
                                            variable=variable)))
    base_hist = (rootfile.Get(_name_string.format(
                                    dataset=_dataset_map[procs_to_add[0]],
                                    channel=channel,
                                    process="-" + _process_map[procs_to_add[0]],
                                    selection="-" + selection if selection !="" else "",
                                    variation=variation,
                                    variable=variable)
        )).Clone()
    for proc in procs_to_add[1:]:
        logger.debug("Trying to get object {}".format(
                            _name_string.format(dataset=_dataset_map[proc],
                                                channel=channel,
                                                process="-" + _process_map[proc],
                                                selection="-" + selection if selection != "" else "",
                                                variation=variation,
                                                variable=variable)))
        base_hist.Add(rootfile.Get(_name_string.format(
                                        dataset=_dataset_map[proc],
                                        channel=channel,
                                        process="-" + _process_map[proc],
                                        selection="-" + selection if selection !="" else "",
                                        variation=variation,
                                        variable=variable)))
    proc_name = "wFakes"
    if variation in ["wfakes"]:
        wf_variation = "Nominal"
    else:
        wf_variation = variation.replace("wFakes_", "")
    variation_name = base_hist.GetName().replace(_process_map[procs_to_add[0]], proc_name) \
                                        .replace(_dataset_map[procs_to_add[0]], proc_name) \
                                        .replace(variation, wf_variation)
    base_hist.SetName(variation_name)
    base_hist.SetTitle(variation_name)
    return base_hist


def main(args):
    input_file = ROOT.TFile(args.input, "update")
    # Loop over histograms in root file to find available FF inputs.
    ff_inputs = {}
    qcd_inputs = {}
    wfakes_inputs = {}
    emb_categories = {}
    logger.info("Reading inputs from file {}".format(args.input))
    for key in input_file.GetListOfKeys():
        logger.debug("Processing histogram %s",key.GetName())
        dataset, selection, variation, variable = key.GetName().split("#")
        if "anti_iso" in variation or "same_sign" in variation \
                                   or "wfakes" in variation:
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
                if (len(sel_split[1].split("-")) > 2
                    or ("Embedded" in sel_split[1] and len(sel_split[1].split("-")) > 1)
                    or ("W" in sel_split[1] and len(sel_split[1].split("-")) > 1)):
                    process = "-".join(sel_split[1].split("-")[:-1])
                    category = sel_split[1].split("-")[-1]
                else:
                    # Set only process if no categorization applied.
                    process = sel_split[1]
            if "anti_iso" in variation and not variation.startswith("abcd"):
                if channel in ff_inputs:
                    if category in ff_inputs[channel]:
                        if variable in ff_inputs[channel][category]:
                            if variation in ff_inputs[channel][category][variable]:
                                ff_inputs[channel][category][variable][variation].append(process)
                            else:
                                ff_inputs[channel][category][variable][variation] = [process]
                        else:
                            ff_inputs[channel][category][variable] = {variation: [process]}
                    else:
                        ff_inputs[channel][category] = {
                                                        variable: {
                                                            variation: [process]
                                                            }
                                                        }
                else:
                    ff_inputs[channel] = {
                                            category: {
                                                variable: {
                                                    variation: [process]
                                                }
                                            }
                                        }
            if "same_sign" in variation:
                if channel in qcd_inputs:
                    if channel in ["et", "mt", "em"] or "abcd_same_sign_anti_iso" in variation:
                        if category in qcd_inputs[channel]:
                            if variable in qcd_inputs[channel][category]:
                                if variation in qcd_inputs[channel][category][variable]:
                                    qcd_inputs[channel][category][variable][variation].append(process)
                                else:
                                    qcd_inputs[channel][category][variable][variation] = [process]
                            else:
                                qcd_inputs[channel][category][variable] = {variation: [process]}
                        else:
                            qcd_inputs[channel][category] = {
                                                        variable: {
                                                            variation: [process]
                                                            }
                                                        }
                else:
                    qcd_inputs[channel] = {
                                            category: {
                                                variable: {
                                                    variation: [process]
                                                }
                                            }
                                        }
            if "wfakes" in variation:
                if channel in wfakes_inputs:
                    if category in wfakes_inputs[channel]:
                        if variable in wfakes_inputs[channel][category]:
                            if variation in wfakes_inputs[channel][category][variable]:
                                wfakes_inputs[channel][category][variable][variation].append(process)
                            else:
                                wfakes_inputs[channel][category][variable][variation] = [process]
                        else:
                            wfakes_inputs[channel][category][variable] = {variation: [process]}
                    else:
                        wfakes_inputs[channel][category] = {
                                                    variable: {
                                                        variation: [process]
                                                        }
                                                    }
                else:
                    wfakes_inputs[channel] = {
                                            category: {
                                                variable: {
                                                    variation: [process]
                                                }
                                            }
                                        }
        #  Booking of necessary categories for embedded tt bar variation.
        if "Nominal" in variation:
            sel_split = selection.split("-", maxsplit=1)

            if "EMB" in dataset:
                channel = sel_split[0]
                category = sel_split[1].replace("Embedded", "").strip("-")
                if channel in emb_categories:
                    if category in emb_categories[channel]:
                        emb_categories[channel][category].append(variable)
                    else:
                        emb_categories[channel][category] = [variable]
                else:
                    emb_categories[channel] = {category: [variable]}

    # Loop over available ff inputs and do the estimations
    logger.info("Starting estimations for fake factors and their variations")
    logger.debug("%s", json.dumps(ff_inputs, sort_keys=True, indent=4))
    for ch in ff_inputs:
        for cat in ff_inputs[ch]:
            logger.info("Do estimation for category %s", cat)
            for var in ff_inputs[ch][cat]:
                for variation in ff_inputs[ch][cat][var]:
                   estimated_hist = fake_factor_estimation(input_file, ch, cat, var, variation=variation)
                   estimated_hist.Write()
                   estimated_hist = fake_factor_estimation(input_file, ch, cat, var, variation=variation, is_embedding=False)
                   estimated_hist.Write()
    logger.info("Starting estimations for the QCD mulitjet process.")
    logger.debug("%s", json.dumps(qcd_inputs, sort_keys=True, indent=4))
    for ch in qcd_inputs:
        for cat in qcd_inputs[ch]:
            logger.info("Do estimation for category %s", cat)
            for var in qcd_inputs[ch][cat]:
                for variation in qcd_inputs[ch][cat][var]:
                    if ch in ["et", "mt", "em"]:
                        if ch in ["et", "mt"] and  args.era == "2016":
                            extrapolation_factor = 1.17
                        elif ch in ["em"]:
                            if "NbtagGt1" in cat:
                                if args.era == "2016":
                                    extrapolation_factor = 0.71
                                elif args.era == "2017":
                                    extrapolation_factor = 0.69
                                elif args.era == "2018":
                                    extrapolation_factor = 0.67
                                else:
                                    logger.warning("No correction for given era %s available. "
                                                   "Setting extrapolation factor to 1.0",
                                                   args.era)
                                    extrapolation_factor = 1.0
                        else:
                            extrapolation_factor = 1.0
                        estimated_hist = qcd_estimation(input_file, ch, cat, var,
                                                        variation=variation,
                                                        extrapolation_factor=extrapolation_factor)
                        estimated_hist.Write()
                        estimated_hist = qcd_estimation(input_file, ch, cat, var,
                                                        variation=variation,
                                                        is_embedding=False,
                                                        extrapolation_factor=extrapolation_factor)
                        estimated_hist.Write()
                    else:
                        estimated_hist = abcd_estimation(input_file, ch, cat, var,
                                                         variation=variation)
                        estimated_hist.Write()
                        estimated_hist = abcd_estimation(input_file, ch, cat, var,
                                                         variation=variation,
                                                         is_embedding=False)
                        estimated_hist.Write()
    logger.info("Starting estimations for wfakes")
    logger.debug("%s", json.dumps(ff_inputs, sort_keys=True, indent=4))
    for ch in wfakes_inputs:
        for cat in wfakes_inputs[ch]:
            logger.info("Do estimation for category %s", cat)
            for var in wfakes_inputs[ch][cat]:
                for variation in wfakes_inputs[ch][cat][var]:
                   estimated_hist = wfakes_estimation(input_file, ch, cat, var, variation=variation)
                   estimated_hist.Write()
    if args.emb_tt:
        logger.info("Producing embedding ttbar variations.")
        logger.debug("%s", json.dumps(emb_categories, sort_keys=True, indent=4))
        for ch in emb_categories:
            for cat in emb_categories[ch]:
                logger.info("Do estimation for category %s", cat)
                for var in emb_categories[ch][cat]:
                    estimated_hist = emb_ttbar_contamination_estimation(input_file, ch, cat, var, sub_scale=0.1)
                    estimated_hist.Write()
                    estimated_hist = emb_ttbar_contamination_estimation(input_file, ch, cat, var, sub_scale=-0.1)
                    estimated_hist.Write()
    logger.info("Successfully finished estimations.")

    # Clean-up.
    input_file.Close()
    return


if __name__ == "__main__":
    args = parse_args()
    setup_logging("do_estimations.log", level=logging.INFO)
    main(args)
