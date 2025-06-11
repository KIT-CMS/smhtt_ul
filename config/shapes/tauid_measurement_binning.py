import logging 
import numpy as np
from ntuple_processor.utils import Selection
from ntuple_processor import Histogram
from config.logging_setup_configs import setup_logging
import yaml

logger = setup_logging(logger=logging.getLogger(__name__))


def load_tauid_categorization(era: str, channel: str, TAG: str, dm_bin: str) -> dict:
    """
    Load tau ID categorization based on the era and channel.
    """
   
   # Import special binning yaml here:
    special_flag = True
    special_binning = {}
    try:
        with open(f"config/gof_binning/binning_{era}_{channel}_{TAG}.yaml", "r") as stream:
            try:
                special_binning = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
    except:
        logger.error(f"Could not load special binning for era {era}, channel {channel}, tag {TAG}. Using default binning.")
        special_flag = False
   
    discriminator_variable = "m_vis"
    discriminator_binning = np.arange(30, 130, 12) # -> [ 30  42  54  66  78  90 102 114 126]
    # discriminator_binning = np.array([30, 50, 80, 100, 130])
    # discriminator_binning = special_binning["m_vis"]["bins"]
    discriminator_binning_enlarged = np.arange(30, 160, 5)
    logger.info(f"Using discriminator variable {discriminator_variable} with binning {discriminator_binning} as default. Special binning is used for specific categories:{special_flag}")
    
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
            "DM1011": {
                "var": discriminator_variable,
                "bins": discriminator_binning,
                "expression": discriminator_variable,
                "cut": "(tau_decaymode_2 == 10 || tau_decaymode_2 == 11) && (pt_2 >= 20)",
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
            "DM1011_PT20_40": {
                "var": discriminator_variable,
                "bins": discriminator_binning,
                "expression": discriminator_variable,
                "cut": "(tau_decaymode_2 == 10 || tau_decaymode_2 == 11) && (pt_2 >= 20) && (pt_2 < 40)",
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
            "DM1011_PT40_200": {
                "var": discriminator_variable,
                "bins": discriminator_binning,
                "expression": discriminator_variable,
                "cut": "(tau_decaymode_2 == 10 || tau_decaymode_2 == 11) && (pt_2 >= 40) && (pt_2 <= 200)",
            },
            "Inclusive": {
                "var": discriminator_variable,
                "bins": discriminator_binning,
                "expression": discriminator_variable,
                "cut": "(pt_2 >= 20)",
            },
        }
    }

    if special_flag:
        for key, cat_dict in categories["mt"].items():
            if key in special_binning.keys():
                cat_dict["bins"] = special_binning[key]["m_vis"]["bins"]

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
    return categorization
