from ntuple_processor import Unit


def add_process(analysis_unit, name, dataset, selections, categorization, channel):

    if not isinstance(selections, list):
        selections = [selections]
    unitlist = []
    for category_selection, actions in categorization[channel]:
        full_selection = [category_selection] + selections
        unitlist.append(Unit(dataset, full_selection, actions))

    analysis_unit[name] = unitlist


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
