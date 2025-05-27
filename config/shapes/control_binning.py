from ntuple_processor import Histogram
import numpy as np
from typing import Any, Dict, Union
from config.helper_collection import ObjBuildingDict


class HistogramBuildingDict(ObjBuildingDict):
    """
    Constructing Histogram objects from raw data arrays using `Histogram(tag, name, value)`.

    Assumption: each key in the dictionary corresponds to a Histogram or bin edges,
    either as a list or numpy array.
    """

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]):
        super().__init__(*args, obj=Histogram, **kwargs)

    def build_obj(self, key: str, value: Union[np.ndarray, list]) -> Histogram:
        """
        Build a Histogram object for the given key from the raw data using
        `Histogram(tag, name, value)` constructor.

        Parameters
        ----------
        key : str
            The key associated with the histogram.
        value : Union[np.ndarray, list]
            The raw data, which must be either a numpy array or a list of values.

        Returns
        -------
        Histogram
            A new Histogram object built from the provided data.
        """
        if isinstance(value, (np.ndarray, list)):
            return self.obj(key, key, value)
        else:
            raise ValueError(f"Value for key {key} is not a list or numpy array")


common_binning = HistogramBuildingDict(
    {
        "mass_2": np.arange(0, 2.1, 0.1),
        "mass_1": np.arange(0, 2.1, 0.1),
        "genbosonpt": np.arange(0, 150, 10),
        "deltaR_ditaupair": np.arange(0, 5.2, 0.2),
        "mTdileptonMET_puppi": np.arange(0, 200, 4),
        "mTdileptonMET": np.arange(0, 200, 4),
        "pzetamissvis": np.arange(-150, 150, 5),
        "pzetamissvis_pf": np.arange(-150, 150, 5),
        "m_sv_puppi": np.arange(0, 225, 5),
        "pt_sv_puppi": np.arange(0, 160, 5),
        "eta_sv_puppi": np.linspace(-2.5, 2.5, 50),
        "m_vis": np.arange(0, 202, 5),
        "ME_q2v1": np.arange(0, 300000, 6000),
        "ME_q2v2": np.arange(0, 300000, 6000),
        "ME_costheta1": np.linspace(-1, 1, 50),
        "ME_costheta2": np.linspace(-1, 1, 50),
        "ME_costhetastar": np.linspace(-1, 1, 50),
        "ME_phi": np.linspace(-np.pi, np.pi, 50),
        "ME_phi1": np.linspace(-np.pi, np.pi, 50),
        "pfmetphi": np.linspace(-np.pi, np.pi, 50),
        "metphi": np.linspace(-np.pi, np.pi, 50),
        "mt_tot": np.arange(0, 400, 8),
        "mt_tot_puppi": np.arange(0, 400, 8),
        "pt_1": np.concatenate(([0], np.arange(20, 140, 5))),
        "pt_2": [0, 30, 35, 40, 45, 50, 60, 70, 90, 110, 140],
        "eta_1": np.linspace(-2.5, 2.5, 50),
        "eta_2": np.linspace(-2.5, 2.5, 50),
        "jpt_1": np.concatenate(([0], np.arange(20, 250, 5))),
        "jpt_2": np.concatenate(([0], np.arange(20, 250, 5))),
        "jeta_1": np.linspace(-3, 3, 50),
        "jeta_2": np.linspace(-3, 3, 50),
        "jphi_1": np.linspace(-np.pi, np.pi, 50),
        "jphi_2": np.linspace(-np.pi, np.pi, 50),
        "jdeta": np.arange(0, 6, 0.2),
        "njets": np.arange(-0.5, 7.5, 1),
        "nbtag": np.arange(-0.5, 7.5, 1),
        "tau_decaymode_1": np.arange(-0.5, 12.5, 1),
        "tau_decaymode_2": np.arange(-0.5, 12.5, 1),
        "jet_hemisphere": [-0.5, 0.5, 1.5],
        "rho": np.arange(0, 100, 2),
        "mass_1": np.linspace(0, 3, 50),
        "mass_2": np.linspace(0, 3, 50),
        "mt_1": np.arange(0, 160, 5),
        "mt_2": np.arange(0, 160, 5),
        "mt_1_pf": np.arange(0, 160, 5),
        "mt_2_pf": np.arange(0, 160, 5),
        "pt_vis": np.arange(0, 250, 10),
        "pt_tt": np.arange(0, 165, 5),
        "pt_dijet": np.arange(0, 165, 5),
        "pt_tt_pf": np.arange(0, 160, 5),
        "pt_ttjj": np.arange(0, 160, 5),
        "mjj": np.arange(0, 300, 10),
        "met": np.arange(0, 160, 5),
        "pfmet": np.concatenate((np.arange(0, 160, 5), [200, 400])),
        "iso_1": np.linspace(0, 0.3, 50),
        "iso_2": np.linspace(0, 1.0, 50),
        # fastmtt variables
        "m_fastmtt": np.arange(0, 225, 5),
        "pt_fastmtt": np.arange(0, 300, 10),
        "eta_fastmtt": np.linspace(-2.5, 2.5, 50),
        "phi_fastmtt": np.linspace(-np.pi, np.pi, 50),
        "phi_1": np.linspace(-2.5, 2.5, 50),
        "phi_2": np.linspace(-2.5, 2.5, 50),
        "q_1": [-4, 4],  # for overall yield
        # b jets
        "bpt_1": np.arange(0, 250, 5),
        "bpt_2": np.arange(0, 250, 5),
        "beta_1": np.linspace(-5, 5, 20),
        "beta_2": np.linspace(-5, 5, 20),
        "bphi_1": np.linspace(-3.14, 3.14, 30),
        "bphi_2": np.linspace(-3.14, 3.14, 30),
        "btag_value_1": np.linspace(0.2, 1.0, 40),
        "btag_value_2": np.linspace(0.2, 1.0, 40),
        "bpair_pt_1": np.arange(0, 260, 10),
        "bpair_pt_2": np.arange(0, 180, 10),
        "bpair_eta_1": np.linspace(-3, 3, 20),
        "bpair_eta_2": np.linspace(-3, 3, 20),
        "bpair_phi_1": np.linspace(-3.14, 3.14, 20),
        "bpair_phi_2": np.linspace(-3.14, 3.14, 20),
        "bpair_btag_value_1": np.linspace(0.2, 1.0, 15),
        "bpair_btag_value_2": np.linspace(0.0, 1.0, 20),
        "bpair_m_inv": np.arange(0, 425, 20),
        "bpair_pt_dijet": np.arange(0, 300, 20),
        "bpair_deltaR": np.arange(0, 5, 0.2),
        "bpair_pt_1_boosted": np.arange(0, 260, 10),
        "bpair_pt_2_boosted": np.arange(0, 180, 10),
        "bpair_eta_1_boosted": np.linspace(-3, 3, 15),
        "bpair_eta_2_boosted": np.linspace(-3, 3, 15),
        "bpair_phi_1_boosted": np.linspace(-3.14, 3.14, 15),
        "bpair_phi_2_boosted": np.linspace(-3.14, 3.14, 15),
        "bpair_btag_value_1_boosted": np.linspace(0.2, 1.0, 15),
        "bpair_btag_value_2_boosted": np.linspace(0.0, 1.0, 20),
        "bpair_m_inv_boosted": np.arange(0, 425, 20),
        "bpair_pt_dijet_boosted": np.arange(0, 300, 20),
        "bpair_deltaR_boosted": np.arange(0, 5, 0.4),
        # bbtt variables
        "npartons": [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        "pt_tautaubb": np.arange(0, 510, 20),
        "mass_tautaubb": np.arange(100, 905, 30),
        "mtt_coll_approx": np.arange(0, 405, 10),
    }
)

control_binning = {ch: common_binning for ch in ["et", "mt", "tt", "em", "ee", "mm"]}
