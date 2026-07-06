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

import build_binning_helper as build_binning_helper


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
    parser.add_argument(
        "--njets-cut",
        type=str,
        default="(njets >= 0)",
        help="Global cut expression applied on the input data before calculations (e.g. 'njets == 0', 'njets >= 2')",
    )
    return parser.parse_args()


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


VARIABLE_CATEGORIES = {
    "quantized": [
        "njets",
        "nbtag",
        "tau_decaymode_1",
        "tau_decaymode_2",
    ],
    ("njets", 0): [
        "njets",
        "nbtag",
        "pt_1",
        "eta_1",
        "phi_1",
        "tau_decaymode_1",
        "mt_1",
        "iso_1",
        "mass_1",
        "pt_2",
        "eta_2",
        "phi_2",
        "tau_decaymode_2",
        "mt_2",
        "iso_2",
        "mass_2",
        "pt_tt",
        "pt_vis",
        "mt_tot",
        "m_vis",
        "met",
        "metphi",
        "mTdileptonMET",
        "metSumEt",
        "pzetamissvis",
        "deltaR_ditaupair",
        "deltaEta_ditaupair",
        "eta_fastmtt",
        "m_fastmtt",
        "phi_fastmtt",
        "pt_fastmtt",
    ],
    ("njets", 1): [
        "jpt_1",
        "jeta_1",
        "jphi_1",
        "bpt_1",
        "beta_1",
        "bphi_1",
        "btag_value_1",
        "deltaR_1j1",
        "deltaR_2j1",
        "deltaR_12j1",
        "deltaEta_1j1",
        "deltaEta_2j1",
        "deltaEta_12j1",
    ],
    ("njets", 2): [
        "jpt_2",
        "jeta_2",
        "jphi_2",
        "bpt_2",
        "beta_2",
        "bphi_2",
        "btag_value_2",
        "pt_dijet",
        "pt_ttjj",
        "mjj",
        "deltaR_jj",
        "deltaEta_jj",
        "deltaR_1j2",
        "deltaR_2j2",
        "deltaR_12j2",
        "deltaEta_1j2",
        "deltaEta_2j2",
        "deltaEta_12j2",
    ],
}

# --- binning helpers --- #


