import logging
import sys
import os
import yaml
import pathlib
from collections import OrderedDict
import pandas as pd
import numpy as np
from itertools import pairwise, combinations
from typing import Union
from collections import OrderedDict
from rich.table import Table 

sys.path.extend([".", "trainings"])

from trainings.src.dataset_manipulation import ROOTToPlain
from trainings.src.helper import Iterate, Keys, PipeDict, RuntimeVariables, optional_process_pool
from config.logging_setup_configs import setup_logging, capture_rich_renderable_as_string, CONSOLE

logger = setup_logging(logger=logging.getLogger(__name__), console_markup=True)

def _equipopulated_binned_variable(
    item: Union[np.ndarray, pd.Series],
    n_bins: int,
    weights: Union[np.ndarray, list, None] = None
) -> Union[np.ndarray, list]:
    """
    Helper function to calculate equipopulated bin edges.

    Args:
        item (pd.Series or np.ndarray): The data to bin.
        n_bins (int): The number of bins to create.
        weights (np.ndarray or list, optional): Weights for the data points. If None, uniform weights are assumed.

    Returns:
        list: A list of bin edges.
    """
    
    item = item.dropna()
    weights = weights[item.index] if weights is not None else None

    if len(item) == 0 or n_bins == 0:
        return np.array([])

    return np.quantile(
        a=item,
        q=np.linspace(0, 1, n_bins + 1),
        weights=weights,
        method="linear" if weights is None else "inverted_cdf",
    )


def get_events_per_bin(df: pd.DataFrame, variable: str, bins: list) -> list:
    """
    Calculates the number of events in each bin.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        variable (str): The column name of the variable to bin.
        bins (list): The list of bin edges.

    Returns:
        list: A list of counts of events in each bin.
    """
    if not bins or len(bins) < 2: return []
    counts = []
    pairs = list(pairwise(bins))
    for lower, upper in pairs[:-1]:
        count = df.query(f"{variable} >= {lower} and {variable} < {upper}").shape[0]
        counts.append(count)
    lower_last, upper_last = pairs[-1]
    count_last = df.query(f"{variable} >= {lower_last} and {variable} <= {upper_last}").shape[0]
    counts.append(count_last)
    return counts


