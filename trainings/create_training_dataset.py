import argparse
import logging
import os
from copy import deepcopy
from functools import partial
from pathlib import Path
from typing import Iterable, Tuple, Union
from collections import defaultdict

import numpy as np
import pandas as pd
import yaml
from src.dataset_manipulation import CombinedDataFrameManipulation, ProcessDataFrameManipulation, ROOTToPlain, tuple_column
from src.helper import Iterate, Keys, PipeDict, RuntimeVariables, optional_process_pool
from tqdm import tqdm

try:
    from config.logging_setup_configs import setup_logging
except ModuleNotFoundError:
    import sys
    sys.path.extend([".", ".."])
    from config.logging_setup_configs import setup_logging


def parse_args():
    parser = argparse.ArgumentParser(description="Create training datasets")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the config file",
    )
    parser.add_argument(
        "--base-dataset-directory",
        type=str,
        default=f"/ceph/{os.environ['USER']}/smhtt_ul_new/training_datasets",
        help="Base directory for the output files",
    )
    parser.add_argument(
        "--common-setup-config",
        type=str,
        default="",
        help="Path to the common setup config file",
    )
    return parser.parse_args()


def tiled_mask(
    df: pd.DataFrame,
    pattern: Iterable[bool],
) -> np.ndarray:
    """
    Helper to create a mask for the training and validation folds.
    The pattern is repeated to cover the length of the dataframe.

    Args:
        df (pd.DataFrame): The dataframe to create the mask for.
        pattern (Iterable[bool]): The pattern to repeat, i.e. [True, True, False, False].

    Returns:
        np.ndarray: A boolean mask of the same length as the dataframe.
    """
    return np.tile(pattern, int(np.ceil(len(df) / len(pattern))))[:len(df)].astype(bool)


def odd_id(df: pd.DataFrame, key: str = "event") -> np.ndarray:
    """
    Helper to create a mask for odd IDs.

    Args:
        df (pd.DataFrame): The dataframe to create the mask for.

    Returns:
        np.ndarray: A boolean mask of the same length as the dataframe.
    """
    return (df[Keys.EVENT][key] % 2).astype(bool)


def exemplary_remove_cut_regions(df: pd.DataFrame, regions: Iterable[str]) -> pd.DataFrame:
    """
    Exemplary function.

    Removes the cut regions from the dataframe that are not needed for the training.

    Args:
        df (pd.DataFrame): The dataframe to remove the cut regions from.
        regions (Iterable[str]): The regions to remove.

    Returns:
        pd.DataFrame: The dataframe without the cut regions.
    """
    for region in regions:
        cut_column = tuple_column(Keys.NOMINAL, region, Keys.CUT)
        if cut_column in df.columns:
            df = df[~df[cut_column].astype(bool)].copy()
            for column in df.columns:
                _level0, _level1, *_ = column
                if (_level0, _level1) == (Keys.NOMINAL, region):
                    df = df.drop(column, axis=1)

    return df.copy()


def exemplary_custom_selection(df: pd.DataFrame, selections: Union[None, dict] = None) -> pd.DataFrame:
    """
    Exemplary function.

    Selects the processes (subprocesses) and cut regions that are needed for the training.

    Args:
        df (pd.DataFrame): The dataframe to select the processes and cut regions from.
        optimize_selection (bool): If True, the selection is optimized to including only the needed cut regions.
            If False, all cut regions are included.
            Default is False.

    Returns:
        pd.DataFrame: The dataframe with the selected processes and cut regions.
    """
    
    is_nominal = [it for it in df.columns if Keys.CUT in it]  # applied for nominal region
    is_anti_iso = [it for it in df.columns if Keys.ANTI_ISO_CUT in it]  # applied for anti iso region

    _mapping = {
        "nominal": [is_nominal],
        "anti_iso": [is_anti_iso],
        "anti_iso+nominal": [is_nominal, is_anti_iso],
        "nominal+anti_iso": [is_nominal, is_anti_iso],
    }

    selections = defaultdict(lambda: "nominal", selections or {}) 
    
    mask = False
    for _process_label_column in df[Keys.LABELS].columns:
        _process = _process_label_column[0]
        
        selection_mask = df[sum(_mapping[selections[_process]], start=[])].astype(bool).any(axis=1)
        process_mask = df[tuple_column(Keys.LABELS, *_process_label_column)].astype(bool)
        
        mask |= (process_mask & selection_mask)

    return df[mask].copy()


