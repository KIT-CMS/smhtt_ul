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


# --- helpers --- #


def to_python_native(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, float) and np.isinf(obj):
        if obj < 0:
            return -9.9
        else:
            raise ValueError("Positive infinity encountered in bin edges, which is not allowed.")
    elif isinstance(obj, list):
        return [to_python_native(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: to_python_native(v) for k, v in obj.items()}
    else:
        return obj


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


# --- data aquisition helpers --- #


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


# --- binning helpers --- #


def get_quantized_1d_bins(data, target_nbins, min_yield_fraction=0.15, high_cutoff=50):
    counts = Counter(data)
    sorted_unique_vals = sorted(counts.keys())
    total_events = len(data)

    if not sorted_unique_vals:
        return [-0.5, 0.5]

    if len(sorted_unique_vals) <= target_nbins:
        edges = [val - 0.5 for val in sorted_unique_vals]
        edges.append(sorted_unique_vals[-1] + 0.5)
    else:
        target_per_bin = total_events / target_nbins
        edges = [sorted_unique_vals[0] - 0.5]
        cumulative_events = 0
        for val in sorted_unique_vals:
            if cumulative_events > 0 and cumulative_events + counts[val] / 2 > target_per_bin:
                edges.append(val - 0.5)
                cumulative_events = 0
            cumulative_events += counts[val]
        edges.append(sorted_unique_vals[-1] + 0.5)
    
    edges = sorted(list(set(edges)))

    while len(edges) > 2:
        bin_populations = [np.sum((data >= edges[i]) & (data < edges[i+1])) for i in range(len(edges)-1)]
        if not bin_populations: break
        min_pop = min(bin_populations)
        if min_pop >= total_events * min_yield_fraction:
            break
        min_idx = bin_populations.index(min_pop)
        if min_idx == 0:
            edges.pop(1)
        elif min_idx == len(bin_populations) - 1:
            edges.pop(-2)
        else:
            if bin_populations[min_idx - 1] < bin_populations[min_idx + 1]:
                edges.pop(min_idx)
            else:
                edges.pop(min_idx + 1)
    
    if edges[-1] < high_cutoff + 0.5:
        edges[-1] = high_cutoff + 0.5
        
    return edges


def calculate_1d_binning_from_numpy(channel, var_data_np, variables, percentiles):
    binning, bad_values = {}, [-11.0, -999.0, -10.0, -1.0]  # usually it is -10

    for v in tqdm(variables, desc="Calculating 1D binning"):
        values_clean = var_data_np[v][~np.isin(var_data_np[v], bad_values)]

        if len(values_clean) == 0:
            logger.fatal(f"No valid values for variable {v} in channel {channel}.")
            raise Exception

        if is_quantized(values_clean):
            num_bins = len(percentiles) - 1
            borders = get_quantized_1d_bins(values_clean, num_bins)
        else:
            borders = [float(x) for x in np.percentile(values_clean, percentiles)]
            borders = sorted(list(set(borders)))

        if len(borders) < 2:
            borders = [values_clean.min(), values_clean.max()]

        borders[0] -= abs(borders[0] * 1e-4) if borders[0] != 0 else 1e-4
        borders[-1] += abs(borders[-1] * 1e-4) if borders[-1] != 0 else 1e-4

        binning[v] = {
            "bins": borders,
            "expression": v,
            "cut": f"({v}>{borders[0]})&&({v}<{borders[-1]})"
        }
    return to_python_native(binning)


def is_quantized(data, unique_threshold=30):
    if len(data) == 0:
        return False
    unique_vals = np.unique(data)
    is_integer_like = np.all(np.equal(np.mod(unique_vals, 1), 0))
    return is_integer_like and len(unique_vals) < unique_threshold


def get_quantized_slice_bins(data, num_slices, high_cutoff=50):
    """
    Finds more robustly equipopulated bin edges for a quantized variable.
    """
    if num_slices <= 1 or len(np.unique(data)) <= 1:
        return [np.min(data) - 0.5, high_cutoff + 0.5]

    counts = Counter(data)
    sorted_unique_vals = sorted(counts.keys())

    total_events = len(data)
    target_per_slice = total_events / num_slices

    edges = [sorted_unique_vals[0] - 0.5]
    cumulative_events = 0

    for i, val in enumerate(sorted_unique_vals):
        # Look ahead to see if adding this value would be a good cut point
        if cumulative_events >= target_per_slice:
            edges.append(val - 0.5)
            cumulative_events = 0
        cumulative_events += counts[val]

    edges.append(high_cutoff + 0.5)

    final_edges = sorted(list(set(edges)))
    if len(final_edges) < num_slices:
        logger.warning("Quantized binning created fewer slices than requested. Check data distribution.")

    return final_edges


def add_2d_unrolled_binning_from_numpy(variables, binning, var_data_np, num_primary_slices=5, target_total_bins=25):
    new_binning = binning.copy()
    correlations = {}

    for v1, v2 in tqdm(list(itertools.combinations(variables, 2)), desc="Calculating 2D unrolled binning"):
        val1_raw, val2_raw = var_data_np[v1], var_data_np[v2]
        v1_min, v1_max = binning[v1]['bins'][0], binning[v1]['bins'][-1]
        v2_min, v2_max = binning[v2]['bins'][0], binning[v2]['bins'][-1]
        bad_values = [-11.0, -999.0, -10.0, -1.0]
        final_mask = np.logical_and(
            ~np.isin(val1_raw, bad_values),
            ~np.isin(val2_raw, bad_values),
            (val1_raw > v1_min),
            (val1_raw < v1_max),
            (val2_raw > v2_min),
            (val2_raw < v2_max),
        )
        val1_local, val2_local = val1_raw[final_mask], val2_raw[final_mask]

        try:
            corr_val = np.corrcoef(val1_local, val2_local)[0, 1]
            if np.isnan(corr_val):
                corr_val = 0.0
        except Exception:
            corr_val = 0.0

        correlations[f"{v1}_{v2}"] = float(corr_val)

        if len(val1_local) < target_total_bins:
            continue

        # Select slicing (v_slice) and adaptive (v_cont) variables
        v1_is_quantized = "njets" in v1 or "nbtag" in v1
        v2_is_quantized = "njets" in v2 or "nbtag" in v2
        if v1_is_quantized and not v2_is_quantized:
            v_slice_name, v_cont_name = v1, v2
            slice_data, cont_data = val1_local, val2_local
        elif v2_is_quantized and not v1_is_quantized:
            v_slice_name, v_cont_name = v2, v1
            slice_data, cont_data = val2_local, val1_local
        else:  # Covers continuous-continuous and quantized-quantized
            if len(val1_local) <= len(val2_local):
                v_slice_name, v_cont_name = v1, v2
                slice_data, cont_data = val1_local, val2_local
            else:
                v_slice_name, v_cont_name = v2, v1
                slice_data, cont_data = val2_local, val1_local

        # Define primary slices for v_slice
        slice_is_quantized_check = is_quantized(slice_data)
        if slice_is_quantized_check:
            slice_edges = get_quantized_slice_bins(slice_data, num_primary_slices)
        else:
            noise = np.random.normal(0, 1e-9, slice_data.shape)
            slice_edges = np.percentile(slice_data + noise, np.linspace(0, 100, num_primary_slices + 1))
        slice_edges = sorted(list(set(slice_edges)))
        if len(slice_edges) < 2:
            continue

        # Pre-calculate the adaptive number of sub-bins and their edges for each slice
        slice_info, total_valid_events = [], len(slice_data)
        global_target_yield = max(1, total_valid_events / target_total_bins) if target_total_bins > 0 else 1
        for i in range(len(slice_edges) - 1):
            start, end = slice_edges[i], slice_edges[i + 1]
            is_last = (i == len(slice_edges) - 2)
            mask = (slice_data >= start) & (slice_data <= end if is_last else slice_data < end)
            cont_in_slice = cont_data[mask]
            if len(cont_in_slice) < 2:
                slice_info.append({'valid': False})
                continue
            num_sub_bins = int(round(len(cont_in_slice) / global_target_yield))
            if num_sub_bins < 1:
                num_sub_bins = 1
            noise = np.random.normal(0, 1e-9, cont_in_slice.shape)
            secondary_edges = np.percentile(cont_in_slice + noise, np.linspace(0, 100, num_sub_bins + 1))
            slice_info.append({'valid': True, 'num_sub_bins': num_sub_bins, 'secondary_edges': secondary_edges})

        # Build the nested expression for bin index
        expression_parts, slice_conditions, bin_offset = [], [], 0
        for i, info in enumerate(slice_info):
            if not info['valid']:
                continue
            start_slice, end_slice = slice_edges[i], slice_edges[i + 1]
            is_last_slice = (i == len(slice_edges) - 2)

            sub_bin_expr_parts = []
            for j in range(info['num_sub_bins']):
                start_sub, end_sub = info['secondary_edges'][j], info['secondary_edges'][j + 1]
                is_last_sub = (j == info['num_sub_bins'] - 1)
                sub_cond = f"((({v1} > -10) && ({v2} > -10)) && (({v_cont_name} >= {start_sub}) && ({v_cont_name} {'<=' if is_last_sub else '<'} {end_sub})))"
                sub_bin_expr_parts.append(f"{j}*{sub_cond}")

            sub_bin_index_expr = f"({' + '.join(sub_bin_expr_parts)})"

            slice_condition = f"((({v1} > -10) && (({v2} > -10)) && ({v_slice_name} >= {start_slice}) && ({v_slice_name} {'<=' if is_last_slice else '<'} {end_slice})))"
            slice_conditions.append(slice_condition)

            expression_parts.append(f"({bin_offset + 1} + {sub_bin_index_expr}) * {slice_condition}")

            bin_offset += info['num_sub_bins']

        if not expression_parts:
            continue

        new_binning[f"{v1}_{v2}"] = {
            "bins": np.arange(bin_offset + 1, dtype=float) + 0.5,  # everything else lands in bin 0
            "expression": ' + '.join(expression_parts),
            "cut": f"(({v1} > {v1_min}) && ({v1} < {v1_max}) && ({v2} > {v2_min}) && ({v2} < {v2_max}))",
        }

    return to_python_native(new_binning), correlations


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

    var_data_np = extract_data_from_chain(chain, variables, cache_path=skim_file_path.replace(".root", "_variables.pkl"))

    percentiles = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]

    outputfile = os.path.join(args.output_folder, f"binning_{args.era}_{args.channel}.yaml")
    binning = calculate_1d_binning_from_numpy(args.channel, var_data_np, variables, percentiles)
    with open(outputfile, "w") as f:
        yaml.dump(binning, f, default_flow_style=False)

    logger.info(f"Done: 1d binning, written to {outputfile}")

    outputfile2d = os.path.join(args.output_folder, f"binning_{args.era}_{args.channel}_2D.yaml")
    binning, correlations = add_2d_unrolled_binning_from_numpy(variables, binning, var_data_np)
    with open(outputfile2d, "w") as f:
        yaml.dump(binning, f, default_flow_style=False)
    with open(outputfile2d.replace(".yaml", "_correlations.yaml"), "w") as f:
        yaml.dump(correlations, f, default_flow_style=False)
    logger.info(f"Done: 2d unrolled binning, written to {outputfile2d}")


if __name__ == "__main__":
    args = parse_arguments()
    logger = setup_logging(logger=logging.getLogger(__name__), level=logging.DEBUG)
    main(args)
