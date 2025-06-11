import inspect
import logging
from typing import Any, Callable

from ntuple_processor.utils import Cut, Weight
from ntuple_processor.variations import (
    AddCut,
    AddWeight,
    ChangeDatasetReplaceMultipleCutsAndAddWeight,
    RemoveCut,
    RemoveWeight,
    ReplaceCut,
    ReplaceCutAndAddWeight,
    ReplaceMultipleCuts,
    ReplaceMultipleCutsAndAddWeight,
    ReplaceVariable,
    ReplaceVariableReplaceCutAndAddWeight,
    ReplaceWeight,
    SquareWeight,
)
from config.logging_setup_configs import setup_logging

logger = setup_logging(logger=logging.getLogger(__name__))


FF_OPTIONS = {
    "fake_factor": {
        "lt": "fake_factor_2",
        "tt_1": "fake_factor_1",
        "tt_2": "fake_factor_2",
    },
    "fake_factor_w_bias_corr": {
        "lt": """(
                    (
                        raw_qcd_fake_factor_2 *
                        qcd_fake_factor_fraction_2 *
                        qcd_correction_wo_DR_SR_2
                    ) +
                    (
                        raw_wjets_fake_factor_2 *
                        wjets_fake_factor_fraction_2 *
                        wjets_correction_wo_DR_SR_2
                    ) +
                    (
                        raw_ttbar_fake_factor_2 *
                        ttbar_fake_factor_fraction_2 *
                        ttbar_correction_wo_DR_SR_2
                    )
                )"""
    },
    "fake_factor_with_DR_SR_corr": {
        "lt": """(
                    (
                        raw_qcd_fake_factor_2 *
                        qcd_fake_factor_fraction_2 *
                        qcd_DR_SR_correction_2
                    ) +
                    (
                        raw_wjets_fake_factor_2 *
                        wjets_fake_factor_fraction_2 *
                        wjets_DR_SR_correction_2
                    ) +
                    (
                        raw_ttbar_fake_factor_2 *
                        ttbar_fake_factor_fraction_2
                    )
                )""",
    },
    "fake_factor_with_DR_SR_and_bias_corr": {
        "lt": """(
                    (
                        raw_qcd_fake_factor_2 *
                        qcd_fake_factor_fraction_2 *
                        qcd_fake_factor_correction_2
                    ) +
                    (
                        raw_wjets_fake_factor_2 *
                        wjets_fake_factor_fraction_2 *
                        wjets_fake_factor_correction_2
                    ) +
                    (
                        raw_ttbar_fake_factor_2 *
                        ttbar_fake_factor_fraction_2 *
                        ttbar_fake_factor_correction_2
                    )
                )""",
    },
    # --------------------------------------------------------------------------------------
    "raw_fake_factor": {
        "lt": "raw_fake_factor_2",
        "tt_1": "raw_fake_factor_1",
        "tt_2": "raw_fake_factor_2",
    },
    # --------------------------------------------------------------------------------------
    "raw_qcd_fake_factor_with_fraction": {
        "lt": "(raw_qcd_fake_factor_2 * qcd_fake_factor_fraction_2)",
    },
    "raw_qcd_fake_factor": {
        "lt": "raw_qcd_fake_factor_2",
    },
    "raw_qcd_fake_factor_w_bias_corr": {
        "lt": "(raw_qcd_fake_factor_2 * qcd_correction_wo_DR_SR_2)",
    },
    "raw_qcd_fake_factor_w_DR_SR_corr": {
        "lt": "(raw_qcd_fake_factor_2 * qcd_DR_SR_correction_2)",
    },
    "raw_qcd_fake_factor_w_DR_SR_and_bias_corr": {
        "lt": "(raw_qcd_fake_factor_2 * qcd_correction_wo_DR_SR_2 * qcd_DR_SR_correction_2)",
    },
    # --------------------------------------------------------------------------------------
    "raw_wjets_fake_factor_with_fraction": {
        "lt": "(raw_wjets_fake_factor_2 * wjets_fake_factor_fraction_2)",
    },
    "raw_wjets_fake_factor": {
        "lt": "raw_wjets_fake_factor_2",
    },
    "raw_wjets_fake_factor_w_bias_corr": {
        "lt": "(raw_wjets_fake_factor_2 * wjets_correction_wo_DR_SR_2)",
    },
    "raw_wjets_fake_factor_w_DR_SR_corr": {
        "lt": "(raw_wjets_fake_factor_2 * wjets_DR_SR_correction_2)",
    },
    "raw_wjets_fake_factor_w_DR_SR_and_bias_corr": {
        "lt": "(raw_wjets_fake_factor_2 * wjets_correction_wo_DR_SR_2 * wjets_DR_SR_correction_2)",
    },
    # --------------------------------------------------------------------------------------
    "raw_ttbar_fake_factor_with_fraction": {
        "lt": "(raw_ttbar_fake_factor_2 * ttbar_fake_factor_fraction_2)",
    },
    "raw_ttbar_fake_factor": {
        "lt": "raw_ttbar_fake_factor_2",
    },
    "raw_ttbar_fake_factor_w_bias_corr": {
        "lt": "(raw_ttbar_fake_factor_2 * ttbar_correction_wo_DR_SR_2)",
    },
    "raw_ttbar_fake_factor_w_DR_SR_corr": {
        "lt": "(raw_ttbar_fake_factor_2 * 1.0)",
    },
    "raw_ttbar_fake_factor_w_DR_SR_and_bias_corr": {
        "lt": "(raw_ttbar_fake_factor_2 * ttbar_correction_wo_DR_SR_2 * 1.0)",
    },
    # --------------------------------------------------------------------------------------
}

__FF_OPTION_info__ = """
    Different implementation of accessing full (FF_OPTIONS["fake_factor"]) and raw fake factors
    (FF_OPTIONS["raw_fake_factor"]) and their individual combinations with different corrections
    this can be set to a default value in RuntimeVariables or via set_ff_type function.

    In case of usage: This is mainly intendet to investigate individual contributions of the fake factors
    and their corrections to the SR in the DR region. Make sure that the corresponding components
    that are specified are also present in the produced ntuples!

    possible options based on https://github.com/KIT-CMS/TauAnalysis-CROWN/commit/d73463bfdf5a7023b6b032a0c2d05b00f88e4150
      - "fake_factor_2"
      - "qcd_DR_SR_correction_2"
      - "qcd_correction_wo_DR_SR_2"
      - "qcd_fake_factor_2"
      - "qcd_fake_factor_correction_2"
      - "qcd_fake_factor_fraction_2"
      - "raw_fake_factor_2"
      - "raw_qcd_fake_factor_2"
      - "raw_ttbar_fake_factor_2"
      - "raw_wjets_fake_factor_2"
      - "ttbar_DR_SR_correction_2"
      - "ttbar_correction_wo_DR_SR_2"
      - "ttbar_fake_factor_2"
      - "ttbar_fake_factor_correction_2"
      - "ttbar_fake_factor_fraction_2"
      - "wjets_DR_SR_correction_2"
      - "wjets_correction_wo_DR_SR_2"
      - "wjets_fake_factor_2"
      - "wjets_fake_factor_correction_2"
      - "wjets_fake_factor_fraction_2"
"""


