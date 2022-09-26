import argparse
from copy import deepcopy
from dataclasses import dataclass
import logging
import os
import yaml
from ntuple_processor import Histogram
from ntuple_processor.utils import Selection

from shapes.utils import get_nominal_datasets, add_process

from config.shapes.file_names import files

from shapes.produce_shapes import setup_logging, get_analysis_units

# for fake factors
from config.shapes.channel_selection import channel_selection
from config.shapes.process_selection import FF_training_process_selection


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for the legacy MSSM analysis."
    )
    parser.add_argument(
        "--eras",
        required=True,
        type=lambda eralist: [era for era in eralist.split(",")],
        help="Experiment eras.",
    )
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist: [channel for channel in channellist.split(",")],
        help="Channels to be considered, seperated by a comma without space",
    )
    parser.add_argument(
        "--directory", required=True, type=str, help="Directory with Artus outputs."
    )
    parser.add_argument(
        "--et-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for et.",
    )
    parser.add_argument(
        "--mt-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for mt.",
    )
    parser.add_argument(
        "--tt-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for tt.",
    )
    parser.add_argument(
        "--em-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for em.",
    )
    parser.add_argument(
        "--mm-friend-directory",
        type=str,
        default=[],
        nargs="+",
        help="Directories arranged as Artus output and containing a friend tree for mm.",
    )
    parser.add_argument(
        "--process-selection",
        default=None,
        type=lambda proclist: set([process.lower() for process in proclist.split(",")]),
        help="Subset of processes to be processed.",
    )
    parser.add_argument(
        "--special-analysis",
        default=None,
        type=str,
        help="Special analysis to be considered.",
    )
    parser.add_argument(
        "--no-embedding",
        action="store_true",
        help="Do not include embedding in the training.",
    )
    parser.add_argument(
        "--no-fake-factors",
        action="store_true",
        help="Do not include fake factors in the training.",
    )
    parser.add_argument(
        "--trainings-config",
        required=True,
        type=str,
        help="Path to the trainings config file to use.",
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        default="training_files",
        help="Path where the training config files should be stored.",
    )
    return parser.parse_args()


logger = logging.getLogger("")


def setup_default_class_ordering(inputclasses):
    final_order = []
    # put signal first
    default_order = ["ggh", "qqh", "ztt", "ff", "zll", "tt", "misc"]
    for default in default_order:
        for cls in inputclasses:
            if cls == default:
                final_order.append(cls)
    return final_order


def create_training_configs(
    outputfolder,
    trainings,
    process_config_path,
    base_config,
    no_embedding,
    no_fake_factors,
):

    # load the base config
    with open(base_config, "r") as f:
        base_config = yaml.safe_load(f)
    config = {}
    for training in trainings["trainings"]:
        seleted_training = trainings["trainings"][training]
        config[training] = deepcopy(base_config)
        config[training]["variables"] = seleted_training["variables"]
        config[training]["identifier"] = {
            "era": seleted_training["identifier"]["era"],
            "channel": seleted_training["identifier"]["channel"],
        }
        config[training]["mapping"] = create_process_mapping(
            seleted_training["identifier"]["channel"],
            seleted_training["identifier"]["era"],
            no_embedding,
            no_fake_factors,
        )
        config[training]["processes"] = list(config[training]["mapping"].keys())
        config[training]["classes"] = setup_default_class_ordering(
            list(set(config[training]["mapping"].values()))
        )
        config[training]["processes_config"] = process_config_path

    # also add all combined trainings here
    for combined_training in trainings["combined_trainings"]:
        config[combined_training] = {}
        config[combined_training]["trainings"] = trainings["combined_trainings"][
            combined_training
        ]["trainings"]
        config[combined_training]["condor_parameters"] = {
            "condor_gpu": 1,
            "condor_memory": "16000",
        }
        config[combined_training]["composite"] = True

    # write the configs to files
    filename = f"{outputfolder}/trainings.yaml"
    with open(filename, "w") as f:
        print(config)
        yaml.dump(config, f)
    return filename


