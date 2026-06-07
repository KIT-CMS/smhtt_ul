import argparse
import logging
import os
import gc
import json
from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from src.dataset_manipulation import (
    CombinedDataFrameManipulation,
    ProcessDataFrameManipulation,
    ROOTToPlain,
    exemplary_custom_selection,
    exemplary_remove_cut_regions,
    get_fold_conditions,
)
from src.helper import Iterate, Keys, PipeDict, downcast_dataframe
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


def filepath(directory: str, basename: str = "", extension: str = "feather"):
    path = (Path(args.base_dataset_directory) / Path(directory))
    path.mkdir(parents=True, exist_ok=True)
    return path.joinpath(f"{basename}.{extension}") if basename else path


def collect_filtered_plain_dataframes(
    config: dict,
    channel: str,
    era: str,
    process: str,
    subprocess: str,
    subprocess_dict: dict,
    drop_raw: bool = True,
) -> tuple:
    """
    TODO: Update docstring
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

    tree_and_filepaths_tuples = list(Iterate.rdf_files(config[channel][era][process][Keys.PATHS]))
    definitions_tuples = list(Iterate.common_dict(config[channel][era][process][Keys.COMMON]))
    subprocess_flag_tuples = [it for it in subprocess_dict.items() if it[0].startswith("is_")]
    additional_columns = list(config[channel][era][process][Keys.VARIABLES].keys())

    raw_path = None if drop_raw else filepath("raw", f"{channel}_{era}_{process}_{subprocess}")
    filtered_path = filepath("filtered", f"{channel}_{era}_{process}_{subprocess}")

    cut_columns = [k for k, _ in definitions_tuples if "__common__cut__" in k]

    base_fallback_weights = [
        "ps_weight__FsrWeight",
        "ps_weight__IsrWeight",
    ]

    fallback_defs = {}
    for weight in base_fallback_weights:
        fallback_defs[weight] = "1.0f"  # Nominal -> 1.0f
        fallback_defs[f"{weight}Up"] = weight  # Up -> Nominal
        fallback_defs[f"{weight}Down"] = weight  # Down -> Nominal

    r2p = ROOTToPlain(raw_path=raw_path, filtered_path=filtered_path).setup_raw_dataframe(
        tree_and_filepaths=tree_and_filepaths_tuples,
        definitions=definitions_tuples + subprocess_flag_tuples,
        additional_columns=additional_columns + list(Keys.EVENT_IDENTIFIER_COLUMNS),
        fallback_definitions=fallback_defs,
        filters={"any_cut": " || ".join(cut_columns)} if cut_columns else {"any_cut": "false"},
        description=f"{channel}_{era}_{process}_{subprocess}",
        max_workers=32,
    )

    if not drop_raw:
        def any_cut(df):
            pattern = "__common__cut__"
            return df[[it for it in df.columns if it.startswith(pattern)]].any(axis=1)
        r2p.filter_dataframe(filter_function=any_cut)

    return (channel, era, process, subprocess, subprocess_dict, r2p)


def create_process_folds(
    config: dict,
    channel: str,
    era: str,
    process: str,
    subprocess: str,
    subprocess_dict: dict,
    plain_subprocess_dataframe_obj: ROOTToPlain,
    common_setup_config: dict,
) -> None:
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

    fold_conditions = get_fold_conditions()
    filenames = {
        fold_name: filepath("_folds", f"__{fold_name}__{channel}_{era}_{process}_{subprocess}")
        for fold_name in fold_conditions.keys()
    }

    if not all(filename.exists() for filename in filenames.values()):

        raw_df = plain_subprocess_dataframe_obj.dataframe.reset_index(drop=True)
        plain_subprocess_dataframe_obj._dataframe = None
        gc.collect()

        add = ProcessDataFrameManipulation(
            config=config,
            subprocess_dict=subprocess_dict,
            subprocess_df=raw_df,
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
            .pipe(add.update_subprocess_df, by="index")
            .pipe(add.event_quantities, columns=list(Keys.EVENT_IDENTIFIER_COLUMNS))
            .pipe(add.nominal_variables)
            .pipe(add.nominal_weight_and_cut)
            .pipe(add.additional_nominal_cuts)
            .pipe(add.weight_like_uncertainties)
            .pipe(add.shift_like_uncertainties)
            .pipe(add.add_accumulated_data)
            .pipe(exemplary_remove_cut_regions, regions=("same_sign", "same_sign_anti_iso"))
        )

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
        ).copy()

        add.subprocess_df = None
        del raw_df
        gc.collect()

        msg = f"Creating folds for {channel} {era} {process} - {subprocess}"

        for fold_name, fold_condition in fold_conditions.items():
            df = CombinedDataFrameManipulation.split_folds(
                df=process_df,
                condition=fold_condition,
            )
            df = df.reset_index(drop=True).copy()
            msg += f"\n\t{fold_name}: {df.shape}"
            df.to_feather(filenames[fold_name])

            del df
            gc.collect()

        del process_df
        gc.collect()

        logger.info(msg)
    else:
        logger.info(f"Folds for {channel} {era} {process} - {subprocess} already exist in {filepath('_folds')}, skipping creation.")

    try:
        del add
        gc.collect()
    except UnboundLocalError:
        pass


def combine_folds(
    class_weighted: bool = True,
    default_in_nominal_additional: float = 0.0,
) -> None:
    for fold_name in get_fold_conditions().keys():
        logger.info(f"Start processing fold {fold_name}")

        fold_files = list(Path(filepath("_folds")).glob(f"__{fold_name}__*.feather"))
        if not fold_files:
            logger.warning(f"No feather files found for fold {fold_name}, skipping.")
            continue

        fold = pd.concat(
            downcast_dataframe(pd.read_feather(it)).reset_index(drop=True)
            for it in tqdm(fold_files, desc=f"Loading fold {fold_name} parts")
        ).reset_index(drop=True)
        logger.info(f"Combining fold {fold_name} to shape {fold.shape}")

        fold = (
            fold
            .pipe(
                CombinedDataFrameManipulation.add_class_weights,
                class_weighted=class_weighted,
            )
            .pipe(CombinedDataFrameManipulation.fill_nans_in_weight_like)
            .pipe(CombinedDataFrameManipulation.fill_nans_in_shift_like)
            .pipe(
                CombinedDataFrameManipulation.fill_nans_in_nominal_additional,
                default_value=default_in_nominal_additional,
            )
        )
        logger.info(f"Final shape of fold {fold_name} is {fold.shape}")
        fold.to_feather(filepath("folds", f"{fold_name}"))
        logger.info(f"Saved combined fold {fold_name} at {filepath('folds', f'{fold_name}')}")

        try:
            folder_path = filepath("folds", f"{fold_name}").with_suffix("")
            folder_path.mkdir(parents=True, exist_ok=True)

            partitions = []

            for level0 in [Keys.EVENT, Keys.NOMINAL, Keys.WEIGHT_LIKE, Keys.LABELS]:
                if level0 in fold.columns.levels[0]:
                    file_name = f"{level0}.feather"
                    fold[level0].to_feather(folder_path.joinpath(file_name))
                    partitions.append({"file": file_name, "prefix": [str(level0)]})
                    logger.info(f"Saved {level0} part of fold {fold_name}")

            if Keys.SHIFT_LIKE in fold.columns.levels[0]:
                for uncertainty in tqdm(fold[Keys.SHIFT_LIKE].columns.unique(level=0)):
                    file_name = f"{Keys.SHIFT_LIKE}_{uncertainty}.feather"
                    fold[Keys.SHIFT_LIKE][uncertainty].to_feather(folder_path.joinpath(file_name))
                    partitions.append({"file": file_name, "prefix": [str(Keys.SHIFT_LIKE), str(uncertainty)]})
                    logger.info(f"Saved ShiftLike uncertainty {uncertainty} of fold {fold_name}")

            with open(folder_path.joinpath("metadata.json"), "w") as f:
                json.dump(
                    {
                        "num_rows": len(fold),
                        "columns": [list(col) for col in fold.columns],
                        "dtypes": [[list(col), str(dtype)] for col, dtype in fold.dtypes.items()],
                        "partitions": partitions
                    },
                    f,
                    indent=2,
                )
            logger.info(f"Saved metadata at {folder_path.joinpath('metadata.json')}")
        except Exception as e:
            logger.error(f"Error while saving parts of fold {fold_name}: {e}")

        del fold
        gc.collect()


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
    SUBPROCESSES_TO_SKIP = args.common_setup_config.recursive_get(["dataset_modifications", "subprocesses_to_skip"], set())

    processing_pipeline = (
        collect_filtered_plain_dataframes(config, channel, era, process, subprocess, subprocess_dict)
        for channel, era, process, subprocess, subprocess_dict in Iterate.subprocesses(config)
        if subprocess not in SUBPROCESSES_TO_SKIP
    )

    for items in processing_pipeline:
        create_process_folds(config, *items, args.common_setup_config)

        items[-1]._dataframe = None
        del items
        gc.collect()

    combine_folds()