def set_ff_type(ff_type):
    if ff_type not in FF_OPTIONS:
        logger.error(f"Fake factor option {ff_type} not found in FF_OPTIONS.")
        raise KeyError(f"Fake factor option {ff_type} not found in FF_OPTIONS.")

    logger.info(f"Setting fake factor option to {ff_type}= {FF_OPTIONS[ff_type]}")
    RuntimeVariables.FF_name_lt = FF_OPTIONS[ff_type]["lt"]
    logger.warning(
        """
            Setting fake factor option for tt_1 and tt_2 is in parts not implemented yet.
            Will not change the fake factor for tt_1 and tt_2 for now, only for lt.
            Please make sure to set the fake factor for tt_1 and tt_2 accordingly if needed.
        """
    )


class RuntimeVariables(object):
    """
    A singleton-like container class holding several variables that can be adjusted in time.

    Attributes:
        FF_name_lt (str): Fake factor name for the "lt" channel.
        FF_name_tt_1 (str): Fake factor name for the first "tt" channel.
        FF_name_tt_2 (str): Fake factor name for the second "tt" channel.

    Usage:
        >>> used = Used()
        >>> print(used.FF_name_lt)

    Note:
        This class implements a singleton-like pattern by returning the same instance
        on every instantiation.
    """
    FF_name_lt = FF_OPTIONS["fake_factor"]["lt"]
    FF_name_tt_1 = FF_OPTIONS["fake_factor"]["tt_1"]
    FF_name_tt_2 = FF_OPTIONS["fake_factor"]["tt_2"]

    def __new__(cls) -> "RuntimeVariables":
        if not hasattr(cls, "instance"):
            cls.instance = super(RuntimeVariables, cls).__new__(cls)
            return cls.instance


class LazyVariable:
    """
    A lazy evaluation wrapper for variables whose underlying value may change over time.

    This class accepts a factory callable that produces the actual instance to use.
    Any attribute access or string representation is delegated to the instance returned
    by the factory at call time, ensuring that modifications to the underlying variable
    are reflected immediately.

    Usage:
        >>> def my_factory() -> SomeClass:
        ...     return SomeClass()
        >>> lazy_var = LazyVariable(my_factory)
        >>> # Any attribute access on lazy_var is delegated to the instance returned by my_factory.
        >>> value = lazy_var.some_attribute
    """

    def __init__(self, factory: Callable[[], Any]) -> None:
        """
        Initializes a LazyVariable with a factory callable.

        Args:
            factory (Callable[[], Any]): A callable that returns the actual variable instance.
        """
        self.factory: Callable[[], Any] = factory
        try:
            caller = inspect.stack()[1]
            logger.debug(f"LazyVariable created at {caller.filename}:{caller.lineno} with {inspect.getsource(factory)}")
        except NameError:  # logger or inspect not defined
            pass

    def __getattr__(self, name: str) -> Any:
        """
        Delegates attribute access to the instance returned by the factory.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            Any: The attribute value from the instantiated object.
        """
        instance = self.factory()
        try:
            caller = inspect.stack()[1]
            logger.debug(f"LazyVariable __getattr__: '{name}' called from {caller.filename}:{caller.lineno}, returning {instance}")
        except NameError:  # logger or inspect not defined
            pass
        return getattr(instance, name)

    def __repr__(self) -> str:
        """
        Returns the official string representation of the LazyVariable.

        Returns:
            str: The string representation of the object returned by the factory.
        """
        result = repr(self.factory())
        try:
            caller = inspect.stack()[1]
            logger.debug(f"LazyVariable __repr__: called from {caller.filename}:{caller.lineno}, returning {result}")
        except NameError:  # logger or inspect not defined
            pass
        return result

    def __str__(self) -> str:
        """
        Returns the informal string representation of the LazyVariable.

        Returns:
            str: The string representation of the object returned by the factory.
        """
        result = str(self.factory())
        try:
            caller = inspect.stack()[1]
            logger.debug(f"LazyVariable __str__: called from {caller.filename}:{caller.lineno}, returning {result}")
        except NameError:  # logger or inspect not defined
            pass
        return result


#  Variations needed for the various jet background estimations.
# TODO: In order to properly use this variation friend trees with the correct weights need to be created.
same_sign = ReplaceCut("same_sign", "os", Cut("q_1*q_2>0", "ss"))

# TODO: In order to properly use this variation friend trees with the correct weights need to be created.
same_sign_em = ReplaceCutAndAddWeight(
    "same_sign",
    "os",
    Cut("q_1*q_2>0", "ss"),
    Weight("em_qcd_osss_binned_Weight", "qcd_weight"),
)
abcd_method = [
    ReplaceCut("abcd_same_sign", "os", Cut("q_1*q_2>0", "ss")),
    ReplaceCut(
        "abcd_anti_iso",
        "tau_iso",
        Cut(
            "(id_tau_vsJet_Tight_1>0.5 && id_tau_vsJet_Tight_2<0.5 && id_tau_vsJet_VLoose_2>0.5)",
            "tau_anti_iso",
        ),
    ),
    ReplaceMultipleCuts(
        "abcd_same_sign_anti_iso",
        ["os", "tau_iso"],
        [
            Cut("q_1*q_2>0", "ss"),
            Cut(
                "(id_tau_vsJet_Tight_1>0.5 && id_tau_vsJet_Tight_2<0.5 && id_tau_vsJet_VLoose_2>0.5)",
                "tau_anti_iso",
            ),
        ],
    ),
]

same_sign_anti_iso_lt = ReplaceMultipleCuts(
    "same_sign_anti_iso",
    ["os", "tau_iso"],
    [
        Cut("q_1*q_2>0", "ss"),
        Cut("(id_tau_vsJet_Tight_2<0.5 && id_tau_vsJet_VLoose_2>0.5)", "tau_anti_iso"),
    ]
)


