import numpy as np
from ntuple_processor import Histogram
from ntuple_processor.utils import Selection

IS_STAGE0 = True

fine_binning = np.linspace(0.0, 1.0, 11)
category_mapping = {
    "mt": {
        "vbf_bin201to210": {"index": 0, "binning": fine_binning},
        "ggh_bin101to104": {"index": 1, "binning": fine_binning},
        "ggh_bin105to106": {"index": 2, "binning": fine_binning},
        "ggh_bin107to109": {"index": 3, "binning": fine_binning},
        "ggh_bin110to116": {"index": 4, "binning": fine_binning},
        "embedding": {"index": 5, "binning": fine_binning},
        "jetFakes": {"index": 6, "binning": fine_binning},
        "ttbar": {"index": 7, "binning": fine_binning},
        "dyjets": {"index": 8, "binning": fine_binning},
        "diboson": {"index": 9, "binning": fine_binning},
    }
} if not IS_STAGE0 else {
    "mt": {
        "vbf_bin201to210": {"index": 0, "binning": fine_binning},
        "ggh_bin101to116": {"index": 1, "binning": fine_binning},
        "embedding": {"index": 2, "binning": fine_binning},
        "jetFakes": {"index": 3, "binning": fine_binning},
        "ttbar": {"index": 4, "binning": fine_binning},
        "dyjets": {"index": 5, "binning": fine_binning},
        "diboson": {"index": 6, "binning": fine_binning},
    }
}
categorization = {}
for channel in ["mt"]:
    categorization[channel] = []
    for category in category_mapping[channel].keys():
        selection = (
            Selection(
                name=category,
                cuts=[
                    (
                        f"nn_predicted_class == {category_mapping[channel][category]['index']}",
                        "category selection",
                    )
                ],
            ),
            [
                Histogram(
                    f"{channel}_score",
                    "nn_predicted_max_value",
                    category_mapping[channel][category]["binning"],
                )
            ],
        )
        categorization[channel].append(selection)
    categorization[channel].append(selection)
