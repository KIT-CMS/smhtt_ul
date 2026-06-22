import mplhep as hep
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import argparse
from itertools import product, combinations_with_replacement, combinations
import seaborn as sns
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
from Dumbledraw.styles import x_label_dict
from typing import Optional, Callable, Dict, Set, Tuple
import matplotlib.ticker as mplticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
import yaml
import logging
from scipy.stats import norm

from config.logging_setup_configs import setup_logging

logger = setup_logging(logger=logging.getLogger(__name__))

hep.style.use(hep.style.CMS)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Plot goodness of fit results")
    parser.add_argument("--variables", help="Considered variables (comma separated)")
    parser.add_argument("--path", help="Path to directory with results")
    parser.add_argument("--channel", type=str, help="Channel")
    parser.add_argument("--era", type=str, help="Era")
    parser.add_argument("--corr-path", type=str, default="./config/gof_binning/binning_2018_mt_2D_correlations.yaml")
    parser.add_argument("-a", "--alpha", type=float, default=0.05, help="Alpha level")
    parser.add_argument("-tt", "--test-type", type=str, default="gof")
    return parser.parse_args()


def fetch_p_value(base_path: Path, prefix: str, var1: str, var2: str, test_type: str) -> float:
    p1 = base_path / (f"{prefix}_{var1}_{var2}" if var1 != var2 else f"{prefix}_{var1}")
    p2 = base_path / f"{prefix}_{var2}_{var1}"

    folder_path = None
    if p1.exists():
        folder_path = p1
    elif p2.exists():
        folder_path = p2
    else:
        return -1.0

    json_file = folder_path / f"{test_type}.json"
    if not json_file.exists():
        return -1.0

    try:
        with open(json_file, "r") as f:
            content = f.read()
            if not content:
                return -1.0
            data = json.loads(content)

        mass_dict = data.get("125.0")
        if not isinstance(mass_dict, dict):
            return -1.0

        p_value = mass_dict.get("p")
        if p_value is None and mass_dict:
            nested = next(iter(mass_dict.values()), None)
            if isinstance(nested, dict):
                p_value = nested.get("p")

        return float(p_value) if p_value is not None else -1.0
    except (KeyError, json.JSONDecodeError, ValueError):
        return -1.0


def Meff(correlation_matrix: np.ndarray) -> float:
    assert (correlation_matrix.T == correlation_matrix).all(), "Matrix must be symmetric"
    M = correlation_matrix.shape[0]
    var = np.var(np.linalg.eigvalsh(correlation_matrix), ddof=0)
    return 1 + (M - 1) * (1 - (var / M))


def get_holm_step_down_results(args: argparse.Namespace, p_values_dict: Dict[str, float]) -> Tuple[Set[str], float]:
    variables = args.variables
    corr_path = Path(args.corr_path)

    if not corr_path.exists():
        logger.warning("Correlation file not found. Using identity.")
        correlations_matrix = np.eye(len(variables))
    else:
        with open(corr_path, "r") as f:
            existing_correlations = yaml.safe_load(f)
        correlations_matrix = np.eye(len(variables))
        for (i, v1), (j, v2) in combinations(enumerate(variables), 2):
            key = f"{v1}_{v2}" if f"{v1}_{v2}" in existing_correlations else f"{v2}_{v1}"
            corr = existing_correlations.get(key, 0.0)
            correlations_matrix[i, j] = corr
            correlations_matrix[j, i] = corr

    m_eff = Meff(correlations_matrix)  # no correction here would be: correlations_matrix.shape[0]
    logger.info(f"M_eff: {m_eff:.4f}")

    valid_items = {k: v for k, v in p_values_dict.items() if v >= 0 and not np.isnan(v)}
    sorted_items = sorted(valid_items.items(), key=lambda x: x[1])
    rejected_keys = set()
    for i, (key, p_val) in enumerate(sorted_items):
        k = i + 1
        denom = m_eff + 1 - k
        if denom <= 0:
            break  # Avoid invalid thresholds
        threshold = args.alpha / denom
        if p_val > threshold:
            break  # Stop and accept remaining
        rejected_keys.add(key)

    return rejected_keys, m_eff


