import inspect
import logging
from itertools import product
from typing import Any, Callable

from config.logging_setup_configs import setup_logging
from config.shapes.process_selection import _get_stxs_bin_or_range
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

logger = setup_logging(logger=logging.getLogger(__name__))

FF_OPTIONS = {
    "fake_factor": {
        "lt": "fake_factor_2",
        "tt_1": "fake_factor_1",
        "tt_2": "fake_factor_2",
    },
    "fake_factor_with_bias_corr": {
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
    "raw_qcd_fake_factor_with_bias_corr": {
        "lt": "(raw_qcd_fake_factor_2 * qcd_correction_wo_DR_SR_2)",
    },
    "raw_qcd_fake_factor_with_DR_SR_corr": {
        "lt": "(raw_qcd_fake_factor_2 * qcd_DR_SR_correction_2)",
    },
    "raw_qcd_fake_factor_with_DR_SR_and_bias_corr": {
        "lt": "(raw_qcd_fake_factor_2 * qcd_correction_wo_DR_SR_2 * qcd_DR_SR_correction_2)",
    },
    # --------------------------------------------------------------------------------------
    "raw_wjets_fake_factor_with_fraction": {
        "lt": "(raw_wjets_fake_factor_2 * wjets_fake_factor_fraction_2)",
    },
    "raw_wjets_fake_factor": {
        "lt": "raw_wjets_fake_factor_2",
    },
    "raw_wjets_fake_factor_with_bias_corr": {
        "lt": "(raw_wjets_fake_factor_2 * wjets_correction_wo_DR_SR_2)",
    },
    "raw_wjets_fake_factor_with_DR_SR_corr": {
        "lt": "(raw_wjets_fake_factor_2 * wjets_DR_SR_correction_2)",
    },
    "raw_wjets_fake_factor_with_DR_SR_and_bias_corr": {
        "lt": "(raw_wjets_fake_factor_2 * wjets_correction_wo_DR_SR_2 * wjets_DR_SR_correction_2)",
    },
    # --------------------------------------------------------------------------------------
    "raw_ttbar_fake_factor_with_fraction": {
        "lt": "(raw_ttbar_fake_factor_2 * ttbar_fake_factor_fraction_2)",
    },
    "raw_ttbar_fake_factor": {
        "lt": "raw_ttbar_fake_factor_2",
    },
    "raw_ttbar_fake_factor_with_bias_corr": {
        "lt": "(raw_ttbar_fake_factor_2 * ttbar_correction_wo_DR_SR_2)",
    },
    "raw_ttbar_fake_factor_with_DR_SR_corr": {
        "lt": "(raw_ttbar_fake_factor_2 * 1.0)",
    },
    "raw_ttbar_fake_factor_with_DR_SR_and_bias_corr": {
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
        Weight(
            f"""(
                (0.5) * (
                    ({RuntimeVariables.FF_name_tt_1} * (id_tau_vsJet_Tight_1 < 0.5)) +
                    ({RuntimeVariables.FF_name_tt_2} * (id_tau_vsJet_Tight_2 < 0.5))
                )
            )""",
            "fake_factor",
        ),
    )
)

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

# Jet energy scale split by sources.
jet_es_hem = [
    ReplaceVariable("CMS_scale_j_HEMIssue_EraUp", "jesUncHEMIssueUp"),
    ReplaceVariable("CMS_scale_j_HEMIssue_EraDown", "jesUncHEMIssueDown"),
]
jet_es = [
    ReplaceVariable("CMS_scale_j_TotalUp", "jesUncTotalUp"),
    ReplaceVariable("CMS_scale_j_TotalDown", "jesUncTotalDown"),
    # ---
    ReplaceVariable("CMS_scale_j_AbsoluteUp", "jesUncAbsoluteUp"),
    ReplaceVariable("CMS_scale_j_AbsoluteDown", "jesUncAbsoluteDown"),
    ReplaceVariable("CMS_scale_j_Absolute_EraUp", "jesUncAbsoluteYearUp"),
    ReplaceVariable("CMS_scale_j_Absolute_EraDown", "jesUncAbsoluteYearDown"),
    # ---
    ReplaceVariable("CMS_scale_j_FlavorQCDUp", "jesUncFlavorQCDUp"),
    ReplaceVariable("CMS_scale_j_FlavorQCDDown", "jesUncFlavorQCDDown"),
    # ---
    ReplaceVariable("CMS_scale_j_BBEC1Up", "jesUncBBEC1Up"),
    ReplaceVariable("CMS_scale_j_BBEC1Down", "jesUncBBEC1Down"),
    ReplaceVariable("CMS_scale_j_BBEC1_EraUp", "jesUncBBEC1YearUp"),
    ReplaceVariable("CMS_scale_j_BBEC1_EraDown", "jesUncBBEC1YearDown"),
    # ---
    ReplaceVariable("CMS_scale_j_HFUp", "jesUncHFUp"),
    ReplaceVariable("CMS_scale_j_HFDown", "jesUncHFDown"),
    ReplaceVariable("CMS_scale_j_HF_EraUp", "jesUncHFYearUp"),
    ReplaceVariable("CMS_scale_j_HF_EraDown", "jesUncHFYearDown"),
    # ---
    ReplaceVariable("CMS_scale_j_EC2Up", "jesUncEC2Up"),
    ReplaceVariable("CMS_scale_j_EC2Down", "jesUncEC2Down"),
    ReplaceVariable("CMS_scale_j_EC2_EraUp", "jesUncEC2YearUp"),
    ReplaceVariable("CMS_scale_j_EC2_EraDown", "jesUncEC2YearDown"),
    # ---
    ReplaceVariable("CMS_scale_j_RelativeBalUp", "jesUncRelativeBalUp"),
    ReplaceVariable("CMS_scale_j_RelativeBalDown", "jesUncRelativeBalDown"),
    # ---
    ReplaceVariable("CMS_scale_j_RelativeSample_EraUp", "jesUncRelativeSampleYearUp"),
    ReplaceVariable("CMS_scale_j_RelativeSample_EraDown", "jesUncRelativeSampleYearDown"),
    # ---
    ReplaceVariable("CMS_res_j_EraUp", "jerUncUp"),
    ReplaceVariable("CMS_res_j_EraDown", "jerUncDown"),
]

# LHE/PS  variations
LHE_scale_norm_muR = [
    AddWeight("LHE_scale_muR_normUp", Weight("(lhe_scale_weight__LHEScaleMuRWeightUp)", "muR2p0_muF1p0_weight")),
    AddWeight("LHE_scale_muR_normDown", Weight("(lhe_scale_weight__LHEScaleMuRWeightDown)", "muR0p5_muF1p0_weight"))
]
LHE_scale_norm_muF = [
    AddWeight("LHE_scale_muF_normUp", Weight("(lhe_scale_weight__LHEScaleMuFWeightUp)", "muR1p0_muF2p0_weight")),
    AddWeight("LHE_scale_muF_normDown", Weight("(lhe_scale_weight__LHEScaleMuFWeightDown)", "muR1p0_muF0p5_weight"))
]
PS_scale_norm_Fsr = [
    AddWeight("PS_scale_Fsr_normUp", Weight('(ps_weight__FsrWeightUp)', "FsR2p0_weight")),
    AddWeight("PS_scale_Fsr_normDown", Weight('(ps_weight__FsrWeightDown)', "FsR0p5_weight")),
]
LHE_pdf = [
    AddWeight("LHE_pdfUp", Weight("(lhe_pdf_weight__PdfWeightUp)", "lhe_pdf_up_weight")),
    AddWeight("LHE_pdfDown", Weight("(lhe_pdf_weight__PdfWeightDown)", "lhe_pdf_down_weight")),
]
LHE_alphaS = [
    AddWeight("LHE_alphaSUp", Weight("(lhe_alphaS_weight__AlphaSWeightUp)", "lhe_alphaS_up_weight")),
    AddWeight("LHE_alphaSDown", Weight("(lhe_alphaS_weight__AlphaSWeightDown)", "lhe_alphaS_down_weight")),
]

# MET variations.
met_unclustered = [
    ReplaceVariable("CMS_scale_met_unclustered_EraUp", "metUnclusteredEnUp"),
    ReplaceVariable("CMS_scale_met_unclustered_EraDown", "metUnclusteredEnDown"),
]

# Recoil correction uncertainties
recoil_resolution = [
    ReplaceVariable("CMS_htt_boson_res_met_EraUp", "metRecoilResolutionUp"),
    ReplaceVariable("CMS_htt_boson_res_met_EraDown", "metRecoilResolutionDown"),
]
recoil_response = [
    ReplaceVariable("CMS_htt_boson_scale_met_EraUp", "metRecoilResponseUp"),
    ReplaceVariable("CMS_htt_boson_scale_met_EraDown", "metRecoilResponseDown"),
]

# B-tagging uncertainties.
btagging = [
    ReplaceVariable("CMS_btag_b_HFUp", "btagUncHFUp"),
    ReplaceVariable("CMS_btag_b_HFDown", "btagUncHFDown"),
    # ---
    ReplaceVariable("CMS_btag_b_HFstats1_EraUp", "btagUncHFstats1Up"),
    ReplaceVariable("CMS_btag_b_HFstats1_EraDown", "btagUncHFstats1Down"),
    # ---
    ReplaceVariable("CMS_btag_b_HFstats2_EraUp", "btagUncHFstats2Up"),
    ReplaceVariable("CMS_btag_b_HFstats2_EraDown", "btagUncHFstats2Down"),
    # ---
    ReplaceVariable("CMS_btag_j_LFUp", "btagUncLFUp"),
    ReplaceVariable("CMS_btag_j_LFDown", "btagUncLFDown"),
    # ---
    ReplaceVariable("CMS_btag_j_LFstats1_EraUp", "btagUncLFstats1Up"),
    ReplaceVariable("CMS_btag_j_LFstats1_EraDown", "btagUncLFstats1Down"),
    # ---
    ReplaceVariable("CMS_btag_j_LFstats2_EraUp", "btagUncLFstats2Up"),
    ReplaceVariable("CMS_btag_j_LFstats2_EraDown", "btagUncLFstats2Down"),
    # ---
    ReplaceVariable("CMS_btag_c_CFerr1Up", "btagUncCFerr1Up"),
    ReplaceVariable("CMS_btag_c_CFerr1Down", "btagUncCFerr1Down"),
    # ---
    ReplaceVariable("CMS_btag_c_CFerr2Up", "btagUncCFerr2Up"),
    ReplaceVariable("CMS_btag_c_CFerr2Down", "btagUncCFerr2Down"),
]

# Eta binned uncertainty
ele_fake_es_1prong = [
    ReplaceVariable("CMS_ZLShape_et_1prong_barrel_EraUp", "tauEleFakeEs1prongBarrelUp"),
    ReplaceVariable("CMS_ZLShape_et_1prong_barrel_EraDown", "tauEleFakeEs1prongBarrelDown"),
    ReplaceVariable("CMS_ZLShape_et_1prong_endcap_EraUp", "tauEleFakeEs1prongEndcapUp"),
    ReplaceVariable("CMS_ZLShape_et_1prong_endcap_EraDown", "tauEleFakeEs1prongEndcapDown"),
]
ele_fake_es_1prong1pizero = [
    ReplaceVariable("CMS_ZLShape_et_1prong1pizero_barrel_EraUp", "tauEleFakeEs1prong1pizeroBarrelUp"),
    ReplaceVariable("CMS_ZLShape_et_1prong1pizero_barrel_EraDown", "tauEleFakeEs1prong1pizeroBarrelDown"),
    ReplaceVariable("CMS_ZLShape_et_1prong1pizero_endcap_EraUp", "tauEleFakeEs1prong1pizeroEndcapUp"),
    ReplaceVariable("CMS_ZLShape_et_1prong1pizero_endcap_EraDown", "tauEleFakeEs1prong1pizeroEndcapDown"),
]
ele_fake_es = ele_fake_es_1prong + ele_fake_es_1prong1pizero

# TODO add split by decay mode?
# Mu Fake uncertainties
mu_fake_es_inc = [
    ReplaceVariable("CMS_ZLShape_mt_EraUp", "tauMuFakeEsUp"),
    ReplaceVariable("CMS_ZLShape_mt_EraDown", "tauMuFakeEsDown"),
]

# TODO add high pt tau ID efficiency
# Efficiency corrections.
# Tau ID efficiency.
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
    ReplaceVariable("CMS_eff_t_emb_40-Inf_EraUp", "vsJetTau40toInfUp"),
    ReplaceVariable("CMS_eff_t_emb_40-Inf_EraDown", "vsJetTau40toInfDown"),
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
    ReplaceVariable("CMS_eff_t_emb_dm0_EraUp", "vsJetTauDM0Up"),
    ReplaceVariable("CMS_eff_t_emb_dm0_EraDown", "vsJetTauDM0Down"),
    ReplaceVariable("CMS_eff_t_emb_dm1_EraUp", "vsJetTauDM1Up"),
    ReplaceVariable("CMS_eff_t_emb_dm1_EraDown", "vsJetTauDM1Down"),
    ReplaceVariable("CMS_eff_t_emb_dm10_EraUp", "vsJetTauDM10Up"),
    ReplaceVariable("CMS_eff_t_emb_dm10_EraDown", "vsJetTauDM10Down"),
    ReplaceVariable("CMS_eff_t_emb_dm11_EraUp", "vsJetTauDM11Up"),
    ReplaceVariable("CMS_eff_t_emb_dm11_EraDown", "vsJetTauDM11Down"),
]

