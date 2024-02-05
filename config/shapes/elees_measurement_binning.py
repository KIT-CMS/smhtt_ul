import numpy as np
from ntuple_processor.utils import Selection
from ntuple_processor import Histogram

discriminator_variable = "m_vis"
discriminator_binning = np.arange(60, 120, 1.0)


categories = {
    "ee": {
        "barrel": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(abs(eta_1) <= 1.479)",
        },
        "endcap": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(abs(eta_1) > 1.479)",
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
    "ee": [
        (
            Selection(
                name=x, cuts=[(categories["ee"][x]["cut"], "category_selection")]
            ),
            [
                Histogram(
                    categories["ee"][x]["var"],
                    categories["ee"][x]["expression"],
                    categories["ee"][x]["bins"],
                )
            ],
        )
        for x in categories["ee"]
    ]
}
