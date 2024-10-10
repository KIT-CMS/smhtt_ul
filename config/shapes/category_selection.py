import numpy as np
from ntuple_processor import Histogram
from ntuple_processor.utils import Selection


fine_binning = np.linspace(0.0, 1.0, 11)
category_mapping = {
    "mt": {
        "YbbHtt_res": {
            "index": 0,
            "binning": fine_binning,
        },
        "YbbHtt_boost": {
            "index": 1,
            "binning": fine_binning,
        },
        "YttHbb_res": {
            "index": 2,
            "binning": fine_binning,
        },
        "YttHbb_boost": {
            "index": 3,
            "binning": fine_binning,
        },
        "genuine_tau": {
            "index": 4,
            "binning": fine_binning,
        },
        "tau_fakes": {
            "index": 5,
            "binning": fine_binning,
        },
        "ttbar": {
            "index": 6,
            "binning": fine_binning,
        },
        "misc": {
            "index": 7,
            "binning": fine_binning,
        },
    },
    "et": {
        "YbbHtt_res": {
            "index": 0,
            "binning": fine_binning,
        },
        "YbbHtt_boost": {
            "index": 1,
            "binning": fine_binning,
        },
        "YttHbb_res": {
            "index": 2,
            "binning": fine_binning,
        },
        "YttHbb_boost": {
            "index": 3,
            "binning": fine_binning,
        },
        "genuine_tau": {
            "index": 4,
            "binning": fine_binning,
        },
        "tau_fakes": {
            "index": 5,
            "binning": fine_binning,
        },
        "ttbar": {
            "index": 6,
            "binning": fine_binning,
        },
        "misc": {
            "index": 7,
            "binning": fine_binning,
        },
    },
    "tt": {
        "YbbHtt_res": {
            "index": 0,
            "binning": fine_binning,
        },
        "YbbHtt_boost": {
            "index": 1,
            "binning": fine_binning,
        },
        "YttHbb_res": {
            "index": 2,
            "binning": fine_binning,
        },
        "YttHbb_boost": {
            "index": 3,
            "binning": fine_binning,
        },
        "genuine_tau": {
            "index": 4,
            "binning": fine_binning,
        },
        "tau_fakes": {
            "index": 5,
            "binning": fine_binning,
        },
        "ttbar": {
            "index": 6,
            "binning": fine_binning,
        },
        "misc": {
            "index": 7,
            "binning": fine_binning,
        },
    }
}
boosted_category_mapping = {
    "mt": {
        "boosted_YbbHtt_res": {
            "index": 0,
            "binning": fine_binning,
        },
        "boosted_YbbHtt_boost": {
            "index": 1,
            "binning": fine_binning,
        },
        "boosted_YttHbb_res": {
            "index": 2,
            "binning": fine_binning,
        },
        "boosted_YttHbb_boost": {
            "index": 3,
            "binning": fine_binning,
        },
        "boosted_genuine_tau": {
            "index": 4,
            "binning": fine_binning,
        },
        "boosted_tau_fakes": {
            "index": 5,
            "binning": fine_binning,
        },
        "boosted_ttbar": {
            "index": 6,
            "binning": fine_binning,
        },
        "boosted_misc": {
            "index": 7,
            "binning": fine_binning,
        },
    },
    "et": {
        "boosted_YbbHtt_res": {
            "index": 0,
            "binning": fine_binning,
        },
        "boosted_YbbHtt_boost": {
            "index": 1,
            "binning": fine_binning,
        },
        "boosted_YttHbb_res": {
            "index": 2,
            "binning": fine_binning,
        },
        "boosted_YttHbb_boost": {
            "index": 3,
            "binning": fine_binning,
        },
        "boosted_genuine_tau": {
            "index": 4,
            "binning": fine_binning,
        },
        "boosted_tau_fakes": {
            "index": 5,
            "binning": fine_binning,
        },
        "boosted_ttbar": {
            "index": 6,
            "binning": fine_binning,
        },
        "boosted_misc": {
            "index": 7,
            "binning": fine_binning,
        },
    },
    "tt": {
        "boosted_YbbHtt_res": {
            "index": 0,
            "binning": fine_binning,
        },
        "boosted_YbbHtt_boost": {
            "index": 1,
            "binning": fine_binning,
        },
        "boosted_YttHbb_res": {
            "index": 2,
            "binning": fine_binning,
        },
        "boosted_YttHbb_boost": {
            "index": 3,
            "binning": fine_binning,
        },
        "boosted_genuine_tau": {
            "index": 4,
            "binning": fine_binning,
        },
        "boosted_tau_fakes": {
            "index": 5,
            "binning": fine_binning,
        },
        "boosted_ttbar": {
            "index": 6,
            "binning": fine_binning,
        },
        "boosted_misc": {
            "index": 7,
            "binning": fine_binning,
        },
    }
}

def get_categorization(massX, massY, boosted_tt=False):
    categorization = {}
    if not boosted_tt:
        for channel in ["et", "mt", "tt"]:
            categorization[channel] = []
            for category in category_mapping[channel].keys():
                selection = (
                    Selection(
                        name=category,
                        cuts=[
                            (
                                f"max_index_{massX}_{massY} == {category_mapping[channel][category]['index']}",
                                "category selection",
                            )
                        ],
                    ),
                    [
                        Histogram(
                            f"{channel}_score",
                            f"max_score_{massX}_{massY}",
                            category_mapping[channel][category]["binning"],
                        )
                    ],
                )
                categorization[channel].append(selection)
    else:
        for channel in ["et", "mt", "tt"]:
            categorization[channel] = []
            for category in boosted_category_mapping[channel].keys():
                selection = (
                    Selection(
                        name=category,
                        cuts=[
                            (
                                f"boosted_max_index_{massX}_{massY} == {boosted_category_mapping[channel][category]['index']}",
                                "category selection",
                            )
                        ],
                    ),
                    [
                        Histogram(
                            f"{channel}_score_boosted",
                            f"boosted_max_score_{massX}_{massY}",
                            boosted_category_mapping[channel][category]["binning"],
                        )
                    ],
                )
                categorization[channel].append(selection)
                
    return categorization