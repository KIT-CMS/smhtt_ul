from copy import deepcopy
from typing import List, Union, Literal

IMPORTANCE_TO_PROCESS = {  # importance ordering
    # --- Embedding ---
    0.00: "EMB",
    # --- MC Embedding equivalent ---
    0.10: "ZTT",
    0.11: "ZTT_NLO",
    0.20: "TTT",
    0.30: "VVT",
    # --- JetFakes ---
    1.00: "jetFakesEMB",  # with EMB
    1.10: "jetFakes",  # without EMB
    # --- JetFakes: W ---
    1.20: "JetFakesW",
    1.21: "W",
    1.22: "W_NLO",
    # --- JetFakes: QCD ---
    1.30: "JetFakesQCD",
    1.31: "QCD",
    1.32: "QCD_NLO",
    1.33: "QCDEMB",
    1.34: "QCDEMB_NLO",
    # --- JetFakes: TT ---
    1.40: "JetFakesTT",
    1.41: "TTJ",
    # --- ST ---
    1.50: "STT",
    1.51: "STJ",
    1.52: "STL",
    # --- Other ---
    2.00: "VVJ",
    3.00: "ZJ",
    3.10: "ZJ_NLO",
    4.00: "ZL",
    4.10: "ZL_NLO",
    5.00: "TTL",
    6.00: "VVL",
}

PROCESS_TO_IMPORTANCE = dict(map(reversed, IMPORTANCE_TO_PROCESS.items()))


def sorted_bkg_processes(x: List[str], /, *, ordering: Union[None, dict[float, str]] = None) -> List[str]:
    assert isinstance(x, list), "Only implemented for list"
    if ordering is None:
        ordering = PROCESS_TO_IMPORTANCE
    elif ordering is not None and all(isinstance(k, float) for k in ordering) and all(isinstance(v, str) for v in ordering.values()):
        ordering = dict(map(reversed, deepcopy(ordering).items()))
    elif not (all(isinstance(k, str) for k in ordering) and all(isinstance(v, float) for v in ordering.values())):
        pass
    else:
        raise ValueError("ordering must be None or dict[float, str] or dict[str, float]")
    return sorted(
        deepcopy(x),
        key=lambda p: ordering.get(p, 999),
        reverse=True,
    )


