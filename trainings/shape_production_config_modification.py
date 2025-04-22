import argparse
import logging
import re
import sys
from copy import deepcopy
from functools import partial
from typing import List, Union

import yaml

sys.path.append(".")

from config.logging_setup_configs import setup_logging
from common_helper import TRAINING_VARIABLES, Iterate, Keys, PipeDict, find_variable_expansions


def parse_args():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--config-input",
        default=[],
        nargs="+",
        type=str,
        help="Path to the input config file(s) to be modified",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./mt__tmp_config__modified.yaml",
        help="Path to the output config file",
    )
    return parser.parse_args()


class MissingCutOrWeight(Exception):
    pass


class _GeneralConfigManipulation(object):
    @staticmethod
    def set_common(config: dict) -> dict:
        config = deepcopy(config)
        for channel, era, process, *_ in Iterate.subprocesses(deepcopy(config)):
            config[channel][era][process].setdefault(Keys.COMMON, {})
            logger.info(f"Setting {Keys.COMMON} key for {channel} {era} {process}")
        return config

    @staticmethod
    def remove_variation_pattern(
        config: dict,
        ff_pattern: str = "anti_iso_CMS_",
        ignore_process: str = "data",
    ) -> dict:
        config = deepcopy(config)
        for channel, channel_dict in config.items():
            if channel not in Keys.CHANNELS or not isinstance(channel_dict, dict):
                continue
            for era_dict in channel_dict.values():
                if not isinstance(era_dict, dict):
                    continue
                for process, process_dict in era_dict.items():
                    if process == ignore_process or not isinstance(process_dict, dict):
                        continue
                    for subprocess, subprocess_dict in process_dict.items():
                        if not isinstance(subprocess_dict, dict):
                            continue
                        for key in [key for key in subprocess_dict if ff_pattern in key]:
                            logger.info(f"Removing {key} from {subprocess}")
                            del subprocess_dict[key]
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
            if _GeneralConfigManipulation._should_remove(key, criteria.get(current_level, [])):
                logger.info(f"Removing {key} from {current_level}")
                del x[key]
            else:
                if isinstance(x[key], dict):
                    _GeneralConfigManipulation._recursive_remove(x[key], level + 1, level_keys, criteria)

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
        _GeneralConfigManipulation._recursive_remove(config, 0, levels, removal)
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

        logger.info(
            f"""
            Renaming processes: {processes}
            Renaming subprocesses: {subprocesses}
            Renaming shifts: {shifts}
            """
        )

        for channel, channel_dict in config.items():
            if channel not in Keys.CHANNELS or not isinstance(channel_dict, dict):
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
                    _GeneralConfigManipulation.recursive_update(x[k], v)
                else:
                    x[k] = v
            else:
                x[k] = v
        return x

    @staticmethod
    def recursive_update_from_file(
        config: dict,
        path: Union[str, List[str]],
    ) -> dict:
        path = [path] if isinstance(path, str) else path
        config = deepcopy(config)
        for p in path:
            with open(p, "r") as f:
                config = _GeneralConfigManipulation.recursive_update(config, yaml.safe_load(f))
            logger.info(f"Updated config from {p}")
        return config

    @staticmethod
    def add_era_and_process_name_flags(config):
        config = deepcopy(config)

        process_subprocesses = set([(p, subp) for _, _, p, subp, *_ in Iterate.subprocesses(config)])

        for channel, era, process, subprocess, *_ in Iterate.subprocesses(config):
            for _era in Keys.ERAS:
                logger.info(f"Adding is_{_era} flag for {channel} {era} {process}")
                config[channel][era][process][Keys.COMMON][f"is_{_era}"] = f"(float){int(_era == era)}."

        for channel, era, process, subprocess, *_ in Iterate.subprocesses(config):
            for _process, _subprocess in process_subprocesses:
                flag = int(_process == process and _subprocess == subprocess)
                key = f"is_{_process}__{_subprocess.replace('-', '_')}"
                config[channel][era][process][Keys.COMMON][key] = f"(float){flag}."
                logger.info(f"Adding {key} flag for {channel} {era} {process}")

        return config


