import argparse
import logging
import os
import pickle
import re

import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Set CMS Style ---
# This automatically handles ticks, fonts, and sizes to match your second image
plt.style.use(hep.style.CMS)


def c_to_py_syntax(expression):
    """Translates ROOT/C++ logic strings from YAML to Python/Numpy syntax."""
    expression = expression.replace("&&", "&")
    expression = expression.replace("||", "|")
    expression = re.sub(r"!(?!=)", "~", expression)
    expression = expression.replace("abs(", "np.abs(")
    expression = expression.replace("sqrt(", "np.sqrt(")
    return expression


def evaluate_expression(expression, data_dict):
    """Evaluates a string expression using variables found in data_dict."""
    py_expr = c_to_py_syntax(expression)
    try:
        return eval(py_expr, {"__builtins__": None, "np": np}, data_dict)
    except Exception as e:
        logger.error(f"Failed to evaluate expression: {py_expr}")
        raise e


def produce_histograms(yaml_path, pickle_path):
    """Calculates histograms from data."""
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML not found: {yaml_path}")
    if not os.path.exists(pickle_path):
        raise FileNotFoundError(f"Pickle not found: {pickle_path}")

    logger.info("Loading configuration and data...")
    with open(yaml_path, "r") as f:
        binning_config = yaml.safe_load(f)
    with open(pickle_path, "rb") as f:
        data = pickle.load(f)

    # Ensure numpy arrays
    for k, v in data.items():
        if not isinstance(v, np.ndarray):
            data[k] = np.array(v)

    results = {}

    for var_name, config in binning_config.items():
        bins = np.array(config["bins"])
        expression_str = config["expression"]
        cut_str = config["cut"]

        # 1. Apply Cut
        try:
            mask = evaluate_expression(cut_str, data)
        except NameError:
            continue  # Skip if variable missing

        masked_data = {k: v[mask] for k, v in data.items() if len(v) == len(mask)}
        if len(masked_data) == 0:
            continue

        # 2. Evaluate
        try:
            values = evaluate_expression(expression_str, masked_data)
        except NameError:
            continue

        # 3. Histogram
        counts, edges = np.histogram(values, bins=bins)
        errors = np.sqrt(counts)  # Poisson errors

        results[var_name] = {"counts": counts, "edges": edges, "errors": errors, "cut_string": cut_str}

    return results


def plot_style_reference(hist_data, output_folder, era="Run2", channel=""):
    """
    Plots histograms using exactly the style from the user's reference snippet:
    - ax.errorbar with fmt="ko"
    - markerfacecolor="none" (Open Circles)
    - Fixed Y-limits (1, 1e6)
    - Log Scale
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for var_name, h in hist_data.items():
        # Prepare Data
        counts = h["counts"].astype(float)
        edges = h["edges"]
        widths = np.diff(edges)
        centers = edges[:-1] + widths / 2

        # Poisson errors
        errors = np.sqrt(counts)

        # --- Detection Logic: 1D vs 2D ---
        # 2D Unrolled bins are always integers with width 1.0 (0.5, 1.5, 2.5...)
        is_unrolled_2d = np.allclose(widths, 1.0) and (edges[0] == 0.5 or edges[0] == 0.0)

        if is_unrolled_2d:
            # --- 2D Case (Events per Bin) ---
            # Raw counts, exactly like the reference snippet
            y_vals = counts
            y_errs = errors
            ylabel = "Events / bin"
            xlabel = var_name  # or f"Unrolled Bin Index ({var_name})"
        else:
            # --- 1D Case (Events per Unit) ---
            # Normalize by width for proper density representation
            y_vals = counts
            y_errs = errors
            ylabel = "Events / Unit"
            xlabel = var_name

        # --- Plotting ---
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        # This is the specific style requested:
        ax.errorbar(
            x=centers,
            y=y_vals,
            xerr=widths / 2,  # Errors cover the full bin width
            yerr=y_errs,
            fmt="ko",  # Black circles, no line connecting them
            label="data",
            markerfacecolor="none",  # The key: Open circles
            markersize=5,
            linewidth=1,  # Thinner lines for the error bars
        )

        # CMS Label
        hep.cms.label(loc=0, ax=ax, data=True, label="Work in Progress", rlabel=f"{era} {channel}")

        # Axes Styling
        ax.legend(loc="upper right")
        ax.set_yscale("log")
        ax.set_ylim(1, 1e6)  # Fixed limits as requested
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        # Save
        save_path = os.path.join(output_folder, f"{var_name}.png")
        # save_path_pdf = os.path.join(output_folder, f"{var_name}.pdf")

        logger.info(f"Saving plot to {save_path}")
        plt.savefig(save_path, bbox_inches="tight")
        # plt.savefig(save_path_pdf, bbox_inches='tight')
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yaml", type=str, required=True)
    parser.add_argument("--pickle", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--era", type=str, default="2018")
    parser.add_argument("--channel", type=str, default="mt")

    args = parser.parse_args()

    try:
        results = produce_histograms(args.yaml, args.pickle)
        plot_style_reference(results, args.output, era=args.era, channel=args.channel)
    except Exception as e:
        logger.exception("An error occurred.")


if __name__ == "__main__":
    main()
