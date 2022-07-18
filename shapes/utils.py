from ntuple_processor import Unit


def add_process(analysis_unit, name, dataset, selections, categorization, channel):

    if not isinstance(selections, list):
        selections = [selections]
    unitlist = []
    for category_selection, actions in categorization[channel]:
        full_selection = [category_selection] + selections
        unitlist.append(Unit(dataset, full_selection, actions))

    analysis_unit[name] = unitlist
