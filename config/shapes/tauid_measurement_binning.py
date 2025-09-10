import numpy as np
from ntuple_processor.utils import Selection
from ntuple_processor import Histogram

discriminator_variable = "m_vis"
discriminator_binning = np.arange(30, 130, 5)
discriminator_binning_enlarged = np.arange(30, 160, 5)

categories = {
    "mt": {
        category: {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": cut
        }
        for category, cut in {
            "Pt20to25": "(pt_2 >= 20) && (pt_2 < 25)",
            "Pt25to30": "(pt_2 >= 25) && (pt_2 < 30)",
            "Pt30to35": "(pt_2 >= 30) && (pt_2 < 35)",
            "Pt35to40": "(pt_2 >= 35) && (pt_2 < 40)",
            "PtGt40": "(pt_2 >= 40)",
            "DM0": "(tau_decaymode_2 == 0) && (pt_2 >= 40)",
            "DM1": "(tau_decaymode_2 == 1) && (pt_2 >= 40)",
            "DM10_11": "((tau_decaymode_2 == 10) || (tau_decaymode_2 == 11)) && (pt_2 >= 40)",
            "Inclusive": "(pt_2 >= 20)",
        }.items(),
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
    ],
    "mm": [
        (
            Selection(name="control_region", cuts=[("m_vis > 60 && m_vis < 120", "category_selection")]),
            [ Histogram("m_vis", "m_vis", [60,120])],
        )
    ]
}