# Jet to tau fake rate.
jet_to_tau_fake = [
    AddWeight(
        "CMS_htt_fake_j_EraUp",
        Weight("max(1.0-pt_2*0.002, 0.6)", "jetToTauFake_weight"),
    ),
    AddWeight(
        "CMS_htt_fake_j_EraDown",
        Weight("min(1.0+pt_2*0.002, 1.4)", "jetToTauFake_weight"),
    ),
]

# vsEle ID
zll_et_fake_rate = [
    ReplaceVariable("CMS_fake_e_BA_EraUp", "vsEleBarrelUp"),
    ReplaceVariable("CMS_fake_e_BA_EraDown", "vsEleBarrelDown"),
    ReplaceVariable("CMS_fake_e_EC_EraUp", "vsEleEndcapUp"),
    ReplaceVariable("CMS_fake_e_EC_EraDown", "vsEleEndcapDown"),
]

# vsMu ID
zll_mt_fake_rate_up = [
    ReplaceVariable(f"CMS_fake_m_WH{region}_EraUp", f"vsMuWheel{region}Up")
    for region in ["1", "2", "3", "4", "5"]
]
zll_mt_fake_rate_down = [
    ReplaceVariable(f"CMS_fake_m_WH{region}_EraDown", f"vsMuWheel{region}Down")
    for region in ["1", "2", "3", "4", "5"]
]
zll_mt_fake_rate = zll_mt_fake_rate_up + zll_mt_fake_rate_down

