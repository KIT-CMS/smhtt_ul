import numpy as np
from ntuple_processor.utils import Selection
from ntuple_processor import Histogram

discriminator_variable = "m_vis"
discriminator_binning = np.arange(30, 130, 5)
discriminator_binning_enlarged = np.arange(30, 160, 5)


categories = {
    "mt": {
        "Pt20to25": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(pt_2 >= 20) && (pt_2 < 25)",
        },
        "Pt25to30": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(pt_2 >= 25) && (pt_2 < 30)",
        },
        "Pt30to35": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(pt_2 >= 30) && (pt_2 < 35)",
        },
        "Pt35to40": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(pt_2 >= 35) && (pt_2 < 40)",
        },
        "PtGt40": {
            "var": discriminator_variable,
            "bins": discriminator_binning_enlarged,
            "expression": discriminator_variable,
            "cut": "(pt_2 >= 40)",
        },
        "DM0": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(decaymode_2 == 0) && (pt_2 >= 40)",
        },
        "DM1": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(decaymode_2 == 1) && (pt_2 >= 40)",
        },
        "DM10_11": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "((decaymode_2 == 10) || (decaymode_2 == 11)) && (pt_2 >= 40)",
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
    ],
    "mm": [
        (
            Selection(name="control_region", cuts=[("m_vis > 60 && m_vis < 120", "category_selection")]),
            [ Histogram("m_vis", "m_vis", [60,120])],
        )
    ]
}
