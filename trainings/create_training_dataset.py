import argparse
import logging
import os
from functools import partial
from tqdm import tqdm

import pandas as pd
import yaml
from src.dataset_manipulation import CombinedDataFrameManipulation, ProcessDataFrameManipulation, RootToPandasRaw, odd_id, tiled_mask
from src.helper import Iterate, PipeDict

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
        default="./mt__tmp_config__modified.yaml",
        help="Path to the config file",
    )
    parser.add_argument(
        "--base-dataset-directory",
        type=str,
        default="/ceph/amonsch/HiggsToTauTau/training_datasets",
        help="Base directory for the output files",
    )
    return parser.parse_args()


if __name__ == "__main__":

    logger = setup_logging(logger=logging.getLogger(__name__))
    args = parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    ignore_for_now = {  # until fixed, TODO:
        "lhe_scale_weight__LHEScaleMuFWeig",
        "lhe_scale_weight__LHEScaleMuRWeig",
    }
    Iterate.common_dict = partial(Iterate.common_dict, ignore_weight_and_cuts=ignore_for_now)
    logger.warning(f"Ignoring cuts and weights of {ignore_for_now}, until fixed!")

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

    process_dataframes = []
    for channel, era, process, process_dict in Iterate.process(config):
        logger.info(f"Processing {channel} {era} {process}")

        raw_process_df = RootToPandasRaw(
            raw_path=os.path.join(args.base_dataset_directory, "raw", f"{channel}_{era}_{process}.feather"),
            filtered_path=os.path.join(args.base_dataset_directory, "filtered", f"{channel}_{era}_{process}.feather"),
        ).setup_raw_dataframe(
            process_dict=process_dict,
            max_workers=16,
            description=f"{channel}_{era}_{process}",
        ).generic_filtered(
            filter_funciton=lambda df: df[[it for it in df.columns if it.startswith("__common__cut__")]].any(axis=1),
        ).dataframe

        add = ProcessDataFrameManipulation(
            config=config,
            process_dict=process_dict,
            process_df=raw_process_df,
        )
        process_df = (
            pd.DataFrame()
            .pipe(add.labels, renaming_map={"is_data": "is_jetFakes"})
            .pipe(add.event_quantities)
            .pipe(add.nominal_variables)
            .pipe(add.nominal_weight)
            .pipe(add.nominal_additional if process not in {"qqH", "ggH"} else add.passtrough)
            .pipe(add.weight_like_uncertainties)
            .pipe(add.shift_like_uncertainties)
        )

        process_df.columns = pd.MultiIndex.from_tuples(process_df.columns)

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

    folds = (
        PipeDict(
            {
                k: pd.concat(v["data"], ignore_index=True).reset_index(drop=True)
                for k, v in tqdm(folds_splitted.items())
            }
        )
        # Not needed if you do not include any systematic variations
        .pipe(CombinedDataFrameManipulation.fill_nans_in_weight_like)
        .pipe(CombinedDataFrameManipulation.fill_nans_in_shift_like)
        # Potentially not needed here, depending on the data
        .pipe(CombinedDataFrameManipulation.fill_nans_in_nominal_additional)
    )

    os.makedirs(os.path.join(args.base_dataset_directory, "folds"), exist_ok=True)

    for fold_name, fold in folds.items():
        path = os.path.join(args.base_dataset_directory, "folds", f"{fold_name}.feather")
        fold.to_feather(path)
        logger.info(f"Created {fold_name} with shape {fold.shape} at {path}")
