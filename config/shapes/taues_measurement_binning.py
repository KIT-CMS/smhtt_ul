import numpy as np
from ntuple_processor.utils import Selection
from ntuple_processor import Histogram

discriminator_variable = "m_vis"
discriminator_binning = np.arange(45, 115, 2.5)


categories = {
    "mt": {
        "DM0": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(decaymode_2 == 0)",
        },
        "DM1": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(decaymode_2 == 1)",
        },
        "DM10": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(decaymode_2 == 10)",
        },
        "DM11": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(decaymode_2 == 11)",
        },
        "Inclusive": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(pt_2 >= 20)",
        },
    }
}

categorization = {
    "mt": [
        (
            Selection(
                name=x, cuts=[(categories["mt"][x]["cut"], "category_selection")]
            ),
            [
                Histogram(
                    categories["mt"][x]["var"],
                    categories["mt"][x]["expression"],
                    categories["mt"][x]["bins"],
                )
            ],
        )
        for x in categories["mt"]
    ]
}
