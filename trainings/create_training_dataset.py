import argparse
import logging
import os
from functools import partial
from tqdm import tqdm
import numpy as np
from pathlib import Path
import os
from typing import Iterable

import pandas as pd
import yaml
from src.dataset_manipulation import CombinedDataFrameManipulation, ProcessDataFrameManipulation, ROOTToPlain, tuple_column
from src.helper import Iterate, PipeDict, Keys

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
        default=f"/ceph/{os.environ['USER']}/smhtt_ul/training_datasets",
        help="Base directory for the output files",
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


def odd_id(df: pd.DataFrame) -> np.ndarray:
    """
    Helper to create a mask for odd IDs.

    Args:
        df (pd.DataFrame): The dataframe to create the mask for.

    Returns:
        np.ndarray: A boolean mask of the same length as the dataframe.
    """
    return (df[Keys.EVENT][Keys.ID] % 2).astype(bool)


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


def exemplary_custom_selection(df: pd.DataFrame, optimize_selection: bool = False) -> pd.DataFrame:
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
    mask = False
    is_nominal = tuple_column(Keys.NOMINAL, Keys.CUT)
    is_anti_iso = tuple_column(Keys.NOMINAL, "anti_iso", Keys.CUT)
    for _process, _cut in [
        ("is_jetFakes", [is_anti_iso]),
        ("is_ttbar", [is_anti_iso, is_nominal]),
        ("is_dyjets", [is_anti_iso, is_nominal]),
        ("is_embedding", [is_anti_iso, is_nominal]),
        ("is_diboson", [is_anti_iso, is_nominal]),
        ("is_vbf_htautau", [is_nominal]),
        ("is_ggh_htautau", [is_nominal]),
    ]:
        process_mask = df[Keys.LABELS][_process].astype(bool)

        selection_mask = True
        if optimize_selection:
            selection_mask = df[[it for it in _cut if it in df.columns]].astype(bool).any(axis=1)

        mask |= (process_mask & selection_mask)

    mask &= df[[it for it in df.columns if Keys.CUT in it]].astype(bool).any(axis=1)  # any cut

    return df[mask].copy()


