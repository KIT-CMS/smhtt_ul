import yaml
import re
from copy import deepcopy
from typing import Generator, Union

ERAS = {"2016preVFP", "2016postVFP", "2017", "2018"}
CHANNELS = {"mt", "et", "tt"}
CUT_KEY = "cut"
WEIGHT_KEY = "weight"
COMMON_KEY = "common"
VARIABLES_KEY = "variables"
NOMINAL_VARIABLES_KEY = "nominal_variables"
NOMINAL_KEY = "Nominal"
UNCERTAINTY_TYPE = "uncertainty_type"
UNCERTAINTIES_KEY = "Uncertainties"


def find_variable_expansions(full_expression: str, substring: str) -> list[str]:
    pattern = re.compile(r'\b' + re.escape(substring) + r'(?:__[A-Za-z0-9_]+)?\b')
    return pattern.findall(full_expression)


def iter_subprocesses(
    config: dict,
) -> Generator[tuple[str, str, str, str, dict], None, None]:
    skip_subprocesses = {"paths", "common", "variables", "nominal_variables"}
    for channel, channel_dict in config.items():
        if channel not in CHANNELS or not isinstance(channel_dict, dict):
            continue
        for era, era_dict in channel_dict.items():
            if era not in ERAS or not isinstance(era_dict, dict):
                continue
            for process, process_dict in era_dict.items():
                if not isinstance(process_dict, dict):
                    continue
                for subprocess, subprocess_dict in process_dict.items():
                    if isinstance(subprocess_dict, dict) and subprocess not in skip_subprocesses:
                        yield channel, era, process, subprocess, subprocess_dict


class MissingCutOrWeight(Exception):
    pass


class GeneralConfigManipulation(object):
    @staticmethod
    def set_common(config: dict) -> dict:
        config = deepcopy(config)
        for channel, era, process, *_ in iter_subprocesses(deepcopy(config)):
            config[channel][era][process].setdefault(COMMON_KEY, {})
        return config

    @staticmethod    
    def remove_variation_pattern(
        config: dict,
        ff_pattern: str = "anti_iso_CMS_",
        ignore_process: str = "data",
    ) -> dict:
        config = deepcopy(config)
        for channel, channel_dict in config.items():
            if channel not in CHANNELS or not isinstance(channel_dict, dict):
                continue
            for era_dict in channel_dict.values():
                if not isinstance(era_dict, dict):
                    continue
                for process, proc_dict in era_dict.items():
                    if process == ignore_process or not isinstance(proc_dict, dict):
                        continue
                    for subproc_dict in proc_dict.values():
                        if not isinstance(subproc_dict, dict):
                            continue
                        for key in [key for key in subproc_dict if ff_pattern in key]:
                            del subproc_dict[key]
        return config

    @staticmethod
    def _should_remove(key: str, collection: list) -> bool:
        return collection and (key in collection or any(item in key for item in collection))

    @staticmethod
    def _recursive_remove(x: dict, /, level: int, level_keys: list[str], criteria: dict) -> None:
        if level >= len(level_keys):
            return None

        current_level = level_keys[level]
        for key in list(x.keys()):
            if GeneralConfigManipulation._should_remove(key, criteria.get(current_level, [])):
                del x[key]
            else:
                if isinstance(x[key], dict):
                    GeneralConfigManipulation._recursive_remove(x[key], level + 1, level_keys, criteria)

    @staticmethod
    def remove_from_config(
        config: dict,
        channels: list[str] = None,
        eras: list[str] = None,
        processes: list[str] = None,
        subprocesses: list[str] = None,
        shifts: list[str] = None,
    ) -> dict:
        config = deepcopy(config)
        levels = ["channel", "era", "process", "subprocess", "shift"]
        removal = {
            "channel": channels or [],
            "era": eras or [],
            "process": processes or [],
            "subprocess": subprocesses or [],
            "shift": shifts or [],
        }
        GeneralConfigManipulation._recursive_remove(config, 0, levels, removal)
        return config

    @staticmethod
    def rename(
        config: dict,
        processes: dict = None,
        subprocesses: dict = None,
        shifts: dict = None,
    ) -> dict:
        config = deepcopy(config)
        processes = processes or {}
        subprocesses = subprocesses or {}
        shifts = shifts or {}

        for channel, channel_dict in config.items():
            if channel not in CHANNELS or not isinstance(channel_dict, dict):
                continue
            for era, era_dict in channel_dict.items():
                if not isinstance(era_dict, dict):
                    continue
                new_era = {}
                for process, process_dict in era_dict.items():
                    new_process = processes.get(process, process)
                    if not isinstance(process_dict, dict):
                        new_era[new_process] = process_dict
                        continue
                    new_processes = {}
                    for subprocess, subprocess_dict in process_dict.items():
                        new_subprocesses = subprocesses.get(subprocess, subprocess)
                        if isinstance(subprocess_dict, dict):
                            new_shifts = {
                                shifts.get(shift, shift): shift_dict
                                for shift, shift_dict in subprocess_dict.items()
                            }
                            new_processes[new_subprocesses] = new_shifts
                        else:
                            new_processes[new_subprocesses] = subprocess_dict
                    new_era[new_process] = new_processes
                channel_dict[era] = new_era
        return config

    @staticmethod
    def recursive_update(x: dict, y: dict, /) -> dict:
        for k, v in y.items():
            if k in x:
                if isinstance(x[k], dict) and isinstance(v, dict):
                    GeneralConfigManipulation.recursive_update(x[k], v)
                else:
                    x[k] = v
            else:
                x[k] = v
        return x

    @staticmethod
    def add_additional_flags(config):
        config = deepcopy(config)

        process_subprocesses = set([(p, subp) for _, _, p, subp, *_ in iter_subprocesses(config)])

        for channel, era, process, subprocess, *_ in iter_subprocesses(config):
            for _era in ERAS:
                config[channel][era][process][COMMON_KEY][f"is_{_era}"] = f"(float){int(_era == era)}."

        for channel, era, process, subprocess, *_ in iter_subprocesses(config):
            for _process, _subprocess in process_subprocesses:
                flag = int(_process == process and _subprocess == subprocess)
                key = f"is_{_process}__{_subprocess.replace('-', '_')}"
                config[channel][era][process][COMMON_KEY][key] = f"(float){flag}."

        return config


