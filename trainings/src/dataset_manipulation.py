import logging
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Literal, Tuple, Union

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


def tuple_column(*args: str, length: int = 5) -> str:
    """
    Helpers to create a tuple column name with a fixed length.
    If the length of args is less than the specified length,
    it will be padded with empty strings.
    Args:
        *args (str): The column name parts.
        length (int, optional): The desired length of the tuple. Defaults to 5.

    Returns:
        str: The tuple column name.
    """
    return tuple(list(args) + [""] * (length - len(args)))


class ROOTToPlain(object):

    def __init__(
        self,
        raw_path: Union[str, None],
        filtered_path: Union[str, None] = None,
        dtype: Literal["pandas", "ROOT"] = "pandas",
        tree_name: Union[str, None] = None,
    ) -> None:
        self.raw_path = Path(raw_path)
        self.filtered_path = Path(filtered_path)
        self._dataframe = None
        self.dataframe_path = None
        self.dtype = dtype
        self.tree_name = tree_name
        self.columns = None

    @property
    def _pandas_dataframe(self) -> pd.DataFrame:
        """
        Returns a dataframe. If the dataframe is None, it tries to load it from the raw_path or filtered_path,
        where the filtered_path is preferred.

        If both paths are None or do not exist, it raises a FileNotFoundError.
        (execute setup_raw_dataframe at least once before calling this method)

        Returns:
            pd.DataFrame: The loaded plain dataframe.
        """
        if self._dataframe is None:
            if self.filtered_path is not None and self.filtered_path.exists():
                logger.info(f"Loading filtered dataframe from {self.filtered_path}")
                self._dataframe = pd.read_feather(self.filtered_path)
            elif self.raw_path is not None and self.raw_path.exists():
                logger.info(f"Loading raw dataframe from {self.raw_path}")
                self._dataframe = pd.read_feather(self.raw_path)
            else:
                raise FileNotFoundError("No raw or filtered dataframe found.")
        return self._dataframe

    @property
    def _ROOT_dataframe(self) -> ROOT.RDataFrame:
        """
        Returns a ROOT RDataFrame. If the dataframe is None, it tries to load it from the raw_path or filtered_path,
        where the filtered_path is preferred.

        If both paths are None or do not exist, it raises a FileNotFoundError.
        (execute setup_raw_dataframe at least once before calling this method)

        Returns:
            ROOT.RDataFrame: The loaded ROOT dataframe.
        """
        if self._dataframe is None:
            if self.filtered_path is not None and self.filtered_path.exists():
                if self.tree_name is None:
                    logger.warning("Tree 'tree_name' is None. Assuming to be 'ntuple'. Set it if you want to use a different tree.")
                    self.tree_name = "ntuple"
                logger.info(f"Loading filtered dataframe from {self.filtered_path}")
                self._dataframe = ROOT.RDataFrame(self.tree_name, str(self.filtered_path))
            elif self.raw_path is not None and self.raw_path.exists():
                if self.tree_name is None:
                    logger.warning("Tree 'tree_name' is None. Assuming to be 'ntuple'. Set it if you want to use a different tree.")
                    self.tree_name = "ntuple"
                logger.info(f"Loading raw dataframe from {self.raw_path}")
                self._dataframe = ROOT.RDataFrame(self.tree_name, str(self.raw_path))
            else:
                raise FileNotFoundError("No raw or filtered dataframe found.")
        return self._dataframe

    @property
    def dataframe(self) -> Union[pd.DataFrame, ROOT.RDataFrame]:
        """
        Returns the dataframe based on the specified dtype.
        If dtype is "pandas", it returns a pandas DataFrame.
        If dtype is "ROOT", it returns a ROOT RDataFrame.

        Returns:
            Union[pd.DataFrame, ROOT.RDataFrame]: The loaded dataframe.
        """
        try:
            return getattr(self, f"_{self.dtype}_dataframe")
        except AttributeError:
            raise ValueError(f"Unsupported dtype: {self.dtype}")

    @staticmethod
    def _build_single_rdf(
        tree_and_paths: Tuple[str, str, list[str]],
    ) -> Tuple[ROOT.TChain, ROOT.RDataFrame]:
        """
        Builds a ROOT TChain and RDataFrame from the provided tree and file paths.
        The first element of tree_and_paths is the tree name, the second is the file paths tuple,
        and the third is a tuple of friend paths.

        Args:
            tree_and_paths (Tuple[str, str, list[str]]): A tuple containing the tree name, file paths, and friend paths.

        Returns:
            Tuple[ROOT.TChain, ROOT.RDataFrame]: A tuple containing the TChain and RDataFrame.
        """
        tree_name, ntuple_file, *friend_files = tree_and_paths
        logger.debug(f"Adding {ntuple_file} with friends {friend_files}")

        chain = ROOT.TChain(tree_name)
        chain.Add(ntuple_file)

        for friend in friend_files:
            fchain = ROOT.TChain(tree_name)
            fchain.Add(friend)
            chain.AddFriend(fchain)

        return chain, ROOT.RDataFrame(chain)

    @staticmethod
    def _define_and_collect_columns(
        rdf: ROOT.RDataFrame,
        filters: Union[Iterable[Tuple[str, str]], Dict[str, str], Iterable, None] = None,
        definitions: Union[Iterable[Tuple[str, str]], Dict[str, str], None] = None,
        additional_columns: Union[None, Iterable[str]] = None,
    ) -> Tuple[ROOT.RDataFrame, list]:
        """
        Creates a ROOT RDataFrame and collects the columns based on the provided filters,
        definitions, and additional columns.

        Args:
            rdf (ROOT.RDataFrame): The ROOT RDataFrame to modify.
            filters (Union[Iterable[Tuple[str, str]], Dict[str, str], Iterable, None], optional): Filters to be applied. Defaults to None.
            definitions (Union[Iterable[Tuple[str, str]], Dict[str, str], None], optional): Definitions to be applied. Defaults to None.
            additional_columns (Union[None, Iterable[str]], optional): Additional columns to be collected. Defaults to None.

        Returns:
            Tuple[ROOT.RDataFrame, list]: A tuple containing the modified RDataFrame and a list of collected columns.
        """
        columns = []

        if definitions is not None:
            if isinstance(definitions, dict):
                iterator = definitions.items()
            elif isinstance(definitions, (list, tuple)) and all(isinstance(it, tuple) for it in definitions):
                iterator = definitions
            else:
                raise ValueError("Definitions must be a dictionary or a list/tuple of list/tuple pairs.")

            for k, v in iterator:
                rdf = rdf.Define(k, v)
                columns.append(k)

        if filters is not None:
            if isinstance(filters, dict):
                iterator = filters.items()
            elif isinstance(filters, (list, tuple)) and all(isinstance(it, tuple) for it in filters):
                iterator = filters
            elif isinstance(filters, (list, tuple)) and all(isinstance(it, str) for it in filters):
                iterator = [(f"filter_{i}", it) for i, it in enumerate(filters)]
            else:
                raise ValueError("Filters must be a dictionary or a list/tuple of list/tuple pairs. or a list/tuple of strings.")

            for k, v in iterator:
                rdf = rdf.Filter(v, k)

        if additional_columns is not None:
            if not (isinstance(additional_columns, (list, tuple)) and all(isinstance(it, str) for it in additional_columns)):
                raise ValueError("Additional columns must be a list/tuple of strings.")

            columns += list(additional_columns)

        logger.debug(f"Columns: {columns}")

        return rdf, list(set(columns))

    @staticmethod
    def _single_pandasDataFrame(
        args: Tuple[str, str, str, dict, str, str, list[str]],
    ) -> pd.DataFrame:
        """
        Creates a pandas DataFrame from a ROOT RDataFrame, applying filters and definitions
        and collecting the columns.

        Args:
            args (Tuple[str, str, str, dict, str, str, list[str]]): A tuple containing
            (directory, index, filters, definitions, additional columns, tree name, file paths, and friend paths).
            directory and index not used in this function.

        Returns:
            pd.DataFrame: A pandas DataFrame with the collected columns.
        """
        _, _, filters, definitions, additional_columns, *paths = args

        _, rdf = ROOTToPlain._build_single_rdf(tree_and_paths=paths)
        rdf, columns = ROOTToPlain._define_and_collect_columns(
            rdf=rdf,
            filters=filters,
            definitions=definitions,
            additional_columns=additional_columns,
        )

        return pd.DataFrame(rdf.AsNumpy(columns))

    @staticmethod
    def _single_ROOTDataFrame(
        args: Tuple[str, str, str, dict, str, str, list[str]],
    ) -> List[str]:
        """
        Creates a ROOT RDataFrame from the provided arguments.
        The function builds a ROOT RDataFrame, applies the filters and definitions,
        and collects the columns to create a ROOT RDataFrame and saves it to a (temporary) file.

        Args:
            args (Tuple[str, str, str, dict, str, str, list[str]]): A tuple containing
            (filters, definitions, additional columns, tree name, file paths, and friend paths).

        Returns:
            List[str]: A list of collected columns.
        """
        directory, index, filters, definitions, additional_columns, *paths = args

        _, rdf = ROOTToPlain._build_single_rdf(tree_and_paths=paths)
        rdf, columns = ROOTToPlain._define_and_collect_columns(
            rdf=rdf,
            filters=filters,
            definitions=definitions,
            additional_columns=additional_columns,
        )
        # needs to be saved before combining multiple files
        rdf.Snapshot(paths[0], str(directory.joinpath(f"{index}.root")), columns)
        return columns

    def setup_raw_dataframe(
        self,
        tree_and_filepaths: Iterable[Tuple[str, ...]],
        filters: Union[Iterable[Tuple[str, str]], Dict[str, str], Iterable[str], None] = None,
        definitions: Union[Iterable[Tuple[str, str]], Dict[str, str], None] = None,
        additional_columns: Union[None, Iterable[str]] = None,
        max_workers: int = 16,
        description: str = "",
    ) -> "ROOTToPlain":
        """
        Sets up the raw dataframe by creating a ROOT RDataFrame from the provided
        tree and ntuple, friend files. The function applies the filters and definitions
        and collects the columns to create a ROOT RDataFrame that are eighter kept as
        RDataFrame or saved to a pandas DataFrame in feather format.

        Args:
            tree_and_filepaths (Iterable[Tuple[str, ...]]): A list of tuples containing
            the elements of (tree name, file paths, friend paths).
            filters (Union[Iterable[Tuple[str, str]], Dict[str, str], Iterable[str], None], optional): Filters to be applied. Defaults to None.
            definitions (Union[Iterable[Tuple[str, str]], Dict[str, str], None], optional): Definitions to be applied. Defaults to None.
            additional_columns (Union[None, Iterable[str]], optional): Additional columns to be collected. Defaults to None.
            max_workers (int, optional): Number of workers for parallel processing. Defaults to 16.
            description (str, optional): Description for the progress bar. Defaults to "".

        Returns:
            ROOTToRaw: The current instance of the ROOTToRaw class.
        """
        if self.raw_path is not None and self.raw_path.exists():
            logger.info(f"Raw dataframe already exists at {self.raw_path}")
            self.dataframe_path = self.raw_path
            return self

        logger.info(f"Creating {self.raw_path} from provided files")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            logger.info(f"Temporary directory created at {tmpdir}")

            results = optional_process_pool(
                args_list=[
                    (
                        tmpdir,
                        idx,
                        filters,
                        definitions,
                        additional_columns,
                        *tree_and_filepaths,
                    )
                    for idx, tree_and_filepaths in enumerate(tree_and_filepaths)
                ],
                function=(
                    ROOTToPlain._single_pandasDataFrame if self.dtype == "pandas"
                    else ROOTToPlain._single_ROOTDataFrame
                ),
                max_workers=max_workers,
                description=description,
            )

            if self.dtype == "ROOT":
                self.tree_name, self.columns = tree_and_filepaths[0][0], results[0]
                self._dataframe = ROOT.RDataFrame(
                    self.tree_name,
                    [str(tmpdir.joinpath(f"{i}.root")) for i, _ in enumerate(results)],
                )

            if self.dtype == "pandas":
                self._dataframe = pd.concat(results, axis=0, ignore_index=True, sort=False)

            if self.raw_path is not None:
                logger.info(f"Saving raw dataframe to {self.raw_path}")
                self.raw_path.parent.mkdir(parents=True, exist_ok=True)

                if self.dtype == "pandas":
                    self._dataframe.to_feather(str(self.raw_path))

                if self.dtype == "ROOT":
                    import ipdb; ipdb.set_trace()
                    self._dataframe.Snapshot(self.tree_name, str(self.raw_path), self.columns)

                self.dataframe_path = self.raw_path

        return self

    def filter_dataframe(
        self,
        filter_function: Union[Iterable[Callable], Callable, str, Iterable[str]],
    ) -> "ROOTToPlain":
        """
        Applys a filter to the dataframe. The filter can be a single function, a list of functions,
        (pandas) or a (list of) string(s) (ROOT). The function modifies the dataframe in place
        and saves it to the filtered_path if provided.

        Args:
            filter_function (Union[Iterable[Callable], Callable, str, Iterable[str]]): The filter function(s) to be applied.

        Returns:
            ROOTToPlain: The current instance of the ROOTToPlain class.
        """
        if self.filtered_path is not None and self.filtered_path.exists():
            logger.info(f"Filtered dataframe already exists at {self.filtered_path}")
            self.dataframe_path = self.filtered_path            
            return self

        assert self._dataframe is not None or self.raw_path.exists(), "Dataframe is None. Please call setup_raw_dataframe first."
        logger.info(f"Filtering dataframe with {filter_function}")

        if self.dtype == "pandas":
            initial_shape, mask = self.dataframe.shape, True

            if isinstance(filter_function, (list, tuple)):
                assert all(callable(it) for it in filter_function), "filter_funciton must be a callable function"
                for _filter_function in filter_function:
                    mask &= _filter_function(self._dataframe)
            elif isinstance(filter_function, dict):
                assert all(callable(it) for it in filter_function.values()), "filter_funciton must be a callable function"
                for _filter_function in filter_function.values():
                    mask &= _filter_function(self._dataframe)
            elif callable(filter_function):
                mask = filter_function(self._dataframe)

            self._dataframe = self._dataframe[mask].copy()
            logger.info(f"Filtered dataframe shape: {initial_shape} -> {self._dataframe.shape}")

        if self.dtype == "ROOT":
            initial_shape = self.dataframe.Count()

            if isinstance(filter_function, (list, tuple)):
                assert all(isinstance(it, str) for it in filter_function), "filter_funciton must be a string"
                filter_function = " && ".join([f"({it})" for it in filter_function])
            elif isinstance(filter_function, dict):
                assert all(isinstance(it, str) for it in filter_function.values()), "filter_funciton must be a string"
                filter_function = " && ".join([f"({it})" for it in filter_function.values()])
            elif isinstance(filter_function, str):
                pass

            self._dataframe = self._dataframe.Filter(filter_function)
            logger.info(f"Filtered dataframe shape: {initial_shape} -> {self._dataframe.Count()}")
        if self.filtered_path is not None:
            logger.info(f"Saving filtered dataframe to {self.filtered_path}")
            self.filtered_path.parent.mkdir(parents=True, exist_ok=True)

            if self.dtype == "pandas":
                self._dataframe.to_feather(str(self.filtered_path))
            if self.dtype == "ROOT":
                self._dataframe.Snapshot(
                    self.tree_name,
                    str(self.filtered_path),
                    [it for it in self._dataframe.GetColumnNames()],
                )

            self.dataframe_path = self.filtered_path

        return self