def generate_equipopulated_bins(
    df: pd.DataFrame,
    config: dict,
    weights_column: str = None,
    separator: str = ";",
) -> dict:
    """
    Generates 1D or 2D equipopulated binning from a pre-filtered DataFrame.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        config (dict): Configuration dictionary specifying variables and binning options.
        weights_column (str, optional): Column name for weights. If None, uniform weights are assumed.
        separator (str, optional): Separator for 2D variable keys in the config. Default is ';'.

    Returns:
        dict: A dictionary with variable names as keys and lists of bin edges or nested dictionaries for 2D binning as values.
        The structure is as follows:
            {
                "var1": [edges],
                "var2;var3": {
                    "(var2 >= a && var2 < b)": [edges_var3],
                    "(var2 >= b && var2 <= c)": [edges_var3],
                    ...
                },
                ...
            }
    """
    output_bins = OrderedDict()
    weights = df[weights_column] if weights_column and weights_column in df else None

    logger.info(f"Starting bin generation for {len(config)} variable(s)...")

    class Defaults:
        rounding: int = 4
        n_bins: int = 10

    for var_key, options in config.items():
        options = options or {} 
        logger.info(f"\nProcessing [bold cyan]'{var_key}'[/bold cyan]")

        if separator in var_key:  # 2D Case
            try:
                var1, var2 = var_key.split(separator)
                n_bins1, n_bins2 = options.get("n_bins", [Defaults.n_bins, Defaults.n_bins])
                rounding1, rounding2 = options.get("rounding", [Defaults.rounding, Defaults.rounding])
            except (ValueError, IndexError) as e:
                logger.error(f"  [red]ERROR[/red]: Invalid config for 2D binning '{var_key}'. Skipping. Details: {e}")
                continue
            
            output_bins[var_key] = OrderedDict()
            
            if var1 not in df or df[var1].notna().sum() == 0:
                logger.warning(f"  [yellow]WARNING[/yellow]: Primary axis variable '{var1}' not found or has no valid data. Skipping 2D binning.")
                continue

            edges1 = _equipopulated_binned_variable(df[var1], n_bins1, weights)
            unique_edges1 = np.unique(edges1)

            if len(unique_edges1) - 1 < n_bins1 and len(unique_edges1) > 1:
                logger.warning(f"  [dim]Note: Requested {n_bins1} bins for '{var1}', but generated {len(unique_edges1) - 1} unique bins due to discrete data.[/dim]")
            if len(unique_edges1) < 2:
                logger.warning(f"  [yellow]WARNING[/yellow]: Could not generate more than one unique bin for primary axis '{var1}'. Skipping 2D binning.")
                continue
            edges1_rounded = np.round(unique_edges1, rounding1)
            
            # Pre-compute validity of each initial bin
            bin_specs = []
            for i, (lower, upper) in enumerate(pairwise(edges1_rounded)):
                is_last_bin = (i == len(edges1_rounded) - 2)
                mask_str = f"({var1} >= {lower}) & ({var1} <= {upper})" if is_last_bin else f"({var1} >= {lower}) & ({var1} < {upper})"
                sub_df = df.query(mask_str)
                is_valid = not sub_df.empty and sub_df[var2].notna().any()
                bin_specs.append({"lower": lower, "upper": upper, "is_valid": is_valid, "is_last_bin": is_last_bin})

            # Group consecutive invalid bins with next valid one
            bin_groups = []
            current_group = []
            for spec in bin_specs:
                current_group.append(spec)
                if spec["is_valid"]:
                    bin_groups.append(current_group)
                    current_group = []
            
            # If last bins invalid: merge with last valid group
            if current_group and bin_groups:
                bin_groups[-1].extend(current_group)

            if not bin_groups:
                logger.error(f"  [red]ERROR[/red]: No bins in '{var1}' contain any valid data for '{var2}'. Cannot generate 2D binning.")
                continue

            table = Table(title=f"Binning for '{var2}' nested in '{var1}'", show_header=True, header_style="bold magenta")
            table.add_column(f"Primary Slice ({var1})", style="dim", width=42)
            table.add_column("Total Events", justify="right")
            table.add_column(f"Bin Edges ({var2})", style="yellow")
            table.add_column("Events/Bin", style="green")

            # Process the merged groups
            for group in bin_groups:
                lower_bound = group[0]['lower']
                upper_bound = group[-1]['upper']
                is_last_group_bin = group[-1]['is_last_bin']

                if len(group) > 1:
                     logger.warning(f"  [dim]Note: Merging {len(group)} bins of '{var1}' from {lower_bound} to {upper_bound} due to missing '{var2}' data.[/dim]")

                mask_str = f"({var1} >= {lower_bound}) & ({var1} <= {upper_bound})" if is_last_group_bin else f"({var1} >= {lower_bound}) & ({var1} < {upper_bound})"
                category_key = mask_str.replace(" & ", " && ")
                
                sub_df = df.query(mask_str)
                sub_weights = sub_df[weights_column] if weights_column in sub_df else None
                
                edges2 = _equipopulated_binned_variable(sub_df[var2], n_bins2, sub_weights)
                unique_edges2 = np.unique(edges2)
                
                if len(unique_edges2) < 2:
                     edges2_rounded_str = "[dim]Could not bin[/dim]"
                     events_in_bins_2_str = ""
                     output_bins[var_key][category_key] = []
                else:
                    edges2_rounded = np.round(unique_edges2, rounding2).tolist()
                    events_in_bins_2 = get_events_per_bin(sub_df, var2, edges2_rounded)
                    output_bins[var_key][category_key] = edges2_rounded
                    edges2_rounded_str = str(edges2_rounded)
                    events_in_bins_2_str = str(events_in_bins_2)

                table.add_row(category_key, str(len(sub_df)), edges2_rounded_str, events_in_bins_2_str)

            table_string = capture_rich_renderable_as_string(table, width=400).strip()
            logger.info(table_string, extra={'file_only': True})
            CONSOLE.print(table)

        else:  # 1D Case
            try:
                n_bins = options.get("n_bins", Defaults.n_bins)
                rounding = options.get("rounding", Defaults.rounding)
            except (KeyError, TypeError) as e:
                logger.error(f"  [red]ERROR[/red]: Invalid config for 1D binning '{var_key}'. Skipping. Details: {e}")
                continue

            if var_key not in df or df[var_key].notna().sum() == 0:
                logger.warning(f"  [yellow]WARNING[/yellow]: Variable '{var_key}' not found or contains only NaN values. Skipping.")
                continue

            edges = _equipopulated_binned_variable(df[var_key], n_bins, weights)
            unique_edges = np.unique(edges)

            if len(unique_edges) - 1 < n_bins and len(unique_edges) > 1:
                logger.info(f"  [dim]Note: Requested {n_bins} bins, but generated {len(unique_edges) - 1} unique bins due to discrete data.[/dim]")
            if len(unique_edges) < 2:
                logger.warning(f"  [yellow]WARNING[/yellow]: Could not generate more than one unique bin for '{var_key}'. Resulting edges: {unique_edges.tolist()}. Skipping.")
                continue
            
            edges_rounded = np.round(unique_edges, rounding).tolist()
            output_bins[var_key] = edges_rounded
            events_in_bins = get_events_per_bin(df, var_key, edges_rounded)
            
            table = Table(title=f"Binning for '{var_key}'", show_header=True, header_style="bold magenta")
            table.add_column("Category", style="dim", width=42) # Re-use width for alignment
            table.add_column("Total Events", justify="right")
            table.add_column(f"Bin Edges ({var_key})", style="yellow")
            table.add_column("Events/Bin", style="green")

            table.add_row(
                f"Full Range ({var_key})",
                str(df[var_key].notna().sum()),
                str(edges_rounded),
                str(events_in_bins)
            )

            table_string = capture_rich_renderable_as_string(table, width=400).strip()
            logger.info(table_string, extra={'file_only': True})
            CONSOLE.print(table)

    return output_bins


