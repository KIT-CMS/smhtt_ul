from copy import deepcopy
from typing import List, Union, Literal

GLOBAL_BKG_ORDERING_IMPORTANCE_TO_PROCESS = {  # importance ordering
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
    # --- Other ---
    2.00: "VVJ",
    3.00: "ZJ",
    3.10: "ZJ_NLO",
    4.00: "ZL",
    4.10: "ZL_NLO",
    5.00: "TTL",
    6.00: "VVL",
}

GLOBAL_BKG_ORDERING_PROCESS_TO_IMPORTANCE = dict(
    map(
        reversed,
        GLOBAL_BKG_ORDERING_IMPORTANCE_TO_PROCESS.items(),
    ),
)


def sorted_bkg_processes(x: List[str], /):
    assert isinstance(x, list), "Only implemented for list"
    return sorted(
        deepcopy(x),
        key=lambda p: GLOBAL_BKG_ORDERING_PROCESS_TO_IMPORTANCE.get(p, 999),
        reverse=True,
    )


class ControlShapeBkgProcesses:
    FULLY_CLASSIC = ['VVL', 'TTL', 'ZL', 'ZJ', 'VVJ', 'TTJ', 'QCD', 'W', 'VVT', 'TTT', 'ZTT']
    EMB_CLASSIC = ['VVL', 'TTL', 'ZL', 'ZJ', 'VVJ', 'TTJ', 'QCDEMB', 'W', 'EMB']
    EMB_FF = ['VVL', 'TTL', 'ZL', 'jetFakesEMB', 'EMB']
    CLASSIC_FF = ['VVL', 'TTL', 'ZL', 'jetFakes', 'VVT', 'TTT', 'ZTT']

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
        ff_DR: Literal["wjet", "qcd", "tt", None] = None,
        draw_jet_fake_variation: Union[str, None] = None,
    ) -> None:
        self._embedding = embedding,
        self._fake_factor = fake_factor
        self._nlo = nlo
        self._channel = channel
        self._ff_DR = ff_DR.lower() if ff_DR is not None else None
        self._draw_jet_fake_variation = draw_jet_fake_variation

        self._pipe = [
            self.ff_DR_modification,
            self.channel_modification,
            self.lo_to_nlo_replacement,
        ]

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
                return ["QCD", "VVT", "VVL", "W", "TTT", "TTL", "ZL", "ZTT"]
            if self._embedding:
                return ["QCDEMB", "VVL", "W", "TTL", "ZL", "EMB"]
            if self._draw_jet_fake_variation is not None and not self._embedding:
                return ["VVT", "VVL", "W", "TTT", "TTL", "ZL", "ZTT"]
            if self._draw_jet_fake_variation is not None and self._embedding:    
                return ["VVL", "W", "TTL", "ZL", "EMB"]
        if self._channel in {"mm", "ee"}:
            bkg_processes = ["QCD", "VVL", "W", "TTL", "ZL"]
            if self._is_emb_classic:
                bkg_processes = ["QCDEMB", "W", "EMB"]
            return bkg_processes

    def ff_DR_modification(self, bkg_processes: List[str], /) -> List[str]:
        if not self._fake_factor or self._ff_DR is None:
            return bkg_processes

        _QCD = "QCDEMB" if self._embedding else "QCD"
        ff_processes = ['ZJ', 'VVJ', 'TTJ', _QCD, 'W']
        if self._channel in {"mt", "et"}:
            if self._ff_DR == "qcd":
                ff_processes.remove(_QCD)
            elif self._ff_DR == "wjet":
                ff_processes.remove("W")
            elif self._ff_DR == "ttbar":
                ff_processes.remove("TTJ")
            else:
                raise NotImplementedError(f"DR for {self._ff_DR} not implemented")
        elif self._channel in {"tt"}:
            raise NotImplementedError(f"DR for {self._channel} not implemented")
        else:
            raise NotImplementedError(f"Channel {self._channel} not implemented")

        return list(set(bkg_processes + ff_processes))

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

        return sorted_bkg_processes(bkg_processes)
