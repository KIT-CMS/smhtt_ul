import argparse
import logging
import os
import gc
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
        default=f"/ceph/{os.environ.get('USER', 'user')}/smhtt_ul_ML/training_datasets",
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


def get_memory_usage_mb():
    """Returns the current Resident Set Size (RSS) memory usage of the process in MB."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 ** 2)
    except ImportError:
        # Fallback for Linux if psutil is not installed
        try:
            with open('/proc/self/status') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        return float(line.split()[1]) / 1024.0
        except Exception:
            pass
    return 0.0


def log_gc(step_name):
    """Forces garbage collection and logs overall process memory usage."""
    mem_before = get_memory_usage_mb()
    collected = gc.collect()
    mem_after = get_memory_usage_mb()
    logger.info(
        f"[{step_name}] GC collected {collected} objects. "
        f"Process Memory: {mem_before:.2f} MB -> {mem_after:.2f} MB"
    )


def log_dataframe_size(df, df_name):
    """Logs the memory allocated to a specific dataframe."""
    size_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
    logger.info(f"DataFrame '{df_name}' memory allocation: {size_mb:.2f} MB")

### Old ###
def collect_filtered_plain_dataframes_old(
    config: dict,
    channel: str,
    era: str,
    process: str,
    subprocess: str,
    subprocess_dict: dict,
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
    def any_cut(df):
        pattern = "__common__cut__"
        return df[[it for it in df.columns if it.startswith(pattern)]].any(axis=1)

    tree_and_filepaths_tuples = list(Iterate.rdf_files(config[channel][era][process][Keys.PATHS]))
    definitions_tuples = list(Iterate.common_dict(config[channel][era][process][Keys.COMMON]))
    subprocess_flag_tuples =[it for it in subprocess_dict.items() if it[0].startswith("is_")]
    additional_columns = list(config[channel][era][process][Keys.VARIABLES].keys())

    return (
        channel,
        era,
        process,
        subprocess,
        subprocess_dict,
        ROOTToPlain(
            raw_path=filepath("raw", f"{channel}_{era}_{process}_{subprocess}"),
            filtered_path=filepath("filtered", f"{channel}_{era}_{process}_{subprocess}"),
        ).setup_raw_dataframe(
            tree_and_filepaths=tree_and_filepaths_tuples,
            definitions=definitions_tuples + subprocess_flag_tuples,
            additional_columns=additional_columns + list(Keys.EVENT_IDENTIFIER_COLUMNS),
            filters=None,
            description=f"{channel}_{era}_{process}_{subprocess}",
            max_workers=16,
        ).filter_dataframe(
            filter_function=any_cut,
        ),
    )


def create_process_folds_old(
    config: dict,
    channel: str,
    era: str,
    process: str,
    subprocess: str,
    subprocess_dict: dict,
    plain_subprocess_dataframe_obj: ROOTToPlain,
    common_setup_config: dict,
) -> None:

    fold_conditions = get_fold_conditions()
    filenames = {
        fold_name: filepath("_folds", f"__{fold_name}__{channel}_{era}_{process}_{subprocess}")
        for fold_name in fold_conditions.keys()
    }

    if not all(filename.exists() for filename in filenames.values()):
        add = ProcessDataFrameManipulation(
            config=config,
            subprocess_dict=subprocess_dict,
            subprocess_df=plain_subprocess_dataframe_obj.dataframe.reset_index(drop=True),
            process_name=process,
            subprocess_name=subprocess,
        )
        
        # 🟢 CRITICAL CLEANUP 1: 
        # `add` now has its own copy of the DataFrame. 
        # We must immediately destroy the original DataFrame from the ROOTToPlain object!
        plain_subprocess_dataframe_obj._dataframe = None
        del plain_subprocess_dataframe_obj
        log_gc("After destroying ROOTToPlain dataframe")

        logger.info(f"Processing {process} - {subprocess}")
        process_df = (
            pd.DataFrame()
            .pipe(
                add.labels,
                renaming_map=common_setup_config.recursive_get(["dataset_modifications", "labels", "renaming_map"])
            )
            .pipe(add.update_subprocess_df, by="index")
            .pipe(add.event_quantities, columns=list(Keys.EVENT_IDENTIFIER_COLUMNS))
            .pipe(add.nominal_variables)
            .pipe(add.nominal_weight_and_cut)
            .pipe(add.additional_nominal_cuts)
            # .pipe(add.weight_like_uncertainties)
            # .pipe(add.shift_like_uncertainties)
            .pipe(exemplary_remove_cut_regions, regions=("same_sign", "same_sign_anti_iso"))
        )

        if subprocess == "jetFakes":
            process_df = process_df.pipe(add.adjust_jetFakes_weights)

        process_df.columns = pd.MultiIndex.from_tuples(process_df.columns)

        process_df = process_df.pipe(
            exemplary_custom_selection,
            selections=common_setup_config.recursive_get(["dataset_modifications", "selections"])
        )

        # 🟢 CRITICAL CLEANUP 2: 
        # The pipeline is done building `process_df`. 
        # The `add` object (which holds `add.subprocess_df`, a huge chunk of RAM) is completely dead weight now.
        # Delete it BEFORE we start looping and slicing folds!
        try:
            del add
        except UnboundLocalError:
            pass
        log_gc("After pipeline completion, destroying ProcessDataFrameManipulation object")

        log_dataframe_size(process_df, f"process_df ({channel}_{era}_{process}_{subprocess})")

        msg = f"Creating folds for {channel} {era} {process} - {subprocess}"

        for fold_name, fold_condition in fold_conditions.items():
            df = CombinedDataFrameManipulation.split_folds(
                df=process_df,
                condition=fold_condition,
            )
            msg += f"\n\t{fold_name}: {df.shape}"
            df.to_feather(filenames[fold_name])
            
            # Explicitly delete the small DF right after dumping it
            del df 
            
        logger.info(msg)
        
        # Explicitly delete the big DF
        del process_df
    else:
        logger.info(f"Folds already exist, skipping creation.")

    log_gc(f"After create_process_folds ({channel}_{era}_{process}_{subprocess})")
### ###

### Optimized ? ###

def collect_filtered_plain_dataframes(
    config: dict,
    channel: str,
    era: str,
    process: str,
    subprocess: str,
    subprocess_dict: dict,
) -> tuple:
    """
    Collects filtered plain dataframes. The row-level filter is applied inside
    each worker process so the full unfiltered dataset never exists in memory.
    """
    tree_and_filepaths_tuples = list(Iterate.rdf_files(config[channel][era][process][Keys.PATHS]))
    definitions_tuples = list(Iterate.common_dict(config[channel][era][process][Keys.COMMON]))
    subprocess_flag_tuples = [it for it in subprocess_dict.items() if it[0].startswith("is_")]
    additional_columns = list(config[channel][era][process][Keys.VARIABLES].keys())

    return (
        channel,
        era,
        process,
        subprocess,
        subprocess_dict,
        ROOTToPlain(
            raw_path=filepath("raw", f"{channel}_{era}_{process}_{subprocess}"),
            filtered_path=filepath("filtered", f"{channel}_{era}_{process}_{subprocess}"),
        ).setup_and_filter_dataframe(
            tree_and_filepaths=tree_and_filepaths_tuples,
            definitions=definitions_tuples + subprocess_flag_tuples,
            additional_columns=additional_columns + list(Keys.EVENT_IDENTIFIER_COLUMNS),
            filter_column_pattern="__common__cut__",
            filters=None,
            description=f"{channel}_{era}_{process}_{subprocess}",
            max_workers=16,
        ),
    )

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

    fold_conditions = get_fold_conditions()
    filenames = {
        fold_name: filepath("_folds", f"__{fold_name}__{channel}_{era}_{process}_{subprocess}")
        for fold_name in fold_conditions.keys()
    }

    if not all(filename.exists() for filename in filenames.values()):
        add = ProcessDataFrameManipulation(
            config=config,
            subprocess_dict=subprocess_dict,
            subprocess_df=plain_subprocess_dataframe_obj.dataframe.reset_index(drop=True),
            process_name=process,
            subprocess_name=subprocess,
        )
        
        # 🟢 CRITICAL CLEANUP 1: 
        plain_subprocess_dataframe_obj._dataframe = None
        del plain_subprocess_dataframe_obj
        log_gc("After destroying ROOTToPlain dataframe")
        
        logger.info(f"Processing {process} - {subprocess}")
        process_df = (
            pd.DataFrame()
            .pipe(
                add.labels,
                renaming_map=common_setup_config.recursive_get(["dataset_modifications", "labels", "renaming_map"])
            )
            .pipe(add.update_subprocess_df, by="index")
            .pipe(add.event_quantities, columns=list(Keys.EVENT_IDENTIFIER_COLUMNS))
            .pipe(add.nominal_variables)
            .pipe(add.nominal_weight_and_cut)
            .pipe(add.additional_nominal_cuts)
            # .pipe(add.weight_like_uncertainties)
            # .pipe(add.shift_like_uncertainties)
            .pipe(exemplary_remove_cut_regions, regions=("same_sign", "same_sign_anti_iso"))
        )

        if subprocess == "jetFakes":
            process_df = process_df.pipe(add.adjust_jetFakes_weights)

        process_df.columns = pd.MultiIndex.from_tuples(process_df.columns)

        process_df = process_df.pipe(
            exemplary_custom_selection,
            selections=common_setup_config.recursive_get(["dataset_modifications", "selections"])
        )

        # 🟢 CRITICAL CLEANUP 2: 
        # The pipeline is done building `process_df`. 
        # The `add` object (which holds `add.subprocess_df`, a huge chunk of RAM) is completely dead weight now.
        # Delete it BEFORE we start looping and slicing folds!
        try:
            del add
        except UnboundLocalError:
            pass
        log_gc("After pipeline completion, destroying ProcessDataFrameManipulation object")

        log_dataframe_size(process_df, f"process_df ({channel}_{era}_{process}_{subprocess})")

        msg = f"Creating folds for {channel} {era} {process} - {subprocess}"

        for fold_name, fold_condition in fold_conditions.items():
            df = CombinedDataFrameManipulation.split_folds(
                df=process_df,
                condition=fold_condition,
            )
            msg += f"\n\t{fold_name}: {df.shape}"
            df.to_feather(filenames[fold_name])
            
            # Explicitly delete the small DF right after dumping it
            del df 
            
        logger.info(msg)
        
        # Explicitly delete the big DF
        del process_df
    else:
        logger.info(f"Folds already exist, skipping creation.")

    log_gc(f"After create_process_folds ({channel}_{era}_{process}_{subprocess})")


### ###
def combine_folds(
    class_weighted: bool = True,
    default_in_nominal_additional: float = 0.0,
) -> None:
    for fold_name in get_fold_conditions().keys():
        logger.info(f"Start processing fold {fold_name}")

        fold = pd.concat([
                downcast_dataframe(pd.read_feather(it)).reset_index(drop=True)
                for it in tqdm(
                    Path(filepath("_folds")).glob(f"__{fold_name}__*.feather"),
                    desc=f"Loading fold {fold_name} parts",
                )
            ]
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
        
        log_dataframe_size(fold, f"Combined Fold {fold_name}")
        
        fold.to_feather(filepath("folds", f"{fold_name}"))
        logger.info(f"Saved combined fold {fold_name} at {filepath('folds', f'{fold_name}')}")

        # Ensure memory from this fold is returned before beginning the next
        del fold
        log_gc(f"After processing combined fold {fold_name}")


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

    processing_pipeline = (
        collect_filtered_plain_dataframes(config, channel, era, process, subprocess, subprocess_dict)
        for channel, era, process, subprocess, subprocess_dict in Iterate.subprocesses(config)
        if subprocess not in SUBPROCESSES_TO_SKIP
    )

    for items in processing_pipeline:
        create_process_folds(config, *items, args.common_setup_config)
        
        # The dataframe is already cleared inside create_process_folds now.
        # Just delete the tuple references to clear up any lingering variables.
        del items
        log_gc("After processing pipeline chunk")

    combine_folds()