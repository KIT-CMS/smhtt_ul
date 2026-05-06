import numpy as np
from ntuple_processor import Histogram
from ntuple_processor.utils import Selection

# analysis shape binning
fine_binning = np.linspace(0.0, 1.0, 51)
standard_binning = np.linspace(0.0, 1.0, 21)
custom_binning = np.array(
    [0.0, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.82, 0.84, 0.86, 0.88, 0.9, 0.92, 0.94, 0.96, 0.98, 1.0]
)
category_template = {
    "HH2B2Tau": {
        "index": 0,
        "binning": custom_binning,
    },
    "DY": {
        "index": 1,
        "binning": standard_binning,
    },
    "ST": {
        "index": 2,
        "binning": standard_binning,
    },
    "TT": {
        "index": 3,
        "binning": standard_binning,
    },
    "VV": {
        "index": 4,
        "binning": standard_binning,
    },
    "jetFakesMC": {
        "index": 5,
        "binning": standard_binning,
    },
    "Other": {
        "index": 6,
        "binning": standard_binning,
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