# # Trigger efficiency uncertainties.
# mt
trigger_eff_mt = [
    ReplaceVariable("CMS_eff_trigger_mt_EraUp", "singleMuonTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_mt_EraDown", "singleMuonTriggerSFDown"),
]
trigger_eff_mt_emb = [
    ReplaceVariable("CMS_eff_trigger_emb_mt_EraUp", "singleMuonTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_emb_mt_EraDown", "singleMuonTriggerSFDown"),
]

# et
trigger_eff_et = [
    ReplaceVariable("CMS_eff_trigger_et_EraUp", "singleElectronTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_et_EraDown", "singleElectronTriggerSFDown"),
]
trigger_eff_et_emb = [
    ReplaceVariable("CMS_eff_trigger_emb_et_EraUp", "singleElectronTriggerSFUp"),
    ReplaceVariable("CMS_eff_trigger_emb_et_EraDown", "singleElectronTriggerSFDown"),
]

# Embedding specific variations.
# TODO Embedding electron scale
emb_e_es = [
    ReplaceVariable("CMS_scale_e_barrel_embUp", "eleEsBarrelUp"),
    ReplaceVariable("CMS_scale_e_barrel_embDown", "eleEsBarrelDown"),
    ReplaceVariable("CMS_scale_e_endcap_embUp", "eleEsEndcapUp"),
    ReplaceVariable("CMS_scale_e_endcap_embDown", "eleEsEndcapDown"),
]

# TODO add embeddedDecayModeWeight?

# Prefiring
prefiring = [
    ReplaceWeight(
        "CMS_prefiringUp",
        "prefireWeight",
        Weight("prefiring_wgt__prefiringUp", "prefireWeight"),
    ),
    ReplaceWeight(
        "CMS_prefiringDown",
        "prefireWeight",
        Weight("prefiring_wgt__prefiringDown", "prefireWeight"),
    ),
]

# Z pT reweighting
zpt = [
    SquareWeight("CMS_htt_dyShape_EraUp", "zPtReweightWeight"),
    RemoveWeight("CMS_htt_dyShape_EraDown", "zPtReweightWeight"),
]

