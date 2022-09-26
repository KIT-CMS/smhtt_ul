from shapes.utils import get_nominal_datasets
from ntuple_processor import Histogram
from ntuple_processor.utils import Selection
from config.shapes.file_names import files
import yaml

from shapes.produce_shapes import setup_logging, get_analysis_units
import logging
import argparse
import numpy as np
import os
import ROOT

logger = logging.getLogger("calculate_binning.py")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--era",
        type=str,
        required=True,
        help="Era of the data",
    )
    parser.add_argument(
        "--channel",
        type=str,
        required=True,
        help="Channel to be processed",
    )
    parser.add_argument(
        "--directory",
        type=str,
        required=True,
        help="Directory where the ntuples are stored",
    )
    parser.add_argument(
        "--variables",
        type=str,
        default=[],
        nargs="+",
        help="List of variables to be processed",
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
        "--output-folder",
        type=str,
        required=True,
        help="folder name where the output will be stored",
    )
    return parser.parse_args()


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def set_dummy_categorization():
    # this is just a dummy selection we need to trick the framework, we do not use it !
    inclusive = [
        (
            Selection(name="Inclusive", cuts=[("", "category_selection")]),
            [Histogram("m_vis", "m_vis", [i for i in range(0, 255, 5)])],
        )
    ]
    training_categorization = {
        "et": inclusive,
        "mt": inclusive,
        "tt": inclusive,
        "em": inclusive,
    }
    return training_categorization


def get_data_selection(era, channel, name, unit, categorization, basedir, frienddirs):
    cuts = ""
    weights = ""
    files = []
    friend_paths = []
    if unit[0].dataset.ntuples[0].friends is not None:
        for friend_dir in frienddirs:
            for friendfile in [x.path for x in unit[0].dataset.ntuples[0].friends]:
                if friend_dir in friendfile and friend_dir not in friend_paths:
                    friend_paths.append(f"{friend_dir}/")
    files = [ntuple.path.replace(basedir, "") for ntuple in unit[0].dataset.ntuples]
    for selection in unit[0].selections:
        cutstring = " && ".join(
            [
                "({})".format(cut.expression)
                for cut in selection.cuts
                if cut.expression != ""
            ]
        )
        weightstring = " * ".join(
            [
                "({})".format(weight.expression)
                for weight in selection.weights
                if weight.expression != ""
            ]
        )
        if cutstring != "":
            cuts += cutstring + " && "
        if weightstring != "":
            weights += weightstring + " * "
    if len(weights) > 0:
        weights = weights[:-3]
    if len(cuts) > 0:
        cuts = cuts[:-4]
    data = {
        "process": name,
        "weight_string": f"({weights})",
        "files": files,
        "cut_string": f"({cuts})",
        "tree_path": "ntuple",
        "base_path": basedir,
        "friend_paths": friend_paths,
    }
    return data


def build_chain(dict_):
    # Build chain
    friend_paths = dict_["friend_paths"]
    logger.debug("Use tree path %s for chain.", dict_["tree_path"])
    chain = ROOT.TChain(dict_["tree_path"])
    friendchains = {}
    for d in friend_paths:
        friendchains[d] = ROOT.TChain(dict_["tree_path"])
    for i, f in enumerate(dict_["files"]):
        filename = f"{dict_['base_path']}/{f}"
        chain.AddFile(filename)
        for friendchain in friendchains:
            friendfile = f"{d}/{f}"
            friendchains[friendchain].AddFile(friendfile)

    chain_numentries = chain.GetEntries()
    if not chain_numentries > 0:
        logger.fatal("Chain (before skimming) does not contain any events.")
        raise Exception
    logger.debug("Found %s events before skimming with cut string.", chain_numentries)
    logger.debug("Using cut string %s", dict_["cut_string"])

    # Skim chain
    chain_skimmed = chain.CopyTree(dict_["cut_string"])
    chain_skimmed_numentries = chain_skimmed.GetEntries()
    friendchains_skimmed = {}
    # Apply skim selection also to friend chains
    for d in friendchains:
        friendchains[d].AddFriend(chain)
        friendchains_skimmed[d] = friendchains[d].CopyTree(dict_["cut_string"])
    if not chain_skimmed_numentries > 0:
        logger.fatal("Chain (after skimming) does not contain any events.")
        raise Exception
    logger.debug(
        "Found %s events after skimming with cut string.", chain_skimmed_numentries
    )
    for d in friendchains_skimmed:
        chain_skimmed.AddFriend(
            friendchains_skimmed[d], "fr_{}".format(os.path.basename(d.rstrip("/")))
        )

    return chain_skimmed