def get_benjamini_hochberg_results(args: argparse.Namespace, p_values_dict: Dict[str, float]) -> Tuple[Set[str], float]:
    """
    Benjamini-Hochberg procedure adapted for Effective Number of Tests (M_eff).
    Controls False Discovery Rate (FDR).
    """
    variables = args.variables
    corr_path = Path(args.corr_path)

    # 1. Filter and Sort p-values
    valid_items = {k: v for k, v in p_values_dict.items() if v >= 0 and not np.isnan(v)}
    sorted_items = sorted(valid_items.items(), key=lambda x: x[1])
    n_tests_performed = len(sorted_items)

    rejected_keys = set()

    # 2. Calculate M_eff
    if not corr_path.exists():
        logger.warning("Correlation file not found. Using identity.")
        m_eff_tests = float(n_tests_performed)
    else:
        with open(corr_path, "r") as f:
            existing_correlations = yaml.safe_load(f)
        correlations_matrix = np.eye(len(variables))
        for (i, v1), (j, v2) in combinations(enumerate(variables), 2):
            key = f"{v1}_{v2}" if f"{v1}_{v2}" in existing_correlations else f"{v2}_{v1}"
            corr = existing_correlations.get(key, 0.0)
            correlations_matrix[i, j] = corr
            correlations_matrix[j, i] = corr

        m_eff_vars = Meff(correlations_matrix)
        m_eff_vars = correlations_matrix.shape[0]
        # Calculate Effective Tests (Triangle number)
        m_eff_tests = (m_eff_vars * (m_eff_vars + 1)) / 2
        # Safety cap
        m_eff_tests = min(m_eff_tests, float(n_tests_performed))

    logger.info(f"M_eff (Tests): {m_eff_tests:.4f}")

    # 3. Step-Up Procedure
    # Find largest k such that p_(k) <= (k / M_eff) * alpha
    max_k_reject = -1

    for i, (key, p_val) in enumerate(sorted_items):
        k = i + 1  # Rank (1-based)

        # BH Threshold
        threshold = (k / m_eff_tests) * args.alpha

        if p_val <= threshold:
            max_k_reject = i

    if max_k_reject != -1:
        for i in range(max_k_reject + 1):
            rejected_keys.add(sorted_items[i][0])

    return rejected_keys, m_eff_tests


def get_stouffer_z_score_results(args: argparse.Namespace, p_values_dict: Dict[str, float]) -> Tuple[Set[str], float]:
    """
    Row-wise Stouffer's Z-Score method.
    Aggregates p-values for each variable to find systematically bad features.
    """
    variables = args.variables
    corr_path = Path(args.corr_path)

    rejected_keys = set()

    # 1. Calculate M_eff for Variables (not tests)
    if not corr_path.exists():
        m_eff_vars = float(len(variables))
    else:
        with open(corr_path, "r") as f:
            existing_correlations = yaml.safe_load(f)
        correlations_matrix = np.eye(len(variables))
        for (i, v1), (j, v2) in combinations(enumerate(variables), 2):
            key = f"{v1}_{v2}" if f"{v1}_{v2}" in existing_correlations else f"{v2}_{v1}"
            corr = existing_correlations.get(key, 0.0)
            correlations_matrix[i, j] = corr
            correlations_matrix[j, i] = corr
        m_eff_vars = Meff(correlations_matrix)

    logger.info(f"M_eff (Variables): {m_eff_vars:.4f}")

    # 2. Iterate over each variable to calculate its aggregate score
    # We apply a Bonferroni correction for the number of Effective Variables
    row_threshold = args.alpha / m_eff_vars

    for var in variables:
        # Collect all p-values involving this variable
        p_vals_for_var = []
        related_keys = []

        for key, val in p_values_dict.items():
            if val < 0 or np.isnan(val):
                continue

            # Key format is usually "var1_var2"
            # We check if 'var' is part of the key
            if f"{var}_" in key or f"_{var}" in key:
                p_vals_for_var.append(val)
                related_keys.append(key)

        if not p_vals_for_var:
            continue

        # 3. Convert to Z-scores
        # Clip p-values to avoid infinity (standard numerical safety)
        p_clipped = np.clip(p_vals_for_var, 1e-15, 1.0 - 1e-15)
        z_scores = norm.ppf(1 - p_clipped)

        # Stouffer's Sum
        # Note: Ideally we would weight this by the correlation of the specific pairs,
        # but unweighted Stouffer is standard for simple screening.
        z_sum = np.sum(z_scores)
        z_combined = z_sum / np.sqrt(len(z_scores))

        # Convert back to p-value
        p_combined = 1 - norm.cdf(z_combined)

        # 4. Reject Logic
        if p_combined <= row_threshold:
            logger.info(f"Stouffer Reject: Variable '{var}' (p_comb={p_combined:.2e})")
            # If the variable is bad, we mark ALL its pairings as rejected
            for k in related_keys:
                rejected_keys.add(k)

    return rejected_keys, m_eff_vars


