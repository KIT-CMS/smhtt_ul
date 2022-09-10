import numpy as np
from ntuple_processor import Histogram
from ntuple_processor.utils import Selection

category_mapping = {
    "mt": {
    "ff": 0,
    "zll": 1,
    "ztt": 2,
    "ggh": 3,
    "qqh": 4,
    "misc": 5,
    "tt": 6,
    }
}
# updated order to be used starting with the next training
# category_mapping = {
#     "mt": {
#         "qqh": 0,
#         "ggh": 1,
#         "ztt": 2,
#         "ff": 3,
#         "misc": 4,
#         "zll": 5,
#         "tt": 6,
#     }
# }

categorization = {}
for channel in ["mt"]:
    categorization[channel] = []
    for category in category_mapping[channel].keys():
        selection = (Selection(name=category,
        cuts=[
            f"{channel}_max_index == {category_mapping[channel][category]}", "category selection"
        ]),
        [Histogram(f"{channel}_max_score", f"{channel}_max_score", np.linspace(0.0, 1.0, 10))])
        categorization[channel].append(selection)