if __name__ == "__main__":

    logger = setup_logging(logger=logging.getLogger(__name__))
    args = parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    WEIGHT_AND_CUT_CONTAINING = {  # until fixed, TODO:
        "lhe_scale_weight__LHEScaleMuFWeigt",
        "lhe_scale_weight__LHEScaleMuRWeigt",
    }
    Iterate.common_dict = partial(Iterate.common_dict, ignore_weight_and_cuts=WEIGHT_AND_CUT_CONTAINING)
    logger.warning(f"Ignoring cuts and weights of {WEIGHT_AND_CUT_CONTAINING}, until fixed!")

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
    # SMHtt mt specific, will differ for other analysis
    # TODO: individually select for each analysis if needed
    SUBPROCESSES_TO_SKIP = {"DY-ZJ", "DY-ZTT", "TT-TTJ", "TT-TTT", "VV-VVJ", "VV-VVT"}

    process_dataframes = []
    for channel, era, process, subprocess, subprocess_dict in Iterate.subprocesses(config):

        if subprocess in SUBPROCESSES_TO_SKIP:
            continue

        logger.info(f"Processing {channel} {era} {process} - {subprocess}")

        def _path(directory, extension="feather"):
            name = f"{channel}_{era}_{process}_{subprocess}.{extension}"
            return (Path(args.base_dataset_directory) / Path(directory)).joinpath(name)

        def any_cut(df):
            pattern = "__common__cut__"
            return df[[it for it in df.columns if it.startswith(pattern)]].any(axis=1)

        # TODO:: Columns can be set here, also independent of the config!
        tree_and_filepaths_tuples = list(Iterate.rdf_files(config[channel][era][process][Keys.PATHS]))
        definitions_tuples = list(Iterate.common_dict(config[channel][era][process][Keys.COMMON]))

        fake_factor_columns = []
        for fake_factor_name in ["fake_factor_2", "fake_factor_1"]:
            if (fake_factor_name, fake_factor_name) in definitions_tuples:
                definitions_tuples.remove((fake_factor_name, fake_factor_name))
                fake_factor_columns.append(fake_factor_name)

        subprocess_flag_tuples = [it for it in subprocess_dict.items() if it[0].startswith("is_")]
        additional_columns = list(config[channel][era][process][Keys.VARIABLES].keys())

        plain_subprocess_dataframe = ROOTToPlain(
            raw_path=_path("raw"),
            filtered_path=_path("filtered"),
        ).setup_raw_dataframe(
            tree_and_filepaths=tree_and_filepaths_tuples,
            definitions=definitions_tuples + subprocess_flag_tuples,
            additional_columns=additional_columns + fake_factor_columns,
            filters=None,
            description=f"{channel}_{era}_{process}_{subprocess}",
            max_workers=16,
        ).filter_dataframe(
            filter_function=any_cut,
        ).dataframe

        add = ProcessDataFrameManipulation(
            config=config,
            subprocess_dict=subprocess_dict,
            subprocess_df=plain_subprocess_dataframe.reset_index(drop=True),
            process_name=process,
            subprocess_name=subprocess,
        )
        process_df = (
            pd.DataFrame()
            .pipe(
                add.labels,
                renaming_map={
                    # SMHtt mt specific, will differ for other analysis
                    # TODO: individually adjust for each analysis
                    "is_DY__DY-ZL": "is_dyjets",
                    "is_EMB__Embedded": "is_embedding",
                    "is_TT__TT-TTL": "is_ttbar",
                    "is_VV__VV_VVL": "is_diboson",
                    "is_data": "is_jetFakes",
                    "is_ggH__ggH125": "is_ggh_htautau",
                    "is_VBF__VBF125": "is_vbf_htautau",
                },
            )
            # exemplary custom function before setting pd.MultiIndex
            # TODO: individually check for each analysis or remove completely
            .pipe(exemplary_remove_cut_regions, regions=("same_sign", "same_sign_anti_iso"))
            # adjusting add.subprocess_df based on cut from remove_cut_regions requiered
            .pipe(add.update_subprocess_df, by="index")
            .pipe(add.event_quantities)
            .pipe(add.nominal_variables)
            .pipe(add.nominal_weight_and_cut)
            .pipe(add.additional_nominal_cuts)
            .pipe(add.weight_like_uncertainties)
            .pipe(add.shift_like_uncertainties)
            .pipe(add.fake_factor_columns, columns=fake_factor_columns)
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
            # exemplary custom function after setting pd.MultiIndex
            # independent from ProcessDataFrameManipulation
            # TODO: Adjust for each analysis, or remove completely
            .pipe(exemplary_custom_selection, optimize_selection=True)
        )

        logger.info("Creating folds:")
        for fold_name, fold in folds_splitted.items():
            fold["data"].append(
                CombinedDataFrameManipulation.split_folds(
                    df=process_df,
                    condition=fold["condition"],
                ),
            )
            logger.info(f"\t{fold_name}: Shape: {fold['data'][-1].shape}")

    logger.info("Merging folds and adjusting")
    folds = PipeDict(
        {
            k: pd.concat(v["data"], ignore_index=True).reset_index(drop=True)
            for k, v in tqdm(folds_splitted.items())
        }
    )

    folds = (
        folds
        .pipe(
            CombinedDataFrameManipulation.fill_nans_in_weight_like,
            has_jetFakes=True,  # SMHtt specific, might differ, TODO: set to False if not present
            jetFakes_identifier="is_jetFakes",  # SMHtt specific, might differ, TODO: adjust if needed
        )
        .pipe(CombinedDataFrameManipulation.fill_nans_in_shift_like)
        .pipe(CombinedDataFrameManipulation.fill_nans_in_nominal_additional, default_value=0.0)
    )

    (Path(args.base_dataset_directory) / Path("folds")).mkdir(parents=True, exist_ok=True)

    for fold_name, fold in folds.items():
        fold_path = (Path(args.base_dataset_directory) / Path("folds")).joinpath(f"{fold_name}.feather")
        fold.to_feather(fold_path)
        logger.info(f"Created {fold_name} with shape {fold.shape} at {fold_path}")
