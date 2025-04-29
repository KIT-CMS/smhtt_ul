import logging
import os
import sys
from collections import defaultdict
from typing import Callable, Iterable, List, Tuple, Union

import numpy as np
import pandas as pd
import ROOT
from src.helper import Iterate, Keys, optional_process_pool
from tqdm import tqdm

try:
    from config.logging_setup_configs import duplicate_filter_context, setup_logging
except ModuleNotFoundError:
    import sys
    sys.path.extend([".", ".."])
    from config.logging_setup_configs import duplicate_filter_context, setup_logging


logger = setup_logging(logger=logging.getLogger(__name__))


class RootToPandasRaw(object):

    def __init__(self, raw_path: Union[str, None], filtered_path: Union[str, None] = None) -> None:
        self.raw_path = raw_path
        self.filtered_path = filtered_path
        self.dataframe = None

    @staticmethod
    def build_rdf(
        tree_and_files: Tuple[str, str, list[str]],
    ) -> Tuple[ROOT.TChain, ROOT.RDataFrame]:
        key, ntuple, *friends = tree_and_files
        logger.debug(f"Adding {ntuple} with friends {friends}")

        chain = ROOT.TChain(key)
        chain.Add(ntuple)

        for friend in friends:
            fchain = ROOT.TChain(key)
            fchain.Add(friend)
            chain.AddFriend(fchain)

        return chain, ROOT.RDataFrame(chain)

    @staticmethod
    def define_and_collect_columns(
        rdf: ROOT.RDataFrame,
        process_dict: dict,
    ) -> Tuple[ROOT.RDataFrame, list]:
        columns = []
        for k, v in Iterate.common_dict(process_dict[Keys.COMMON]):
            rdf = rdf.Define(k, v)
            columns.append(k)
        columns += list(process_dict[Keys.VARIABLES].keys())

        logger.debug(f"Columns: {columns}")

        return rdf, list(set(columns))

    @staticmethod
    def pandasDataFrame(
        args: Tuple[str, str, str, dict, str, str, list[str]],
    ) -> dict[tuple[str, ...], pd.DataFrame]:
        process_dict, *tree_and_files = args

        _, rdf = RootToPandasRaw.build_rdf(tree_and_files)
        rdf, columns = RootToPandasRaw.define_and_collect_columns(rdf, process_dict)

        return pd.DataFrame(rdf.AsNumpy(columns))

    def setup_raw_dataframe(
        self,
        process_dict: dict,
        max_workers: int = 16,
        description: str = "",
    ) -> "RootToPandasRaw":
        if self.raw_path and not os.path.exists(self.raw_path):
            logger.info(f"Creating {self.raw_path}")
            dataframe = pd.concat(
                optional_process_pool(
                    args_list=[
                        (process_dict, *tree_and_files)
                        for tree_and_files in Iterate.rdf_files(process_dict[Keys.PATHS])
                    ],
                    function=RootToPandasRaw.pandasDataFrame,
                    max_workers=max_workers,
                    description=description,
                ),
                axis=0,
                ignore_index=True,
                sort=False,
            )

            os.makedirs(os.path.split(self.raw_path)[0], exist_ok=True)
            dataframe.to_feather(self.raw_path)
            logger.info(f"finished creation of {self.raw_path}\n\tshape: {dataframe.shape}")

            self.dataframe = dataframe

        return self

    def generic_filtered(
        self,
        filter_funciton: Callable,
    ) -> "RootToPandasRaw":
        if self.filtered_path and os.path.exists(self.filtered_path):
            self.dataframe = pd.read_feather(self.filtered_path)
            logger.info(f"Loaded filtered from {self.filtered_path}\n\tshape: {self.dataframe.shape}")

            return self

        if self.dataframe is None:
            self.dataframe = pd.read_feather(self.raw_path)
            logger.info(f"Loaded raw from {self.raw_path}")

        initial_shape = self.dataframe.shape
        self.dataframe = self.dataframe[filter_funciton(self.dataframe)]
        logger.info(f"Filtered {self.filtered_path}\n\tshape: {initial_shape} -> {self.dataframe.shape}")

        if self.filtered_path is not None:
            os.makedirs(os.path.split(self.filtered_path)[0], exist_ok=True)
            self.dataframe.to_feather(self.filtered_path)

        return self