class ConfigManipulation(object):
    @staticmethod
    def convert_weights_and_cuts_to_common(config: dict) -> dict:
        config = deepcopy(config)

        for channel, era, process, _, subprocess_dict in iter_subprocesses(config):
            config[channel][era][process].get(COMMON_KEY, {})
            config[channel][era][process][COMMON_KEY][CUT_KEY] = {}
            config[channel][era][process][COMMON_KEY][WEIGHT_KEY] = {}
            common_cuts_rev, common_weights_rev = {}, {}

            for shift, shift_dict in subprocess_dict.items():
                cut, weight = shift_dict.get(CUT_KEY), shift_dict.get(WEIGHT_KEY)
                if cut is None or weight is None:
                    raise MissingCutOrWeight(
                        f"Missing cut or weight for {shift} in {subprocess_dict}, aborting."
                    )
                if cut in common_cuts_rev:
                    shift_dict[CUT_KEY] = common_cuts_rev[cut]
                else:
                    new_cut = f'__{COMMON_KEY}__{CUT_KEY}__{len(common_cuts_rev)}__'
                    config[channel][era][process][COMMON_KEY][CUT_KEY][new_cut] = cut
                    common_cuts_rev[cut] = new_cut
                    shift_dict[CUT_KEY] = new_cut

                if weight in common_weights_rev:
                    shift_dict[WEIGHT_KEY] = common_weights_rev[weight]
                else:
                    new_weight = f'__{COMMON_KEY}__{WEIGHT_KEY}__{len(common_weights_rev)}__'
                    config[channel][era][process][COMMON_KEY][WEIGHT_KEY][new_weight] = weight
                    common_weights_rev[weight] = new_weight
                    shift_dict[WEIGHT_KEY] = new_weight

        return config

    @staticmethod
    def add_set_of_training_variables(
        config: dict,
        training_vars: list[str],
    ) -> dict:
        config = deepcopy(config)

        default_variables = {k: k for k in training_vars}

        for channel, era, process, subprocess, subprocess_dict in iter_subprocesses(deepcopy(config)):
            if isinstance(subprocess_dict, dict):
                config[channel][era][process].setdefault(COMMON_KEY, {})
                config[channel][era][process].setdefault(VARIABLES_KEY, deepcopy(default_variables))
                config[channel][era][process].setdefault(NOMINAL_VARIABLES_KEY, deepcopy(default_variables))

            for shift_name, shift_dict in subprocess_dict.items():
                if not isinstance(shift_dict, dict):
                    continue

                if (cut := shift_dict.get(CUT_KEY)) is None or (weight := shift_dict.get(WEIGHT_KEY)) is None:
                    raise MissingCutOrWeight(f"Missing cut or weight for {shift_dict}, aborting.")
                if f"__{COMMON_KEY}__{CUT_KEY}__" in str(cut):
                    if (cut := config[channel][era][process][COMMON_KEY][CUT_KEY].get(cut)) is None:
                        raise MissingCutOrWeight(f"Missing common cut for {shift_dict}, aborting.")
                if f"__{COMMON_KEY}__{WEIGHT_KEY}__" in str(weight):
                    if (weight := config[channel][era][process][COMMON_KEY][WEIGHT_KEY].get(weight)) is None:
                        raise MissingCutOrWeight(f"Missing common weight for {shift_dict}, aborting.")

                combined, variables_dict = f"{cut} && {weight}", {}
                for variable in training_vars:
                    if len((matches := list(set(find_variable_expansions(combined, variable))))) > 1:
                        raise AssertionError(f"{variable} appears multiple times in under different names ({matches}) aborting.")
                    variables_dict[variable] = matches[0] if matches else variable

                if variables_dict == default_variables:
                    config[channel][era][process][subprocess][shift_name][VARIABLES_KEY] = f"__{NOMINAL_VARIABLES_KEY}__"
                else:
                    config[channel][era][process][subprocess][shift_name][VARIABLES_KEY] = variables_dict
                    config[channel][era][process][VARIABLES_KEY].update({v: v for v in variables_dict.values()})

        return config

    @staticmethod
    def nest_and_categorize_uncertainties(config: dict) -> dict:
        config = deepcopy(config)
        pattern = re.compile(r"^(.*?)(Up|Down)(?:_.*)?$")

        for *_, subprocess_dict in iter_subprocesses(config):
            subprocess_dict.setdefault(UNCERTAINTIES_KEY, {})
            uncertainty_group, shifts_to_remove = {}, []
            for shift in list(subprocess_dict.keys()):
                if not (m := pattern.match(shift)):
                    continue
                base_name, direction = m.groups()
                shifts_to_remove.append(shift)
                group = uncertainty_group.setdefault(base_name, {})
                shift_data = deepcopy(subprocess_dict[shift])
                group[direction] = shift_data

            for key in shifts_to_remove:
                del subprocess_dict[key]

            if uncertainty_group:
                for base_name, group in uncertainty_group.items():  # promote common keys
                    for key in (CUT_KEY, VARIABLES_KEY, WEIGHT_KEY):
                        up, down = group["Up"].get(key), group["Down"].get(key)
                        if up == down:
                            group[key] = up
                            del group["Up"][key], group["Down"][key]
                    if CUT_KEY in group and VARIABLES_KEY in group:
                        group[UNCERTAINTY_TYPE] = "weight_like"
                    else:
                        group[UNCERTAINTY_TYPE] = "shift_like"
                sorted_uncertainty_group = {k: v for k, v in sorted(uncertainty_group.items(), key=lambda item: item[0])}
                subprocess_dict[UNCERTAINTIES_KEY] = sorted_uncertainty_group

        return config