class _SpecificConfigManipulation(object):
    @staticmethod
    def convert_weights_and_cuts_to_common(config: dict) -> dict:
        config = deepcopy(config)

        for channel, era, process, _, subprocess_dict in Iterate.subprocesses(config):
            config[channel][era][process].get(Keys.COMMON, {})
            config[channel][era][process][Keys.COMMON][Keys.CUT] = {}
            config[channel][era][process][Keys.COMMON][Keys.WEIGHT] = {}
            common_cuts_rev, common_weights_rev = {}, {}

            for shift, shift_dict in subprocess_dict.items():
                cut, weight = shift_dict.get(Keys.CUT), shift_dict.get(Keys.WEIGHT)
                if cut is None or weight is None:
                    raise MissingCutOrWeight(f"Missing cut or weight for {shift} in {subprocess_dict}, aborting.")
                if cut in common_cuts_rev:
                    shift_dict[Keys.CUT] = common_cuts_rev[cut]
                else:
                    new_cut = f'__{Keys.COMMON}__{Keys.CUT}__{len(common_cuts_rev)}__'
                    config[channel][era][process][Keys.COMMON][Keys.CUT][new_cut] = cut
                    common_cuts_rev[cut] = new_cut
                    shift_dict[Keys.CUT] = new_cut

                if weight in common_weights_rev:
                    shift_dict[Keys.WEIGHT] = common_weights_rev[weight]
                else:
                    new_weight = f'__{Keys.COMMON}__{Keys.WEIGHT}__{len(common_weights_rev)}__'
                    config[channel][era][process][Keys.COMMON][Keys.WEIGHT][new_weight] = weight
                    common_weights_rev[weight] = new_weight
                    shift_dict[Keys.WEIGHT] = new_weight
            logger.info(f"Added common cuts and weights for {channel} {era} {process}")
        return config

    @staticmethod
    def add_set_of_training_variables(
        config: dict,
        training_variables: list[str],
    ) -> dict:
        config = deepcopy(config)

        default_variables = {k: k for k in training_variables}

        for channel, era, process, subprocess, subprocess_dict in Iterate.subprocesses(deepcopy(config)):
            if isinstance(subprocess_dict, dict):
                config[channel][era][process].setdefault(Keys.COMMON, {})
                config[channel][era][process].setdefault(Keys.VARIABLES, deepcopy(default_variables))
                config[channel][era][process].setdefault(Keys.NOMINAL_VARIABLES, deepcopy(default_variables))

            for shift_name, shift_dict in subprocess_dict.items():
                if not isinstance(shift_dict, dict):
                    continue

                if (cut := shift_dict.get(Keys.CUT)) is None or (weight := shift_dict.get(Keys.WEIGHT)) is None:
                    raise MissingCutOrWeight(f"Missing cut or weight for {shift_dict}, aborting.")
                if f"__{Keys.COMMON}__{Keys.CUT}__" in str(cut):
                    if (cut := config[channel][era][process][Keys.COMMON][Keys.CUT].get(cut)) is None:
                        raise MissingCutOrWeight(f"Missing common cut for {shift_dict}, aborting.")
                if f"__{Keys.COMMON}__{Keys.WEIGHT}__" in str(weight):
                    if (weight := config[channel][era][process][Keys.COMMON][Keys.WEIGHT].get(weight)) is None:
                        raise MissingCutOrWeight(f"Missing common weight for {shift_dict}, aborting.")

                combined, variables_dict = f"{cut} && {weight}", {}
                for variable in training_variables:
                    if len((matches := list(set(find_variable_expansions(combined, variable))))) > 1:
                        raise AssertionError(f"{variable} appears multiple times in under different names ({matches}) aborting.")
                    variables_dict[variable] = matches[0] if matches else variable

                if variables_dict == default_variables:
                    config[channel][era][process][subprocess][shift_name][Keys.VARIABLES] = f"__{Keys.NOMINAL_VARIABLES}__"
                else:
                    config[channel][era][process][subprocess][shift_name][Keys.VARIABLES] = variables_dict
                    config[channel][era][process][Keys.VARIABLES].update({v: v for v in variables_dict.values()})
            logger.info(f"Added training variables for {channel} {era} {process}")
        return config

    @staticmethod
    def nest_and_categorize_uncertainties(config: dict) -> dict:
        config = deepcopy(config)
        pattern = re.compile(r"^(.*?)(Up|Down)(?:_.*)?$")

        for *info, subprocess_dict in Iterate.subprocesses(config):
            subprocess_dict.setdefault(Keys.UNCERTAINTIES, {})
            uncertainty_group, shifts_to_remove = {}, []
            for shift in list(subprocess_dict.keys()):
                if not (m := pattern.match(shift)):
                    continue
                base_name, direction = m.groups()
                shifts_to_remove.append(shift)
                group = uncertainty_group.setdefault(base_name, {})
                shift_data = deepcopy(subprocess_dict[shift])
                group[direction.lower()] = shift_data

            for key in shifts_to_remove:
                del subprocess_dict[key]

            if uncertainty_group:
                for base_name, group in uncertainty_group.items():
                    if group[Keys.UP].get(Keys.VARIABLES) == group[Keys.DOWN].get(Keys.VARIABLES):
                        group[Keys.VARIABLES] = group[Keys.UP].get(Keys.VARIABLES)
                        del group[Keys.UP][Keys.VARIABLES]
                        del group[Keys.DOWN][Keys.VARIABLES]
                        group[Keys.UNCERTAINTY_TYPE] = Keys.WEIGHT_LIKE
                    else:
                        group[Keys.UNCERTAINTY_TYPE] = Keys.SHIFT_LIKE
                sorted_uncertainty_group = {k: v for k, v in sorted(uncertainty_group.items(), key=lambda item: item[0])}
                subprocess_dict[Keys.UNCERTAINTIES] = sorted_uncertainty_group
            logger.info(f"Categorized uncertainties for {' '.join(info)}")
        return config