# Top pT reweighting
top_pt = [
    SquareWeight("CMS_htt_ttbarShapeUp", "topPtReweightWeight"),
    RemoveWeight("CMS_htt_ttbarShapeDown", "topPtReweightWeight"),
]

# FF variations
# Variations on the jet backgrounds estimated with the fake factor method.
ff_variations_lt = [
    ReplaceCutAndAddWeight(
        f"anti_iso_CMS_{syst}{shift}_Channel_Era",
        "tau_iso",
        Cut("id_tau_vsJet_Tight_2<0.5&&id_tau_vsJet_VLoose_2>0.5", "tau_anti_iso"),
        Weight(f"{RuntimeVariables.FF_name_lt}__{syst}{shift}", "fake_factor"),
    )
    for shift in ["Up", "Down"]
    for syst in [
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
        # 'QCD_DR_SR_Corr',  # TODO: Add them when actually applying this correction!
        'Wjets_non_closure_m_vis_Corr',
        'Wjets_non_closure_mass_2_Corr',
        'Wjets_non_closure_deltaR_ditaupair_Corr',
        'Wjets_non_closure_iso_1_Corr',
        'Wjets_non_closure_tau_decaymode_2_Corr',
        # 'Wjets_DR_SR_Corr',  # TODO: Add them when actually applying this correction!
        'ttbar_non_closure_m_vis_Corr',
        'ttbar_non_closure_mass_2_Corr',
        'ttbar_non_closure_deltaR_ditaupair_Corr',
        'ttbar_non_closure_iso_1_Corr',
        'ttbar_non_closure_tau_decaymode_2_Corr'
    ]
]

# TODO: Check if variations are applied

# Propagation of tau ES systematics on jetFakes process
# lt channel
ff_variations_tau_es_lt = LazyVariable(  # requieres LazyVariation since Used.FF_name_lt may be defined later
    lambda: [
        ReplaceVariableReplaceCutAndAddWeight(
            name,
            variation,
            "tau_iso",
            Cut(f"id_tau_vsJet_Tight_2__{variation} < 0.5 && id_tau_vsJet_VLoose_2__{variation} > 0.5", "tau_anti_iso"),
            Weight(f"{RuntimeVariables.FF_name_lt}__{variation}", "fake_factor"),
        )
        for shift in ("Up", "Down")
        for name, variation in [
            (f"anti_iso_CMS_scale_t_1prong_Era{shift}", f"tauEs1prong0pizero{shift}"),
            (f"anti_iso_CMS_scale_t_1prong1pizero_Era{shift}", f"tauEs1prong1pizero{shift}"),
            (f"anti_iso_CMS_scale_t_3prong_Era{shift}", f"tauEs3prong0pizero{shift}"),
            (f"anti_iso_CMS_scale_t_3prong1pizero_Era{shift}", f"tauEs3prong1pizero{shift}"),
        ]
    ]
)

# lt for emb only for correlation
ff_variations_tau_es_emb_lt = LazyVariable(  # requieres LazyVariation since Used.FF_name_lt may be defined later
    lambda: [
        ReplaceVariableReplaceCutAndAddWeight(
            name,
            variation,
            "tau_iso",
            Cut(f"id_tau_vsJet_Tight_2__{variation} < 0.5 && id_tau_vsJet_VLoose_2__{variation} > 0.5", "tau_anti_iso"),
            Weight(f"{RuntimeVariables.FF_name_lt}__{variation}", "fake_factor"),
        )
        for shift in ("Up", "Down")
        for name, variation in [
            (f"anti_iso_CMS_scale_t_emb_1prong_Era{shift}", f"tauEs1prong0pizero{shift}"),
            (f"anti_iso_CMS_scale_t_emb_1prong1pizero_Era{shift}", f"tauEs1prong1pizero{shift}"),
            (f"anti_iso_CMS_scale_t_emb_3prong_Era{shift}", f"tauEs3prong0pizero{shift}"),
            (f"anti_iso_CMS_scale_t_emb_3prong1pizero_Era{shift}", f"tauEs3prong1pizero{shift}"),
        ]
    ]
)

# # tt channel
ff_variations_tau_es_tt = LazyVariable(  # requieres LazyVariation since Used.FF_name_tt may be defined later
    lambda: [
        ReplaceVariableReplaceCutAndAddWeight(
            name,
            variation,
            "tau_iso",
            Cut(
                f"""(
                        (
                            (id_tau_vsJet_Tight_1__{variation} < 0.5) &&
                            (id_tau_vsJet_Tight_2__{variation} > 0.5) &&
                            (id_tau_vsJet_VLoose_1__{variation} > 0.5)
                        ) ||
                        (
                            (id_tau_vsJet_Tight_1__{variation} > 0.5) &&
                            (id_tau_vsJet_Tight_2__{variation} < 0.5) &&
                            (id_tau_vsJet_VLoose_2__{variation} > 0.5)
                        )
                    )""",
                "tau_anti_iso"
            ),
            Weight(
                f"""(
                    (0.5) * (
                        ({RuntimeVariables.FF_name_tt_1}__{variation} * (id_tau_vsJet_Tight_1__{variation} < 0.5)) +
                        ({RuntimeVariables.FF_name_tt_2}__{variation} * (id_tau_vsJet_Tight_2__{variation} < 0.5))
                    )
                )""",
                "fake_factor",
            ),
        )
        for shift in ("Up", "Down")
        for name, variation in [
            (f"anti_iso_CMS_scale_t_1prong_Era{shift}", f"tauEs1prong0pizero{shift}"),
            (f"anti_iso_CMS_scale_t_1prong1pizero_Era{shift}", f"tauEs1prong1pizero{shift}"),
            (f"anti_iso_CMS_scale_t_3prong_Era{shift}", f"tauEs3prong0pizero{shift}"),
            (f"anti_iso_CMS_scale_t_3prong1pizero_Era{shift}", f"tauEs3prong1pizero{shift}"),
        ]
    ]
)