anti_iso_lt = LazyVariable(  # requieres LazyVariation since Used.FF_name_lt may be defined later
    lambda: ReplaceCutAndAddWeight(
        "anti_iso",
        "tau_iso",
        Cut("(id_tau_vsJet_Tight_2<0.5 && id_tau_vsJet_VLoose_2>0.5)", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    )
)

anti_iso_lt_no_ff = ReplaceCutAndAddWeight(
    "anti_iso",
    "tau_iso",
    Cut("(id_tau_vsJet_Tight_2<0.5 && id_tau_vsJet_VLoose_2>0.5)", "tau_anti_iso"),
    Weight("1.0", "fake_factor"),
)

anti_iso_tt_mcl = LazyVariable(  # requieres LazyVariation since Used.FF_name_lt may be defined later
    lambda: ReplaceMultipleCutsAndAddWeight(
        "anti_iso",
        ["tau_iso", "ff_veto"],
        [
            Cut(
                "(id_tau_vsJet_Tight_2>0.5 && id_tau_vsJet_Tight_1<0.5 && id_tau_vsJet_VLoose_1>0.5)",
                "tau_anti_iso",
            ),
            Cut("gen_match_1 != 6", "tau_anti_iso"),
        ],
        Weight(RuntimeVariables.FF_name_tt_2, "fake_factor"),
    )
)

anti_iso_tt = LazyVariable(  # requieres LazyVariation since Used.FF_name_lt may be defined later
    lambda: ReplaceCutAndAddWeight(
        "anti_iso",
        "tau_iso",
        Cut(
            """(
                    (
                        (id_tau_vsJet_Tight_1 < 0.5) &&
                        (id_tau_vsJet_Tight_2 > 0.5) &&
                        (id_tau_vsJet_VLoose_1 > 0.5)
                    ) ||
                    (
                        (id_tau_vsJet_Tight_1 > 0.5) &&
                        (id_tau_vsJet_Tight_2 < 0.5) &&
                        (id_tau_vsJet_VLoose_2 > 0.5)
                    )
                )""",
            "tau_anti_iso"
        ),
        Weight(f"0.5 * {RuntimeVariables.FF_name_tt_1} * (id_tau_vsJet_Tight_1 < 0.5) + 0.5 * {RuntimeVariables.FF_name_tt_2} * (id_tau_vsJet_Tight_2 < 0.5)", "fake_factor"),
    )
)

wfakes_tt = ReplaceCut(
    "wfakes", "ff_veto", Cut("(gen_match_1!=6 && gen_match_2 == 6)", "wfakes_cut")
)
wfakes_w_tt = AddCut(
    "wfakes", Cut("(gen_match_1!=6 && gen_match_2 == 6)", "wfakes_cut")
)

# anti_iso_split_lt = [
#     ReplaceCutAndAddWeight(
#         "anti_iso_w",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff_lt_wjets", "fake_factor"),
#     ),
#     ReplaceCutAndAddWeight(
#         "anti_iso_qcd",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff_lt_qcd", "fake_factor"),
#     ),
#     ReplaceCutAndAddWeight(
#         "anti_iso_tt",
#         "tau_iso",
#         Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
#         Weight("ff_lt_ttbar", "fake_factor"),
#     ),
# ]
# Pileup reweighting
pileup_reweighting = [
    ReplaceVariable("CMS_PileUpUp", "PileUpUp"),
    ReplaceVariable("CMS_PileUpDown", "PileUpDown")
]


# Energy scales.
# Previously defined with 2017 in name.
tau_es_3prong = [
    ReplaceVariable("CMS_scale_t_3prong_EraUp", "tauEs3prong0pizeroUp"),
    ReplaceVariable("CMS_scale_t_3prong_EraDown", "tauEs3prong0pizeroDown"),
]

tau_es_3prong1pizero = [
    ReplaceVariable("CMS_scale_t_3prong1pizero_EraUp", "tauEs3prong1pizeroUp"),
    ReplaceVariable("CMS_scale_t_3prong1pizero_EraDown", "tauEs3prong1pizeroDown"),
]

tau_es_1prong = [
    ReplaceVariable("CMS_scale_t_1prong_EraUp", "tauEs1prong0pizeroUp"),
    ReplaceVariable("CMS_scale_t_1prong_EraDown", "tauEs1prong0pizeroDown"),
]

tau_es_1prong1pizero = [
    ReplaceVariable("CMS_scale_t_1prong1pizero_EraUp", "tauEs1prong1pizeroUp"),
    ReplaceVariable("CMS_scale_t_1prong1pizero_EraDown", "tauEs1prong1pizeroDown"),
]

emb_tau_es_3prong = [
    ReplaceVariable("CMS_scale_t_emb_3prong_EraUp", "tauEs3prong0pizeroUp"),
    ReplaceVariable("CMS_scale_t_emb_3prong_EraDown", "tauEs3prong0pizeroDown"),
]

emb_tau_es_3prong1pizero = [
    ReplaceVariable("CMS_scale_t_emb_3prong1pizero_EraUp", "tauEs3prong1pizeroUp"),
    ReplaceVariable("CMS_scale_t_emb_3prong1pizero_EraDown", "tauEs3prong1pizeroDown"),
]

emb_tau_es_1prong = [
    ReplaceVariable("CMS_scale_t_emb_1prong_EraUp", "tauEs1prong0pizeroUp"),
    ReplaceVariable("CMS_scale_t_emb_1prong_EraDown", "tauEs1prong0pizeroDown"),
]

emb_tau_es_1prong1pizero = [
    ReplaceVariable("CMS_scale_t_emb_1prong1pizero_EraUp", "tauEs1prong1pizeroUp"),
    ReplaceVariable("CMS_scale_t_emb_1prong1pizero_EraDown", "tauEs1prong1pizeroDown"),
]


# Electron energy scale
# TODO add in ntuples ?
# ele_es = [
#     ReplaceVariable("CMS_scale_eUp", "eleScaleUp"),
#     ReplaceVariable("CMS_scale_eDown", "eleScaleDown"),
# ]

# ele_res = [
#     ReplaceVariable("CMS_res_eUp", "eleSmearUp"),
#     ReplaceVariable("CMS_res_eDown", "eleSmearDown"),
# ]

# Jet energy scale split by sources.
jet_es = [
    ReplaceVariable("CMS_scale_j_AbsoluteUp", "jesUncAbsoluteUp"),
    ReplaceVariable("CMS_scale_j_AbsoluteDown", "jesUncAbsoluteDown"),
    ReplaceVariable("CMS_scale_j_Absolute_EraUp", "jesUncAbsoluteYearUp"),
    ReplaceVariable("CMS_scale_j_Absolute_EraDown", "jesUncAbsoluteYearDown"),
    ReplaceVariable("CMS_scale_j_BBEC1Up", "jesUncBBEC1Up"),
    ReplaceVariable("CMS_scale_j_BBEC1Down", "jesUncBBEC1Down"),
    ReplaceVariable("CMS_scale_j_BBEC1_EraUp", "jesUncBBEC1YearUp"),
    ReplaceVariable("CMS_scale_j_BBEC1_EraDown", "jesUncBBEC1YearDown"),
    ReplaceVariable("CMS_scale_j_EC2Up", "jesUncEC2Up"),
    ReplaceVariable("CMS_scale_j_EC2Down", "jesUncEC2Down"),
    ReplaceVariable("CMS_scale_j_EC2_EraUp", "jesUncEC2YearUp"),
    ReplaceVariable("CMS_scale_j_EC2_EraDown", "jesUncEC2YearDown"),
    ReplaceVariable("CMS_scale_j_HFUp", "jesUncHFUp"),
    ReplaceVariable("CMS_scale_j_HFDown", "jesUncHFDown"),
    ReplaceVariable("CMS_scale_j_HF_EraUp", "jesUncHFYearUp"),
    ReplaceVariable("CMS_scale_j_HF_EraDown", "jesUncHFYearDown"),
    ReplaceVariable("CMS_scale_j_FlavorQCDUp", "jesUncFlavorQCDUp"),
    ReplaceVariable("CMS_scale_j_FlavorQCDDown", "jesUncFlavorQCDDown"),
    ReplaceVariable("CMS_scale_j_RelativeBalUp", "jesUncRelativeBalUp"),
    ReplaceVariable("CMS_scale_j_RelativeBalDown", "jesUncRelativeBalDown"),
    ReplaceVariable("CMS_scale_j_RelativeSample_EraUp", "jesUncRelativeSampleYearUp"),
    ReplaceVariable("CMS_scale_j_RelativeSample_EraDown", "jesUncRelativeSampleYearDown"),
    ReplaceVariable("CMS_res_j_EraUp", "jerUncUp"),
    ReplaceVariable("CMS_res_j_EraDown", "jerUncDown"),
]

jet_es_hem = [
    ReplaceVariable("CMS_scale_j_HEMIssue_EraUp", "jesUncHEMIssueUp"),
    ReplaceVariable("CMS_scale_j_HEMIssue_EraDown", "jesUncHEMIssueDown"),
]

LHE_scale_norm_muR = [
    AddWeight("LHE_scale_muR_normUp", Weight("(lhe_scale_weight__LHEScaleMuRWeightUp)", "muR2p0_muF2p0_weight")),
    AddWeight("LHE_scale_muR_normDown", Weight("(lhe_scale_weight__LHEScaleMuRWeightDown)", "muR0p5_muF0p5_weight"))
]

LHE_scale_norm_muF = [
    AddWeight("LHE_scale_muF_normUp", Weight("(lhe_scale_weight__LHEScaleMuFWeightUp)", "muR2p0_muF2p0_weight")),
    AddWeight("LHE_scale_muF_normDown", Weight("(lhe_scale_weight__LHEScaleMuFWeightDown)", "muR0p5_muF0p5_weight"))
]


met_unclustered = [
    ReplaceVariable("CMS_scale_met_unclustered_energy_EraUp", "metUnclusteredEnUp"),
    ReplaceVariable("CMS_scale_met_unclustered_energy_EraDown", "metUnclusteredEnDown"),
]


recoil_resolution = [
    ReplaceVariable("CMS_res_met_EraUp", "metRecoilResolutionUp"),
    ReplaceVariable("CMS_res_met_EraDown", "metRecoilResolutionDown"),
]

recoil_response = [
    ReplaceVariable("CMS_scale_met_EraUp", "metRecoilResponseUp"),
    ReplaceVariable("CMS_scale_met_EraDown", "metRecoilResponseDown"),
]

# # fake met scaling in embedded samples
# TODO still needed ?
# emb_met_scale = [
#         ReplaceVariable("scale_embed_metUp", "emb_scale_metUp"),
#         ReplaceVariable("scale_embed_metDown", "emb_scale_metDown")
#         ]

# Energy scales of leptons faking tau leptons.
# Inclusive in eta
# TODO do we need the ones without barrel / endcap plit ?
# ele_fake_es = [
#         ReplaceVariable("CMS_ZLShape_et_1prong_EraUp", "tauEleFakeEsOneProngCommonUp"),
#         ReplaceVariable("CMS_ZLShape_et_1prong_EraDown", "tauEleFakeEsOneProngCommonDown"),
#         ReplaceVariable("CMS_ZLShape_et_1prong1pizero_EraUp", "tauEleFakeEsOneProngPiZerosCommonUp"),
#         ReplaceVariable("CMS_ZLShape_et_1prong1pizero_EraDown", "tauEleFakeEsOneProngPiZerosCommonDown"),
#         ]

# Eta binned uncertainty
ele_fake_es_1prong = [
    ReplaceVariable("CMS_ZLShape_et_1prong_barrel_EraUp", "tauEleFakeEs1prongBarrelUp"),
    ReplaceVariable("CMS_ZLShape_et_1prong_barrel_EraDown", "tauEleFakeEs1prongBarrelDown"),
    ReplaceVariable("CMS_ZLShape_et_1prong_endcap_EraUp", "tauEleFakeEs1prongEndcapUp"),
    ReplaceVariable("CMS_ZLShape_et_1prong_endcap_EraDown", "tauEleFakeEs1prongEndcapDown"),
]

ele_fake_es_1prong1pizero = [
    ReplaceVariable("CMS_ZLShape_et_1prong1pizero_barrel_EraUp", "tauEleFakeEs1prong1pizeroBarrelUp"),
    ReplaceVariable("CMS_ZLShape_et_1prong1pizero_barrel_EraDown","tauEleFakeEs1prong1pizeroBarrelDown"),
    ReplaceVariable("CMS_ZLShape_et_1prong1pizero_endcap_EraUp", "tauEleFakeEs1prong1pizeroEndcapUp"),
    ReplaceVariable("CMS_ZLShape_et_1prong1pizero_endcap_EraDown","tauEleFakeEs1prong1pizeroEndcapDown"),
]

ele_fake_es = ele_fake_es_1prong + ele_fake_es_1prong1pizero

# TODO add split by decay mode ?
# mu_fake_es_1prong = [
#         ReplaceVariable("CMS_ZLShape_mt_1prong_EraUp", "tauMuFakeEsOneProngUp"),
#         ReplaceVariable("CMS_ZLShape_mt_1prong_EraDown", "tauMuFakeEsOneProngDown")
#         ]

# mu_fake_es_1prong1pizero = [
#         ReplaceVariable("CMS_ZLShape_mt_1prong1pizero_EraUp", "tauMuFakeEsOneProngPiZerosUp"),
#         ReplaceVariable("CMS_ZLShape_mt_1prong1pizero_EraDown", "tauMuFakeEsOneProngPiZerosDown")
#         ]

mu_fake_es_inc = [    # scale_fake_m -> ZLShape_mt_Era...
    ReplaceVariable("CMS_scale_fake_m_EraUp", "tauMuFakeEsUp"),
    ReplaceVariable("CMS_scale_fake_m_EraDown", "tauMuFakeEsDown"),
]

# # B-tagging uncertainties.
# TODO correct naming for these ?
# btag_eff = [
#         ReplaceVariable("CMS_htt_eff_b_EraUp", "btagEffUp"),
#         ReplaceVariable("CMS_htt_eff_b_EraDown", "btagEffDown")
#         ]

# mistag_eff = [
#         ReplaceVariable("CMS_htt_mistag_b_EraUp", "btagMistagUp"),
#         ReplaceVariable("CMS_htt_mistag_b_EraDown", "btagMistagDown")
#         ]

# Efficiency corrections.
# Tau ID efficiency.

# TODO add high pt tau ID efficiency
tau_id_eff_lt = [
    ReplaceVariable("CMS_eff_t_30-35_EraUp", "vsJetTau30to35Up"),
    ReplaceVariable("CMS_eff_t_30-35_EraDown", "vsJetTau30to35Down"),
    ReplaceVariable("CMS_eff_t_35-40_EraUp", "vsJetTau35to40Up"),
    ReplaceVariable("CMS_eff_t_35-40_EraDown", "vsJetTau35to40Down"),
    ReplaceVariable("CMS_eff_t_40-500_EraUp", "vsJetTau40to500Up"),
    ReplaceVariable("CMS_eff_t_40-500_EraDown", "vsJetTau40to500Down"),
    ReplaceVariable("CMS_eff_t_500-1000_EraUp", "vsJetTau500to1000Up"),
    ReplaceVariable("CMS_eff_t_500-1000_EraDown", "vsJetTau500to1000Down"),
    ReplaceVariable("CMS_eff_t_1000-Inf_EraUp", "vsJetTau1000toInfUp"),
    ReplaceVariable("CMS_eff_t_1000-Inf_EraDown", "vsJetTau1000toInfDown"),
]
emb_tau_id_eff_lt = [
    ReplaceVariable("CMS_eff_t_emb_30-35_EraUp", "vsJetTau30to35Up"),
    ReplaceVariable("CMS_eff_t_emb_30-35_EraDown", "vsJetTau30to35Down"),
    ReplaceVariable("CMS_eff_t_emb_35-40_EraUp", "vsJetTau35to40Up"),
    ReplaceVariable("CMS_eff_t_emb_35-40_EraDown", "vsJetTau35to40Down"),
    ReplaceVariable("CMS_eff_t_emb_40-500_EraUp", "vsJetTau40toInfUp"),
    ReplaceVariable("CMS_eff_t_emb_40-500_EraDown", "vsJetTau40toInfDown"),
]
# tauid variations used for correlation with mc ones
emb_tau_id_eff_lt_corr = [
    ReplaceVariable("CMS_eff_t_30-35_EraUp", "vsJetTau30to35Up"),
    ReplaceVariable("CMS_eff_t_30-35_EraDown", "vsJetTau30to35Down"),
    ReplaceVariable("CMS_eff_t_35-40_EraUp", "vsJetTau35to40Up"),
    ReplaceVariable("CMS_eff_t_35-40_EraDown", "vsJetTau35to40Down"),
    ReplaceVariable("CMS_eff_t_40-500_EraUp", "vsJetTau40toInfUp"),
    ReplaceVariable("CMS_eff_t_40-500_EraDown", "vsJetTau40toInfDown"),
]

tau_id_eff_tt = [
    ReplaceVariable("CMS_eff_t_dm0_EraUp", "vsJetTauDM0Up"),
    ReplaceVariable("CMS_eff_t_dm0_EraDown", "vsJetTauDM0Down"),
    ReplaceVariable("CMS_eff_t_dm1_EraUp", "vsJetTauDM1Up"),
    ReplaceVariable("CMS_eff_t_dm1_EraDown", "vsJetTauDM1Down"),
    ReplaceVariable("CMS_eff_t_dm10_EraUp", "vsJetTauDM10Up"),
    ReplaceVariable("CMS_eff_t_dm10_EraDown", "vsJetTauDM10Down"),
    ReplaceVariable("CMS_eff_t_dm11_EraUp", "vsJetTauDM11Up"),
    ReplaceVariable("CMS_eff_t_dm11_EraDown", "vsJetTauDM11Down"),
]

emb_tau_id_eff_tt = [
    ReplaceVariable("CMS_eff_t_dm0_EraUp", "vsJetTauDM0Up"),
    ReplaceVariable("CMS_eff_t_dm0_EraDown", "vsJetTauDM0Down"),
    ReplaceVariable("CMS_eff_t_dm1_EraUp", "vsJetTauDM1Up"),
    ReplaceVariable("CMS_eff_t_dm1_EraDown", "vsJetTauDM1Down"),
    ReplaceVariable("CMS_eff_t_dm10_EraUp", "vsJetTauDM10Up"),
    ReplaceVariable("CMS_eff_t_dm10_EraDown", "vsJetTauDM10Down"),
    ReplaceVariable("CMS_eff_t_dm11_EraUp", "vsJetTauDM11Up"),
    ReplaceVariable("CMS_eff_t_dm11_EraDown", "vsJetTauDM11Down"),
]


# Jet to tau fake rate.
jet_to_tau_fake = [
    AddWeight(
        "CMS_fake_j_EraUp",
        Weight("max(1.0-pt_2*0.002, 0.6)", "jetToTauFake_weight"),
    ),
    AddWeight(
        "CMS_fake_j_EraDown",
        Weight("min(1.0+pt_2*0.002, 1.4)", "jetToTauFake_weight"),
    ),
]

zll_et_fake_rate = [
    ReplaceVariable("CMS_fake_e_BA_EraUp", "vsEleBarrelUp"),
    ReplaceVariable("CMS_fake_e_BA_EraDown", "vsEleBarrelDown"),
    ReplaceVariable("CMS_fake_e_EC_EraUp", "vsEleEndcapUp"),
    ReplaceVariable("CMS_fake_e_EC_EraDown", "vsEleEndcapDown"),
]

zll_mt_fake_rate_up = [
    ReplaceVariable(f"CMS_fake_m_WH{region}_EraUp", f"vsMuWheel{region}Up")
    for region in ["1", "2", "3", "4", "5"]
]
zll_mt_fake_rate_down = [
    ReplaceVariable(f"CMS_fake_m_WH{region}_EraDown", f"vsMuWheel{region}Down")
    for region in ["1", "2", "3", "4", "5"]
]

zll_mt_fake_rate = zll_mt_fake_rate_up + zll_mt_fake_rate_down


trigger_eff_mt = [
    ReplaceVariable("CMS_eff_m_trigger_EraUp", "singleMuonTriggerSFUp"),
    ReplaceVariable("CMS_eff_m_trigger_EraDown", "singleMuonTriggerSFDown"),
]
trigger_eff_mt_emb = [
    ReplaceVariable("CMS_eff_m_trigger_emb_EraUp", "singleMuonTriggerSFUp"),
    ReplaceVariable("CMS_eff_m_trigger_emb_EraDown", "singleMuonTriggerSFDown"),
]

trigger_eff_et = [
    ReplaceVariable("CMS_eff_e_trigger_EraUp", "singleElectronTriggerSFUp"),
    ReplaceVariable("CMS_eff_e_trigger_EraDown", "singleElectronTriggerSFDown"),
]
trigger_eff_et_emb = [
    ReplaceVariable("CMS_eff_e_trigger_emb_EraUp", "singleElectronTriggerSFUp"),
    ReplaceVariable("CMS_eff_e_trigger_emb_EraDown", "singleElectronTriggerSFDown"),
]
# TODO cross triggers
# trigger_eff_mt = [
#     ReplaceWeight(
#         "CMS_eff_trigger_mt_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singlelep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_mt_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singlelep_down", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_mt_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_crosslep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_mt_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_crosslep_down", "triggerweight"),
#     ),
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_mt_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight("mtau_triggerweight_ic_dm{dm}_up".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_mt_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight("mtau_triggerweight_ic_dm{dm}_down".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# trigger_eff_mt_emb = [
#     ReplaceWeight(
#         "CMS_eff_trigger_emb_mt_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singlelep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_emb_mt_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singlelep_down", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_emb_mt_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_crosslep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_emb_mt_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_crosslep_down", "triggerweight"),
#     ),
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_mt_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight("mtau_triggerweight_ic_dm{dm}_up".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_mt_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight("mtau_triggerweight_ic_dm{dm}_down".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraUp",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraDown",
#         "triggerweight",
#         Weight("mtau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# trigger_eff_et = [
#     ReplaceWeight(
#         "CMS_eff_trigger_et_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singlelep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_et_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singlelep_down", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_et_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_crosslep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_et_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_crosslep_down", "triggerweight"),
#     ),
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_et_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight("etau_triggerweight_ic_dm{dm}_up".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_et_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight("etau_triggerweight_ic_dm{dm}_down".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# trigger_eff_et_emb = [
#     ReplaceWeight(
#         "CMS_eff_trigger_emb_et_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singlelep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_emb_et_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singlelep_down", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_emb_et_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_crosslep_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_xtrigger_l_emb_et_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_crosslep_down", "triggerweight"),
#     ),
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_et_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight("etau_triggerweight_ic_dm{dm}_up".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_et_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight("etau_triggerweight_ic_dm{dm}_down".format(dm=dm), "triggerweight"),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraUp",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraDown",
#         "triggerweight",
#         Weight("etau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# TODO Tau Triggers
# tau_trigger_eff_tt = [
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_tt_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_lowpt_dm{dm}_up".format(dm=dm), "triggerweight"
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_tt_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_lowpt_dm{dm}_down".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_tt_dm{dm}_highpT_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_highpt_dm{dm}_up".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_tt_dm{dm}_highpT_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_highpt_dm{dm}_down".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraUp",
#         "triggerweight",
#         Weight("tautau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_EraDown",
#         "triggerweight",
#         Weight("tautau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# tau_trigger_eff_tt_emb = [
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_tt_dm{dm}_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_lowpt_dm{dm}_up".format(dm=dm), "triggerweight"
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_tt_dm{dm}_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_lowpt_dm{dm}_down".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_tt_dm{dm}_highpT_EraUp".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_highpt_dm{dm}_up".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     *[
#         ReplaceWeight(
#             "CMS_eff_xtrigger_t_emb_tt_dm{dm}_highpT_EraDown".format(dm=dm),
#             "triggerweight",
#             Weight(
#                 "tautau_triggerweight_ic_highpt_dm{dm}_down".format(dm=dm),
#                 "triggerweight",
#             ),
#         )
#         for dm in [0, 1, 10, 11]
#     ],
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraUp",
#         "triggerweight",
#         Weight("tautau_triggerweight_ic_singletau_up", "triggerweight"),
#     ),
#     ReplaceWeight(
#         "CMS_eff_trigger_single_t_emb_EraDown",
#         "triggerweight",
#         Weight("tautau_triggerweight_ic_singletau_down", "triggerweight"),
#     ),
# ]

# Embedding specific variations.
# TODO Embedding electron scale
emb_e_es = [
    ReplaceVariable("CMS_scale_e_barrel_embUp", "eleEsBarrelUp"),
    ReplaceVariable("CMS_scale_e_barrel_embDown", "eleEsBarrelDown"),
    ReplaceVariable("CMS_scale_e_endcap_embUp", "eleEsEndcapUp"),
    ReplaceVariable("CMS_scale_e_endcap_embDown", "eleEsEndcapDown"),
]

# TODO add embeddedDecayModeWeight

# emb_decay_mode_eff_lt = [
#     ReplaceWeight(
#         "CMS_3ProngEff_EraUp",
#         "decayMode_SF",
#         Weight(
#             "(pt_2<100)*embeddedDecayModeWeight_effUp_pi0Nom+(pt_2>=100)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_3ProngEff_EraDown",
#         "decayMode_SF",
#         Weight(
#             "(pt_2<100)*embeddedDecayModeWeight_effDown_pi0Nom+(pt_2>=100)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_1ProngPi0Eff_EraUp",
#         "decayMode_SF",
#         Weight(
#             "(pt_2<100)*embeddedDecayModeWeight_effNom_pi0Up+(pt_2>=100)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_1ProngPi0Eff_EraDown",
#         "decayMode_SF",
#         Weight(
#             "(pt_2<100)*embeddedDecayModeWeight_effNom_pi0Down+(pt_2>=100)",
#             "decayMode_SF",
#         ),
#     ),
# ]

# emb_decay_mode_eff_tt = [
#     ReplaceWeight(
#         "CMS_3ProngEff_EraUp",
#         "decayMode_SF",
#         Weight(
#             "(pt_2>=100)+(pt_1<100)*embeddedDecayModeWeight_effUp_pi0Nom+(pt_1>=100)*(pt_2<100)*((decayMode_2==0)*0.983+(decayMode_2==1)*0.983*1.051+(decayMode_2==10)*0.983*0.983*0.983+(decayMode_2==11)*0.983*0.983*0.983*1.051)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_3ProngEff_EraDown",
#         "decayMode_SF",
#         Weight(
#             "(pt_2>=100)+(pt_1<100)*embeddedDecayModeWeight_effDown_pi0Nom+(pt_1>=100)*(pt_2<100)*((decayMode_2==0)*0.967+(decayMode_2==1)*0.967*1.051+(decayMode_2==10)*0.967*0.967*0.967+(decayMode_2==11)*0.967*0.967*0.967*1.051)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_1ProngPi0Eff_EraUp",
#         "decayMode_SF",
#         Weight(
#             "(pt_2>=100)+(pt_1<100)*embeddedDecayModeWeight_effNom_pi0Up+(pt_1>=100)*(pt_2<100)*((decayMode_2==0)*0.975+(decayMode_2==1)*0.975*1.065+(decayMode_2==10)*0.975*0.975*0.975+(decayMode_2==11)*0.975*0.975*0.975*1.065)",
#             "decayMode_SF",
#         ),
#     ),
#     ReplaceWeight(
#         "CMS_1ProngPi0Eff_EraDown",
#         "decayMode_SF",
#         Weight(
#             "(pt_2>=100)+(pt_1<100)*embeddedDecayModeWeight_effNom_pi0Down+(pt_1>=100)*(pt_2<100)*((decayMode_2==0)*0.975+(decayMode_2==1)*0.975*1.037+(decayMode_2==10)*0.975*0.975*0.975+(decayMode_2==11)*0.975*0.975*0.975*1.037)",
#             "decayMode_SF",
#         ),
#     ),
# ]


prefiring = [
    ReplaceWeight(
        "CMS_prefiringUp", "prefireWeight", Weight("prefiring_wgt__prefiringUp", "prefireWeight")
    ),
    ReplaceWeight(
        "CMS_prefiringDown",
        "prefireWeight",
        Weight("prefiring_wgt__prefiringDown", "prefireWeight"),
    ),
]

zpt = [
    SquareWeight("CMS_htt_dyShape_EraUp", "zPtReweightWeight"),
    RemoveWeight("CMS_htt_dyShape_EraDown", "zPtReweightWeight"),
]

top_pt = [
    SquareWeight("CMS_htt_ttbarShapeUp", "topPtReweightWeight"),
    RemoveWeight("CMS_htt_ttbarShapeDown", "topPtReweightWeight"),
]

# TODO add fake factors
_ff_variations_lt = [
    'QCDFFunc',
    'QCDFFmcSubUnc',
    'WjetsFFunc',
    'WjetsFFmcSubUnc',
    'ttbarFFunc',
    'process_fractionsfracQCDUnc',
    'process_fractionsfracWjetsUnc',
    'process_fractionsfracTTbarUnc',
    'QCD_non_closure_m_vis_Corr',
    'QCD_non_closure_mass_2_Corr',
    'QCD_non_closure_deltaR_ditaupair_Corr',
    'QCD_non_closure_iso_1_Corr',
    'QCD_non_closure_tau_decaymode_2_Corr',
    'QCD_DR_SR_Corr',
    'Wjets_non_closure_m_vis_Corr',
    'Wjets_non_closure_mass_2_Corr',
    'Wjets_non_closure_deltaR_ditaupair_Corr',
    'Wjets_non_closure_iso_1_Corr',
    'Wjets_non_closure_tau_decaymode_2_Corr',
    'Wjets_DR_SR_Corr',
    'ttbar_non_closure_m_vis_Corr',
    'ttbar_non_closure_mass_2_Corr',
    'ttbar_non_closure_deltaR_ditaupair_Corr',
    'ttbar_non_closure_iso_1_Corr',
    'ttbar_non_closure_tau_decaymode_2_Corr'
]
#  Variations on the jet backgrounds estimated with the fake factor method.
ff_variations_lt = [
    ReplaceCutAndAddWeight(
        f"anti_iso_CMS_{syst}{shift}_Channel_Era",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(f"{RuntimeVariables.FF_name_lt}__{syst}{shift}", "fake_factor"),
    )
    for shift in ["Up", "Down"]
    for syst in _ff_variations_lt
]
# TODO: Check if variations are applied

# # Propagation of tau ES systematics on jetFakes process
ff_variations_tau_es_lt = [
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_1prong_EraDown",
        "tauEs1prong0pizeroDown",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_1prong_EraUp",
        "tauEs1prong0pizeroUp",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_1prong1pizero_EraDown",
        "tauEs1prong1pizeroDown",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_1prong1pizero_EraUp",
        "tauEs1prong1pizeroUp",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_3prong_EraDown",
        "tauEs3prong0pizeroDown",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_3prong_EraUp",
        "tauEs3prong0pizeroUp",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_3prong1pizero_EraDown",
        "tauEs3prong1pizeroDown",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_3prong1pizero_EraUp",
        "tauEs3prong1pizeroUp",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
]

# # Propagation of tau ES systematics on jetFakes process for emb only for correlation
ff_variations_tau_es_emb_lt = [
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_emb_1prong_EraDown",
        "tauEs1prong0pizeroDown",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_emb_1prong_EraUp",
        "tauEs1prong0pizeroUp",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_emb_1prong1pizero_EraDown",
        "tauEs1prong1pizeroDown",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_emb_1prong1pizero_EraUp",
        "tauEs1prong1pizeroUp",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_emb_3prong_EraDown",
        "tauEs3prong0pizeroDown",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_emb_3prong_EraUp",
        "tauEs3prong0pizeroUp",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_emb_3prong1pizero_EraDown",
        "tauEs3prong1pizeroDown",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
    ReplaceVariableReplaceCutAndAddWeight(
        "anti_iso_CMS_scale_t_emb_3prong1pizero_EraUp",
        "tauEs3prong1pizeroUp",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(RuntimeVariables.FF_name_lt, "fake_factor"),
    ),
]

# _ff_variations_tt = [
#     "fake_factor_qcd_stat_njet0_jet_pt_low_unc1{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet0_jet_pt_low_unc2{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet0_jet_pt_low_unc3{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet0_jet_pt_med_unc1{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet0_jet_pt_med_unc2{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet0_jet_pt_med_unc3{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet0_jet_pt_high_unc1{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet0_jet_pt_high_unc2{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet0_jet_pt_high_unc3{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet1_jet_pt_low_unc1{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet1_jet_pt_low_unc2{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet1_jet_pt_low_unc3{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet1_jet_pt_med_unc1{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet1_jet_pt_med_unc2{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet1_jet_pt_med_unc3{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet1_jet_pt_high_unc1{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet1_jet_pt_high_unc2{ch}{era}{shift}",
#     "fake_factor_qcd_stat_njet1_jet_pt_high_unc3{ch}{era}{shift}",
#     "fake_factor_qcd_stat_dR_unc1{ch}{era}{shift}",
#     "fake_factor_qcd_stat_dR_unc2{ch}{era}{shift}",
#     "fake_factor_qcd_stat_pt_unc1{ch}{era}{shift}",
#     "fake_factor_qcd_stat_pt_unc2{ch}{era}{shift}",
#     "fake_factor_qcd_syst{ch}{era}{shift}",
#     "fake_factor_ttbar_syst{ch}{era}{shift}",
#     "fake_factor_wjets_syst{ch}{era}{shift}",
#     "fake_factor_qcd_syst_dr_closure{ch}{era}{shift}",
#     "fake_factor_qcd_syst_pt_2_closure{ch}{era}{shift}",
#     "fake_factor_qcd_syst_met_closure{ch}{era}{shift}",
#     "fake_factor_syst_alt_func{ch}{era}{shift}",
# ]
# ff_variations_tt = [
#     ReplaceCutAndAddWeight(
#         "anti_iso_CMS_{syst}".format(
#             syst=syst.format(shift=shift.capitalize(), era="_Era", ch="_tt")
#         ),
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight(
#             "{syst}".format(syst=syst.format(shift="_" + shift, era="", ch="")),
#             "fake_factor",
#         ),
#     )
#     for shift in ["up", "down"]
#     for syst in _ff_variations_tt
# ]
# ff_variations_tt_mcl = [
#     ReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_{syst}".format(
#             syst=syst.format(shift=shift.capitalize(), era="_Era", ch="_tt")
#         ),
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight(
#             "{syst}".format(syst=syst.format(shift="_" + shift, era="", ch="")),
#             "fake_factor",
#         ),
#     )
#     for shift in ["up", "down"]
#     for syst in _ff_variations_tt
# ]

# # tt channel for embedded processes
# ff_variations_tau_es_tt = [
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraDown",
#         "tauEs1prong0pizeroDown",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraUp",
#         "tauEs1prong0pizeroUp",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraDown",
#         "tauEs1prong1pizeroDown",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraUp",
#         "tauEs1prong1pizeroUp",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraDown",
#         "tauEs3prong0pizeroDown",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraUp",
#         "tauEs3prong0pizeroUp",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraDown",
#         "tauEs3prong1pizeroDown",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ReplaceVariableReplaceCutAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraUp",
#         "tauEs3prong1pizeroUp",
#         "tau_iso",
#         Cut(
#             "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#             "tau_anti_iso",
#         ),
#         Weight("fake_factor", "fake_factor"),
#     ),
# ]

# # tt channel for mcl processes
# ff_variations_tau_es_tt_mcl = [
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraDown",
#         "tauEs1prong0pizeroDown",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong_EraUp",
#         "tauEs1prong0pizeroUp",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraDown",
#         "tauEs1prong1pizeroDown",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_1prong1pizero_EraUp",
#         "tauEs1prong1pizeroUp",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraDown",
#         "tauEs3prong0pizeroDown",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong_EraUp",
#         "tauEs3prong0pizeroUp",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraDown",
#         "tauEs3prong1pizeroDown",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("fake_factor", "fake_factor"),
#     ),
#     ChangeDatasetReplaceMultipleCutsAndAddWeight(
#         "anti_iso_CMS_scale_t_3prong1pizero_EraUp",
#         "tauEs3prong1pizeroUp",
#         ["tau_iso", "ff_veto"],
#         [
#             Cut(
#                 "(id_tau_vsJet_Tight_2>0.5&&id_tau_vsJet_Medium_1<0.5&&id_tau_vsJet_VVVLoose_1>0.5)",
#                 "tau_anti_iso",
#             ),
#             Cut("gen_match_1 != 6", "tau_anti_iso"),
#         ],
#         Weight("fake_factor", "fake_factor"),
#     ),
# ]

# qcd_variations_em = [
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_rate_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_rateup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_rate_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_ratedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_shape_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_shapeup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_shape_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_shapedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_shape2_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_shape2up_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_0jet_shape2_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_0jet_shape2down_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_rate_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_rateup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_rate_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_ratedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_shape_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_shapeup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_shape_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_shapedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_shape2_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_shape2up_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_1jet_shape2_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_1jet_shape2down_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_rate_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_rateup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_rate_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_ratedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_shape_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_shapeup_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_shape_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_shapedown_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_shape2_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_shape2up_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_2jet_shape2_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_osss_stat_2jet_shape2down_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_iso_EraUp",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_extrap_up_Weight", "qcd_weight"),
#     ),
#     ReplaceCutAndAddWeight(
#         "same_sign_CMS_htt_qcd_iso_EraDown",
#         "os",
#         Cut("q_1*q_2>0", "ss"),
#         Weight("em_qcd_extrap_down_Weight", "qcd_weight"),
#     ),
# ]


# ------------------------------------------------------------------------------------------
# collections for ordering


__doc__ = """
Usage Example for Variation Collections

This module defines several systematic variation collections that group different
systematic adjustments such as fake process estimations, energy scale shifts, MET variations,
efficiency corrections, fake rate variations, trigger efficiencies, and additional uncertainties.
Each collection can be applied at once using `<VariationCollection>.unrolled()` that returns a
list of all variations defined within that collection.

For example, instead of fetching each variation individually this would be possible:

    from config.shapes import variations

    # Retrieve and loop over all fake process estimation variations
    variations = [
        tau_es_3prong,
        tau_es_3prong1pizero,
        tau_es_1prong,
        tau_es_1prong1pizero,
        ...
    ]
    # Or use
    variations = variations.EnergyScaleVariations.unrolled()
    # Or another collection you might seems be more fitting i.e. process wise.

This pattern applies similarly to other collections. Thus, you only need to import the corresponding
variation collection and call its `unrolled()` method to obtain a list of all variations, making the
application of systematics both concise and consistent.

The individual Application either trough variations.tau_es_3prong or variations.EnergyScaleVariations.tau_es_3prong
is still possible.
"""


class VariationCollectionMeta(type):
    def __add__(cls, other):
        if not issubclass(other, _VariationCollection):
            raise TypeError("Cannot add {} to {}".format(other, cls))
        merged_attrs = {
            **{k: v for k, v in cls.__dict__.items() if not k.startswith("__")},
            **{k: v for k, v in other.__dict__.items() if not k.startswith("__")},
        }
        return type(f"{cls.__name__}+{other.__name__}", (_VariationCollection,), merged_attrs)


class _VariationCollection(metaclass=VariationCollectionMeta):
    @classmethod
    def unrolled(cls):
        results = []
        for name, value in cls.__dict__.items():
            if not name.startswith("__"):
                results.append(value)
        return results


class SemiLeptonicFFEstimations(_VariationCollection):
    same_sign = same_sign
    anti_iso_lt = anti_iso_lt
    same_sign_anti_iso_lt = same_sign_anti_iso_lt


class FullyHadronicFFEstimations(_VariationCollection):
    abcd_method = abcd_method
    same_sign = same_sign
    anti_iso_tt = anti_iso_tt


# ------------------------------------------------------------------------------------------

class LHE_scale(_VariationCollection):
    muR = LHE_scale_norm_muR
    muF = LHE_scale_norm_muF


class Recoil(_VariationCollection):
    recoil_resolution = recoil_resolution
    recoil_response = recoil_response


class TauEnergyScale(_VariationCollection):
    tau_es_3prong = tau_es_3prong
    tau_es_3prong1pizero = tau_es_3prong1pizero
    tau_es_1prong = tau_es_1prong
    tau_es_1prong1pizero = tau_es_1prong1pizero


class TauEmbeddingEnergyScale(_VariationCollection):
    emb_tau_es_3prong = emb_tau_es_3prong
    emb_tau_es_3prong1pizero = emb_tau_es_3prong1pizero
    emb_tau_es_1prong = emb_tau_es_1prong
    emb_tau_es_1prong1pizero = emb_tau_es_1prong1pizero


class FakeFactorLT(_VariationCollection):
    ff_variations_lt = ff_variations_lt


class TauIDAndTriggerEfficiency(_VariationCollection):
    emb_tau_id_eff_tt = emb_tau_id_eff_tt
    tau_id_eff_tt = tau_id_eff_tt
    # tau_trigger_eff_tt_emb = tau_trigger_eff_tt_emb
    # tau_trigger_eff_tt = tau_trigger_eff_tt
    # emb_decay_mode_eff_tt = emb_decay_mode_eff_tt


# ------------------------------------------------------------------------------------------


class FakeProcessEstimationVariations(_VariationCollection):
    same_sign = same_sign
    same_sign_em = same_sign_em
    anti_iso_lt = anti_iso_lt
    anti_iso_tt = anti_iso_tt
    anti_iso_tt_mcl = anti_iso_tt_mcl
    abcd_method = abcd_method


class EnergyScaleVariations(_VariationCollection):
    tau_es_3prong = tau_es_3prong
    tau_es_3prong1pizero = tau_es_3prong1pizero
    tau_es_1prong = tau_es_1prong
    tau_es_1prong1pizero = tau_es_1prong1pizero
    mu_fake_es_inc = mu_fake_es_inc
    ele_fake_es = ele_fake_es
    emb_tau_es_3prong = emb_tau_es_3prong
    emb_tau_es_3prong1pizero = emb_tau_es_3prong1pizero
    emb_tau_es_1prong = emb_tau_es_1prong
    emb_tau_es_1prong1pizero = emb_tau_es_1prong1pizero
    jet_es = jet_es
    # TODO add missing ES
    # mu_fake_es_1prong = mu_fake_es_1prong
    # mu_fake_es_1prong1pizero = mu_fake_es_1prong1pizero
    # ele_es = ele_es
    # ele_res = ele_res
    emb_e_es,
    # ele_fake_es_1prong = ele_fake_es_1prong
    # ele_fake_es_1prong1pizero = ele_fake_es_1prong1pizero
    # ele_fake_es = ele_fake_es


class METVariations(_VariationCollection):
    met_unclustered = met_unclustered
    recoil_resolution = recoil_resolution
    recoil_response = recoil_response


class EffifiencyVariations(_VariationCollection):
    tau_id_eff_lt = tau_id_eff_lt
    tau_id_eff_tt = tau_id_eff_tt
    emb_tau_id_eff_lt = emb_tau_id_eff_lt
    emb_tau_id_eff_tt = emb_tau_id_eff_tt
    emb_tau_id_eff_lt_corr = emb_tau_id_eff_lt_corr


class FakeRateVariations(_VariationCollection):
    jet_to_tau_fake = jet_to_tau_fake
    zll_et_fake_rate = zll_et_fake_rate
    zll_mt_fake_rate = zll_mt_fake_rate


class TriggerEfficiencyVariations(_VariationCollection):
    # TODO add trigger efficiency uncertainties
    # tau_trigger_eff_tt = tau_trigger_eff_tt
    # tau_trigger_eff_tt_emb = tau_trigger_eff_tt_emb
    trigger_eff_mt = trigger_eff_mt
    trigger_eff_et = trigger_eff_et
    trigger_eff_et_emb = trigger_eff_et_emb
    trigger_eff_mt_emb = trigger_eff_mt_emb


# Additional uncertainties
class AdditionalVariations(_VariationCollection):
    prefiring = prefiring
    zpt = zpt
    top_pt = top_pt
    pileup_reweighting = pileup_reweighting
    # TODO add missing uncertainties
    # btag_eff = btag_eff
    # mistag_eff = mistag_eff
    # emb_decay_mode_eff_lt = emb_decay_mode_eff_lt
    # emb_decay_mode_eff_tt = emb_decay_mode_eff_tt


class JetFakeVariations(_VariationCollection):
    # TODO add jetfake uncertainties
    ff_variations_lt = ff_variations_lt
    ff_variations_tau_es_lt = ff_variations_tau_es_lt
    ff_variations_tau_es_emb_lt = ff_variations_tau_es_emb_lt
    # ff_variations_tt = ff_variations_tt
    # ff_variations_tt_mcl = ff_variations_tt_mcl
    # qcd_variations_em = qcd_variations_em
    # ff_variations_tau_es_tt = ff_variations_tau_es_tt
    # ff_variations_tau_es_tt_mcl = ff_variations_tau_es_tt_mcl