def get_1d_binning(channel, chain, variables, percentiles):
    # Collect values
    values = [[] for v in variables]
    for event in chain:
        for i, v in enumerate(variables):
            value = getattr(event, v)
            if value not in [-11.0, -999.0, -10.0, -1.0]:
                values[i].append(value)

    # Get min and max by percentiles
    binning = {}
    for i, v in enumerate(variables):
        binning[v] = {}
        if len(values[i]) > 0:
            borders = [float(x) for x in np.percentile(values[i], percentiles)]
            # remove duplicates in bins for integer binning
            borders = sorted(list(set(borders)))
            # epsilon offset for integer variables to make it more stable
            borders = [b - 0.0001 for b in borders]
            # stretch last one to include the last border in case it is an integer
            borders[-1] += 0.0002
        else:
            logger.fatal(
                "No valid values found for variable {}. Please remove from list for channel {}.".format(
                    v, channel
                )
            )
            raise Exception

        binning[v]["bins"] = borders
        binning[v]["expression"] = v
        if len(borders) >= 2:
            binning[v]["cut"] = "({VAR}>{MIN})&&({VAR}<{MAX})".format(
                VAR=v, MIN=borders[0], MAX=borders[-1]
            )
        else:
            binning[v]["cut"] = "(1 == 0)"
        logger.debug("Binning for variable %s: %s", v, binning[v]["bins"])
    return binning

def add_2d_unrolled_binning(variables, binning):
    for i1, v1 in enumerate(variables):
        for i2, v2 in enumerate(variables):
            if i2 <= i1:
                continue

            if len(binning[v1]["bins"]) < 11:
                bins1 = binning[v1]["bins"]
            else:
                bins1 = binning[v1]["bins"][::2]
            if len(binning[v2]["bins"]) < 11:
                bins2 = binning[v2]["bins"]
            else:
                bins2 = binning[v2]["bins"][::2]
            range_ = max(bins1) - min(bins1)

            bins = [bins1[0]]
            expression = ""
            for b in range(len(bins2) - 1):
                expression += "({OFFSET}+{VAR1})*({VAR2}>{MIN})*({VAR2}<={MAX})".format(
                    VAR1=v1,
                    VAR2=v2,
                    MIN=bins2[b],
                    MAX=bins2[b + 1],
                    OFFSET=b * range_)
                if b != len(bins2) - 2:
                    expression += "+"
                for c in range(len(bins1)-1):
                    bins.append(b * range_ + bins1[c+1])
            # Add separate term shifting undefined values away from zero.
            # If this is not done the bin including zero is populated with all events
            # with default values.
            # This problem only occurs for variables taking integer values.
            jet_variables = ["mjj", "jdeta", "dijetpt", "ME_q2v1", "ME_q2v2"]
            default_val = -10.
            if v1 in ["njets", "nbtag"]:
                if v2 in jet_variables:
                    expression += "({DEF})*(({VAR2}<{MIN})+({VAR2}>{MAX}))".format(
                            DEF=default_val,
                            VAR2=v2,
                            MIN=bins2[0],
                            MAX=bins2[-1])

            name = "{}_{}".format(v1, v2)
            binning[name] = {}
            binning[name]["bins"] = bins
            binning[name]["expression"] = expression
            binning[name]["cut"] = "({VAR}>{MIN})&&({VAR}<{MAX})".format(
                VAR=v1, MIN=bins1[0], MAX=bins1[-1])

    return binning


def main(args):
    friend_directories = {
        "et": args.et_friend_directory,
        "mt": args.mt_friend_directory,
        "tt": args.tt_friend_directory,
        "em": args.em_friend_directory,
        "mm": args.mm_friend_directory,
    }
    era = args.era
    channel = args.channel
    nominals = {}
    nominals[era] = {}
    nominals[era]["datasets"] = {}
    nominals[era]["units"] = {}
    logger.info("Processing era {}".format(era))
    logger.info("Processing channel {}".format(channel))
    logger.info("Friends: {}".format(friend_directories[channel]))
    if "," in args.variables[0]:
        variables = args.variables[0].split(",")
    else:
        variables = args.variables
    logger.info("Variables: {}".format(variables))
    nominals[era]["datasets"][channel] = get_nominal_datasets(
        era, channel, friend_directories, files, args.directory
    )
    logger.info("Found {} datasets".format(len(nominals[era]["datasets"][channel])))
    logger.info("Creating analysis units")
    nominals[era]["units"][channel] = get_analysis_units(
        channel,
        era,
        nominals[era]["datasets"][channel],
        set_dummy_categorization(),
        None,
    )
    data_selection = get_data_selection(
        era,
        channel,
        "data",
        nominals[era]["units"][channel]["data"],
        set_dummy_categorization(),
        args.directory,
        friend_directories[channel],
    )

    percentiles = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]

    outputfile = os.path.join(args.output_folder, f"binning_{era}_{channel}.yaml")
    outputfile2d = os.path.join(args.output_folder, f"binning_{era}_{channel}_2D.yaml")
    chain = build_chain(data_selection)
    binning = get_1d_binning(channel, chain, variables, percentiles)
    with open(outputfile, "w") as f:
        yaml.dump(binning, f, default_flow_style=False)

    binning = add_2d_unrolled_binning(variables, binning)
    with open(outputfile2d, "w") as f:
        yaml.dump(binning, f, default_flow_style=False)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("create_gof_binning.txt", logging.DEBUG)
    main(args)
