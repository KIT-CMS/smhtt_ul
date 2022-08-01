from ntuple_processor import dataset_from_crownoutput, Unit
import re


# def add_process(analysis_unit, name, dataset, selections, categorization, channel):
#     """
#     Add a process to the analysis unit.
#     """
#     if not isinstance(selections, list):
#         selections = [selections]
#     unitlist = []
#     for category_selection, actions in categorization[channel]:
#         full_selection = selections + [category_selection]
#         unitlist.append(Unit(dataset, full_selection, actions))

#     analysis_unit[name] = unitlist


def add_process(
    analysis_unit, name, dataset, selections, categorization, channel, variations=None
):
    """
    Add a process to the analysis unit.
    """
    if not isinstance(selections, list):
        selections = [selections]
    unitlist = []
    if variations is not None:
        for variation in variations:
            for category_selection, actions in categorization[channel]:
                full_selection = selections + [category_selection]
                unitlist.append(Unit(dataset, full_selection, actions, variation))
    else:
        for category_selection, actions in categorization[channel]:
            full_selection = selections + [category_selection]
            unitlist.append(Unit(dataset, full_selection, actions))

    analysis_unit[name] = unitlist


def add_control_process(
    analysis_unit, name, dataset, selections, channel, binning, variables
):
    """Function used to add control plots of various variables to the analysis unit.

    Args:
        analysis_unit (dict): the dict used to book the histograms
        name (str): name of the process
        dataset (any): name of the dataset
        selections (list): list of selections to be applied
        channel (str): the channel to be used
        binning (dict): a dict containing the binning of the histogram
        variables (set): a set of variables to be used
    """

    if not isinstance(selections, list):
        selections = [selections]
    control_binning = []
    for variable in variables:
        control_binning.append(binning[channel][variable])
    analysis_unit[name] = [(Unit(dataset, selections, control_binning))]


def book_histograms(manager, processes, datasets, variations=None, enable_check=False):
    if not isinstance(processes, set):
        processes = set(processes)
    unitlist = [unit for process in processes for unit in datasets[process]]
    if variations is not None:
        variationlist = []
        for variation in variations:
            if isinstance(variation, list):
                variationlist.extend(variation)
            else:
                variationlist.append(variation)
    else:
        variationlist = None
    manager.book(
        unitlist,
        variationlist,
        enable_check=enable_check,
    )


def filter_friends(dataset, friend):
    # Add fake factor friends only for backgrounds.
    if re.match("(gg|qq|susybb|susygg|tt|w|z|v)h", dataset.lower()):
        if "FakeFactors" in friend or "EMQCDWeights" in friend:
            return False
    # Add NLOReweighting friends only for ggh signals.
    if "NLOReweighting" in friend:
        if re.match("(susygg)h", dataset.lower()) and not "powheg" in dataset.lower():
            pass
        else:
            return False
    elif re.match("data", dataset.lower()):
        if "xsec" in friend:
            return False
    elif re.match("emb", dataset.lower()):
        if "xsec" in friend:
            return False
    return True


def get_nominal_datasets(era, channel, friend_directories, files, directory):
    datasets = dict()

    for key, names in files[era][channel].items():
        datasets[key] = dataset_from_crownoutput(
            key,
            names,
            era,
            channel,
            channel + "_nominal",
            directory,
            [fdir for fdir in friend_directories[channel] if filter_friends(key, fdir)],
        )
    return datasets
