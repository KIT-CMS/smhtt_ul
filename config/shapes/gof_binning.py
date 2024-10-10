import yaml
import os
from ntuple_processor import Histogram


def load_gof_binning(era, channel, boosted_tau):
    if boosted_tau:
        binningfile = os.path.join("config", "gof_binning", f"nmssm_boosted_gof_binning_{era}_{channel}.yaml")
    else:
        binningfile = os.path.join("config", "gof_binning", f"nmssm_gof_binning_{era}_{channel}.yaml")
    with open(binningfile, "r") as f:
        binning = yaml.safe_load(f)
    # convert the binning to a ntuple_processor format

    data = {}
    data[channel] = {}
    for variable in binning.keys():
        data[channel][variable] = Histogram(variable, binning[variable]["expression"], binning[variable]["bins"])
    return data