class BinningStrategyTargetBinning:
    @staticmethod
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
            bin_populations = [np.sum((data >= edges[i]) & (data < edges[i + 1])) for i in range(len(edges) - 1)]
            if not bin_populations:
                break
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

    @staticmethod
    def calculate_1d_binning_from_numpy(channel, var_data_np, variables, percentiles):
        binning, bad_values = {}, [-11.0, -999.0, -10.0, -1.0]  # usually it is -10

        for v in tqdm(variables, desc="Calculating 1D binning"):
            values_clean = var_data_np[v][~np.isin(var_data_np[v], bad_values)]

            if len(values_clean) == 0:
                logger.fatal(f"No valid values for variable {v} in channel {channel}.")
                raise Exception

            if BinningStrategyTargetBinning.is_quantized(values_clean):
                num_bins = len(percentiles) - 1
                borders = BinningStrategyTargetBinning.get_quantized_1d_bins(values_clean, num_bins)
            else:
                borders = [float(x) for x in np.percentile(values_clean, percentiles)]
                borders = sorted(list(set(borders)))

            if len(borders) < 2:
                borders = [values_clean.min(), values_clean.max()]

            borders[0] -= abs(borders[0] * 1e-4) if borders[0] != 0 else 1e-4
            borders[-1] += abs(borders[-1] * 1e-4) if borders[-1] != 0 else 1e-4

            binning[v] = {"bins": borders, "expression": v, "cut": f"({v}>{borders[0]})&&({v}<{borders[-1]})"}
        return to_python_native(binning)

    @staticmethod
    def is_quantized(data, unique_threshold=30):
        if len(data) == 0:
            return False
        unique_vals = np.unique(data)
        is_integer_like = np.all(np.equal(np.mod(unique_vals, 1), 0))
        return is_integer_like and len(unique_vals) < unique_threshold

    @staticmethod
    def get_quantized_slice_bins(data, num_slices, high_cutoff=50, min_yield=None):
        if num_slices <= 1 or len(np.unique(data)) <= 1:
            return [np.min(data) - 0.5, high_cutoff + 0.5]

        counts = Counter(data)
        sorted_unique_vals = sorted(counts.keys())

        total_events = len(data)
        target_per_slice = total_events / num_slices
        
        if min_yield is None:
            min_yield = target_per_slice * 0.5

        edges = [sorted_unique_vals[0] - 0.5]
        cumulative_events = 0

        for i, val in enumerate(sorted_unique_vals):
            cumulative_events += counts[val]

            if cumulative_events >= target_per_slice:
                remaining_events = total_events - sum(counts[v] for v in sorted_unique_vals[:i + 1])
                # Tail protection: only cut if remaining events justify a new bin
                if i < len(sorted_unique_vals) - 1 and remaining_events >= min_yield:
                    edges.append(val + 0.5)
                    cumulative_events = 0

        edges.append(high_cutoff + 0.5)

        final_edges = sorted(list(set(edges)))
        if len(final_edges) < num_slices:
            logger.warning("Quantized binning created fewer slices than requested. Check data distribution.")

        return final_edges

    @staticmethod
    def add_2d_unrolled_binning_from_numpy(variables, binning, var_data_np, num_primary_slices=5, target_total_bins=25):
        new_binning = binning.copy()
        correlations = {}

        for v1, v2 in tqdm(list(itertools.combinations(variables, 2)), desc="Calculating 2D unrolled binning"):
            val1_raw, val2_raw = var_data_np[v1], var_data_np[v2]
            v1_min, v1_max = binning[v1]["bins"][0], binning[v1]["bins"][-1]
            v2_min, v2_max = binning[v2]["bins"][0], binning[v2]["bins"][-1]
            bad_values = [-11.0, -999.0, -10.0, -1.0]
            final_mask = (
                ~np.isin(val1_raw, bad_values)
                & ~np.isin(val2_raw, bad_values)
                & (val1_raw > v1_min)
                & (val1_raw < v1_max)
                & (val2_raw > v2_min)
                & (val2_raw < v2_max)
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
            v1_quant = "njets" in v1 or "nbtag" in v1 or "tau_decaymode" in v1 or BinningStrategyTargetBinning.is_quantized(val1_local)
            v2_quant = "njets" in v2 or "nbtag" in v2 or "tau_decaymode" in v2 or BinningStrategyTargetBinning.is_quantized(val2_local)
            
            u1, u2 = len(np.unique(val1_local)), len(np.unique(val2_local))

            if v1_quant and not v2_quant:
                v_slice_name, v_cont_name, slice_data, cont_data = v1, v2, val1_local, val2_local
            elif v2_quant and not v1_quant:
                v_slice_name, v_cont_name, slice_data, cont_data = v2, v1, val2_local, val1_local
            elif u1 <= u2:
                v_slice_name, v_cont_name, slice_data, cont_data = v1, v2, val1_local, val2_local
            else:
                v_slice_name, v_cont_name, slice_data, cont_data = v2, v1, val2_local, val1_local

            # Define primary slices for v_slice
            slice_info, total_valid_events = [], len(slice_data)
            global_target_yield = max(1, total_valid_events / target_total_bins) if target_total_bins > 0 else 1

            if BinningStrategyTargetBinning.is_quantized(slice_data):
                slice_edges = BinningStrategyTargetBinning.get_quantized_slice_bins(slice_data, num_primary_slices, min_yield=global_target_yield)
            else:
                slice_edges = sorted(list(set(np.percentile(slice_data, np.linspace(0, 100, num_primary_slices + 1)))))
            
            if len(slice_edges) < 2:
                continue

            for i in range(len(slice_edges) - 1):
                start, end = slice_edges[i], slice_edges[i + 1]
                is_last = i == len(slice_edges) - 2
                mask = (slice_data >= start) & (slice_data <= end if is_last else slice_data < end)
                cont_in_slice = cont_data[mask]
                if len(cont_in_slice) < 2:
                    slice_info.append({"valid": False})
                    continue

                ratio = len(cont_in_slice) / global_target_yield
                n_floor, n_ceil = max(1, int(np.floor(ratio))), max(1, int(np.ceil(ratio)))

                if abs((len(cont_in_slice) / n_floor) - global_target_yield) <= abs((len(cont_in_slice) / n_ceil) - global_target_yield):
                    num_sub_bins = n_floor
                else:
                    num_sub_bins = n_ceil

                cont_is_quant = "njets" in v_cont_name or "nbtag" in v_cont_name or "tau_decaymode" in v_cont_name or BinningStrategyTargetBinning.is_quantized(cont_in_slice)

                if cont_is_quant:
                    secondary_edges = BinningStrategyTargetBinning.get_quantized_slice_bins(cont_in_slice, num_sub_bins, min_yield=global_target_yield)
                else:
                    secondary_edges = sorted(list(set(np.percentile(cont_in_slice, np.linspace(0, 100, num_sub_bins + 1)))))

                if len(secondary_edges) < 2:
                    secondary_edges = [np.min(cont_in_slice) - 1e-4, np.max(cont_in_slice) + 1e-4]

                num_sub_bins = len(secondary_edges) - 1
                slice_info.append({"valid": True, "num_sub_bins": num_sub_bins, "secondary_edges": secondary_edges})

            # Build the nested expression for bin index
            expression_parts, slice_conditions, bin_offset = [], [], 0
            for i, info in enumerate(slice_info):
                if not info["valid"]:
                    continue
                start_slice, end_slice = slice_edges[i], slice_edges[i + 1]
                is_last_slice = i == len(slice_edges) - 2

                sub_bin_expr_parts = []
                for j in range(info["num_sub_bins"]):
                    start_sub, end_sub = info["secondary_edges"][j], info["secondary_edges"][j + 1]
                    is_last_sub = j == info["num_sub_bins"] - 1
                    sub_cond = (
                        f"((({v1} != -10) && ({v2} != -10)) && (({v_cont_name} >= {start_sub}) && ({v_cont_name} {'<=' if is_last_sub else '<'} {end_sub})))"
                    )
                    sub_bin_expr_parts.append(f"{j}*{sub_cond}")

                sub_bin_index_expr = f"({' + '.join(sub_bin_expr_parts)})"

                slice_condition = f"((({v1} != -10) && (({v2} != -10)) && ({v_slice_name} >= {start_slice}) && ({v_slice_name} {'<=' if is_last_slice else '<'} {end_slice})))"
                slice_conditions.append(slice_condition)

                expression_parts.append(f"({bin_offset + 1} + {sub_bin_index_expr}) * {slice_condition}")

                bin_offset += info["num_sub_bins"]

            if not expression_parts:
                continue

            new_binning[f"{v1}_{v2}"] = {
                "bins": np.arange(bin_offset + 1, dtype=float) + 0.5,  # everything else lands in bin 0
                "expression": " + ".join(expression_parts),
                "cut": f"(({v1} > {v1_min}) && ({v1} < {v1_max}) && ({v2} > {v2_min}) && ({v2} < {v2_max}))",
            }

        return to_python_native(new_binning), correlations


class BinningStrategyYieldPerBin:
    def __init__(self, target_yield_per_bin=100.0):
        self.target_yield = float(target_yield_per_bin)
        self.bad_values = [-11.0, -999.0, -10.0, -1.0, np.nan, np.inf]

    def is_quantized(self, data, unique_threshold=30):
        if len(data) == 0:
            return False
        unique_vals = np.unique(data)
        is_integer_like = np.all(np.equal(np.mod(unique_vals, 1), 0))
        return is_integer_like and len(unique_vals) < unique_threshold

    def get_yield_based_edges(self, data, target_yield, is_quantized=False, high_cutoff=50, min_yield=None):
        total_events = len(data)
        if total_events == 0:
            return [-0.5, 0.5] if is_quantized else [0.0, 1.0]

        if total_events < target_yield:
            return [np.min(data) - (0.5 if is_quantized else 0), np.max(data) + (0.5 if is_quantized else 0)]

        if min_yield is None:
            min_yield = target_yield * 0.5

        if is_quantized:
            counts = Counter(data)
            sorted_vals = sorted(counts.keys())

            edges = [sorted_vals[0] - 0.5]
            current_bin_yield = 0

            for i, val in enumerate(sorted_vals):
                current_bin_yield += counts[val]

                if current_bin_yield >= target_yield:
                    remaining_events = total_events - np.sum([counts[v] for v in sorted_vals[: i + 1]])
                    # Tail protection
                    if i < len(sorted_vals) - 1 and remaining_events >= min_yield:
                        edges.append(val + 0.5)
                        current_bin_yield = 0

            if edges[-1] < high_cutoff + 0.5:
                edges[-1] = high_cutoff + 0.5

            return sorted(list(set(edges)))

        else:
            n_bins = int(total_events / target_yield)
            if n_bins < 1:
                n_bins = 1

            p_values = np.linspace(0, 100, n_bins + 1)
            edges = np.percentile(data, p_values)

            edges = sorted(list(set(edges)))
            edges[0] -= abs(edges[0] * 1e-4) if edges[0] != 0 else 1e-4
            edges[-1] += abs(edges[-1] * 1e-4) if edges[-1] != 0 else 1e-4

            return edges

    def calculate_1d_binning_from_numpy(self, channel, var_data_np, variables, percentiles=None):
        binning = {}

        for v in tqdm(variables, desc="Calculating 1D Yield-Based Binning"):
            raw_vals = var_data_np[v]
            values_clean = raw_vals[~np.isin(raw_vals, self.bad_values)]

            if len(values_clean) == 0:
                logger.warning(f"No valid values for variable {v}. Using dummy bins.")
                borders = [0.0, 1.0]
            else:
                quantized = self.is_quantized(values_clean)
                borders = self.get_yield_based_edges(values_clean, self.target_yield, is_quantized=quantized)

            binning[v] = {"bins": borders, "expression": v, "cut": f"(({v} > {borders[0]} ) && ( {v} < {borders[-1]}))"}

        return to_python_native(binning)

    def add_2d_unrolled_binning_from_numpy(self, variables, binning, var_data_np):
        new_binning, correlations = binning.copy(), {}

        for v1, v2 in tqdm(list(itertools.combinations(variables, 2)), desc="Calculating 2D Yield-Based Binning"):
            val1_raw, val2_raw = var_data_np[v1], var_data_np[v2]
            v1_min, v1_max = binning[v1]["bins"][0], binning[v1]["bins"][-1]
            v2_min, v2_max = binning[v2]["bins"][0], binning[v2]["bins"][-1]

            mask = (
                ~np.isin(val1_raw, self.bad_values)
                & ~np.isin(val2_raw, self.bad_values)
                & (val1_raw > v1_min)
                & (val1_raw < v1_max)
                & (val2_raw > v2_min)
                & (val2_raw < v2_max)
            )
            val1_local, val2_local = val1_raw[mask], val2_raw[mask]

            total_valid_events = len(val1_local)

            try:
                corr_val = np.corrcoef(val1_local, val2_local)[0, 1]
                correlations[f"{v1}_{v2}"] = float(0.0 if np.isnan(corr_val) else corr_val)
            except Exception as e:
                logger.warning(f"Could not compute correlation for {v1} and {v2}: {e}")
                correlations[f"{v1}_{v2}"] = 0.0

            if total_valid_events < self.target_yield:
                continue

            dynamic_slice_yield = np.sqrt(total_valid_events * self.target_yield)

            # Ensure slice yield isn't smaller than target yield (need at least 1 bin per slice)
            if dynamic_slice_yield < self.target_yield:
                dynamic_slice_yield = self.target_yield

            # Priority: Quantized > Continuous. If both same, larger range or alphabetical
            v1_quant = "njets" in v1 or "nbtag" in v1 or "tau_decaymode" in v1 or self.is_quantized(val1_local)
            v2_quant = "njets" in v2 or "nbtag" in v2 or "tau_decaymode" in v2 or self.is_quantized(val2_local)

            u1, u2 = len(np.unique(val1_local)), len(np.unique(val2_local))

            if v1_quant and not v2_quant:
                v_slice_name, v_cont_name, slice_data, cont_data = v1, v2, val1_local, val2_local
            elif v2_quant and not v1_quant:
                v_slice_name, v_cont_name, slice_data, cont_data = v2, v1, val2_local, val1_local
            elif u1 <= u2:
                v_slice_name, v_cont_name, slice_data, cont_data = v1, v2, val1_local, val2_local
            else:
                v_slice_name, v_cont_name, slice_data, cont_data = v2, v1, val2_local, val1_local

            # 4. Determine Primary Slices (Slicing Variable)
            slice_is_quantized_check = self.is_quantized(slice_data)

            slice_edges = self.get_yield_based_edges(slice_data, target_yield=dynamic_slice_yield, is_quantized=slice_is_quantized_check, min_yield=self.target_yield)

            bin_offset = 0
            expression_parts = []

            for i in range(len(slice_edges) - 1):
                start, end = slice_edges[i], slice_edges[i + 1]
                is_last_slice = i == len(slice_edges) - 2

                slice_mask = (slice_data >= start) & (slice_data <= end if is_last_slice else slice_data < end)
                cont_in_slice = cont_data[slice_mask]

                n_events_slice = len(cont_in_slice)
                ratio = n_events_slice / self.target_yield
                n_floor, n_ceil = max(1, int(np.floor(ratio))), max(1, int(np.ceil(ratio)))

                if abs((n_events_slice / n_floor) - self.target_yield) <= abs((n_events_slice / n_ceil) - self.target_yield):
                    num_sub_bins = n_floor
                else:
                    num_sub_bins = n_ceil

                cont_is_quant = "njets" in v_cont_name or "nbtag" in v_cont_name or "tau_decaymode" in v_cont_name or self.is_quantized(cont_in_slice)

                if cont_is_quant:
                    secondary_edges = self.get_yield_based_edges(cont_in_slice, target_yield=self.target_yield, is_quantized=True, min_yield=self.target_yield)
                else:
                    secondary_edges = sorted(list(set(np.percentile(cont_in_slice, np.linspace(0, 100, num_sub_bins + 1)))))

                if len(secondary_edges) < 2:
                    secondary_edges = [np.min(cont_in_slice) - 1e-4, np.max(cont_in_slice) + 1e-4]

                num_sub_bins = len(secondary_edges) - 1

                # Build Expression Strings
                sub_bin_expr_parts = []
                for j in range(num_sub_bins):
                    sub_start, sub_end = secondary_edges[j], secondary_edges[j + 1]
                    is_last_sub = j == num_sub_bins - 1

                    sub_cond = (
                        f"((({v1} != -10) && ({v2} != -10)) && (({v_cont_name} >= {sub_start}) && ({v_cont_name} {'<=' if is_last_sub else '<'} {sub_end})))"
                    )
                    sub_bin_expr_parts.append(f"{j}*{sub_cond}")

                sub_bin_index_expr = f"({' + '.join(sub_bin_expr_parts)})"
                slice_condition = (
                    f"((({v1} != -10) && (({v2} != -10)) && ({v_slice_name} >= {start}) && ({v_slice_name} {'<=' if is_last_slice else '<'} {end})))"
                )

                expression_parts.append(f"({bin_offset + 1} + {sub_bin_index_expr}) * {slice_condition}")

                bin_offset += num_sub_bins

            if not expression_parts:
                continue

            new_binning[f"{v1}_{v2}"] = {
                "bins": np.arange(bin_offset + 1, dtype=float) + 0.5,
                "expression": " + ".join(expression_parts),
                "cut": f"(({v1} > {v1_min}) && ({v1} < {v1_max}) && ({v2} > {v2_min}) && ({v2} < {v2_max}))",
            }

        return to_python_native(new_binning), correlations


def main(args):
    skim_file_path = os.path.join(args.output_folder, f".skimmed_{args.era}_{args.channel}.root")
    skim_file_path_np = skim_file_path.replace(".root", "_variables.pkl")

    if "," in args.variables[0]:
        variables = args.variables[0].split(",")
    else:
        variables = args.variables

    variables_unique = list(dict.fromkeys(variables))
    if len(variables_unique) != len(variables):
        logger.warning(f"Removed duplicate variables from input list: {sorted(set(v for v in variables if variables.count(v) > 1))}")
    variables = variables_unique
    args.variables = variables

    logger.info("Processing era {}".format(args.era))
    logger.info("Processing channel {}".format(args.channel))
    logger.info("Variables: {}".format(variables))

    if not os.path.exists(skim_file_path_np):
        build_binning_helper.main(args=args)
        logger.info(f"Skimmed ntuple and extracted variables saved to {skim_file_path} and {skim_file_path_np}")

    chain = build_binning_helper.build_chain({"tree_path": "ntuple"}, cache_path=skim_file_path)
    var_data_np = build_binning_helper.extract_data_from_chain(chain, variables, cache_path=skim_file_path.replace(".root", "_variables.pkl"))

    if args.njets_cut:
        expr = args.njets_cut.replace("&&", "&").replace("||", "|")
        mask = eval(expr, {}, var_data_np)
        var_data_np = {k: v[mask] for k, v in var_data_np.items()}
        logger.info(f"Applied filter '{args.njets_cut}'. Events: {len(mask)} -> {np.sum(mask)}")

    strategy = BinningStrategyTargetBinning()
    # strategy = BinningStrategyYieldPerBin(3000)

    if isinstance(strategy, BinningStrategyTargetBinning):
        percentiles = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        binning_1d = strategy.calculate_1d_binning_from_numpy(args.channel, var_data_np, variables, percentiles)
        binning_2d, correlations = strategy.add_2d_unrolled_binning_from_numpy(variables, binning_1d, var_data_np)

    if isinstance(strategy, BinningStrategyYieldPerBin):
        binning_1d = strategy.calculate_1d_binning_from_numpy(args.channel, var_data_np, variables)
        binning_2d, correlations = strategy.add_2d_unrolled_binning_from_numpy(variables, binning_1d, var_data_np)

    outputfile = os.path.join(args.output_folder, f"binning_{args.era}_{args.channel}.yaml")
    outputfile2d = os.path.join(args.output_folder, f"binning_{args.era}_{args.channel}_2D.yaml")

    with open(outputfile, "w") as f:
        yaml.dump(binning_1d, f, default_flow_style=False)

    logger.info(f"Done: 1d binning, written to {outputfile}")

    with open(outputfile2d, "w") as f:
        yaml.dump(binning_2d, f, default_flow_style=False)
    with open(outputfile2d.replace(".yaml", "_correlations.yaml"), "w") as f:
        yaml.dump(correlations, f, default_flow_style=False)

    logger.info(f"Done: 2d unrolled binning, written to {outputfile2d}")


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
