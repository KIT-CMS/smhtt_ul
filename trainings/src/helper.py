import concurrent.futures
import re
from typing import Any, Callable, Generator, List, Optional, Tuple, Union

from tqdm import tqdm

VARS_TAUS = "iso_1,iso_2,mass_1,mass_2,pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,tau_decaymode_1,tau_decaymode_2"
VARS_TAUS = VARS_TAUS.split(",")
VARS_TAU_PAIR = "m_vis,mt_1,mt_2,mt_1_pf,mt_2_pf,pfmet,met,pzetamissvis,metphi,deltaR_ditaupair,pt_vis,mtt_coll_approx"
VARS_TAU_PAIR = VARS_TAU_PAIR.split(",")
VARS_JETS="jpt_1,jpt_2,jeta_1,jeta_2,jphi_1,jphi_2,mjj,njets,pt_dijet,jet_hemisphere"
VARS_JETS = VARS_JETS.split(",")
VARS_BJETS="nbtag,bpair_pt_1,bpair_pt_2,bpair_eta_1,bpair_eta_2,bpair_phi_1,bpair_phi_2,bpair_btag_value_1,bpair_btag_value_2,bpair_m_inv,bpair_pt_dijet,bpair_deltaR"
VARS_BJETS = VARS_BJETS.split(",")
# VARS_DISTANCES="deltaPhi_met_tau1,deltaPhi_met_tau2,deltaPhi_met_fatjet,deltaPhi_met_bjet1,deltaPhi_met_bjet2,deltaR_tau1_fatjet,deltaR_tau2_fatjet,balance_pT_fatjet_Z,deltaR_bjet1_fatjet,deltaR_bjet2_fatjet,deltaR_tau1_bjet1,deltaR_tau1_bjet2,deltaR_tau2_bjet1,deltaR_tau2_bjet2"
VARS_BBTT="mt_tot,pt_tautaubb,mass_tautaubb"
VARS_BBTT = VARS_BBTT.split(",")
# VARS_KINFIT="kinfit_mX,kinfit_mY,kinfit_chi2,kinfit_convergence,kinfit_mX_YToBB,kinfit_mY_YToBB,kinfit_chi2_YToBB,kinfit_convergence_YToBB,kinfit_mX_YToTauTau,kinfit_mY_YToTauTau,kinfit_chi2_YToTauTau,kinfit_convergence_YToTauTau"
VARS_FASTMTT="m_fastmtt,pt_fastmtt,eta_fastmtt,phi_fastmtt"
VARS_FASTMTT = VARS_FASTMTT.split(",")

ALL_VARIABLES = (
    VARS_TAUS + VARS_TAU_PAIR + VARS_JETS + VARS_BJETS + VARS_BBTT + VARS_FASTMTT
)