def create_process_mapping(channel, era, no_embedding, no_fake_factors):
    default_mapping = {
        # 'ewkz': 'misc',
        "ttl": "tt",
        "vvl": "misc",
        "zl": "zll",
        "ggh": "ggh",
        "qqh": "qqh",
    }
    if no_embedding:
        default_mapping["ztt"] = "ztt"
        default_mapping["ttt"] = "ztt"
        default_mapping["vvt"] = "ztt"
    else:
        default_mapping["emb"] = "ztt"
    if no_fake_factors:
        default_mapping["wj"] = "ff"
        default_mapping["zj"] = "ff"
        default_mapping["ttj"] = "ff"
        default_mapping["vvj"] = "ff"
    else:
        default_mapping["jetfakes"] = "ff"
    # now write the mapping to a file
    return default_mapping


def set_training_categorization():
    # this is just a dummy selection we need to trick the framework, we do not use it !
    inclusive = [
        (
            Selection(name="Inclusive", cuts=[("", "category_selection")]),
            [Histogram("m_vis", "m_vis", [i for i in range(0, 255, 5)])],
        )
    ]
    training_categorization = {
        "et": inclusive,
        "mt": inclusive,
        "tt": inclusive,
        "em": inclusive,
    }
    return training_categorization


def add_fake_factors(era, channel, datasets, categorization, special_analysis):
    selections = []
    selections.append(deepcopy(channel_selection(channel, era, special_analysis)))
    # now we have to remove the 'tau_iso' cut from the channel selection
    selections[0].cuts = [cut for cut in selections[0].cuts if cut.name != "tau_iso"]
    selections.append(FF_training_process_selection(channel, era))
    analysis_unit = {}
    if channel != "em":
        add_process(
            analysis_unit,
            name="jetfakes",
            dataset=datasets["data"],
            selections=selections,
            categorization=categorization,
            channel=channel,
        )
    return analysis_unit["jetfakes"]


def setup_trainings(eras, channels, analysistype):
    trainings = {}
    trainings["channels"] = channels
    trainings["analysis"] = analysistype
    trainings["eras"] = eras
    trainings["trainings"] = {}
    trainings["combined_trainings"] = {}
    if analysistype == "sm":
        default_vars = [
            "pt_1",
            "pt_2",
            "m_vis",
            "njets",
            "nbtag",
            "jpt_1",
            "jpt_2",
            "jeta_1",
            "jeta_2",
            "m_fastmtt",
            "pt_vis",
            "mjj",
            "deltaR_ditaupair",
            "pt_dijet",

        ]
        logger.info(f"Using default variables {default_vars}")
        # here we have one training per era and channel
        for era in eras:
            for channel in channels:
                trainings["trainings"][f"sm_{era}_{channel}"] = {
                    "processes": [],
                    "classes": [],
                    "identifier": {
                        "channel": channel,
                        "era": era,
                    },
                    "variables": default_vars,
                    "single_training": True,
                }
        # if we have multiple channels, also define a combined training for testing purposes
        if len(channels) > 1:
            for era in eras:
                trainings["combined_trainings"][f"sm_{era}_{'_'.join(channels)}"] = {
                    "trainings": [f"sm_{era}_{channel}" for channel in channels],
                    "single_training": False,
                }
    else:
        raise NotImplementedError(f"Analysis type {analysistype} not implemented.")
    return trainings


def create_process_yaml(
    era, channel, name, unit, outputfolder, categorization, basedir, frienddirs
):
    cut_to_be_removed = categorization[channel][0][0].cuts[0].expression
    print(cut_to_be_removed)
    # first get the information from the unit
    logger.info("Unit: {}".format(unit[0]))
    filename = "{}_{}_{}.yaml".format(era, channel, name)
    # first get all selections
    cuts = ""
    weights = ""
    files = []
    friend_paths = []
    # get the friends, this we only have to do for the first ntuple
    if unit[0].dataset.ntuples[0].friends is not None:
        for friend_dir in frienddirs:
            for friendfile in [x.path for x in unit[0].dataset.ntuples[0].friends]:
                if friend_dir in friendfile and friend_dir not in friend_paths:
                    friend_paths.append(f"{friend_dir}/")
    files = [ntuple.path.replace(basedir, "") for ntuple in unit[0].dataset.ntuples]
    for selection in unit[0].selections:
        logger.debug("adding cuts: {}".format(selection.cuts))
        logger.debug("adding weights: {}".format(selection.weights))
        cutstring = " && ".join(
            [
                "({})".format(cut.expression)
                for cut in selection.cuts
                if cut.expression != ""
            ]
        )
        weightstring = " * ".join(
            [
                "({})".format(weight.expression)
                for weight in selection.weights
                if weight.expression != ""
            ]
        )
        if cutstring != "":
            cuts += cutstring + " && "
        if weightstring != "":
            weights += weightstring + " * "
    if len(weights) > 0:
        weights = weights[:-3]
    if len(cuts) > 0:
        cuts = cuts[:-4]
    data = {
        "process": name,
        "weight_string": f"({weights})",
        "files": files,
        "cut_string": f"({cuts})",
        "friend_paths": friend_paths,
        "tree_path": "ntuple",
        "base_path": basedir,
        "training_weight_branch": "weight",
        "condor_parameter": {
            "condor_gpu": 1,
            "condor_memory": "16000",
        },
    }
    with open(os.path.join(outputfolder, filename), "w") as f:
        yaml.dump(data, f)