def get_higher_criticism_results(args: argparse.Namespace, p_values_dict: Dict[str, float]) -> Tuple[Set[str], float]:
    """
    Higher Criticism (HC) thresholding.
    Identifies the subset of p-values that maximize the deviation from the Null Hypothesis.
    """
    variables = args.variables
    corr_path = Path(args.corr_path)

    # 1. Filter and Sort
    valid_items = {k: v for k, v in p_values_dict.items() if v >= 0 and not np.isnan(v)}
    sorted_items = sorted(valid_items.items(), key=lambda x: x[1])
    n_tests = len(sorted_items)

    rejected_keys = set()

    # 2. M_eff calculation
    if not corr_path.exists():
        m_eff_tests = float(n_tests)
    else:
        with open(corr_path, "r") as f:
            existing_correlations = yaml.safe_load(f)
        correlations_matrix = np.eye(len(variables))
        for (i, v1), (j, v2) in combinations(enumerate(variables), 2):
            key = f"{v1}_{v2}" if f"{v1}_{v2}" in existing_correlations else f"{v2}_{v1}"
            corr = existing_correlations.get(key, 0.0)
            correlations_matrix[i, j] = corr
            correlations_matrix[j, i] = corr
        m_eff_vars = Meff(correlations_matrix)
        m_eff_tests = (m_eff_vars * (m_eff_vars + 1)) / 2
        m_eff_tests = min(m_eff_tests, float(n_tests))

    logger.info(f"M_eff (HC Normalization): {m_eff_tests:.4f}")

    # 3. Calculate HC Statistic for every k
    # HC_k = sqrt(N) * ( (k/N) - p_(k) ) / sqrt( p_(k)*(1-p_(k)) )
    # Adapted: Use M_eff for N

    hc_scores = []

    for i, (key, p_val) in enumerate(sorted_items):
        k = i + 1

        # Observed fraction vs Expected fraction
        observed_frac = k / m_eff_tests
        expected_p = p_val

        # Singularity protection
        if expected_p <= 0 or expected_p >= 1:
            hc_val = 0.0
        else:
            numerator = np.sqrt(m_eff_tests) * (observed_frac - expected_p)
            denominator = np.sqrt(expected_p * (1 - expected_p))
            hc_val = numerator / denominator

        hc_scores.append(hc_val)

    # 4. Find the maximizing k (The "Signal" boundary)
    if not hc_scores:
        return rejected_keys, m_eff_tests

    max_hc_idx = np.argmax(hc_scores)
    max_hc_val = hc_scores[max_hc_idx]

    # 5. Decision Rule
    # Standard HC uses the objective function to find the cut.
    # We only reject if the max HC indicates a deviation (positive) and is reasonably significant.
    # A simplified engineering threshold is commonly > 2.0 (approx 2 sigma deviation)

    if max_hc_val > 2.0:
        logger.info(f"Higher Criticism Signal found: HC={max_hc_val:.2f} at rank {max_hc_idx+1}")
        for i in range(max_hc_idx + 1):
            rejected_keys.add(sorted_items[i][0])

    return rejected_keys, m_eff_tests


testing_function = get_holm_step_down_results