# tt channel emb process
ff_variations_tau_es_tt = LazyVariable(  # requieres LazyVariation since Used.FF_name_tt may be defined later
    lambda: [
        ReplaceVariableReplaceCutAndAddWeight(
            name,
            variation,
            "tau_iso",
            Cut(
                f"""(
                        (
                            (id_tau_vsJet_Tight_1__{variation} < 0.5) &&
                            (id_tau_vsJet_Tight_2__{variation} > 0.5) &&
                            (id_tau_vsJet_VLoose_1__{variation} > 0.5)
                        ) ||
                        (
                            (id_tau_vsJet_Tight_1__{variation} > 0.5) &&
                            (id_tau_vsJet_Tight_2__{variation} < 0.5) &&
                            (id_tau_vsJet_VLoose_2__{variation} > 0.5)
                        )
                    )""",
                "tau_anti_iso"
            ),
            Weight(
                f"""(
                    (0.5) * (
                        ({RuntimeVariables.FF_name_tt_1}__{variation} * (id_tau_vsJet_Tight_1__{variation} < 0.5)) +
                        ({RuntimeVariables.FF_name_tt_2}__{variation} * (id_tau_vsJet_Tight_2__{variation} < 0.5))
                    )
                )""",
                "fake_factor",
            ),
        )
        for shift in ("Up", "Down")
        for name, variation in [
            (f"anti_iso_CMS_scale_t_emb_1prong_Era{shift}", f"tauEs1prong0pizero{shift}"),
            (f"anti_iso_CMS_scale_t_emb_1prong1pizero_Era{shift}", f"tauEs1prong1pizero{shift}"),
            (f"anti_iso_CMS_scale_t_emb_3prong_Era{shift}", f"tauEs3prong0pizero{shift}"),
            (f"anti_iso_CMS_scale_t_emb_3prong1pizero_Era{shift}", f"tauEs3prong1pizero{shift}"),
        ]
    ]
)

# qcd variations
qcd_variations_em = [  # TODO: Check if the name is correct and if it is still applicable, redo otherwise
    ReplaceCutAndAddWeight(name, "os", Cut("q_1*q_2>0", "ss"), Weight(weight, "qcd_weight"))
    for shift in ("Up", "Down")
    for name, weight in [
        (f"same_sign_CMS_htt_qcd_0jet_rate_Era{shift}", f"em_qcd_osss_stat_0jet_rate{shift.lower()}_Weight"),
        (f"same_sign_CMS_htt_qcd_0jet_shape_Era{shift}", f"em_qcd_osss_stat_0jet_shape{shift.lower()}_Weight"),
        (f"same_sign_CMS_htt_qcd_0jet_shape2_Era{shift}", f"em_qcd_osss_stat_0jet_shape2{shift.lower()}_Weight"),
        (f"same_sign_CMS_htt_qcd_1jet_rate_Era{shift}", f"em_qcd_osss_stat_1jet_rate{shift.lower()}_Weight"),
        (f"same_sign_CMS_htt_qcd_1jet_shape_Era{shift}", f"em_qcd_osss_stat_1jet_shape{shift.lower()}_Weight"),
        (f"same_sign_CMS_htt_qcd_1jet_shape2_Era{shift}", f"em_qcd_osss_stat_1jet_shape2{shift.lower()}_Weight"),
        (f"same_sign_CMS_htt_qcd_2jet_rate_Era{shift}", f"em_qcd_osss_stat_2jet_rate{shift.lower()}_Weight"),
        (f"same_sign_CMS_htt_qcd_2jet_shape_Era{shift}", f"em_qcd_osss_stat_2jet_shape{shift.lower()}_Weight"),
        (f"same_sign_CMS_htt_qcd_2jet_shape2_Era{shift}", f"em_qcd_osss_stat_2jet_shape2{shift.lower()}_Weight"),
        (f"same_sign_CMS_htt_qcd_iso_Era{shift}", f"em_qcd_extrap_{shift.lower()}_Weight"),
        (f"{shift}", f"{shift.lower()}_Weight"),
    ]
]

