import mplhep as hep
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import argparse
from itertools import product
import seaborn as sns
import matplotlib.colors as mcolors
from Dumbledraw.styles import x_label_dict
from typing import Optional

import logging
from itertools import product

from config.logging_setup_configs import setup_logging

logger = setup_logging(logger=logging.getLogger(__name__))


hep.style.use(hep.style.ROOT)
hep.style.use(hep.style.CMS)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Plot goodness of fit results")
    parser.add_argument("--variables", help="Considered variables in goodness of fit test")
    parser.add_argument("--path", help="Path to directory with goodness of fit results")
    parser.add_argument("--channel", type=str, help="Select channel to be plotted")
    parser.add_argument("--era", type=str, help="Select era to be plotted")
    parser.add_argument("-c", "--classification", type=str, default=None)
    parser.add_argument("-tc", "--threshold", type=float, default=0.05)
    parser.add_argument("-tt", "--test-type", type=str, default="gof", help="gof, gof_KS, gof_AD")
    return parser.parse_args()


def fetch_p_value(
    base_path: Path,
    prefix: str,
    var1: str,
    var2: str,
    test_type: str,
) -> Optional[float]:
    folder_path = base_path / (f"{prefix}_{var1}_{var2}" if var1 != var2 else f"{prefix}_{var1}")
    if not folder_path.exists() and var1 != var2:
        folder_path = base_path / f"{prefix}_{var2}_{var1}"

    if not folder_path.exists():
        return -1
    
    json_file = folder_path / f"{test_type}.json"
    if not json_file.exists():
        return -1

    try:
        with open(json_file, 'r') as f:
            content = f.read()
            if not content:
                return -1
            data = json.loads(content)
        
        mass_dict = data.get("125.0")
        if not isinstance(mass_dict, dict):
            return -1

        p_value = mass_dict.get("p")  # simple gof

        if p_value is None:  # KS or AD test
            if mass_dict and isinstance(mass_dict, dict):
                nested_dict = next(iter(mass_dict.values()), None)
                if isinstance(nested_dict, dict):
                    p_value = nested_dict.get("p")
        
        return float(p_value) if p_value is not None else -1
        
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return -1


def get_matrix(args: argparse.Namespace):
    p_values = -1 * np.zeros((len(args.variables), len(args.variables)))
    for (i, row_var), (j, col_var) in product(enumerate(args.variables), repeat=2):
        val = fetch_p_value(Path(args.path), f"{args.era}_{args.channel}", row_var, col_var, args.test_type)
        if val == -1:
            logger.warning(f"{row_var} - {col_var} not found")
        p_values[i, j] = val
        p_values[j, i] = val
    
    return p_values


def plot_2d_matrix(args: argparse.Namespace):
    vmin, vmax = -0.05, 1.0
    def frac(value):
        vmin, vmax = 0.0, 1.0
        return (value - vmin) / (vmax - vmin)

    cmap_list = [
        (0.0, "red"),
        (frac(0.0),  "red"),
        (frac(0.05),  "red"),
        (frac(0.05),  "green"),
        (frac(vmax), "green"),
    ]
    cmap = mcolors.LinearSegmentedColormap.from_list("segmented_cmap", cmap_list)
    norm = mcolors.Normalize(vmin=0.0, vmax=vmax)
    
    matrix = get_matrix(args)
    matrix[matrix == -1] = -0.05

    latex_variables = [
        r"$" + (
            x_label_dict[args.channel]
            .get(it, it)
            .replace("#slash", r"\not\!")
            .replace("#", "\\")
            .replace(" ", "\ ")
        ) + r"$"
        for it in variables
    ]

    fig, ax = plt.subplots(figsize=(18, 18))
    sns.heatmap(
        ax=ax,
        data=matrix,
        vmin=0,
        vmax=1,
        annot=True,
        fmt=".2f",
        annot_kws={"size": 12},
        xticklabels=latex_variables,
        yticklabels=latex_variables,
        cmap=cmap,
        norm=norm,
        cbar_kws={"ticks": [-1.0, 0.0, 0.05, 1.0], "label": "p-value"},
    )

    for ext in {"png", "pdf", "pgf"}:
        plt.savefig(Path(args.path) / f"gof_summary_2d_matrix_{args.test_type}.{ext}", bbox_inches='tight')


if __name__ == "__main__":
    args = parse_arguments()
    plot_2d_matrix(args)