class _FromConfig(object):
    def __init__(self, config: dict):
        self.config = config

    def _from_single_process(self, key: str, condition: callable) -> dict:
        """
        Returns a dictionary of variables from the config for a single process based on the provided key and condition.

        Args:
            key (str): The key to filter the config.
            condition (callable): A function that takes a key and returns True if the key should be included.

        Returns:
            dict: A dictionary of variables from the config for a single process.
        """
        return {k: v for k, v in next(Iterate.process(self.config))[-1][key].items() if condition(k)}

    @property
    def label_columns(self) -> list:
        """
        Returns a list of label columns from the config for a single process. The labels are filtered
        to include only those that start with "is_" and do not contain any of the eras defined in Keys.ERAS.
        """
        def condition(x):
            return x.startswith("is_") and not any(it in x for it in Keys.ERAS)

        return [
            *self._from_single_process(
                "common",
                condition,
            ).keys(),
            *self._from_single_process(
                "nominal_variables",
                condition,
            ).keys(),
            *[]
        ]

    @property
    def variable_columns(self) -> list:
        """
        Returns a list of variable columns from the config for a single process. The variables are filtered
        to include only those that do not start with "is_" or contain any of the eras defined in Keys.ERAS.
        """
        return list(
            self._from_single_process(
                "nominal_variables",
                lambda x: not x.startswith("is_") or any(it in x for it in Keys.ERAS),
            ).keys()
        )

    @property
    def all_shifted_variables(self) -> dict:
        """
        Returns a dictionary of all shifted variables from the config for all processes.    
        """
        shifted_variables = defaultdict(list)

        for channel, era, sample, _ in Iterate.process(self.config):
            for k, v in self.config[channel][era][sample]["variables"].items():
                if k not in self.config[channel][era][sample]["nominal_variables"]:
                    shifted_variables[k.split("__")[0]].append(v)

        return dict(shifted_variables)


