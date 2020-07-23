#!/usr/bin/env python3
# Script adapted from script in https://github.com/KIT-CMS/sm-htt-analysis/shapes/convert_to_synced_shapes.py
import os
import argparse
import logging

import ROOT

logger = logging.getLogger("")

_process_map = {
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
    "jetFakes": "jetFakes",
    "jetFakesMC": "jetFakes",
    "QCD": "QCD",
    "QCD": "QCDMC",
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--era", help="Experiment era.")
    parser.add_argument("-i", "--input", help="Input root file.")
    parser.add_argument("-o", "--output", help="Output directory.")
    parser.add_argument("--gof", action="store_true",
                        help="Convert shapes for GoF or control plots. "
                             "Use variable as category indicator.")
    parser.add_argument("--mc", action="store_true",
                        help="Use jet fake estimation based on mc shapes.")
    parser.add_argument("--variable-selection", default=None, type=str, nargs=1,
                        help="Select final discriminator for shape creation.")
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


def main(args):
    input_file = ROOT.TFile(args.input)

    # Loop over histograms to extract relevant information for synced files.
    logging.info("Reading input histograms from file %s", args.input)
    hist_map = {}
    for key in input_file.GetListOfKeys():
        split_name = key.GetName().split("#")

        channel = split_name[1].split("-")[0]
        if args.gof:
            # Use variable as category label for GOF test and control plots.
            category = split_name[3]
            process = "-".join(split_name[1].split("-")[1:]) if not "data" in split_name[0] else "data_obs"
        else:
            category = split_name[1].split("-")[-1]
            process = "-".join(split_name[1].split("-")[1:-1]) if not "data" in split_name[0] else "data_obs"
            # Skip discriminant variables we do not want in the sync file.
            # This is necessary because the sync file only allows for one type of histogram.
            # A combination of the runs for different variables can then be used in separate files.
            if args.variable_selection is None:
                pass
            else:
                if split_name[3] not in args.variable_selection:
                    continue
        variation = split_name[2]
        # Skip variations necessary for estimations which are of no further use.
        if "same_sign" in variation or "anti_iso" in variation:
            continue

        # Check if channel and category are already in the map
        if not channel in hist_map:
            hist_map[channel] = {}
        if not category in hist_map[channel]:
            hist_map[channel][category] = {}

        _rev_process_map = {val: key for key, val in _process_map.items()}
        # Skip copying of jetFakes estimations based on underlying shapes to be able
        # to use one name in the synced file.
        # TODO: Should this be kept or do we want to put both version in the synced file and
        #       perform the switch on combine level.
        if args.mc:
            if process in ["jetFakes", "QCD"]:
                continue
        else:
            if "MC" in process:
                continue
        if process in _rev_process_map.keys():
            process = _rev_process_map[process]
        name_output = "{process}".format(process=process)
        if "Nominal" not in variation:
            name_output += "_" + variation
        logging.debug("Adding histogram with name %s as %s to category %s.",
                      key.GetName(), name_output, channel + "_" + category)
        hist_map[channel][category][key.GetName()] = name_output

    # Loop over map and create the output file.
    for channel in hist_map:
        logging.info("Writing histograms to file %s",
                     os.path.join(
                            args.output,
                            "{ERA}-{CHANNELS}-synced-MSSM.root".format(
                                                                    CHANNELS=channel,
                                                                    ERA=args.era)))
        filename_output = os.path.join(
                args.output, "{ERA}-{CHANNELS}-synced-MSSM.root".format(CHANNELS=channel, ERA=args.era))
        if not os.path.exists(args.output):
            os.mkdir(args.output)
        output_file = ROOT.TFile(filename_output, "RECREATE")
        for category in sorted(hist_map[channel]):
            output_file.cd()
            dir_name = "{CHANNEL}_{CATEGORY}".format(
                    CHANNEL=channel, CATEGORY=category)
            output_file.mkdir(dir_name)
            output_file.cd(dir_name)
            for name in sorted(hist_map[channel][category]):
                hist = input_file.Get(name)
                name_output = hist_map[channel][category][name]
                if "Era" in name_output:
                    hist.SetTitle(name_output.replace("Era", args.era))
                    hist.SetName(name_output.replace("Era", args.era))
                else:
                    hist.SetTitle(name_output)
                    hist.SetName(name_output)
                hist.Write()

                if "Era" in name_output:
                    if ("_1ProngPi0Eff_" in name_output
                            or "_3ProngEff_" in name_output
                            or "_dyShape_" in name_output):
                        hist.SetTitle(name_output.replace("_Era", ""))
                        hist.SetName(name_output.replace("_Era", ""))
                        hist.Write()
        output_file.Close()

    logging.info("Successfully written all histograms to file.")
    # Clean up
    input_file.Close()

if __name__ == "__main__":
    args = parse_args()
    setup_logging("convert_to_synced_shapes.log", level=logging.INFO)
    main(args)
