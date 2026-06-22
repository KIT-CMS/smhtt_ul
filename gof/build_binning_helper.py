import argparse
import logging
import os

import numpy as np
import ROOT
import yaml
import pickle
import itertools

from copy import deepcopy
import multiprocessing as mp
from collections import Counter

from config.logging_setup_configs import setup_logging
from config.shapes.file_names import files
from ntuple_processor import Histogram
from ntuple_processor.utils import Selection
from shapes.produce_shapes import get_analysis_units
from shapes.utils import get_nominal_datasets
from tqdm import tqdm


logger = setup_logging(logger=logging.getLogger(__name__), level=logging.DEBUG)


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
        "--validation-tag",
        type=str,
        default="",
        help="Validation tag of the ntuples",
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
    parser.add_argument(
        "--n-processes",
        type=int,
        default=30,
        help="Number of processes to use for multiprocessing",
    )
    return parser.parse_args()


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
    cuts, weights, files, friend_paths = "", "", [], []
    files = [ntuple.path for ntuple in unit[0].dataset.ntuples]
    if unit[0].dataset.ntuples[0].friends is not None:
        for friend_file_path in unit[0].dataset.ntuples[0].friends:
            try:
                *friend_path_bulk, _, _, _, _ = friend_file_path.path.split("/")
                friend_paths.append("/".join(friend_path_bulk))
            except ValueError:
                logger.warning(f"Could not parse friend path {friend_file_path.path} with expected structure. Skipping.")
    for selection in unit[0].selections:
        cutstring = " && ".join([f"({cut.expression})" for cut in selection.cuts if cut.expression != ""])
        weightstring = " * ".join([f"({weight.expression})" for weight in selection.weights if weight.expression != ""])
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
        "cut_string": "(" + cuts.replace("\n", "").replace(" ", "").strip() + ")",
        "tree_path": "ntuple",
        "base_path": basedir,
        "friend_paths": friend_paths,
    }
    return data


def build_chain(dict_, cache_path=None):
    if cache_path is not None and os.path.exists(cache_path):
        logger.info(f"Loading cached skimmed tree from {cache_path}...")
        skimmed_chain = ROOT.TChain(dict_["tree_path"])
        skimmed_chain.Add(cache_path)
        if not skimmed_chain or not skimmed_chain.GetEntries() > 0:
            logger.fatal(f"Failed to load a valid tree from {cache_path}.")
            raise RuntimeError("Cached skim file is invalid or empty.")
        logger.info(f"Successfully loaded {skimmed_chain.GetEntries()} events from cache.")
        return skimmed_chain
    else:
        # Build chain
        friend_paths = dict_["friend_paths"]
        logger.debug("Use tree path %s for chain.", dict_["tree_path"])
        chain = ROOT.TChain(dict_["tree_path"])
        friendchains = {}
        for d in friend_paths:
            friendchains[d] = ROOT.TChain(dict_["tree_path"])
        for i, f in enumerate(dict_["files"]):
            chain.AddFile(f)
            *_, __era, __sample, __channel, __file = f.split("/")
            for friendchain in friendchains:
                friendfile = "/".join([friendchain, __era, __sample, __channel, __file])
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

        logger.info(f"Saving skimmed tree to {cache_path} for faster subsequent runs.")
        outfile = ROOT.TFile(cache_path, "RECREATE")
        chain_skimmed.Write()
        outfile.Close()
        logger.info("Skimmed tree saved successfully.")

        return chain_skimmed


def extract_data_from_chain(chain, variables, cache_path=None):
    if cache_path is not None and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            var_data_np = pickle.load(f)
            logger.info(f"Loaded cached variable data from {cache_path}.")
            return var_data_np

    logger.info(f"Extracting {len(variables)} variables from the TChain into memory...")
    var_data_np = {v: [] for v in variables}
    for event in tqdm(chain, desc="Extracting events", total=chain.GetEntries()):
        for v in variables:
            var_data_np[v].append(getattr(event, v))

    for v in variables:
        var_data_np[v] = np.array(var_data_np[v])

    logger.info("Data extraction complete.")

    if cache_path is not None:
        with open(cache_path, "wb") as f:
            pickle.dump(var_data_np, f)
            logger.info(f"Cached variable data to {cache_path} for future runs.")

    return var_data_np


def main(args):
    skim_file_path = os.path.join(args.output_folder, f".skimmed_{args.era}_{args.channel}.root")
    if "," in args.variables[0]:
        variables = args.variables[0].split(",")
    else:
        variables = args.variables

    logger.info("Processing era {}".format(args.era))
    logger.info("Processing channel {}".format(args.channel))
    logger.info("Variables: {}".format(variables))

    if not os.path.exists(skim_file_path):
        friend_directories = {
            "et": args.et_friend_directory,
            "mt": args.mt_friend_directory,
            "tt": args.tt_friend_directory,
            "em": args.em_friend_directory,
            "mm": args.mm_friend_directory,
        }
        nominals = {}
        nominals[args.era] = {}
        nominals[args.era]["datasets"] = {}
        nominals[args.era]["units"] = {}
        logger.info("Friends: {}".format(friend_directories[args.channel]))
        nominals[args.era]["datasets"][args.channel] = get_nominal_datasets(
            era=args.era,
            channel=args.channel,
            friend_directories=friend_directories,
            files=files,
            directory=args.directory,
            validation_tag=args.validation_tag,
            xrootd=True,
        )
        logger.info("Found {} datasets".format(len(nominals[args.era]["datasets"][args.channel])))
        logger.info("Creating analysis units")
        nominals[args.era]["units"][args.channel] = get_analysis_units(
            channel=args.channel,
            era=args.era,
            datasets=nominals[args.era]["datasets"][args.channel],
            categorization=set_dummy_categorization(),
        )
        data_selection = get_data_selection(
            era=args.era,
            channel=args.channel,
            name="data",
            unit=nominals[args.era]["units"][args.channel]["data"],
            categorization=set_dummy_categorization(),
            basedir=args.directory,
            frienddirs=friend_directories[args.channel],
        )
        chain = build_chain(data_selection, cache_path=skim_file_path)
    else:
        chain = build_chain({"tree_path": "ntuple"}, cache_path=skim_file_path)

    extract_data_from_chain(chain, variables, cache_path=skim_file_path.replace(".root", "_variables.pkl"))


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
