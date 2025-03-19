from ntuple_processor import Histogram
import numpy as np
from typing import Any, Dict, Union
from abc import ABC, abstractmethod


class ObjBuildingDict(ABC, dict):
    """
    Dictionary subclass that builds objects on demand from key and value.

    Extends the built‐in dict with the ability to “build” (or convert) a stored
    value into an object of a predefined type.
    Upon accessing an item via __getitem__, if the stored value is already an
    instance of the expected object type (specified during initialization via
    the 'obj' parameter), then that instance is returned as is. Otherwise, the
    abstract method build_obj(key, value) is called for a transformation.

    Subclasses must implement:
        build_obj(key: str, value: Any) -> object:
            Converts the raw value stored under key to a proper instance of the
            expected object type.

    Parameters
    ----------
    *args : any
        Positional arguments passed to the parent dict initializer.
    obj : object or None, optional
        Object used for the transformation. If provided, __getitem__ will check
        whether the stored value is an instance of this type, if not, build_obj
        will be invoked.
    **kwargs : dict
        Keyword arguments passed to the parent dict initializer.
    """
    def __init__(
        self,
        *args: Any,
        obj: Union[object, None] = None,
        **kwargs: Dict[str, Any],
    ):
        super().__init__(*args, **kwargs)
        self.obj = obj

    @abstractmethod
    def build_obj(self, key: str, value: Any) -> object:
        """
        Build and return the object corresponding to the given key.

        Parameters
        ----------
        key : str
            The dictionary key.
        value : Any
            The original value stored in the dictionary; typically not yet in
            the desired object form.

        Returns
        -------
        object
            The constructed object.
        """
        raise NotImplementedError

    def __getitem__(self, key: Any) -> Any:
        """
        Extends the built-in __getitem__ method to return the stored object
        if it is already an instance of the expected type, or build it using
        build_obj() otherwise.

        Parameters
        ----------
        key : str
            The key to look up.

        Returns
        -------
        object
            The stored object if it is already built, or the result of build_obj().
        """
        if self.obj is None:
            return super().__getitem__(key)
        try:
            obj = super().__getitem__(key)
            if isinstance(obj, self.obj):
                return obj
            return self.build_obj(key, obj)
        except KeyError:
            raise KeyError(f"Key {key} not found in the dictionary")


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
        "genbosonpt": np.arange(0, 150, 10),
        "deltaR_ditaupair": np.arange(0, 5, 0.2),
        "mTdileptonMET_puppi": np.arange(0, 200, 4),
        "pzetamissvis": np.arange(-200, 200, 5),
        "pzetamissvis_pf": np.arange(-200, 200, 5),
        "m_sv_puppi": np.arange(0, 225, 5),
        "pt_sv_puppi": np.arange(0, 160, 5),
        "eta_sv_puppi": np.linspace(-2.5, 2.5, 50),
        "m_vis": np.arange(0, 202, 3),
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
        "jpt_1": np.concatenate(([0], np.arange(20, 160, 5))),
        "jpt_2": np.concatenate(([0], np.arange(20, 160, 5))),
        "jeta_1": np.linspace(-5, 5, 50),
        "jeta_2": np.linspace(-5, 5, 50),
        "jphi_1": np.linspace(-np.pi, np.pi, 50),
        "jphi_2": np.linspace(-np.pi, np.pi, 50),
        "jdeta": np.arange(0, 6, 0.2),
        "njets": np.arange(-0.5, 7.5, 1),
        "nbtag": np.arange(-0.5, 7.5, 1),
        "tau_decaymode_1": np.arange(-0.5, 12.5, 1),
        "tau_decaymode_2": np.arange(-0.5, 12.5, 1),
        "jet_hemisphere": [-0.5, 0.5, 1.5],
        "rho": np.arange(0, 100, 2),
        "m_1": np.linspace(0, 3, 50),
        "m_2": np.linspace(0, 3, 50),
        "mt_1": np.arange(0, 160, 5),
        "mt_2": np.arange(0, 160, 5),
        "mt_1_pf": np.arange(0, 160, 5),
        "mt_2_pf": np.arange(0, 160, 5),
        "pt_vis": np.arange(0, 160, 5),
        "pt_tt": np.arange(0, 160, 5),
        "pt_dijet": np.arange(0, 300, 5),
        "pt_tt_pf": np.arange(0, 160, 5),
        "pt_ttjj": np.arange(0, 160, 5),
        "mjj": np.arange(0, 300, 10),
        "met": np.arange(0, 160, 5),
        "pfmet": np.concatenate((np.arange(0, 160, 5), [200, 400])),
        "iso_1": np.linspace(0, 0.3, 50),
        "iso_2": np.linspace(0, 1.0, 50),
        "bpt_1": np.arange(0, 160, 5),
        "bpt_2": np.arange(0, 160, 5),
        "beta_1": np.linspace(-5, 5, 20),
        "beta_2": np.linspace(-5, 5, 20),
        # fastmtt variables
        "m_fastmtt": np.arange(0, 225, 5),
        "pt_fastmtt": np.arange(0, 160, 5),
        "eta_fastmtt": np.linspace(-2.5, 2.5, 50),
        "phi_fastmtt": np.linspace(-np.pi, np.pi, 50),
        "npartons": np.arange(-0.5, 7.5, 1),
        "phi_1": np.linspace(-2.5, 2.5, 50),
        "phi_2": np.linspace(-2.5, 2.5, 50),
        "q_1": [-4, 4],  # for overall yield
    }
)

control_binning = {}
for channel in ["et", "mt", "tt", "em", "ee", "mm"]:
    control_binning[channel] = common_binning
