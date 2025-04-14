import concurrent.futures
import logging
import os
import sys
from typing import Any, Callable, Generator, List, Tuple, Union

import pandas as pd
import ROOT
import yaml
from tqdm import tqdm

sys.path.append("..")
from config.logging_setup_configs import setup_logging


CUT_KEY = "cut"
WEIGHT_KEY = "weight"
COMMON_KEY = "common"
VARIABLES_KEY = "variables"

TEMPORARY_IGNORE_WEIGHTS_AND_CUTS = {
    "lhe_scale_weight__LHEScaleMuFWeig",
    "lhe_scale_weight__LHEScaleMuRWeig",
}


class RuntimeVariables(object):
    USE_MULTIPROCESSING = True

    def __new__(cls) -> "RuntimeVariables":
        if not hasattr(cls, "instance"):
            cls.instance = super(RuntimeVariables, cls).__new__(cls)
            return cls.instance


def optional_process_pool(
    args_list: List[Tuple[Any, ...]],
    function: Callable,
    max_workers: Union[int, None] = None,
    description: Union[str, None] = None,
) -> List[Any]:
    if len(args_list) == 1 or not RuntimeVariables.USE_MULTIPROCESSING:
        results = [function(args) for args in args_list]
    else:
        n = max_workers if max_workers is not None else len(args_list)
        with concurrent.futures.ProcessPoolExecutor(max_workers=n) as executor:
            results = list(
                tqdm(
                    executor.map(function, args_list),
                    total=len(args_list),
                    desc=description,
                )
            )

    return results


class Iterate:
    @staticmethod
    def process(config):
        for channel, channel_dict in config.items():
            for era, era_dict in channel_dict.items():
                for sample, sample_dict in era_dict.items():
                    yield channel, era, sample, sample_dict

    @staticmethod
    def common_dict(common_process_dict):
        for name, value in common_process_dict.items():
            if isinstance(value, dict):
                for sub_name, sub_value in value.items():
                    if any(it in sub_value for it in TEMPORARY_IGNORE_WEIGHTS_AND_CUTS):
                        continue
                    yield sub_name, sub_value
            else:
                yield name, value

    @staticmethod
    def friends(x: dict[str, dict[int, str]], /) -> Generator:
        yield from (v for k, v in x.items() if k.startswith("friends_"))

    @staticmethod
    def rdf_files(paths_dict: dict, tree_name: str = "ntuple") -> Generator:
        for items in zip(
            Iterate.key_sorted_files(paths_dict[tree_name]),
            *(Iterate.key_sorted_files(it) for it in Iterate.friends(paths_dict))
        ):
            ntuple, *friends = items
            assert all(it.endswith(ntuple.split("/")[-1]) for it in friends)
            yield tree_name, ntuple, *friends

    @staticmethod
    def key_sorted_files(x: dict[int, str], /) -> Generator:
        for _, file in sorted(x.items(), key=lambda item: item[0]):
            yield file


class DataRetrieval:
    @staticmethod
    def build_rdf(
        tree_and_files: Tuple[str, str, list[str]],
    ) -> Tuple[ROOT.TChain, ROOT.RDataFrame]:
        key, ntuple, *friends = tree_and_files
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
        for k, v in Iterate.common_dict(process_dict[COMMON_KEY]):
            rdf = rdf.Define(k, v)
            columns.append(k)
        columns += list(process_dict[VARIABLES_KEY])
        return rdf, columns

    @staticmethod
    def get_pandasDataFrame(
        args: Tuple[str, str, str, dict, str, str, list[str]],
    ) -> dict[tuple[str, ...], pd.DataFrame]:
        process_dict, *tree_and_files = args

        _, rdf = DataRetrieval.build_rdf(tree_and_files)
        rdf, columns = DataRetrieval.define_and_collect_columns(rdf, process_dict)

        return pd.DataFrame(rdf.AsNumpy(columns))


def get_raw_dataframe(
    path,
    process_dict,
    msg: str = "",
):
    if os.path.exists(path):
        logger.info(f"Loading (raw) from {path}")
        return pd.read_feather(path)

    logger.info(f"Creating (raw) {msg}")
    dataframes = optional_process_pool(
        args_list=[
            (process_dict, *tree_and_files)
            for tree_and_files in Iterate.rdf_files(process_dict["paths"])
        ],
        function=DataRetrieval.get_pandasDataFrame,
        max_workers=16,
        description=msg,
    )

    dataframe = pd.concat(dataframes, axis=0, ignore_index=True, sort=False)

    os.makedirs(os.path.basename(path)[0], exist_ok=True)
    dataframe.to_feather(path)
    logger.info(f"Raw saved to {path}")

    return dataframe


def get_filtered_dataframe(
    path,
    process_dict,
    filter_function,
    msg: str = "",
    path_replacements: tuple[tuple[str, str]] = (
        ("/raw/", "/filtered/"),
    ),
):
    if os.path.exists(path):
        logger.info(f"Loading (filtered) from {path}")
        return pd.read_feather(path)

    logger.info(f"Creating (filtered) {msg}")
    dataframe = get_raw_dataframe(
        path=path.replace(path_replacements[-1][1], path_replacements[-1][0]),
        process_dict=process_dict,
        msg=msg,
    ) if not os.path.exists(path) else pd.read_feather(path)

    dataframe = dataframe[filter_function(dataframe)]
    os.makedirs(os.path.basename(path)[0], exist_ok=True)
    dataframe.to_feather(path)
    logger.info(f"Filtered saved to {path}")

    return dataframe


def get_converted_dataframe(
    path,
    process_dict,
    filter_function,
    msg: str = "",
    path_replacements: tuple[tuple[str, str]] = (
        ("/raw/", "/filtered/"),
        ("/filtered/", "/converted/"),
    )
):
    if os.path.exists(path):
        logger.info(f"Loading (converted) from {path}")
        return pd.read_feather(path)

    dataframe = get_filtered_dataframe(
        path=path.replace(path_replacements[-1][1], path_replacements[-1][0]),
        process_dict=process_dict,
        filter_function=filter_function,
        msg=msg,
        path_replacements=path_replacements[:-1],
    ) if not os.path.exists(path) else pd.read_feather(path)

    os.makedirs(os.path.basename(path)[0], exist_ok=True)

    return dataframe


if __name__ == "__main__":

    logger = setup_logging(logger=logging.getLogger(__name__))

    with open("./2018_tmp_config_simplified.yaml", "r") as file:
        config = yaml.safe_load(file)

    _dir = "/ceph/amonsch/HiggsToTauTau/training_datasets"
    for it in ["raw", "filtered", "converted"]:
        os.makedirs(os.path.join(_dir, it), exist_ok=True)

    for channel, era, process, process_dict in Iterate.process(config):
        filename = f"{channel}_{era}_{process}.feather"

        if os.path.exists(os.path.join(_dir, "converted", filename)):
            continue

        _ = get_converted_dataframe(
            os.path.join(_dir, "converted", filename),
            process_dict,
            lambda df: df[[it for it in df.columns if it.startswith("__common__cut__")]].any(axis=1),
            msg=f"{channel}, {era}, {process}"
        )

    print("done")