class ControlShapeBkgProcesses:
    #                                    | FF-processes -------------->| EMB-processes --->|
    FULLY_CLASSIC = ['VVL', 'TTL', 'ZL', 'ZJ', 'VVJ', 'TTJ', 'QCD', 'W', 'VVT', 'TTT', 'ZTT', 'STT', 'STJ', 'STL', 'VVVT', 'VVVJ', 'VVVL', 'TTVT', 'TTVJ', 'TTVL', 'EWK',  "ggH", "qqH", "ttH", "VH"]
    EMB_FF = ['VVL', 'TTL', 'ZL', 'jetFakesEMB', 'EMB']
    CLASSIC_FF = ['VVL', 'TTL', 'ZL', 'jetFakes', 'VVT', 'TTT', 'ZTT']
    EMB_CLASSIC = ['VVL', 'TTL', 'ZL', 'ZJ', 'VVJ', 'TTJ', 'QCDEMB', 'W', 'EMB']

    LO_NLO_PROCESSES = {
        "ZTT": "ZTT_NLO",
        "W": "W_NLO",
        "QCD": "QCD_NLO",
        "ZL": "ZL_NLO",
        "QCDEMB": "QCDEMB_NLO",
        "ZJ": "ZJ_NLO",
    }

    def __init__(
        self,
        embedding: bool,
        fake_factor: bool,
        nlo: bool = False,
        channel: Literal["em", "mm", "ee", "mt", "et", "tt", None] = None,
        selection_option: Literal["CR", "DR;ff;wjet", "DR;ff;qcd", "DR;ff;ttbar"] = "SR",
        draw_jet_fake_variation: Union[str, None] = None,
    ) -> None:
        self._embedding = embedding
        self._fake_factor = fake_factor
        self._nlo = nlo
        self._channel = channel
        self._selection_option = selection_option
        self._draw_jet_fake_variation = draw_jet_fake_variation

        self._pipe = [
            self.selection_option_modification,
            self.channel_modification,
            self.lo_to_nlo_replacement,
        ]

        self.ordering = deepcopy(IMPORTANCE_TO_PROCESS)

    @property
    def _is_fully_classic(self) -> bool:
        return not self._embedding and not self._fake_factor

    @property
    def _is_emb_classic(self) -> bool:
        return self._embedding and not self._fake_factor

    @property
    def _is_emb_ff(self) -> bool:
        return self._embedding and self._fake_factor

    @property
    def _is_classic_ff(self) -> bool:
        return not self._embedding and self._fake_factor

    def lo_to_nlo_replacement(self, bkg_process: str, /) -> List[str]:
        if not self._nlo:
            return bkg_process
        return [self.LO_NLO_PROCESSES.get(it, it) for it in bkg_process]

    def channel_modification(self, bkg_processes: List[str], /) -> List[str]:
        # TODO: Find out if this is needed! (currently port from plot_shapes-control.py)

        if self._channel not in {"em", "mm", "ee"}:
            return bkg_processes

        if self._channel == "em":
            if not self._embedding:
                return ["QCD", "VVT", "STT", "VVL", "STL", "W", "TTT", "TTL", "ZL", "ZTT"]
            if self._embedding:
                return ["QCDEMB", "VVL", "STL", "W", "TTL", "ZL", "EMB"]
            if self._draw_jet_fake_variation is not None and not self._embedding:
                return ["VVT", "STT", "VVL", "STL", "W", "TTT", "TTL", "ZL", "ZTT"]
            if self._draw_jet_fake_variation is not None and self._embedding:    
                return ["VVL", "STL", "W", "TTL", "ZL", "EMB"]
        if self._channel in {"mm", "ee"}:
            bkg_processes = ["QCD", "VVL", "STL", "W", "TTL", "ZL"]
            if self._is_emb_classic:
                bkg_processes = ["QCDEMB", "W", "EMB"]
            return bkg_processes

    def selection_option_modification(self, bkg_processes: List[str], /) -> List[str]:
        if self._selection_option == "CR":
            return bkg_processes

        if not self._fake_factor:
            return bkg_processes

        _QCD = "QCDEMB" if self._embedding else "QCD"
        ff_processes_covered_by_mc = ['ZJ', 'VVJ', 'TTJ', _QCD, 'W']
        _jetFakes = self.ordering.pop(1.00 if self._embedding else 1.10)
        if self._channel in {"mt", "et"} and "DR;ff" in self._selection_option:
            if "qcd" in self._selection_option:
                ff_processes_covered_by_mc.remove(_QCD)
                self.ordering[1.30] = _jetFakes
            elif "wjet" in self._selection_option:
                ff_processes_covered_by_mc.remove("W")
                self.ordering[1.20] = _jetFakes
            elif "ttbar" in self._selection_option:
                ff_processes_covered_by_mc.remove("TTJ")
                self.ordering[1.40] = _jetFakes
            else:
                raise NotImplementedError(f"DR for {self._selection_option} not implemented")
        else:
            raise NotImplementedError(f"Channel {self._channel} not implemented")

        return list(set(bkg_processes + ff_processes_covered_by_mc))

    def __call__(self) -> List[str]:
        if self._is_fully_classic:
            bkg_processes = self.FULLY_CLASSIC
        elif self._is_emb_classic:
            bkg_processes = self.EMB_CLASSIC
        elif self._is_emb_ff:
            bkg_processes = self.EMB_FF
        elif self._is_classic_ff:
            bkg_processes = self.CLASSIC_FF

        for modify in self._pipe:
            bkg_processes = modify(bkg_processes)

        return sorted_bkg_processes(
            deepcopy(bkg_processes),
            ordering=self.ordering,
        )