def to_dict(obj: Union[dict, list, OrderedDict]) -> Union[dict, list]:
    """
    Recursively converts an OrderedDict to a standard dict.

    Args:
        obj (Union[dict, list, OrderedDict]): The object to convert.

    Returns:
        Union[dict, list]: The converted object.
    """
    if isinstance(obj, OrderedDict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_dict(v) for v in obj]
    else:
        return obj


if __name__ == "__main__":
    raw_path, filtered_path = pathlib.Path("./.tmp/raw"), pathlib.Path("./.tmp/filtered")
    raw_path.mkdir(parents=True, exist_ok=True)
    filtered_path.mkdir(parents=True, exist_ok=True)

    with open("tmp.yml", "r") as f:
        config = yaml.safe_load(f)
        
    channel, era, process = "mt", "2018", "jetFakes"
        
    definitions_and_cuts = list(Iterate.common_dict(config[channel][era][process][Keys.COMMON]))

    df = ROOTToPlain(
        raw_path=f"{raw_path}/raw_data.feather",
        filtered_path=f"{filtered_path}/filtered_data.feather",
    ).setup_raw_dataframe(
        tree_and_filepaths=list(Iterate.rdf_files(config[channel][era][process][Keys.PATHS])),
        definitions=[it for it in definitions_and_cuts if "__common__" not in it[0]],
        additional_columns=list(config[channel][era][process][Keys.VARIABLES].keys()),
        filters=[it for it in definitions_and_cuts if it[0] in config[channel][era][process][process][Keys.NOMINAL][Keys.CUT]],
        description=f"{channel}_{era}_{process}_{process}",
        max_workers=20,
    ).dataframe

    df = df.drop(columns=[it for it in df.columns if it.startswith("is_") or any(subit in it for subit in ["event"])])
    df = df.replace(-10.0, np.nan)

    myconfig = {
        **{
            key: {
                "n_bins": 10,
                "rounding": 4,
            }
            for key in df.columns
        },
        **{
            ";".join(it): {
                "n_bins": [10, 10],
                "rounding": [4, 4],
            }
            for it in combinations(df.columns, 2)
        },
    }

    with open("gof_binning_autogenerated_config.yaml", "w") as f:
        yaml.dump(to_dict(generate_equipopulated_bins(df, myconfig)), f)