TRAINING_VARIABLES = ALL_VARIABLES + [
    # "pt_1",
    # "pt_2",
    # "m_vis",
    # "njets",
    # "nbtag",
    # "jpt_1",
    # "jpt_2",
    # "jeta_1",
    # "jeta_2",
    # "m_fastmtt",
    # "pt_vis",
    # "mjj",
    # "deltaR_ditaupair",
    # "pt_dijet",

    # -- label flags ---
    "is_data",
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
    """
    Collection of keys used in the configuration files and for columns in training dataframes.
    To be adjusted according to the actual analysis if needed.
    """
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

    ADDITIONAL_NOMINALS = ["abcd_anti_iso", "abcd_same_sign", "abcd_same_sign_anti_iso"]


def find_variable_expansions(full_expression: str, substring: str) -> list[str]:
    """
    Helper to find all occurrences of a substring in a full expression.

    Args:
        full_expression (str): The full expression to search in.
        substring (str): The substring to find.

    Returns:
        list[str]: A list of all occurrences of the substring in the full expression.
    """
    pattern = re.compile(r'\b' + re.escape(substring) + r'(?:__[A-Za-z0-9_]+)?\b')
    return pattern.findall(full_expression)


class RuntimeVariables(object):
    """
    A singleton-like container class holding variables that can be adjusted at runtime.

    Attributes:
        USE_MULTIPROCESSING (bool): Flag to enable or disable multiprocessing globally
    """
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
    """
    Running a function with a list of arguments in parallel using multiprocessing if
    the list of arguments is longer than one and multiprocessing is enabled.

    Args:
        args_list: List of tuples with arguments for the function
        function: Function to be executed
        max_workers: Number of workers to be used in the multiprocessing pool (default: None)

    Return:
        List of results of the function

    """

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
    """
    Collection of usefull iterators to iterate over the configuration files.
    """
    @staticmethod
    def subprocesses(
        config: dict,
    ) -> Generator[tuple[str, str, str, str, dict], None, None]:
        """
        Iterates over all subprocess in the configuration file, ignoring
        the keys "paths", "common", "variables", and "nominal_variables" and label flags.

        Args:
            config (dict): The configuration dictionary to iterate over.

        Yields:
            tuple: A tuple containing the channel, era, process, subprocess, and the corresponding dictionary.
        """
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
        """
        Iterates over all processes in the configuration file.

        Args:
            config (dict): The configuration dictionary to iterate over.
        """
        for channel, channel_dict in config.items():
            for era, era_dict in channel_dict.items():
                for sample, sample_dict in era_dict.items():
                    yield channel, era, sample, sample_dict

    @staticmethod
    def common_dict(
        common_process_dict: dict,
        ignore_weight_and_cuts: Optional[set[str]] = None,
    ):
        """
        Iterates over a process specific "common" dictionary.

        Args:
            common_process_dict (dict): The common dictionary to iterate over.
            ignore_weight_and_cuts (set[str], optional): A set of strings that, if found in the dictionary values, will trigger a skip of the item.

        Yields:
            tuple: A tuple containing the name and value of each item in the dictionary.
        """
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
        """
        Iterates over all keys in a dictionary that start with "friends_".

        Args:
            x (dict): The dictionary to iterate over.

        Yields:
            Generator: A generator yielding the values of the keys that start with "friends_".
        """
        yield from (v for k, v in x.items() if k.startswith("friends_"))

    @staticmethod
    def rdf_files(paths_dict: dict, tree_name: str = "ntuple") -> Generator:
        """
        Iterates over all tree_name files and corresponding firend files in agiven paths_dict.
        The tree_name is the name of the tree in the ROOT file.
        Assumes that tree_name and friends_ have the same (key, value) structure for all
        (tree_name, *firends_) files.

        Args:
            paths_dict (dict): The dictionary containing the paths to the files.
            tree_name (str): The name of the tree in the ROOT file. Defaults to "ntuple".

        Yields:
            Generator: A generator yielding tuples of the form (tree_name, ntuple, *friends).
        """
        for items in zip(
            Iterate.key_sorted_files(paths_dict[tree_name]),
            *(Iterate.key_sorted_files(it) for it in Iterate.friends(paths_dict))
        ):
            ntuple, *friends = items
            assert all(it.endswith(ntuple.split("/")[-1]) for it in friends)
            yield tree_name, ntuple, *friends

    @staticmethod
    def key_sorted_files(x: dict[int, str], /) -> Generator:
        """
        Iterates over a dictionary of files, sorted by their keys.
        The keys are assumed to be integers or floats.

        Args:
            x (dict): The dictionary containing the files to be iterated over.

        Yields:
            Generator: A generator yielding the files sorted by their keys.
        """

        for _, file in sorted(x.items(), key=lambda item: item[0]):
            yield file


class PipeDict(dict):
    """
    Helper class to allow for method chaining on dictionaries like pandas.pipe does.
    """
    def pipe(self, func: callable, *args: Any, **kwargs: Any) -> dict:
        return func(self, *args, **kwargs)