# Signal uncertainties
ggH_htxs = {
    "ggH125": _get_stxs_bin_or_range(100, 117),
    "ggH_GG2H_FWDH125": _get_stxs_bin_or_range(100),
    "ggH_GG2H_PTH_200_300125": _get_stxs_bin_or_range(101),
    "ggH_GG2H_PTH_300_450125": _get_stxs_bin_or_range(102),
    "ggH_GG2H_PTH_450_650125": _get_stxs_bin_or_range(103),
    "ggH_GG2H_PTH_GT650125": _get_stxs_bin_or_range(104),
    "ggH_GG2H_0J_PTH_0_10125": _get_stxs_bin_or_range(105),
    "ggH_GG2H_0J_PTH_GT10125": _get_stxs_bin_or_range(106),
    "ggH_GG2H_1J_PTH_0_60125": _get_stxs_bin_or_range(107),
    "ggH_GG2H_1J_PTH_60_120125": _get_stxs_bin_or_range(108),
    "ggH_GG2H_1J_PTH_120_200125": _get_stxs_bin_or_range(109),
    "ggH_GG2H_GE2J_MJJ_0_350_PTH_0_60125": _get_stxs_bin_or_range(110),
    "ggH_GG2H_GE2J_MJJ_0_350_PTH_60_120125": _get_stxs_bin_or_range(111),
    "ggH_GG2H_GE2J_MJJ_0_350_PTH_120_200125": _get_stxs_bin_or_range(112),
    "ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125": _get_stxs_bin_or_range(113),
    "ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125": _get_stxs_bin_or_range(114),
    "ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125": _get_stxs_bin_or_range(115),
    "ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125": _get_stxs_bin_or_range(116),
}
qqH_htxs = {
    "qqH125": _get_stxs_bin_or_range(200, 210),
    "qqH_QQ2HQQ_FWDH125": _get_stxs_bin_or_range(200),
    "qqH_QQ2HQQ_0J125": _get_stxs_bin_or_range(201),
    "qqH_QQ2HQQ_1J125": _get_stxs_bin_or_range(202),
    "qqH_QQ2HQQ_GE2J_MJJ_0_60125": _get_stxs_bin_or_range(203),
    "qqH_QQ2HQQ_GE2J_MJJ_60_120125": _get_stxs_bin_or_range(204),
    "qqH_QQ2HQQ_GE2J_MJJ_120_350125": _get_stxs_bin_or_range(205),
    "qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200125": _get_stxs_bin_or_range(206),
    "qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125": _get_stxs_bin_or_range(207),
    "qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125": _get_stxs_bin_or_range(208),
    "qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125": _get_stxs_bin_or_range(209),
    "qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125": _get_stxs_bin_or_range(210),
}
WH_htxs = {
    "WH_lep125": _get_stxs_bin_or_range(300, 305),
    "WH_lep_QQ2HLNU_FWDH125": _get_stxs_bin_or_range(300),
    "WH_lep_QQ2HLNU_PTV_0_75125": _get_stxs_bin_or_range(301),
    "WH_lep_QQ2HLNU_PTV_75_150125": _get_stxs_bin_or_range(302),
    "WH_lep_QQ2HLNU_PTV_150_250_0J125": _get_stxs_bin_or_range(303),
    "WH_lep_QQ2HLNU_PTV_150_250_GE1J125": _get_stxs_bin_or_range(304),
    "WH_lep_QQ2HLNU_PTV_GT250125": _get_stxs_bin_or_range(305),
}
ZH_htxs = {
    "ZH_lep125": _get_stxs_bin_or_range(400, 405),
    "ZH_lep_QQ2HLL_FWDH125": _get_stxs_bin_or_range(400),
    "ZH_lep_QQ2HLL_PTV_0_75125": _get_stxs_bin_or_range(401),
    "ZH_lep_QQ2HLL_PTV_75_150125": _get_stxs_bin_or_range(402),
    "ZH_lep_QQ2HLL_PTV_150_250_0J125": _get_stxs_bin_or_range(403),
    "ZH_lep_QQ2HLL_PTV_150_250_GE1J125": _get_stxs_bin_or_range(404),
    "ZH_lep_QQ2HLL_PTV_GT250125": _get_stxs_bin_or_range(405),
}
ggZH_htxs = {
    "ggZH_lep125": _get_stxs_bin_or_range(500, 505),
    "ggZH_lep_GG2HLL_FWDH125": _get_stxs_bin_or_range(500),
    "ggZH_lep_GG2HLL_PTV_0_75125": _get_stxs_bin_or_range(501),
    "ggZH_lep_GG2HLL_PTV_75_150125": _get_stxs_bin_or_range(502),
    "ggZH_lep_GG2HLL_PTV_150_250_0J125": _get_stxs_bin_or_range(503),
    "ggZH_lep_GG2HLL_PTV_150_250_GE1J125": _get_stxs_bin_or_range(504),
    "ggZH_lep_GG2HLL_PTV_GT250125": _get_stxs_bin_or_range(505),
}

scheme_ggH = {
    "ggH_scale_0jet": [
        "ggH_GG2H_0J_PTH_0_10125",
        "ggH_GG2H_0J_PTH_GT10125",
    ],
    "ggH_scale_1jet_lowpt": [
        "ggH_GG2H_1J_PTH_0_60125",
        "ggH_GG2H_1J_PTH_60_120125",
        "ggH_GG2H_1J_PTH_120_200125",
    ],
    "ggH_scale_2jet_lowpt": [
        "ggH_GG2H_GE2J_MJJ_0_350_PTH_0_60125",
        "ggH_GG2H_GE2J_MJJ_0_350_PTH_60_120125",
        "ggH_GG2H_GE2J_MJJ_0_350_PTH_120_200125",
    ],
    "ggH_scale_highpt": [
        "ggH_GG2H_PTH_200_300125",
        "ggH_GG2H_PTH_300_450125",
    ],
    "ggH_scale_very_highpt": [
        "ggH_GG2H_PTH_450_650125",
        "ggH_GG2H_PTH_GT650125",
    ],
    "ggH_scale_vbf": [
        "ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125",
        "ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125",
        "ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125",
        "ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125",
    ],
}
scheme_qqH = {
    "vbf_scale_0jet": ["qqH_QQ2HQQ_0J125"],
    "vbf_scale_1jet": ["qqH_QQ2HQQ_1J125"],
    "vbf_scale_lowmjj": [
        "qqH_QQ2HQQ_GE2J_MJJ_0_60125",
        "qqH_QQ2HQQ_GE2J_MJJ_60_120125",
        "qqH_QQ2HQQ_GE2J_MJJ_120_350125",
    ],
    "vbf_scale_highmjj_lowpt": [
        "qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125",
        "qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125",
        "qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125",
        "qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125",
    ],
    "vbf_scale_highmjj_highpt": ["qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200125"],
}

ggh_acceptance = []
for unc in [
    "THU_ggH_Mig01",
    "THU_ggH_Mig12",
    "THU_ggH_Mu",
    "THU_ggH_PT120",
    "THU_ggH_PT60",
    "THU_ggH_Res",
    "THU_ggH_VBF2j",
    "THU_ggH_VBF3j",
    "THU_ggH_qmtop",
]:
    ggh_acceptance.append(AddWeight(f"{unc}Up", Weight(f"({unc})", f"{unc}_weight")))
    ggh_acceptance.append(AddWeight(f"{unc}Down", Weight(f"(2.0-{unc})", f"{unc}_weight")))