class Modify(object):
    general = _GeneralConfigManipulation
    specific = _SpecificConfigManipulation


if __name__ == "__main__":

    logger = setup_logging(logger=logging.getLogger(__name__))
    args = parse_args()

    ignore_for_now = {  # until fixed, TODO:
        "lhe_scale_weight__LHEScaleMuFWeig",
        "lhe_scale_weight__LHEScaleMuRWeig",
    }
    Iterate.common_dict = partial(Iterate.common_dict, ignore_weight_and_cuts=ignore_for_now)
    logger.warning(f"Ignoring cuts and weights of {ignore_for_now}, until fixed!")

    config = (
        PipeDict()
        .pipe(Modify.general.recursive_update_from_file, path=args.config_input)
        .pipe(Modify.general.set_common)
        .pipe(
            Modify.general.remove_from_config,
            processes=["W", "DYNLO"],
            subprocesses=["-ZJ", "-ZTT", "-TTJ", "-TTT", "-VVJ", "-VVT"],
        )
        .pipe(Modify.general.remove_variation_pattern, ff_pattern="anti_iso_CMS_", ignore_process="data")
        .pipe(Modify.general.rename, processes={"data": "jetFakes"}, subprocesses={"data": "jetFakes"})
        .pipe(Modify.general.add_era_and_process_name_flags)
        .pipe(Modify.specific.convert_weights_and_cuts_to_common)
        .pipe(Modify.specific.add_set_of_training_variables, training_variables=TRAINING_VARIABLES)
        .pipe(Modify.specific.nest_and_categorize_uncertainties)
    )

    with open(args.output, "w") as f:
        yaml.dump(dict(config), f, default_flow_style=False)
        logger.info(f"Modified config saved to {args.output}")
