import concurrent.futures
import re
from typing import Any, Callable, Generator, List, Optional, Tuple, Union

from tqdm import tqdm


TRAINING_VARIABLES = [
    "pt_1",
    "pt_2",
    "m_vis",
    "njets",
    "nbtag",
    "jpt_1",
    "jpt_2",
    "jeta_1",
    "jeta_2",
    # "m_fastmtt",
    "pt_vis",
    "mjj",
    "deltaR_ditaupair",
    "pt_dijet",
    "is_data",
    # -- label flags ---
    "is_dyjets",
    "is_embedding",
    "is_ggh_htautau",
    "is_ttbar",
    "is_vbf_htautau",
    "is_wjets",
    # --- era flags ---
    "is_2018",
    "is_2017",
    "is_2016preVFP",
    "is_2016postVFP",
]


class Keys:
    ERAS = {"2016preVFP", "2016postVFP", "2017", "2018"}
    CHANNELS = {"mt", "et", "tt"}

    COMMON = "common"
    NOMINAL_VARIABLES = "nominal_variables"
    UNCERTAINTIES = "uncertainties"
    UNCERTAINTY_TYPE = "uncertainty_type"
    PATHS = "paths"

    EVENT = "Event"
    LABELS = "Labels"
    NOMINAL = "Nominal"
    WEIGHT_LIKE = "WeightLike"
    SHIFT_LIKE = "ShiftLike"

    VARIABLES = "variables"
    WEIGHT = "weight"
    CUT = "cut"
    UP = "up"
    DOWN = "down"

    ID = "id"

    ADDITIONAL_NOMINALS = ["anti_iso", "same_sign", "same_sign_anti_iso"]


def find_variable_expansions(full_expression: str, substring: str) -> list[str]:
    pattern = re.compile(r'\b' + re.escape(substring) + r'(?:__[A-Za-z0-9_]+)?\b')
    return pattern.findall(full_expression)


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
    def subprocesses(
        config: dict,
    ) -> Generator[tuple[str, str, str, str, dict], None, None]:
        skip_subprocesses = {"paths", "common", "variables", "nominal_variables"}
        for channel, channel_dict in config.items():
            if channel not in Keys.CHANNELS or not isinstance(channel_dict, dict):
                continue
            for era, era_dict in channel_dict.items():
                if era not in Keys.ERAS or not isinstance(era_dict, dict):
                    continue
                for process, process_dict in era_dict.items():
                    if not isinstance(process_dict, dict):
                        continue
                    for subprocess, subprocess_dict in process_dict.items():
                        flagname = f"is_{process}__{subprocess.replace('-', '_')}"
                        if isinstance(subprocess_dict, dict) and subprocess not in skip_subprocesses and subprocess != flagname:
                            yield channel, era, process, subprocess, subprocess_dict

    @staticmethod
    def process(config: dict) -> Generator[tuple[str, str, str, dict], None, None]:
        for channel, channel_dict in config.items():
            for era, era_dict in channel_dict.items():
                for sample, sample_dict in era_dict.items():
                    yield channel, era, sample, sample_dict

    @staticmethod
    def common_dict(
        common_process_dict: dict,
        ignore_weight_and_cuts: Optional[set[str]] = None,
    ):
        for name, value in common_process_dict.items():
            if isinstance(value, dict):
                for sub_name, sub_value in value.items():
                    if ignore_weight_and_cuts and any(
                        it in sub_value for it in ignore_weight_and_cuts
                    ):
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


class PipeDict(dict):
    def pipe(self, func: callable, *args: Any, **kwargs: Any) -> dict:
        return func(self, *args, **kwargs)
