
import argparse
import logging
from functools import partial
import yaml

from src.config_modifications import ConfigModification
from src.helper import Iterate, PipeDict, TRAINING_VARIABLES

try:
    from config.logging_setup_configs import setup_logging
except ModuleNotFoundError:
    import sys
    sys.path.extend([".", ".."])
    from config.logging_setup_configs import setup_logging


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


if __name__ == "__main__":

    logger = setup_logging(logger=logging.getLogger(__name__))
    args = parse_args()

    ignore_for_now = {  # until fixed, TODO:
        "lhe_scale_weight__LHEScaleMuFWeig",
        "lhe_scale_weight__LHEScaleMuRWeig",
    }
    Iterate.common_dict = partial(Iterate.common_dict, ignore_weight_and_cuts=ignore_for_now)
    logger.warning(f"Ignoring cuts and weights of {ignore_for_now}, until fixed!")
    training_variables = TRAINING_VARIABLES

    config = (
        PipeDict()
        .pipe(ConfigModification.general.recursive_update_from_file, path=args.config_input)
        .pipe(ConfigModification.general.set_common)
        .pipe(
            ConfigModification.general.remove_from_config,
            processes=["W", "DYNLO"],
            subprocesses=["-ZJ", "-ZTT", "-TTJ", "-TTT", "-VVJ", "-VVT"],
        )
        .pipe(ConfigModification.general.remove_variation_pattern, ff_pattern="anti_iso_CMS_", ignore_process="data")
        .pipe(ConfigModification.general.rename, processes={"data": "jetFakes"}, subprocesses={"data": "jetFakes"})
        .pipe(ConfigModification.general.add_era_and_process_name_flags)
        .pipe(ConfigModification.specific.convert_weights_and_cuts_to_common)
        .pipe(ConfigModification.specific.add_set_of_training_variables, training_variables=training_variables)
        .pipe(ConfigModification.specific.nest_and_categorize_uncertainties)
    )

    with open(args.output, "w") as f:
        yaml.dump(dict(config), f, default_flow_style=False)
        logger.info(f"Modified config saved to {args.output}")