# ---

qqh_acceptance = []
for unc in [
    "THU_qqH_25",
    "THU_qqH_JET01",
    "THU_qqH_Mjj1000",
    "THU_qqH_Mjj120",
    "THU_qqH_Mjj1500",
    "THU_qqH_Mjj350",
    "THU_qqH_Mjj60",
    "THU_qqH_Mjj700",
    "THU_qqH_PTH200",
    "THU_qqH_TOT",
]:
    qqh_acceptance.append(AddWeight(f"{unc}Up", Weight(f"({unc})", f"{unc}_weight")))
    qqh_acceptance.append(AddWeight(f"{unc}Down", Weight(f"(2.0-{unc})", f"{unc}_weight")))

ggh_muRmuF_acceptance, qqh_muRmuF_acceptance = [], []
for _container, _scheme, _cuts in [
    (ggh_muRmuF_acceptance, scheme_ggH, ggH_htxs),
    (qqh_muRmuF_acceptance, scheme_qqH, qqH_htxs),
]:
    for shift, scale_type in product(("Up", "Down"), ("muR", "muF")):
        for scheme, scheme_collection in _scheme.items():
            _container.append(
                AddWeight(
                    f"{scheme}_{scale_type}_{shift}",
                    Weight(
                        " * ".join(
                            f"""(
                                1.0 + (
                                    (
                                        lhe_scale_weight__LHEScale{scale_type}Weight{shift} - 1.0
                                    ) * ({_cuts[scheme_parts]})
                                )
                            )"""
                            for scheme_parts in scheme_collection
                        ),
                        f"stxs_acceptance_uncertainty_{scale_type}_variation_{scheme}_{shift.lower()}",
                    )
                )
            )

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
    LHE_scale_norm_muR = LHE_scale_norm_muR
    LHE_scale_norm_muF = LHE_scale_norm_muF
    PS_scale_norm_Fsr = PS_scale_norm_Fsr
    LHE_pdf = LHE_pdf
    LHE_alphaS = LHE_alphaS


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
    # qcd_variations_em = qcd_variations_em
    # ff_variations_tau_es_tt = ff_variations_tau_es_tt

# ------------------------------------------------------------------------------------------

# TODO: TBD, needed or not, collection:

# # Electron energy scale
# ele_es = [  # TODO: Check if needed or is replaced
#     ReplaceVariable("CMS_scale_eUp", "eleScaleUp"),
#     ReplaceVariable("CMS_scale_eDown", "eleScaleDown"),
# ]
# ele_res = [  # TODO: Check if needed or is replaced
#     ReplaceVariable("CMS_res_eUp", "eleSmearUp"),
#     ReplaceVariable("CMS_res_eDown", "eleSmearDown"),
# ]
# # fake met scaling in embedded samples
# emb_met_scale = [  # TODO: Check if needed or is replaced
#         ReplaceVariable("scale_embed_metUp", "emb_scale_metUp"),
#         ReplaceVariable("scale_embed_metDown", "emb_scale_metDown")
#         ]
# # Energy scales of leptons faking tau leptons.
# # Inclusive in eta
# ele_fake_es = [    # TODO: Check if needed or is replaced, do we need the ones without barrel / endcap plit ?
#         ReplaceVariable("CMS_ZLShape_et_1prong_EraUp", "tauEleFakeEsOneProngCommonUp"),
#         ReplaceVariable("CMS_ZLShape_et_1prong_EraDown", "tauEleFakeEsOneProngCommonDown"),
#         ReplaceVariable("CMS_ZLShape_et_1prong1pizero_EraUp", "tauEleFakeEsOneProngPiZerosCommonUp"),
#         ReplaceVariable("CMS_ZLShape_et_1prong1pizero_EraDown", "tauEleFakeEsOneProngPiZerosCommonDown"),
#         ]
# mu_fake_es_1prong = [  # TODO: Check if needed or is replaced, add split by decay mode ?
#         ReplaceVariable("CMS_ZLShape_mt_1prong_EraUp", "tauMuFakeEsOneProngUp"),
#         ReplaceVariable("CMS_ZLShape_mt_1prong_EraDown", "tauMuFakeEsOneProngDown")
#         ]
# mu_fake_es_1prong1pizero = [  # TODO: Check if needed or is replaced, add split by decay mode ?
#         ReplaceVariable("CMS_ZLShape_mt_1prong1pizero_EraUp", "tauMuFakeEsOneProngPiZerosUp"),
#         ReplaceVariable("CMS_ZLShape_mt_1prong1pizero_EraDown", "tauMuFakeEsOneProngPiZerosDown")
#         ]
# # cross triggers
# trigger_eff_mt = [  # TODO: Check if needed or is replaced
#     *[
#         ReplaceWeight(
#             name,
#             "triggerweight",
#             Weight(weight, "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for name, weight in [
#             (f"CMS_eff_trigger_mt_Era{shift}", f"mtau_triggerweight_ic_singlelep_{shift.lower()}"),
#             (f"CMS_eff_xtrigger_l_mt_Era{shift}", f"mtau_triggerweight_ic_crosslep_{shift.lower()}"),
#             (f"CMS_eff_trigger_single_t_Era{shift}", f"mtau_triggerweight_ic_singletau_{shift.lower()}")
#         ]
#     ],
#     *[
#         ReplaceWeight(
#             f"CMS_eff_xtrigger_t_mt_dm{dm}_Era{shift}",
#             "triggerweight",
#             Weight(f"mtau_triggerweight_ic_dm{dm}_{shift.lower()}", "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for dm in [0, 1, 10, 11]
#     ],
# ]
# trigger_eff_mt_emb = [  # TODO: Check if needed or is replaced
#     *[
#         ReplaceWeight(
#             name,
#             "triggerweight",
#             Weight(weight, "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for name, weight in [
#             (f"CMS_eff_trigger_emb_mt_Era{shift}", f"mtau_triggerweight_ic_singlelep_{shift.lower()}"),
#             (f"CMS_eff_xtrigger_l_emb_mt_Era{shift}", f"mtau_triggerweight_ic_crosslep_{shift.lower()}"),
#             (f"CMS_eff_trigger_single_t_emb_Era{shift}", f"mtau_triggerweight_ic_singletau_{shift.lower()}")
#         ]
#     ],
#     *[
#         ReplaceWeight(
#             f"CMS_eff_xtrigger_t_emb_mt_dm{dm}_Era{shift}",
#             "triggerweight",
#             Weight(f"mtau_triggerweight_ic_dm{dm}_{shift.lower()}", "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for dm in [0, 1, 10, 11]
#     ]
# ]
# trigger_eff_et = [  # TODO: Check if needed or is replaced
#     *[
#         ReplaceWeight(
#             name,
#             "triggerweight",
#             Weight(weight, "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for name, weight in [
#             (f"CMS_eff_trigger_et_Era{shift}", f"etau_triggerweight_ic_singlelep_{shift.lower()}"),
#             (f"CMS_eff_xtrigger_l_et_Era{shift}", f"etau_triggerweight_ic_crosslep_{shift.lower()}"),
#             (f"CMS_eff_trigger_single_t_Era{shift}", f"etau_triggerweight_ic_singletau_{shift.lower()}")
#         ]
#     ],
#     *[
#         ReplaceWeight(
#             f"CMS_eff_xtrigger_t_et_dm{dm}_Era{shift}",
#             "triggerweight",
#             Weight(f"etau_triggerweight_ic_dm{dm}_{shift.lower()}", "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for dm in [0, 1, 10, 11]
#     ]
# ]
# trigger_eff_et_emb = [  # TODO: Check if needed or is replaced
#     *[
#         ReplaceWeight(
#             name,
#             "triggerweight",
#             Weight(weight, "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for name, weight in [
#             (f"CMS_eff_trigger_emb_et_Era{shift}", f"etau_triggerweight_ic_singlelep_{shift.lower()}"),
#             (f"CMS_eff_xtrigger_l_emb_et_Era{shift}", f"etau_triggerweight_ic_crosslep_{shift.lower()}"),
#             (f"CMS_eff_trigger_single_t_emb_Era{shift}", f"etau_triggerweight_ic_singletau_{shift.lower()}")
#         ]
#     ],
#     *[
#         ReplaceWeight(
#             f"CMS_eff_xtrigger_t_emb_et_dm{dm}_Era{shift}",
#             "triggerweight",
#             Weight(f"etau_triggerweight_ic_dm{dm}_{shift.lower()}", "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for dm in [0, 1, 10, 11]
#     ]
# ]
# tau_trigger_eff_tt = [  # TODO: Check if needed or is replaced
#     *[
#         ReplaceWeight(
#             name,
#             "triggerweight",
#             Weight(weight, "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for dm in [0, 1, 10, 11]
#         for name, weight in [
#             (f"CMS_eff_xtrigger_t_tt_dm{dm}_Era{shift}", f"tautau_triggerweight_ic_lowpt_dm{dm}_{shift.lower()}")
#             (f"CMS_eff_xtrigger_t_tt_dm{dm}_highpT_Era{shift}", f"tautau_triggerweight_ic_highpt_dm{dm}_{shift.lower()}")
#         ]
#     ],
#     *[
#         ReplaceWeight(
#             f"CMS_eff_trigger_single_t_Era{shift}",
#             "triggerweight",
#             Weight(f"tautau_triggerweight_ic_singletau_{shift.lower()}", "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#     ]
# ]
# tau_trigger_eff_tt_emb = [  # TODO: Check if needed or is replaced
#     *[
#         ReplaceWeight(
#             name,
#             "triggerweight",
#             Weight(weight, "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#         for dm in [0, 1, 10, 11]
#         for name, weight in [
#             (f"CMS_eff_xtrigger_t_emb_tt_dm{dm}_Era{shift}", f"tautau_triggerweight_ic_lowpt_dm{dm}_{shift.lower()}"),
#             (f"CMS_eff_xtrigger_t_emb_tt_dm{dm}_highpT_Era{shift}", f"tautau_triggerweight_ic_highpt_dm{dm}_{shift.lower()}")
#         ]
#     ],
#     *[
#         ReplaceWeight(
#             f"CMS_eff_trigger_single_t_emb_Era{shift}",
#             "triggerweight",
#             Weight(f"tautau_triggerweight_ic_singletau_{shift.lower()}", "triggerweight"),
#         )
#         for shift in ("Up", "Down")
#     ]
# ]
# # embedded lt eff by decay mode
# emb_decay_mode_eff_lt = [  # TODO: Check if needed or is replaced,  add embeddedDecayModeWeight, Needed or covered by something other?
#     ReplaceWeight(
#         name,
#         "decayMode_SF",
#         Weight(weight, "decayMode_SF"),
#     )
#     for shift in ("Up", "Down")
#     for name, weight in [
#         (f"CMS_3ProngEff_Era{shift}", f"(pt_2<100)*embeddedDecayModeWeight_eff{shift}_pi0Nom+(pt_2>=100)"),
#         (f"CMS_1ProngPi0Eff_Era{shift}", f"(pt_2<100)*embeddedDecayModeWeight_effNom_pi0{shift}+(pt_2>=100)"),
#     ]
# ]
# _emb_decay_mode_eff_tt = [  # TODO: Check if needed or is replaced,  add embeddedDecayModeWeight, Needed or covered by something other?
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
