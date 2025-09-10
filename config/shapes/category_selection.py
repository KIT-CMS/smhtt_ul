import numpy as np
from ntuple_processor import Histogram
from ntuple_processor.utils import Selection


fine_binning = np.linspace(0.0, 1.0, 21)
category_template = {
    "HH2B2Tau": {
        "index": 0,
        "binning": fine_binning,
    },
    "DY": {
        "index": 1,
        "binning": fine_binning,
    },
    "ST": {
        "index": 2,
        "binning": fine_binning,
    },
    "TT": {
        "index": 3,
        "binning": fine_binning,
    },
    "VV": {
        "index": 4,
        "binning": fine_binning,
    },
    "Other": {
        "index": 5,
        "binning": fine_binning,
    },
}

category_mapping = {
    "et": category_template,
    "mt": category_template,
    "tt": category_template,
}

def get_categorization():
    categorization = {}
    for channel in ["et", "mt", "tt"]:
        categorization[channel] = []
        for category in category_mapping[channel].keys():
            selection = (
                Selection(
                    name=category,
                    cuts=[
                        (
                            f"predicted_class == {category_mapping[channel][category]['index']}",
                            "category selection",
                        )
                    ],
                ),
                [
                    Histogram(
                        f"NN_score",
                        f"predicted_max_value",
                        category_mapping[channel][category]["binning"],
                    )
                ],
            )
            categorization[channel].append(selection)
    return categorization