def collect_filtered_plain_dataframes(arguments: Tuple[dict, str, str, str, str, dict]) -> dict:
    """
    Function to collect filtered plain dataframes. It creates raw and filtered dataframes
    and stores them if not present applying basic filter, collecting any cuts.

    Args:
        arguments (Tuple[dict, str, str, str, str, dict]): A tuple containing the config,
            config: dict: The config dictionary.
            channel: str: The channel name.
            era: str: The era name.
            process: str: The process name.
            subprocess: str: The subprocess name.
            subprocess_dict: dict: The subprocess dictionary.

    Returns:
        dict: A dictionary containing the filtered plain dataframes.
    """
    config, channel, era, process, subprocess, subprocess_dict = arguments

    def _path(directory, extension="feather"):
        name = f"{channel}_{era}_{process}_{subprocess}.{extension}"
        return (Path(args.base_dataset_directory) / Path(directory)).joinpath(name)

    def any_cut(df):
        pattern = "__common__cut__"
        return df[[it for it in df.columns if it.startswith(pattern)]].any(axis=1)

    # TODO:: Columns can be set here, also independent of the config!
    tree_and_filepaths_tuples = list(Iterate.rdf_files(config[channel][era][process][Keys.PATHS]))
    definitions_tuples = list(Iterate.common_dict(config[channel][era][process][Keys.COMMON]))
    subprocess_flag_tuples = [it for it in subprocess_dict.items() if it[0].startswith("is_")]
    additional_columns = list(config[channel][era][process][Keys.VARIABLES].keys())

    return {
        (channel, era, process, subprocess): ROOTToPlain(
            raw_path=_path("raw"),
            filtered_path=_path("filtered"),
        ).setup_raw_dataframe(
            tree_and_filepaths=tree_and_filepaths_tuples,
            definitions=definitions_tuples + subprocess_flag_tuples,
            additional_columns=additional_columns + list(Keys.EVENT_IDENTIFIER_COLUMNS),
            filters=None,
            description=f"{channel}_{era}_{process}_{subprocess}",
            max_workers=8,
        ).filter_dataframe(
            filter_function=any_cut,
        ).dataframe
    }


def collect_folds(arguments: Tuple[dict, str, str, str, str, dict, pd.DataFrame]) -> dict:
    (
        config,
        channel,
        era,
        process,
        subprocess,
        subprocess_dict,
        plain_subprocess_dataframe,
        common_setup_config,
    ) = arguments
    """
    Function to collect folds for the training dataset. It creates a dataframe
    for each process and subprocess, applies the necessary manipulations, adding
    labels, event quantities, nominal variables, weights and cuts, and additional
    nominal cuts. It also handles uncertainties and splits the dataframe into folds.

    Args:
        arguments (Tuple[dict, str, str, str, str, dict, pd.DataFrame]): A tuple containing the config,
            config: dict: The config dictionary.
            channel: str: The channel name.
            era: str: The era name.
            process: str: The process name.
            subprocess: str: The subprocess name.
            subprocess_dict: dict: The subprocess dictionary.
            plain_subprocess_dataframe: pd.DataFrame: The plain subprocess dataframe.

    Returns:
        dict: A dictionary containing the folds for the training dataset.
    """
    add = ProcessDataFrameManipulation(
        config=config,
        subprocess_dict=subprocess_dict,
        subprocess_df=plain_subprocess_dataframe.reset_index(drop=True),
        process_name=process,
        subprocess_name=subprocess,
    )
    logger.info(f"Processing {process} - {subprocess}")
    process_df = (
        pd.DataFrame()
        .pipe(
            add.labels,
            renaming_map=common_setup_config.recursive_get(
                ["dataset_modifications", "labels", "renaming_map"]
            )
        )
        # exemplary custom function before setting pd.MultiIndex
        # TODO: individually check for each analysis or remove completely
        # adjusting add.subprocess_df based on cut from remove_cut_regions requiered
        .pipe(add.update_subprocess_df, by="index")
        .pipe(add.event_quantities, columns=list(Keys.EVENT_IDENTIFIER_COLUMNS))
        .pipe(add.nominal_variables)
        .pipe(add.nominal_weight_and_cut)
        .pipe(add.additional_nominal_cuts)
        .pipe(add.weight_like_uncertainties)
        .pipe(add.shift_like_uncertainties)
        .pipe(exemplary_remove_cut_regions, regions=("same_sign", "same_sign_anti_iso"))
    )

    # SMHtt specific, might differ
    # TODO: Apply only if present, otherwise remove. Name might differ
    if subprocess == "jetFakes":
        process_df = (
            process_df
            .pipe(add.adjust_jetFakes_weights)
        )

    process_df.columns = pd.MultiIndex.from_tuples(process_df.columns)

    process_df = (
        process_df
        .pipe(
            exemplary_custom_selection,
            selections=common_setup_config.recursive_get(
                ["dataset_modifications", "selections"]
            )
        )
    )

    msg = f"Creating folds for {channel} {era} {process} - {subprocess}"

    _folds_splitted = {k: {"data": []} for k in folds_splitted.keys()}
    for fold_name, fold in tqdm(_folds_splitted.items()):
        fold["data"].append(
            CombinedDataFrameManipulation.split_folds(
                df=process_df,
                condition=folds_splitted[fold_name]["condition"],
            ),
        )
        msg += f"\n\t{fold_name}: {fold['data'][-1].shape}"
    logger.info(msg)

    return _folds_splitted