def plot_2d_matrix(args: argparse.Namespace, label_func: Callable):
    n_vars = len(args.variables)
    p_values_dict = {}
    p_value_matrix = np.full((n_vars, n_vars), -1.0)

    for i, row_var in enumerate(args.variables):
        for j, col_var in enumerate(args.variables):
            if i < j:
                continue  # Skip upper triangle loop for fetching

            val = fetch_p_value(Path(args.path), f"{args.era}_{args.channel}", row_var, col_var, args.test_type)

            p_value_matrix[i, j] = val
            p_value_matrix[j, i] = val

            p_values_dict[f"{row_var}_{col_var}"] = val

    rejected_keys, m_eff = testing_function(args, p_values_dict)

    status_matrix = np.zeros((n_vars, n_vars))
    annot_text_matrix = np.empty((n_vars, n_vars), dtype=object)

    for i, row_var in enumerate(args.variables):
        for j, col_var in enumerate(args.variables):
            val = p_value_matrix[i, j]
            if i >= j:
                key = f"{row_var}_{col_var}"
            else:
                key = f"{col_var}_{row_var}"
            if val == -1 or np.isnan(val):
                annot_text_matrix[i, j] = "N/A"
                status_matrix[i, j] = -1
            else:
                annot_text_matrix[i, j] = f"{val:.3f}"
                # Check status
                status_matrix[i, j] = 0.0 if key in rejected_keys else 1.0

    mask = np.triu(np.ones_like(status_matrix, dtype=bool), k=1)

    cmap = mcolors.ListedColormap(["red", "green"])
    bounds = [-0.5, 0.5, 1.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    masked_status = np.ma.masked_where(status_matrix == -1, status_matrix)
    cmap.set_bad(color="white")

    latex_variables = [
        r"$" + (x_label_dict[args.channel].get(it, it).replace("#slash", r"\not\!").replace("#", "\\").replace(" ", "\ ")) + r"$" for it in args.variables
    ]

    cell_size = 1.0
    fig_size = max(6, cell_size * n_vars)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))

    label_func(ax)

    sns.heatmap(
        ax=ax,
        data=masked_status,
        mask=mask,
        annot=False,
        xticklabels=latex_variables,
        yticklabels=latex_variables,
        cmap=cmap,
        norm=norm,
        cbar=False,
        vmin=0,
        vmax=1,
        square=True,
        linewidths=1,
        linecolor="white",
    )

    for _, spine in ax.spines.items():
        spine.set_visible(True)
        spine.set_color("black")
        spine.set_linewidth(1)

    for i in range(n_vars):
        for j in range(n_vars):
            if i < j:
                continue  # Skip upper triangle
            val_status = status_matrix[i, j]
            if val_status == -1:
                continue
            text = annot_text_matrix[i, j]
            text_color = "black" if val_status == 0 else "white"
            ax.text(j + 0.5, i + 0.5, text, ha="center", va="center", color=text_color, fontweight="medium", fontsize=14)

    legend_elements = [
        Patch(facecolor="red", edgecolor="black", label="Rejected"),
        Patch(facecolor="green", edgecolor="black", label="Accepted"),
    ]

    stats_text = (
        f"$\\bf{{Holm-Step-Down}}$\n"
        f"$\\alpha = {args.alpha}, \\; M_{{eff}} = {m_eff:.1f}, \\; p_{{(1)}} \\leq \\dots \\leq p_{{(N)}}$\n"
        f"Reject $H_{{0}}^{{(k)}}$ if $p_{{(k)}} \\leq \\frac{{\\alpha}}{{M_{{eff}} + 1 - k}}$"
    )

    leg = ax.legend(handles=legend_elements, title=stats_text, loc="upper right", bbox_to_anchor=(0.98, 0.98), frameon=True, framealpha=1.0, edgecolor="black")

    leg.get_title().set_ha("left")

    ax.set_aspect("equal", "box")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", va="top")
    plt.setp(ax.get_yticklabels(), rotation=0, ha="right", va="center")

    ax.xaxis.set_minor_locator(mplticker.NullLocator())
    ax.yaxis.set_minor_locator(mplticker.NullLocator())

    plt.tight_layout(rect=[0, 0, 0.96, 1])

    for ext in {"png", "pdf"}:
        out_name = f"gof_summary_2d_matrix_{args.test_type}_holm.{ext}"
        p = Path(args.path) / out_name
        logger.info(f"Saving {p}")
        plt.savefig(p, bbox_inches="tight")


if __name__ == "__main__":
    args = parse_arguments()
    args.variables = [v.strip() for v in args.variables.split(",")]

    label_func = lambda ax: (hep.cms.label("Private Work", data=True, lumi=59.8, year=2018, ax=ax, fontsize=18))

    plot_2d_matrix(args, label_func)