if __name__ == "__main__":

    config_paths = [
        "../2018__mt__tmp_config.yaml",
    ]

    config = {}
    for config_path in config_paths:
        with open(config_path, "r") as f:
            config = GeneralConfigManipulation.recursive_update(config, yaml.safe_load(f))

    # ---

    # those operations defined here can be done in any order and/or left out

    config = GeneralConfigManipulation.set_common(config)
    config = GeneralConfigManipulation.remove_from_config(
        config,
        processes=["W", "DYNLO"],
        subprocesses=["-ZJ", "-ZTT", "-TTJ", "-TTT", "-VVJ", "-VVT"],
    )
    config = GeneralConfigManipulation.remove_variation_pattern(
        config,
        ff_pattern="anti_iso_CMS_",
        ignore_process="data",
    )
    config = GeneralConfigManipulation.rename(
        config,
        processes={"data": "jetFakes"},
        subprocesses={"data": "jetFakes"},
    )
    config = GeneralConfigManipulation.add_additional_flags(config)

    # ---

    # the following operations are done in a specific order

    training_variables = [
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

    config = ConfigManipulation.convert_weights_and_cuts_to_common(config)
    config = ConfigManipulation.add_set_of_training_variables(config, training_variables)
    config = ConfigManipulation.nest_and_categorize_uncertainties(config)

    # ---

    with open("./2018_tmp_config_simplified.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)