class ProcessDataFrameManipulation:
    def __init__(
        self,
        config: dict,
        subprocess_dict: dict,
        subprocess_df: pd.DataFrame,
        process_name: str,
        subprocess_name: str,
    ) -> None:
        self.config = config
        self.subprocess_dict = subprocess_dict
        self.from_config = _FromConfig(config)
        self.subprocess_df = subprocess_df
        self.process_name = process_name
        self.subprocess_name = subprocess_name

    def labels(self, df: pd.DataFrame, renaming_map: Union[dict, None] = None) -> pd.DataFrame:
        """
        Adds labels to the dataframe based on provided labels from config[channel][era][process]
        "common" and "nominal_variables" keys, ignoring all era specific labels.
        The labels are optionally renamed based on the provided renaming_map.

        Args:
            df (pd.DataFrame): DataFrame to add labels to.
            renaming_map (dict, optional): Dictionary to rename labels. Defaults to None.

        Returns:
            pd.DataFrame: DataFrame with added labels.
        """
        renaming_map = renaming_map or {}

        for label in self.from_config.label_columns:
            column = tuple_column(Keys.LABELS, renaming_map.get(label, label))
            df[column] = self.subprocess_df[label].astype(int).values

        for label in (item for item in self.subprocess_dict if item.startswith("is_")):
            column = tuple_column(Keys.LABELS, renaming_map.get(label, label))
            value = int(label == f"is_{self.process_name}__{self.subprocess_name.replace('-', '_')}")
            df[column] = value

        return df.copy()

    def nominal_variables(self, df: pd.DataFrame, renaming_map: Union[dict, None] = None) -> pd.DataFrame:
        """
        Adds nominal variables to the dataframe based on provided variables from
        config[channel][era][process]["nominal_variables"].
        The variables are optionally renamed based on the provided renaming_map.

        Args:
            df (pd.DataFrame): DataFrame to add variables to.
            renaming_map (dict, optional): Dictionary to rename variables. Defaults to None.

        Returns:
            pd.DataFrame: DataFrame with added nominal variables.
        """
        renaming_map = renaming_map or {}

        for variable in self.from_config.variable_columns:
            column = tuple_column(Keys.NOMINAL, Keys.VARIABLES, renaming_map.get(variable, variable))
            df[column] = self.subprocess_df[variable].astype(float).values

        return df.copy()

    def nominal_weight_and_cut(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds nominal weight and cut to the dataframe based on provided subprocess_dict

        Args:
            df (pd.DataFrame): DataFrame to add weight and cut to.

        Returns:
            pd.DataFrame: DataFrame with added nominal weight and cut.
        """
        weight, cut = self.subprocess_dict[Keys.NOMINAL][Keys.WEIGHT], self.subprocess_dict[Keys.NOMINAL][Keys.CUT]
        df[tuple_column(Keys.NOMINAL, Keys.WEIGHT)] = self.subprocess_df[weight].astype(float).values
        df[tuple_column(Keys.NOMINAL, Keys.CUT)] = self.subprocess_df[cut].astype(float).values
        return df.copy()

    def event_quantities(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds event quantities to the dataframe based on provided subprocess_df

        Args:
            df (pd.DataFrame): DataFrame to add event quantities to.

        Returns:
            pd.DataFrame: DataFrame with added event quantities.
        """
        with duplicate_filter_context(logger):
            logger.warning("Update event quantities to use NTuple Event ID!")
        df[tuple_column(Keys.EVENT, Keys.ID)] = range(len(self.subprocess_df))
        return df.copy()

    def additional_nominal_cuts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds additional cuts and weights to the dataframe based on provided subprocess_dict,
        i.e. "anti_iso" or "same_sign"

        Args:
            df (pd.DataFrame): DataFrame to add additional cuts and weights to.

        Returns:
            pd.DataFrame: DataFrame with added additional cuts and weights.
        """
        names = list(set(self.subprocess_dict.keys()) - {Keys.NOMINAL, Keys.UNCERTAINTIES})
        for name in [item for item in names if not item.startswith("is_")]:
            cut = self.subprocess_dict[name][Keys.CUT]
            weight = self.subprocess_dict[name][Keys.WEIGHT]
            df[tuple_column(Keys.NOMINAL, name, Keys.CUT)] = self.subprocess_df[cut].astype(float).values
            df[tuple_column(Keys.NOMINAL, name, Keys.WEIGHT)] = self.subprocess_df[weight].astype(float).values

        return df.copy()

    def weight_like_uncertainties(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds weight-like uncertainties to the dataframe based on provided subprocess_dict
        iterating trough the uncertainty collection provided in the subprocess_dict
        Adding cut and weight columns for each uncertainty

        Args:
            df (pd.DataFrame): DataFrame to add uncertainties to.

        Returns:
            pd.DataFrame: DataFrame with added uncertainties.
        """
        for uncertainty_name, uncertainty_dict in self.subprocess_dict[Keys.UNCERTAINTIES].items():
            if uncertainty_dict[Keys.UNCERTAINTY_TYPE] != Keys.WEIGHT_LIKE:
                continue

            logger.debug(f"Processing weight-like uncertainties for {uncertainty_name}")

            for direction in [Keys.UP, Keys.DOWN]:
                weight_column = tuple_column(Keys.WEIGHT_LIKE, uncertainty_name, direction, Keys.WEIGHT)
                cut_column = tuple_column(Keys.WEIGHT_LIKE, uncertainty_name, direction, Keys.CUT)

                weight, cut = uncertainty_dict[direction][Keys.WEIGHT], uncertainty_dict[direction][Keys.CUT]

                try:
                    df[weight_column] = self.subprocess_df[weight].astype(float).values
                    df[cut_column] = self.subprocess_df[cut].astype(float).values
                except KeyError:
                    logger.warning(f"KeyError for {direction} {uncertainty_name} in {self.subprocess_name}, skipping!")

            df = df.copy()

        return df.copy()

    def shift_like_uncertainties(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds shift-like uncertainties to the dataframe based on provided subprocess_dict
        iterating trough the uncertainty collection provided in the subprocess_dict
        Adding cut and weight columns for each uncertainty and shifted variable

        Args:
            df (pd.DataFrame): DataFrame to add uncertainties to.

        Returns:
            pd.DataFrame: DataFrame with added uncertainties.
        """
        for uncertainty_name, uncertainty_dict in self.subprocess_dict[Keys.UNCERTAINTIES].items():
            if uncertainty_dict[Keys.UNCERTAINTY_TYPE] != Keys.SHIFT_LIKE:
                continue

            logger.debug(f"Processing shift-like uncertainties for {uncertainty_name}")

            for direction in [Keys.UP, Keys.DOWN]:
                weight_column = tuple_column(Keys.SHIFT_LIKE, uncertainty_name, direction, Keys.WEIGHT)
                cut_column = tuple_column(Keys.SHIFT_LIKE, uncertainty_name, direction, Keys.CUT)
                weight, cut = uncertainty_dict[direction][Keys.WEIGHT], uncertainty_dict[direction][Keys.CUT]

                try:
                    df[weight_column] = self.subprocess_df[weight].astype(float).values
                    df[cut_column] = self.subprocess_df[cut].astype(float).values
                except KeyError:
                    logger.warning(f"KeyError for {direction} {uncertainty_name} in {self.subprocess_name}, skipping!")

                for variable in self.from_config.all_shifted_variables:
                    variable_column = tuple_column(Keys.SHIFT_LIKE, uncertainty_name, direction, Keys.VARIABLES, variable)
                    shifted_variable = uncertainty_dict[direction][Keys.VARIABLES][variable]
                    df[variable_column] = self.subprocess_df[shifted_variable].astype(float).values

            df = df.copy()

        return df.copy()

    def update_subprocess_df(self, df: pd.DataFrame, by: str = "index") -> pd.DataFrame:
        """
        Updates the subprocess_df based on the provided dataframe.
        if by is "index", it updates the subprocess_df based on the index of the dataframe,
        removing indices from provided subprocess_df that are not in the passed dataframe.

        Args:
            df (pd.DataFrame): DataFrame to update subprocess_df with.
            by (str): Method to update subprocess_df. Defaults to "index".

        Returns:
            pd.DataFrame: Updated dataframe.
        """
        if by == "index":
            self.subprocess_df = self.subprocess_df.loc[df.index, :].copy()
        else:
            raise NotImplementedError(f"Unsupported method: {by}")

        return df.copy()

    def adjust_jetFakes_weights(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Replace Nominal weight for jetFakes (previously 1.0) with anti_iso weight (F_F)

        Args:
            df (pd.DataFrame): DataFrame to adjust weights for.
        Returns:
            pd.DataFrame: DataFrame with adjusted weights.
        """
        weight = tuple_column(Keys.NOMINAL, Keys.WEIGHT)
        anti_iso = tuple_column(Keys.NOMINAL, "anti_iso", Keys.WEIGHT)
        df[weight] = df[anti_iso].values.astype(df[weight].dtype)

        return df.copy()


class CombinedDataFrameManipulation:
    @staticmethod
    def _fill_nans_in_variables(dfs: pd.DataFrame, filter_function: callable):
        """
        Generic function to fill NaN values in variable columns with the nominal values.

        Args:
            dfs (pd.DataFrame): DataFrame to fill NaNs in.
            filter_function (callable): Function to filter columns.

        Returns:
            pd.DataFrame: DataFrame with NaNs filled.

        """
        for column in filter(filter_function, dfs.columns):
            variable, mask = column[-1], dfs.loc[:, column].isna()
            nominal_column = tuple_column(Keys.NOMINAL, Keys.VARIABLES, variable)
            dfs.loc[mask, column] = dfs.loc[mask, nominal_column]

        return dfs.copy()

    @staticmethod
    def _fill_nans_in_weights_and_cuts_default(dfs: pd.DataFrame, filter_function: callable):
        """
        Generic function to fill NaN values in weight and cut columns with the nominal values.

        Args:
            dfs (pd.DataFrame): DataFrame to fill NaNs in.
            filter_function (callable): Function to filter columns.

        Returns:
            None: The function modifies the DataFrame in place.
        """
        for column in filter(filter_function, dfs.columns):
            if (x := Keys.WEIGHT) in column or (x := Keys.CUT) in column:
                mask = dfs.loc[:, column].isna()
                dfs.loc[mask, column] = dfs.loc[mask, tuple_column(Keys.NOMINAL, x)]

        return dfs.copy()

    @staticmethod
    def _fill_nans_in_weight_like_jetFakes(dfs: pd.DataFrame, jetFakes_identifier: str, filter_function: callable) -> pd.DataFrame:
        """
        Generic function to fill NaN values in weight and cut columns in presence of jetFakes.
        jetFakes events are replaced with anti_iso weight and cut values, other events are
        replaced with nominal weight and cut values.

        Args:
            dfs (pd.DataFrame): DataFrame to fill NaNs in.
            jetFakes_identifier (str): Identifier for jetFakes.
            filter_function (callable): Function to filter columns.

        Returns:
            pd.DataFrame: DataFrame with NaNs filled.
        """
        assert all(
            [
                tuple_column(Keys.LABELS, jetFakes_identifier),
                tuple_column(Keys.NOMINAL, "anti_iso", Keys.WEIGHT),
                tuple_column(Keys.NOMINAL, "anti_iso", Keys.CUT),
            ]
        ), f"Missing columns requiered for jetFakes: {jetFakes_identifier}, anti_iso (weight), anti_iso (cut)"

        for column in filter(filter_function, dfs.columns):
            if (x := Keys.WEIGHT) in column or (x := Keys.CUT) in column:
                is_nan = dfs.loc[:, column].isna()
                is_jetFakes = dfs.loc[:, tuple_column(Keys.LABELS, jetFakes_identifier)].astype(bool)

                dfs.loc[is_nan & is_jetFakes, column] = dfs.loc[is_nan & is_jetFakes, tuple_column(Keys.NOMINAL, "anti_iso", x)]
                dfs.loc[is_nan & ~is_jetFakes, column] = dfs.loc[is_nan & ~is_jetFakes, tuple_column(Keys.NOMINAL, x)]

        return dfs.copy()

    @staticmethod
    def fill_nans_in_weight_like(
        dfs: Union[pd.DataFrame, Iterable[pd.DataFrame]],
        has_jetFakes: bool = False,
        jetFakes_identifier: str = "is_jetFakes",
    ) -> Union[pd.DataFrame, Iterable[pd.DataFrame]]:
        """
        Replaces NaN values in weight-like uncertainties columns with Nominal weight and cut
        values. If has_jetFakes is True, it will replace the cut NaN values for events
        with jetFakes_identifier using anti_iso cut values.

        To be applied after procecss stacking. Any NaNs before stacking are erroneous.

        Args:
            dfs (Union[pd.DataFrame, Iterable[pd.DataFrame]]): DataFrame or iterable of DataFrames to fill NaNs in.
            has_jetFakes (bool, optional): Flag to indicate if jetFakes are present. Defaults to False.
            jetFakes_identifier (str, optional): Identifier for jetFakes. Defaults to "is_jetFakes".

        Returns:
            Union[pd.DataFrame, Iterable[pd.DataFrame]]: DataFrame or iterable of DataFrames with NaNs filled.
        """
        kwargs = dict(has_jetFakes=has_jetFakes, jetFakes_identifier=jetFakes_identifier)

        if isinstance(dfs, (list, tuple)):
            return [CombinedDataFrameManipulation.fill_nans_in_weight_like(it, **kwargs) for it in tqdm(dfs)]
        elif isinstance(dfs, dict):
            return type(dfs)({k: CombinedDataFrameManipulation.fill_nans_in_weight_like(v, **kwargs) for k, v in tqdm(dfs.items())})
        elif isinstance(dfs, pd.DataFrame):
            if has_jetFakes:
                with duplicate_filter_context(logger):
                    logger.info("Filling NaN weight-like uncertainty weight and cut with anti_iso weight and cut for jetFakes and Nominal weight and cut for others")

                return CombinedDataFrameManipulation._fill_nans_in_weight_like_jetFakes(
                    dfs=dfs,
                    filter_function=lambda it: it[0] == Keys.WEIGHT_LIKE,
                    jetFakes_identifier=jetFakes_identifier,
                )
            else:
                with duplicate_filter_context(logger):
                    logger.info("Filling NaN weight-like uncertainty weight and cut with Nominal weight and cut")

                return CombinedDataFrameManipulation._fill_nans_in_weights_and_cuts_default(
                    dfs=dfs,
                    filter_function=lambda it: it[0] == Keys.WEIGHT_LIKE,
                )
        else:
            raise NotImplementedError(f"Unsupported type: {type(dfs)}")

    @staticmethod
    def fill_nans_in_shift_like(
        dfs: Union[pd.DataFrame, Iterable[pd.DataFrame]],
        has_jetFakes: bool = False,
        jetFakes_identifier: str = "is_jetFakes",
    ) -> Union[pd.DataFrame, Iterable[pd.DataFrame]]:
        """
        Replaces NaN values in shifted variables, cut and weight columns with Nominal variable values.
        If has_jetFakes is True, it will replace the cut NaN values for events
        with jetFakes_identifier using anti_iso cut values.

        Args:
            dfs (Union[pd.DataFrame, Iterable[pd.DataFrame]]): DataFrame or iterable of DataFrames to fill NaNs in.
            has_jetFakes (bool, optional): Flag to indicate if jetFakes are present. Defaults to False.
            jetFakes_identifier (str, optional): Identifier for jetFakes. Defaults to "is_jetFakes".

        Returns:
            Union[pd.DataFrame, Iterable[pd.DataFrame]]: DataFrame or iterable of DataFrames with NaNs filled.
        """
        kwargs = dict(has_jetFakes=has_jetFakes, jetFakes_identifier=jetFakes_identifier)

        if isinstance(dfs, (list, tuple)):
            return [CombinedDataFrameManipulation.fill_nans_in_shift_like(it, **kwargs) for it in tqdm(dfs)]
        elif isinstance(dfs, dict):
            return type(dfs)({k: CombinedDataFrameManipulation.fill_nans_in_shift_like(v, **kwargs) for k, v in tqdm(dfs.items())})
        elif isinstance(dfs, pd.DataFrame):
            if has_jetFakes:
                with duplicate_filter_context(logger):
                    logger.info("Filling NaN weight-like uncertainty weight and cut with anti_iso weight and cut for jetFakes and Nominal weight and cut for others")

                dfs = CombinedDataFrameManipulation._fill_nans_in_weight_like_jetFakes(
                    dfs=dfs,
                    filter_function=lambda it: it[0] == Keys.SHIFT_LIKE,
                    jetFakes_identifier=jetFakes_identifier,
                )
            else:
                with duplicate_filter_context(logger):
                    logger.info("Filling NaN weight-like uncertainty weight and cut with Nominal weight and cut")

                dfs = CombinedDataFrameManipulation._fill_nans_in_weights_and_cuts_default(
                    dfs=dfs,
                    filter_function=lambda it: it[0] == Keys.SHIFT_LIKE,
                )

            with duplicate_filter_context(logger):
                logger.info("Filling NaN in shifted variables with Nominal variables")

            return CombinedDataFrameManipulation._fill_nans_in_variables(
                dfs=dfs,
                filter_function=lambda it: it[0] == Keys.SHIFT_LIKE and Keys.VARIABLES in it
            )

        else:
            raise NotImplementedError(f"Unsupported type: {type(dfs)}")

    @staticmethod
    def fill_nans_in_nominal_additional(
        dfs: Union[pd.DataFrame, Iterable[pd.DataFrame]],
        default_value: float = 0.0,
    ) -> Union[pd.DataFrame, Iterable[pd.DataFrame]]:
        """
        Replaces NaN values in nominal additional columns with default_value in case of missing values,
        affecting i.e. signal processes.

        Args:
            dfs (Union[pd.DataFrame, Iterable[pd.DataFrame]]): DataFrame or iterable of DataFrames to fill NaNs in.
            default_value (float, optional): Default value to fill NaNs with. Defaults to 0.0.

        Returns:
            Union[pd.DataFrame, Iterable[pd.DataFrame]]: DataFrame or iterable of DataFrames with NaNs filled.
        """
        if isinstance(dfs, (list, tuple)):
            return [CombinedDataFrameManipulation.fill_nans_in_nominal_additional(it) for it in tqdm(dfs)]
        elif isinstance(dfs, dict):
            return type(dfs)({k: CombinedDataFrameManipulation.fill_nans_in_nominal_additional(v) for k, v in tqdm(dfs.items())})
        elif isinstance(dfs, pd.DataFrame):
            with duplicate_filter_context(logger):
                logger.info("Filling NaNs in nominal additional with Nominal Weights")

            def is_additional_nominal(x):
                return x[0] == Keys.NOMINAL and x[1] not in {
                    Keys.VARIABLES,
                    Keys.WEIGHT,
                    Keys.CUT,
                }

            for column in filter(is_additional_nominal, dfs.columns):
                if Keys.WEIGHT in column or Keys.CUT in column:
                    mask = dfs.loc[:, column].isna()
                    dfs.loc[mask, column] = default_value

            return dfs.copy()
        else:
            raise NotImplementedError(f"Unsupported type: {type(dfs)}")

    @staticmethod
    def split_folds(
        df: Union[pd.DataFrame, Iterable[pd.DataFrame]],
        condition: Union[Callable, Iterable[Callable]],
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        """
        Splits the dataframe into folds based on the provided condition, where the condition
        is a callable function with the dataframe as input, returning a boolean mask.
        If condition is a Iterable, it will be applied to each element in the iterable.

        Args:
            df (Union[pd.DataFrame, Iterable[pd.DataFrame]]): DataFrame or iterable of DataFrames to split.
            condition (Union[Callable, Iterable[Callable]]): Condition to split the dataframe.

        Returns:
            Union[pd.DataFrame, List[pd.DataFrame]]: DataFrame or list of DataFrames split by the condition.
        """
        if isinstance(condition, (tuple, list)):
            return [CombinedDataFrameManipulation.split_folds(df, c) for c in tqdm(condition)]
        elif isinstance(condition, dict):
            return type(condition)({k: CombinedDataFrameManipulation.split_folds(df, v) for k, v in tqdm(condition.items())})
        elif callable(condition):
            return df[condition(df)]
        else:
            raise NotImplementedError(f"Unsupported type: {type(condition)}")
