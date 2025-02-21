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
            "cut": "(tau_decaymode_2 == 0) && (pt_2 >= 20)",
        },
        "DM1": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 1) && (pt_2 >= 20)",
        },
        "DM10": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 10) && (pt_2 >= 20)",
        },
        "DM11": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 11) && (pt_2 >= 20)",
        },
        "DM0_PT20_40": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 0) && (pt_2 >= 20) && (pt_2 < 40)",
        },
        "DM1_PT20_40": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 1) && (pt_2 >= 20) && (pt_2 < 40)",
        },
        "DM10_PT20_40": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 10) && (pt_2 >= 20) && (pt_2 < 40)",
        },
        "DM11_PT20_40": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 11) && (pt_2 >= 20) && (pt_2 < 40)",
        },
        "DM0_PT40_200": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 0) && (pt_2 >= 40) && (pt_2 <= 200)",
        },
        "DM1_PT40_200": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 1) && (pt_2 >= 40) && (pt_2 <= 200)",
        },
        "DM10_PT40_200": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 10) && (pt_2 >= 40) && (pt_2 <= 200)",
        },
        "DM11_PT40_200": {
            "var": discriminator_variable,
            "bins": discriminator_binning,
            "expression": discriminator_variable,
            "cut": "(tau_decaymode_2 == 11) && (pt_2 >= 40) && (pt_2 <= 200)",
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
            Selection(name="control_region", cuts=[("m_vis > 70 && m_vis < 110", "category_selection")]),
            [Histogram("m_vis", "m_vis", [70,110])],
        )
    ]
}