def create_analysis_configs(
    analysis_name, outputfolder, trainings, trainings_config_path, processes_config_path
):
    configname = f"{analysis_name}.yaml"
    data = {}
    for training in trainings["trainings"]:
        subdata = {}
        subdata["training"] = training
        subdata["trainings_config"] = trainings_config_path

        data[training] = subdata
    with open(os.path.join(outputfolder, configname), "w") as f:
        yaml.dump(data, f)


def main(args):
    # Parse given arguments
    # TODO add comments to the config files to make dependencies clear
    friend_directories = {
        "et": args.et_friend_directory,
        "mt": args.mt_friend_directory,
        "tt": args.tt_friend_directory,
        "em": args.em_friend_directory,
        "mm": args.mm_friend_directory,
    }
    outputfolder = args.output_folder
    if not os.path.exists(os.path.join(outputfolder, "processes")):
        os.makedirs(os.path.join(outputfolder, "processes"))
    channels = args.channels
    eras = args.eras
    special_analysis = args.special_analysis
    categorization = set_training_categorization()
    analysis_name = "sm"
    process_config_path = f"{outputfolder}/processes"
    trainings = setup_trainings(eras, channels, analysis_name)
    # first create the processes configs for all processes relevant
    for era in eras:
        nominals = {}
        nominals[era] = {}
        nominals[era]["datasets"] = {}
        nominals[era]["units"] = {}
        logger.info("Processing era {}".format(era))
        # Step 1: create units and book actions
        for channel in channels:
            logger.info("Processing channel {}".format(channel))
            nominals[era]["datasets"][channel] = get_nominal_datasets(
                era, channel, friend_directories, files, args.directory
            )
            logger.info(
                "Found {} datasets".format(len(nominals[era]["datasets"][channel]))
            )
            logger.info("Creating analysis units")
            nominals[era]["units"][channel] = get_analysis_units(
                channel,
                era,
                nominals[era]["datasets"][channel],
                categorization,
                special_analysis,
            )
            # add fake factors
            nominals[era]["units"][channel]["jetfakes"] = add_fake_factors(
                era,
                channel,
                nominals[era]["datasets"][channel],
                categorization,
                special_analysis,
            )
            logger.info(
                "Found {} analysis units".format(len(nominals[era]["units"][channel]))
            )
            logger.info(
                "jetfakes: {}".format(nominals[era]["units"][channel]["jetfakes"])
            )
            logger.info(nominals[era]["units"][channel]["jetfakes"][0])
            logger.info(nominals[era]["units"][channel]["jetfakes"][0].dataset)
            # Step 2: create process yamls
            for unit in nominals[era]["units"][channel]:
                logger.info(
                    "Creating process yaml for {} {} {}".format(era, channel, unit)
                )
                create_process_yaml(
                    era,
                    channel,
                    unit,
                    nominals[era]["units"][channel][unit],
                    process_config_path,
                    categorization,
                    args.directory,
                    friend_directories[channel],
                )
    # Step 3: create training configs
    logger.info("Creating training config")
    trainings_config_path = create_training_configs(
        outputfolder,
        trainings,
        process_config_path,
        args.trainings_config,
        args.no_embedding,
        args.no_fake_factors,
    )
    # Step 4: create analysis configs
    # in the analysis configs, multiple trainings can be combined, e.g. mt channel 2016-2018
    logger.info("Creating analysis config")
    create_analysis_configs(
        analysis_name,
        outputfolder,
        trainings,
        trainings_config_path,
        process_config_path,
    )


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("create_ml_training.txt", logging.INFO)
    main(args)