if __name__ == "__main__":

    logger = setup_logging(logger=logging.getLogger(__name__))
    args = parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
        
    if args.common_setup_config:
        with open(args.common_setup_config, "r") as f:
            args.common_setup_config = yaml.safe_load(f)
            if not args.common_setup_config:
                logger.warning("No common setup config provided or it is empty, using default settings.")
                args.common_setup_config = {}
    else:
        args.common_setup_config = {}

    args.common_setup_config = PipeDict(args.common_setup_config)

    WEIGHT_AND_CUT_CONTAINING = {"ps_weight__FsrWeight", "ps_weight__IsrWeight"}
    Iterate.common_dict = partial(Iterate.common_dict, ignore_weight_and_cuts=WEIGHT_AND_CUT_CONTAINING)
    logger.warning(f"Ignoring cuts and weights of {WEIGHT_AND_CUT_CONTAINING}, until fixed!")

    SUBPROCESSES_TO_SKIP = args.common_setup_config.recursive_get(["dataset_modifications", "subprocesses_to_skip"], set())

    filtered_plain_dataframes = {}
    for result in optional_process_pool(
        args_list=[
            tuple(map(deepcopy, [config] + list(it)))
            for it in Iterate.subprocesses(config)
            if it[-2] not in SUBPROCESSES_TO_SKIP
        ],
        function=collect_filtered_plain_dataframes,
        max_workers=1,
    ):
        filtered_plain_dataframes.update(result)

    subfold_pattern = [True, True, False, False]
    folds_splitted = {
        key: {"data": [], "condition": condition}
        for key, condition in [
            ("fold0", lambda df: odd_id(df)),
            ("fold0_training", lambda df: odd_id(df) & tiled_mask(df, subfold_pattern)),
            ("fold0_validation", lambda df: odd_id(df) & ~tiled_mask(df, subfold_pattern)),
            ("fold1", lambda df: ~odd_id(df)),
            ("fold1_training", lambda df: ~odd_id(df) & tiled_mask(df, subfold_pattern)),
            ("fold1_validation", lambda df: ~odd_id(df) & ~tiled_mask(df, subfold_pattern)),
        ]
    }

    # RuntimeVariables.USE_MULTIPROCESSING = False
    for result in optional_process_pool(
        args_list=[
            tuple(map(deepcopy, [config] + list(it) + [filtered_plain_dataframes[it[:-1]]] + [args.common_setup_config]))
            for it in Iterate.subprocesses(config)
            if it[-2] not in SUBPROCESSES_TO_SKIP
        ],
        function=collect_folds,
    ):
        for fold_name, fold in result.items():
            folds_splitted[fold_name]["data"].extend(fold["data"])

    logger.info("Merging folds and adjusting")
    folds = PipeDict(
        {
            k: pd.concat(v["data"], ignore_index=True).reset_index(drop=True)
            for k, v in tqdm(folds_splitted.items())
        }
    )

    folds = (
        folds
        .pipe(CombinedDataFrameManipulation.fill_nans_in_weight_like)
        .pipe(CombinedDataFrameManipulation.fill_nans_in_shift_like)
        .pipe(CombinedDataFrameManipulation.fill_nans_in_nominal_additional, default_value=0.0)
    )

    (Path(args.base_dataset_directory) / Path("folds")).mkdir(parents=True, exist_ok=True)

    for fold_name, fold in folds.items():
        fold_path = (Path(args.base_dataset_directory) / Path("folds")).joinpath(f"{fold_name}.feather")
        fold.to_feather(fold_path)
        logger.info(f"Created {fold_name} with shape {fold.shape} at {fold_path}")