class _FromConfig(object):
    def __init__(self, config: dict):
        self.config = config

    def _from_single_process(self, key: str, condition: callable) -> dict:
        return {k: v for k, v in next(Iterate.process(self.config))[-1][key].items() if condition(k)}

    @property
    def label_columns(self) -> list:
        return list(
            self._from_single_process(
                "nominal_variables",
                lambda x: x.startswith("is_") and not any(it in x for it in Keys.ERAS),
            ).keys()
        )

    @property
    def variable_columns(self) -> list:
        return list(
            self._from_single_process(
                "nominal_variables",
                lambda x: not x.startswith("is_") or any(it in x for it in Keys.ERAS),
            ).keys()
        )

    @property
    def all_shifted_variables(self) -> dict:
        shifted_variables = defaultdict(list)

        for channel, era, sample, _ in Iterate.process(self.config):
            for k, v in self.config[channel][era][sample]["variables"].items():
                if k not in config[channel][era][sample]["nominal_variables"]:
                    shifted_variables[k.split("__")[0]].append(v)

        return dict(shifted_variables)


class ProcessDataFrameManipulation:
    def __init__(self, config: dict, process_dict: dict, process_df: pd.DataFrame) -> None:
        self.config = config
        self.process_dict = process_dict
        self.from_config = _FromConfig(config)
        self.process_df = process_df

    @property
    def process_name(self) -> str:
        result = list(
            filter(
                lambda it: it not in {
                    "common",
                    "nominal_variables",
                    "paths",
                    "variables",
                },
                self.process_dict.keys(),
            )
        )
        if len(result) == 1:
            return result[0]
        else:
            msg = f"More than one process name found: {result}. Multiple ones are not supported yet."
            logger.error(msg)
            raise NotImplementedError(msg)

    def passtrough(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def labels(self, df: pd.DataFrame, renaming_map: Union[dict, None] = None) -> pd.DataFrame:
        logger.debug(f"Renaming labels: {renaming_map}")
        logger.debug(f"Label columns: {self.from_config.label_columns}")

        for it in self.from_config.label_columns:
            _column = tuple_column(
                Keys.LABELS,
                renaming_map.get(it, it) if renaming_map is not None else it,
            )
            df[_column] = self.process_df[it].astype(int)

        df = df.copy()
        return df

    def nominal_variables(self, df: pd.DataFrame, renaming_map: Union[dict, None] = None) -> pd.DataFrame:
        logger.debug(f"Renaming variables: {renaming_map}")
        logger.debug(f"Variable columns: {self.from_config.variable_columns}")

        for it in self.from_config.variable_columns:
            _column = tuple_column(
                Keys.NOMINAL,
                Keys.VARIABLES,
                renaming_map.get(it, it) if renaming_map is not None else it
            )
            df[_column] = self.process_df[it]

        df = df.copy()
        return df

    def nominal_weight(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.debug(f"Accessing nominal weights via process_dict[{self.process_name}][{Keys.NOMINAL}][{Keys.WEIGHT}]")
        logger.debug(f"Accessing nominal cuts via process_dict[{self.process_name}][{Keys.NOMINAL}][{Keys.CUT}]")

        _weight = self.process_dict[self.process_name][Keys.NOMINAL][Keys.WEIGHT]
        _cut = self.process_dict[self.process_name][Keys.NOMINAL][Keys.CUT]
        df[tuple_column(Keys.NOMINAL, Keys.WEIGHT)] = self.process_df[_weight] * self.process_df[_cut].astype(float)

        df = df.copy()
        return df

    def event_quantities(self, df: pd.DataFrame) -> pd.DataFrame:
        with duplicate_filter_context(logger):
            logger.warning("Updated event quantities to use NTuple Event ID")

        df[tuple_column(Keys.EVENT, Keys.ID)] = range(len(self.process_df))

        df = df.copy()
        return df

    def nominal_additional(self, df: pd.DataFrame) -> pd.DataFrame:
        for name in Keys.ADDITIONAL_NOMINALS:
            _weight = self.process_dict[self.process_name][name][Keys.WEIGHT]
            _cut = self.process_dict[self.process_name][name][Keys.CUT]
            df[tuple_column(Keys.NOMINAL, name)] = self.process_df[_weight] * self.process_df[_cut].astype(float)

        df = df.copy()
        return df

    def weight_like_uncertainties(self, df: pd.DataFrame) -> pd.DataFrame:
        for k, v in self.process_dict[self.process_name][Keys.UNCERTAINTIES].items():
            if v[Keys.UNCERTAINTY_TYPE] != Keys.WEIGHT_LIKE:
                continue

            logger.debug(f"Processing weight-like uncertainties for {k}")

            for direction in [Keys.UP, Keys.DOWN]:
                _column = tuple_column(Keys.WEIGHT_LIKE, k, direction)
                _weight, _cut = v[direction][Keys.WEIGHT], v[direction][Keys.CUT]

                try:
                    df[_column] = self.process_df[_weight] * self.process_df[_cut].astype(float)
                except KeyError:
                    logger.warning(f"KeyError for {direction} {k} in {self.process_name}, skipping!")

        df = df.copy()
        return df

    def shift_like_uncertainties(self, df: pd.DataFrame) -> pd.DataFrame:
        for k, v in self.process_dict[self.process_name][Keys.UNCERTAINTIES].items():
            if v[Keys.UNCERTAINTY_TYPE] != Keys.SHIFT_LIKE:
                continue

            logger.debug(f"Processing shift-like uncertainties for {k}")

            for direction in [Keys.UP, Keys.DOWN]:
                _column = tuple_column(Keys.SHIFT_LIKE, k, direction, Keys.WEIGHT)
                _weight, _cut = v[direction][Keys.WEIGHT], v[direction][Keys.CUT]

                try:
                    df[_column] = self.process_df[_weight] * self.process_df[_cut].astype(float)
                except KeyError:
                    logger.warning(f"KeyError for {direction} {k} in {self.process_name}, skipping!")

                for variable in self.from_config.all_shifted_variables:
                    _column = tuple_column(Keys.SHIFT_LIKE, k, direction, Keys.VARIABLES, variable)
                    _shifted_variable = v[direction][Keys.VARIABLES][variable]
                    df[_column] = self.process_df[_shifted_variable]

        df = df.copy()
        return df


class CombinedDataFrameManipulation:
    @staticmethod
    def fill_nans_in_weight_like(
        dfs: Union[pd.DataFrame, Iterable[pd.DataFrame]],
    ) -> Union[pd.DataFrame, Iterable[pd.DataFrame]]:
        if isinstance(dfs, (list, tuple)):
            return [CombinedDataFrameManipulation.fill_nans_in_weight_like(it) for it in tqdm(dfs)]
        elif isinstance(dfs, dict):
            return type(dfs)({k: CombinedDataFrameManipulation.fill_nans_in_weight_like(v) for k, v in tqdm(dfs.items())})
        elif isinstance(dfs, pd.DataFrame):
            with duplicate_filter_context(logger):
                logger.info("Filling NaN weight-like uncertainties with Nominal Weights")

            nominal_weights_column = tuple_column(Keys.NOMINAL, Keys.WEIGHT)

            for column in dfs.columns:
                if Keys.WEIGHT_LIKE not in column[0]:
                    continue

                mask = dfs.loc[:, column].isna()
                dfs.loc[mask, column] = dfs.loc[mask, nominal_weights_column]

            return dfs
        else:
            raise NotImplementedError(f"Unsupported type: {type(dfs)}")

    @staticmethod
    def fill_nans_in_shift_like(
        dfs: Union[pd.DataFrame, Iterable[pd.DataFrame]],
    ) -> Union[pd.DataFrame, Iterable[pd.DataFrame]]:
        if isinstance(dfs, (list, tuple)):
            return [CombinedDataFrameManipulation.fill_nans_in_shift_like(it) for it in tqdm(dfs)]
        elif isinstance(dfs, dict):
            return type(dfs)({k: CombinedDataFrameManipulation.fill_nans_in_shift_like(v) for k, v in tqdm(dfs.items())})
        elif isinstance(dfs, pd.DataFrame):
            with duplicate_filter_context(logger):
                logger.info("Filling NaNs in shift-like uncertainties with Nominal Weights/Variables")

            nominal_weights_column = tuple_column(Keys.NOMINAL, Keys.WEIGHT)

            for column in dfs.columns:
                if Keys.SHIFT_LIKE not in column[0]:
                    continue

                if Keys.VARIABLES in column[-2]:
                    variable, mask = column[-1], dfs.loc[:, column].isna()
                    nominal_variable_column = tuple_column(Keys.NOMINAL, Keys.VARIABLES, variable)

                    dfs.loc[mask, column] = dfs.loc[mask, nominal_variable_column]

                if Keys.WEIGHT in column[-2]:
                    mask = dfs.loc[:, column].isna()

                    dfs.loc[mask, column] = dfs.loc[mask, nominal_weights_column]

            return dfs
        else:
            raise NotImplementedError(f"Unsupported type: {type(dfs)}")

    @staticmethod
    def fill_nans_in_nominal_additional(
        dfs: Union[pd.DataFrame, Iterable[pd.DataFrame]],
    ) -> Union[pd.DataFrame, Iterable[pd.DataFrame]]:
        if isinstance(dfs, (list, tuple)):
            return [CombinedDataFrameManipulation.fill_nans_in_nominal_additional(it) for it in tqdm(dfs)]
        elif isinstance(dfs, dict):
            return type(dfs)({k: CombinedDataFrameManipulation.fill_nans_in_nominal_additional(v) for k, v in tqdm(dfs.items())})
        elif isinstance(dfs, pd.DataFrame):
            with duplicate_filter_context(logger):
                logger.info("Filling NaNs in nominal additional with Nominal Weights")

            nominal_weights_column = tuple_column(Keys.NOMINAL, Keys.WEIGHT)

            for column in dfs.columns:
                if Keys.NOMINAL in column[0] and column[-1] in Keys.ADDITIONAL_NOMINALS:
                    mask = dfs.loc[:, column].isna()

                    dfs.loc[mask, column] = dfs.loc[mask, nominal_weights_column]

            return dfs
        else:
            raise NotImplementedError(f"Unsupported type: {type(dfs)}")

    @staticmethod
    def split_folds(
        df: Union[pd.DataFrame, Iterable[pd.DataFrame]],
        condition: Union[Callable, Iterable[Callable]],
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        if isinstance(condition, (tuple, list)):
            return [CombinedDataFrameManipulation.split_folds(df, c) for c in tqdm(condition)]
        elif isinstance(condition, dict):
            return type(condition)({k: CombinedDataFrameManipulation.split_folds(df, v) for k, v in tqdm(condition.items())})
        elif callable(condition):
            return df[condition(df)]
        else:
            raise NotImplementedError(f"Unsupported type: {type(condition)}")


def tuple_column(*args: str, length: int = 5) -> str:
    return tuple(list(args) + [""] * (length - len(args)))


def tiled_mask(
    df: pd.DataFrame,
    pattern: Iterable[bool],
) -> np.ndarray:
    return np.tile(pattern, int(np.ceil(len(df) / len(pattern))))[:len(df)].astype(bool)


def odd_id(df: pd.DataFrame) -> np.ndarray:
    return (df[Keys.EVENT][Keys.ID] % 2).astype(bool)
