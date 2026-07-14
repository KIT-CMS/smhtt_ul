import numpy as np

try:
    from ntuple_processor import Histogram
    from ntuple_processor.utils import Selection
    _ntuple_processor_available = True
except ImportError:
    _ntuple_processor_available = False


# Canonical per-channel DNN class definitions: name -> {index, is_signal}.
# This is the single source of truth used by produce_shapes.py (to build
# per-class control categories) and plot_shapes_control.py (to know which
# categories/indices exist and which ones should not have data drawn).
# need to add the split signal later on
DNN_CLASS_MAPPING = {
    "mt": {
        "ggh":       {"index": 0, "is_signal": True, "label": "ggH"},
        "vbf":       {"index": 1, "is_signal": True, "label": "VBF"},
        "dyjets_tt": {"index": 2, "is_signal": False, "label": "DY+Jets (#tau#tau)"},
        "dyjets_ll": {"index": 3, "is_signal": False, "label": "DY+Jets (ll)"},
        "jetFakes":  {"index": 4, "is_signal": False, "label": "Jet Fakes"},
        "ttbar":     {"index": 5, "is_signal": False, "label": "t#bar{t}"},
        "diboson":   {"index": 6, "is_signal": False, "label": "Diboson"},
    },
    "et": {
        "ggh":       {"index": 0, "is_signal": True, "label": "ggH"},
        "vbf":       {"index": 1, "is_signal": True, "label": "VBF"},
        "dyjets_tt": {"index": 2, "is_signal": False, "label": "DY+Jets (#tau#tau)"},
        "dyjets_ll": {"index": 3, "is_signal": False, "label": "DY+Jets (ll)"},
        "jetFakes":  {"index": 4, "is_signal": False, "label": "Jet Fakes"},
        "ttbar":     {"index": 5, "is_signal": False, "label": "t#bar{t}"},
        "diboson":   {"index": 6, "is_signal": False, "label": "Diboson"},
    },
    "tt": {
        "ggh":       {"index": 0, "is_signal": True, "label": "ggH"},
        "vbf":       {"index": 1, "is_signal": True, "label": "VBF"},
        "dyjets_tt": {"index": 2, "is_signal": False, "label": "DY+Jets (#tau#tau)"},
        "jetFakes":  {"index": 3, "is_signal": False, "label": "Jet Fakes"},
        "bkg_rest":  {"index": 4, "is_signal": False, "label": "Remaining backgrounds"},
    },
}


def get_dnn_class_mapping(channel: str) -> dict:
    """name -> {"index": int, "is_signal": bool} for the given channel."""
    if channel not in DNN_CLASS_MAPPING:
        raise NotImplementedError(f"DNN class mapping not defined for channel '{channel}'")
    return DNN_CLASS_MAPPING[channel]


def build_categorization(split_signal: bool = False) -> dict:
    if not _ntuple_processor_available:
        raise ImportError("ntuple_processor is required for build_categorization()")
    fine_binning = np.linspace(0.0, 1.0, 11)
    if split_signal:
        raise NotImplementedError("STXS fine splitting not implemented yet")

    categorization = {}
    for channel, mapping in DNN_CLASS_MAPPING.items():
        categorization[channel] = []
        for category, info in mapping.items():
            selection = (
                Selection(
                    name=category,
                    cuts=[(f"nn_predicted_class == {info['index']}", "category selection")],
                ),
                [Histogram(f"{channel}_score", "nn_predicted_max_value", fine_binning)],
            )
            categorization[channel].append(selection)
    return categorization


# Module-level dict for direct import (mirrors upstream style)
categorization = build_categorization() if _ntuple_processor_available else {}