from unicodedata import category
import correctionlib._core as core
import correctionlib.schemav2 as schema
import correctionlib.JSONEncoder as JSONEncoder
import ROOT
import json
import argparse
import glob
import os
from typing import Union, Tuple
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
import matplotlib.pyplot as plt
import numpy as np
import datetime

class CorrectionSet(object):
    def __init__(self, name):
        self.name = name
        self.corrections = []

    def add_correction_file(self, correction_file):
        with open(correction_file) as file:
            data = json.load(file)
            corr = schema.Correction.model_validate(data)
            self.add_correction(corr)

    def add_correction(self, correction):
        if isinstance(correction, dict):
            self.corrections.append(correction)
        elif isinstance(correction, Correction):
            self.corrections.append(correction.correctionset)
        else:
            raise TypeError(
                "Correction must be a Correction object or a dictionary, not {}".format(
                    type(correction)
                )
            )

    def write_json(self, outputfile):
        # Create the JSON object
        cset = schema.CorrectionSet(
            schema_version=schema.VERSION, corrections=self.corrections
        )
        print(f">>> Writing {outputfile}...")
        JSONEncoder.write(cset, outputfile)
        JSONEncoder.write(cset, outputfile + ".gz")


class Correction(object):
    def __init__(
        self,
        tag,
        name,
        outdir,
        configfile,
        era,
        fname="",
        data_only=False,
        verbose=False,
    ):
        self.tag = tag
        self.name = name
        self.outdir = outdir
        self.configfile = configfile
        self.ptbinning = []
        self.etabinning = []
        self.inputfiles = []
        self.correction = None
        self.era = era
        self.header = ""
        self.fname = fname
        self.info = ""
        self.verbose = verbose
        self.data_only = data_only
        self.correctionset = None
        self.inputobjects = {}
        self.types = ["Data", "Embedding", "DY"]

    def __repr__(self) -> str:
        return "Correction({})".format(self.name)

    def __str__(self) -> str:
        return "Correction({})".format(self.name)

    def parse_config(self):
        pass

    def setup_scheme(self):
        pass

    def generate_sfs(self):
        pass

    def generate_scheme(self):
        pass


class TauID(Correction):
    def __init__(
        self,
        tag,
        name,
        data,
        era,
        outdir,
        fname="",
        verbose=False,
    ):
        super(TauID, self).__init__(
            tag,
            name,
            outdir,
            data,
            era,
            fname,
            data_only=False,
            verbose=False,
        )
        self.data = data
        
        if self.data_only:
            self.types = ["Data"]

    def parse_config(self):
        self.info = "Missing Info"
        self.header = "Missing Header"
        self.pt_binning = {
            "DM0_PT20_40": 20,
            "DM1_PT20_40": 20,
            "DM10_PT20_40": 20,
            "DM1011_PT20_40": 20,
            "DM11_PT20_40": 20,
            "DM0_PT40_200": 40,
            "DM1_PT40_200": 40,
            "DM10_PT40_200": 40,
            "DM10_PT40_200": 40,
            "DM11_PT40_200": 40,
        }
        self.dm_binning = {
            "DM0": 0,
            "DM1": 1,
            "DM10": 10,
            "DM11": 11,
        }
        
        # For dm_pt binns, here each bin receives the lower pt bin value via extra dict layer:
        for wp in self.data.keys():
            for wp_VSe in self.data[wp].keys():
                for pt_bin in self.pt_binning.keys():
                    if pt_bin in self.data[wp][wp_VSe].keys():
                        self.data[wp][wp_VSe][pt_bin] = {self.pt_binning[pt_bin] : self.data[wp][wp_VSe][pt_bin]}
        
        # Dict that contains the list of pt bins for each dm bin, s.t. the scheme generation knows which pt bins are available:
        self.dm_pt_bin_lists = {}
        for wp in self.data.keys():
            if wp not in self.dm_pt_bin_lists:
                self.dm_pt_bin_lists[wp] = {} 
                for wp_VSe in self.data[wp].keys():
                    if wp_VSe not in self.dm_pt_bin_lists[wp]:
                        self.dm_pt_bin_lists[wp][wp_VSe] = {}
                        for dm in self.dm_binning.values():
                            if dm not in self.dm_pt_bin_lists[wp][wp_VSe] and (f'DM{dm}_PT20_40' in self.data[wp][wp_VSe] or f'DM{dm}_PT40_200' in self.data[wp][wp_VSe]):
                                if (f'DM{dm}_PT20_40' in self.data[wp][wp_VSe] and f'DM{dm}_PT40_200' in self.data[wp][wp_VSe]):
                                    self.dm_pt_bin_lists[wp][wp_VSe][dm] = [20, 40, 200]
                                else:
                                    if f'DM{dm}_PT20_40' in self.data[wp][wp_VSe]:
                                        self.dm_pt_bin_lists[wp][wp_VSe][dm] = [20, 40]
                                    elif f'DM{dm}_PT40_200' in self.data[wp][wp_VSe]:
                                        self.dm_pt_bin_lists[wp][wp_VSe][dm] = [40, 200]
                                    else:
                                        raise ValueError(f"Invalid pt bin: {self.dm_pt_bin_data[wp][wp_VSe]}, dm: {dm}")
                                    

    def setup_dm_pt_scheme(self):
        self.correctionset = {
            "version": 0,
            "name": self.name,
            "description": "dm-pt-dependent tau ID scale factor for tau embedded samples",
            "inputs": [
                { "name": "pt",
                "type": "real",
                "description": "Reconstructed tau pT"
                },
                { "name": "dm",
                "type": "int",
                "description": "Reconstructed tau decay mode: 0, 1, 10, 11"
                },
                { "name": "genmatch",
                "type": "int",
                "description": "genmatch: 0 or 6 = unmatched or jet, 1 or 3 = electron, 2 or 4 = muon, 5 = real tau"
                },
                { "name": "wp",
                "type": "string",
                "description": "DeepTau2018v2p5VSjet working point: Medium,Tight"
                },
                { "name": "wp_VSe",
                "type": "string",
                "description": "DeepTau2018v2p5VSe working point: VVLoose,Tight"
                },
                { "name": "syst",
                "type": "string",
                "description": "Systematic variations: 'nom', 'up', 'down'"
                },
                { "name": "flag",
                "type": "string",
                "description": "Flag: 'pt' = DM-pT-dependent SFs(20,40,200), 'dm' = DM-dependent SFs with pt>=20"
                }
            ],
            "output": {
                "name": "sf",
                "type": "real",
                "description": "DM-pT-dependent or DM-dependent scale factor",
            },
            "data": None,
        }

    def generate_dm_pt_sfs(self):
        data = {"nodetype": "category", "input": "flag", "content": []}
        sfs = {
            "nodetype": "category",
            "input": "genmatch",
            "content": [
                {"key": 0, "value": 1.0},
                {"key": 1, "value": 1.0},
                {"key": 2, "value": 1.0},
                {"key": 3, "value": 1.0},
                {"key": 4, "value": 1.0},
                {"key": 6, "value": 1.0},
                {"key": 5,
                "value":{
                    "nodetype": "category",
                    "input": "wp",
                    "content": [
                    {"key": wp,
                     "value": {
                        "nodetype": "category",
                        "input": "wp_VSe",
                        "content": [
                            {
                            "key": wp_VSe,
                            "value": {
                                "nodetype": "category",
                                "input": "dm",
                                "content": [
                                    {"key": dm,
                                    "value": {
                                        "nodetype": "binning",
                                        "input": "pt",
                                        "edges":  self.dm_pt_bin_lists[wp][wp_VSe][dm],
                                        "flow": "clamp",
                                        "content": [
                                            {
                                                "nodetype": "category",
                                                "input": "syst",
                                                "content": [
                                                    {"key": "nom", "value": self.get_tau_sf(pt, "nom", isPt=True, wp=wp, wp_VSe=wp_VSe, dm=dm, id_es="id")},
                                                    {"key": "up", "value": self.get_tau_sf(pt, "up", isPt=True, wp=wp, wp_VSe=wp_VSe, dm=dm, id_es="id")},
                                                    {"key": "down", "value": self.get_tau_sf(pt, "down", isPt=True, wp=wp, wp_VSe=wp_VSe, dm=dm, id_es="id")},
                                                                    ],
                                                                } for pt in self.dm_pt_bin_lists[wp][wp_VSe][dm][:-1]
                                                            ],
                                                        }
                                                    } for dm in self.dm_pt_bin_lists[wp][wp_VSe].keys()
                                                ],
                                            },
                                        } for wp_VSe in self.data[wp].keys()
                                    ],
                                },
                            } for wp in self.data.keys()
                        ],
                    },
                },
            ],
        }
        data["content"].append({"key": "pt", "value": sfs})
        return schema.Category.model_validate(data)

    def setup_dm_scheme(self):
        self.correctionset = {
            "version": 0,
            "name": self.name,
            "description": "dm-dependent tau ID scale factor for tau embedded samples",
            "inputs": [
                { "name": "pt",
                "type": "real",
                "description": "Reconstructed tau pT"
                },
                { "name": "dm",
                "type": "int",
                "description": "Reconstructed tau decay mode: 0, 1, 10, 11"
                },
                { "name": "genmatch",
                "type": "int",
                "description": "genmatch: 0 or 6 = unmatched or jet, 1 or 3 = electron, 2 or 4 = muon, 5 = real tau"
                },
                { "name": "wp",
                "type": "string",
                "description": "DeepTau2018v2p5VSjet working point: Medium,Tight"
                },
                { "name": "wp_VSe",
                "type": "string",
                "description": "DeepTau2018v2p5VSe working point: VVLoose,Tight"
                },
                { "name": "syst",
                "type": "string",
                "description": "Systematic variations: 'nom', 'up', 'down'"
                },
                { "name": "flag",
                "type": "string",
                "description": "Flag: 'pt' = DM-pT-dependent SFs(20,40,200), 'dm' = DM-dependent SFs with pt>=20"
                }
            ],
            "output": {
                "name": "sf",
                "type": "real",
                "description": "DM-dependent scale factor",
            },
            "data": None,
        }

    def generate_dm_sfs(self):
        data = {"nodetype": "category", "input": "flag", "content": []}
        sfs = {
            "nodetype": "category",
            "input": "genmatch",
            "content": [
                {"key": 0, "value": 1.0},
                {"key": 1, "value": 1.0},
                {"key": 2, "value": 1.0},
                {"key": 3, "value": 1.0},
                {"key": 4, "value": 1.0},
                {"key": 6, "value": 1.0},
                {"key": 5,
                "value":{
                    "nodetype": "category",
                    "input": "wp",
                    "content": [
                    {"key": wp,
                     "value": {
                        "nodetype": "category",
                        "input": "wp_VSe",
                        "content": [
                            {"key": wp_VSe,
                            "value": {
                                "nodetype": "category",
                                "input": "dm",
                                "content": [
                                    {"key": self.dm_binning[dm],
                                    "value": {
                                        "nodetype": "binning",
                                        "input": "pt",
                                        "edges":  [20,100000],
                                        "flow": "clamp",
                                        "content": [                                        
                                            {
                                                "nodetype": "category",
                                                "input": "syst",
                                                "content": [
                                                    {"key": "nom","value": self.get_tau_sf(dm,"nom", isDM=True, wp=wp, wp_VSe=wp_VSe, id_es="id")},
                                                    {"key": "up","value": self.get_tau_sf(dm, "up", isDM=True, wp=wp, wp_VSe=wp_VSe, id_es="id")},
                                                    {"key": "down","value": self.get_tau_sf(dm, "down", isDM=True, wp=wp, wp_VSe=wp_VSe, id_es="id")},
                                                                    ],
                                                                }
                                                            ],
                                                        }
                                                    } for dm in self.data[wp][wp_VSe].keys() if dm in self.dm_binning.keys()
                                                ],
                                            },
                                        } for wp_VSe in self.data[wp].keys()
                                    ],
                                },
                            } for wp in self.data.keys() 
                        ],
                    },
                },
            ],
        }
        data["content"].append({"key": "dm", "value": sfs})
        
        return schema.Category.model_validate(data)



    def setup_dm_pt_scheme_es(self):
        self.correctionset = {
            "version": 0,
            "name": self.name,
            "description": "dm-pt-dependent tau ES scale factor for tau embedded samples",
            "inputs": [
                { "name": "pt",
                "type": "real",
                "description": "Reconstructed tau pT"
                },
                { "name": "eta",
                "type": "real",
                "description": "Reconstructed tau eta"
                },
                { "name": "dm",
                "type": "int",
                "description": "Reconstructed tau decay mode: 0, 1, 10, 11"
                },
                { "name": "genmatch",
                "type": "int",
                "description": "genmatch: 0 or 6 = unmatched or jet, 1 or 3 = electron, 2 or 4 = muon, 5 = real tau"
                },
                { "name": "id",
                "type": "string",
                "description": "DeepTau2018v2p5:DeepTau2018v2p5"
                },
                { "name": "wp",
                "type": "string",
                "description": "DeepTau2018v2p5VSjet working point: Medium,Tight"
                },
                { "name": "wp_VSe",
                "type": "string",
                "description": "DeepTau2018v2p5VSe working point: VVLoose,Tight"
                },
                { "name": "syst",
                "type": "string",
                "description": "Systematic variations: 'nom', 'up', 'down'"
                },
                # { "name": "flag",
                # "type": "string",
                # "description": "Flag: 'pt' = DM-pT-dependent SFs(20,40,200), 'dm' = DM-dependent SFs with pt>=20"
                # }
            ],
            "output": {
                "name": "tes",
                "type": "real",
                "description": "DM-pT-dependent tau energy scale",
            },
            "data": None,
        }

    def generate_dm_pt_sfs_es(self):
        # data = {"nodetype": "category", "input": "flag", "content": []}
        sfs = {
            "nodetype": "category",
            "input": "id",
            "content": [
                { "key": "DeepTau2018v2p5",
                "value": {
                    "nodetype": "category",
                    "input": "genmatch",
                    "content": [
                        {"key": 0, "value": 1.0},
                        {"key": 1, "value": 1.0},
                        {"key": 2, "value": 1.0},
                        {"key": 3, "value": 1.0},
                        {"key": 4, "value": 1.0},
                        {"key": 6, "value": 1.0},
                        {"key": 5,
                        "value":{
                            "nodetype": "category",
                            "input": "wp",
                            "content": [
                            {"key": wp,
                            "value": {
                                "nodetype": "category",
                                "input": "wp_VSe",
                                "content": [
                                    {
                                    "key": wp_VSe,
                                    "value": {
                                        "nodetype": "category",
                                        "input": "dm",
                                        "content": [
                                            {"key": dm,
                                            "value": {
                                                "nodetype": "transform",
                                                "input": "eta",
                                                "rule": {
                                                "nodetype": "formula",
                                                "expression": "abs(x)",
                                                "parser": "TFormula",
                                                "variables": [ "eta" ]
                                                },
                                                "content": {
                                                    "nodetype": "binning",
                                                    "input": "eta",
                                                    "edges": [ 0.0, 2.5 ],
                                                    "flow": "clamp",
                                                    "content": [
                                                        {"nodetype": "binning",
                                                        "input": "pt",
                                                        "edges":  self.dm_pt_bin_lists[wp][wp_VSe][dm],
                                                        "flow": "clamp",
                                                        "content": [
                                                            {
                                                                "nodetype": "category",
                                                                "input": "syst",
                                                                "content": [
                                                                    {"key": "nom", "value": self.get_tau_sf(pt, "nom", isPt=True, wp=wp, wp_VSe=wp_VSe, dm=dm, id_es="es")},
                                                                    {"key": "up", "value": self.get_tau_sf(pt, "up", isPt=True, wp=wp, wp_VSe=wp_VSe, dm=dm, id_es="es")},
                                                                    {"key": "down", "value": self.get_tau_sf(pt, "down", isPt=True, wp=wp, wp_VSe=wp_VSe, dm=dm, id_es="es")},
                                                                                            ],
                                                                                        } for pt in self.dm_pt_bin_lists[wp][wp_VSe][dm][:-1]
                                                                                    ],
                                                                                }
                                                                            ],
                                                                        }
                                                                    }
                                                                } for dm in self.dm_pt_bin_lists[wp][wp_VSe].keys()
                                                            ],
                                                        },
                                                    } for wp_VSe in self.data[wp].keys()
                                                ],
                                            },
                                        } for wp in self.data.keys()
                                    ],
                                },
                            },
                        ],
                    },
                },
            ],
        }
        # data["content"].append({"key": "pt", "value": sfs})
        return schema.Category.model_validate(sfs)

    def setup_dm_scheme_es(self):
        self.correctionset = {
            "version": 0,
            "name": self.name,
            "description": "dm-dependent tau ES scale factor for tau embedded samples",
            "inputs": [
                { "name": "pt",
                "type": "real",
                "description": "Reconstructed tau pT"
                },
                { "name": "eta",
                "type": "real",
                "description": "Reconstructed tau eta"
                },
                { "name": "dm",
                "type": "int",
                "description": "Reconstructed tau decay mode: 0, 1, 10, 11"
                },
                { "name": "genmatch",
                "type": "int",
                "description": "genmatch: 0 or 6 = unmatched or jet, 1 or 3 = electron, 2 or 4 = muon, 5 = real tau"
                },
                { "name": "id",
                "type": "string",
                "description": "DeepTau2018v2p5:DeepTau2018v2p5"
                },
                { "name": "wp",
                "type": "string",
                "description": "DeepTau2018v2p5VSjet working point: Medium,Tight"
                },
                { "name": "wp_VSe",
                "type": "string",
                "description": "DeepTau2018v2p5VSe working point: VVLoose,Tight"
                },
                { "name": "syst",
                "type": "string",
                "description": "Systematic variations: 'nom', 'up', 'down'"
                },
                # { "name": "flag",
                # "type": "string",
                # "description": "Flag: 'pt' = DM-pT-dependent SFs(20,40,200), 'dm' = DM-dependent SFs with pt>=20"
                # }
            ],
            "output": {
                "name": "tes",
                "type": "real",
                "description": "DM-dependent tau energy scale",
            },
            "data": None,
        }

    def generate_dm_sfs_es(self):
        # data = {"nodetype": "category", "input": "flag", "content": []}
        sfs = {
            "nodetype": "category",
            "input": "id",
            "content": [
                { "key": "DeepTau2018v2p5",
                "value": {
                    "nodetype": "category",
                    "input": "genmatch",
                    "content": [
                        {"key": 0, "value": 1.0},
                        {"key": 1, "value": 1.0},
                        {"key": 2, "value": 1.0},
                        {"key": 3, "value": 1.0},
                        {"key": 4, "value": 1.0},
                        {"key": 6, "value": 1.0},
                        {"key": 5,
                        "value":{
                            "nodetype": "category",
                            "input": "wp",
                            "content": [
                            {"key": wp,
                            "value": {
                                "nodetype": "category",
                                "input": "wp_VSe",
                                "content": [
                                    {
                                    "key": wp_VSe,
                                    "value": {
                                        "nodetype": "category",
                                        "input": "dm",
                                        "content": [
                                            {"key": self.dm_binning[dm],
                                            "value": {
                                                "nodetype": "transform",
                                                "input": "eta",
                                                "rule": {
                                                "nodetype": "formula",
                                                "expression": "abs(x)",
                                                "parser": "TFormula",
                                                "variables": [ "eta" ]
                                                },
                                                "content": {
                                                    "nodetype": "binning",
                                                    "input": "eta",
                                                    "edges": [ 0.0, 2.5 ],
                                                    "flow": "clamp",
                                                    "content": [
                                                        {"nodetype": "binning",
                                                        "input": "pt",
                                                        "edges":  [20,100000],
                                                        "flow": "clamp",
                                                        "content": [
                                                            {
                                                                "nodetype": "category",
                                                                "input": "syst",
                                                                "content": [
                                                                    {"key": "nom", "value": self.get_tau_sf(dm, "nom", isDM=True, wp=wp, wp_VSe=wp_VSe, id_es="es")},
                                                                    {"key": "up", "value": self.get_tau_sf(dm, "up", isDM=True, wp=wp, wp_VSe=wp_VSe, id_es="es")},
                                                                    {"key": "down", "value": self.get_tau_sf(dm, "down", isDM=True, wp=wp, wp_VSe=wp_VSe, id_es="es")},
                                                                                            ],
                                                                                        }
                                                                                    ],
                                                                                }
                                                                            ],
                                                                        }
                                                                    }
                                                                } for dm in self.data[wp][wp_VSe].keys() if dm in self.dm_binning.keys()
                                                            ],
                                                        },
                                                    } for wp_VSe in self.data[wp].keys()
                                                ],
                                            },
                                        } for wp in self.data.keys()
                                    ],
                                },
                            },
                        ],
                    },
                },
            ],
        }
        # data["content"].append({"key": "dm", "value": sfs})
        return schema.Category.model_validate(sfs)

    def get_tau_sf(self, variable: Union[str,int], variation: str, isPt=False, isDM=False, dm=9000, wp="Medium", wp_VSe="VVLoose", id_es="id"):
        def _convert_tes_to_factor(val:float, id_es="id"):
            if id_es == "id":
                return val
            elif id_es == "es":
                return (100 + val)/100
            else:
                raise ValueError(f"Invalid id_es: {id_es}")
        # vsEle_correction_up = 1.0 if wp_VSe == "VVLoose" else 1.1
        # vsEle_correction_down = 1.0 if wp_VSe == "VVLoose" else 0.9
        if isPt:
            if variable == 20:
                dm_pt = f"DM{dm}_PT{variable}_40"
            elif variable == 40:
                dm_pt = f"DM{dm}_PT{variable}_200"
            data = self.data[wp][wp_VSe]
            for bin in data[dm_pt].keys():
                if variable == bin:
                    if variation == "nom":
                        return _convert_tes_to_factor(data[dm_pt][bin]["r"], id_es=id_es)
                    elif variation == "up":
                        return _convert_tes_to_factor(data[dm_pt][bin]["u"], id_es=id_es) #* vsEle_correction_up
                    elif variation == "down":
                        return _convert_tes_to_factor(data[dm_pt][bin]["d"], id_es=id_es) #* vsEle_correction_down
                    else:
                        raise ValueError(f"Invalid variation: {variation}")
        elif isDM:
            data = self.data[wp][wp_VSe]
            # if id_es == "es":
            #     breakpoint()
            for bin in data.keys():
                if variable == bin:
                    if variation == "nom":
                        return _convert_tes_to_factor(data[bin]["r"], id_es=id_es)
                    elif variation == "up":
                        return _convert_tes_to_factor(data[bin]["u"], id_es=id_es) #* vsEle_correction_up
                    elif variation == "down":
                        return _convert_tes_to_factor(data[bin]["d"], id_es=id_es) #* vsEle_correction_down
                    else:
                        raise ValueError(f"Invalid variation: {variation}")
        else:
            raise ValueError("Invalid argument")

    def generate_dm_pt_scheme(self):
        self.parse_config()
        self.setup_dm_pt_scheme()
        self.correctionset["data"] = self.generate_dm_pt_sfs()
        output_corr = schema.Correction.model_validate(self.correctionset)
        self.correction = output_corr
        # print(JSONEncoder.dumps(self.correction))

    def generate_dm_scheme(self):
        self.parse_config()
        self.setup_dm_scheme()
        self.correctionset["data"] = self.generate_dm_sfs()
        output_corr = schema.Correction.model_validate(self.correctionset)
        self.correction = output_corr
        # print(JSONEncoder.dumps(self.correction))
        
    def generate_dm_pt_scheme_es(self):
        self.parse_config()
        self.setup_dm_pt_scheme_es()
        self.correctionset["data"] = self.generate_dm_pt_sfs_es()
        output_corr = schema.Correction.model_validate(self.correctionset)
        self.correction = output_corr
        # print(JSONEncoder.dumps(self.correction))

    def generate_dm_scheme_es(self):
        self.parse_config()
        self.setup_dm_scheme_es()
        self.correctionset["data"] = self.generate_dm_sfs_es()
        output_corr = schema.Correction.model_validate(self.correctionset)
        self.correction = output_corr
        # print(JSONEncoder.dumps(self.correction))

    def write_scheme(self):
        if self.verbose >= 2:
            print(JSONEncoder.dumps(self.correction))
        elif self.verbose >= 1:
            print(self.correction)
        if self.fname:
            print(f">>> Writing {self.fname}...")
        JSONEncoder.write(self.correction, self.fname)


def recursive_update(x: dict, y: dict, /) -> dict:
    """Merges y dict into x dict, recursively."""
    for k, v in y.items():
        if k in x:
            if isinstance(x[k], dict) and isinstance(v, dict):
                recursive_update(x[k], v)
            else:
                x[k] = v
        else:
            x[k] = v
    return x


def load_fitresults_from_files(filenames, sig_bins):
    
    def _get_data(file: str, tree, fit_name="r_EMB_", bins=sig_bins) -> tuple[dict,str]:
        indices = {}
        count = 1
        results = {}
        binname = []
        for key in tree.GetListOfBranches():
            name = key.GetName()
            for sig_bin in bins:
                if name == fit_name + sig_bin:
                    indices[name] = count
                    count += 2
                    results[name] = [-999, -999, -999]
                    binname += (sig_bin,)
                    break
            if binname:
                break
        
        if not binname:
            return {}
        
        values_lst = []
        for i, row in enumerate(tree):
            for name in indices:
                values_lst.append(getattr(row, name))

        if len(values_lst) != 5:
            print(f"Expected 5, got {len(values_lst)}.")
            return None
            
        dat = {}
        # results_list = values_lst[2:].copy() # values_lst might not be read strictly ordered, maybe look it up.
        
        results_list = list(set(values_lst.copy()))
        results_list.sort()
        if len(results_list) != 3:
            print(f"[ERROR] Wrong number of results found in file {file}. Expected 3, got {len(results_list)}. File is skipped!\n")
            breakpoint()
        if results_list[0] <= results_list[1] <= results_list[2]: 
            dat["r"] = results_list[1]
            dat["d"] = results_list[0]
            dat["u"] = results_list[2]
        else:
            print('[ERROR] Ordering is wrong. Investigate! Errors with float precision possible.')
            breakpoint()
        return dat, binname[0]
    
    def _stack_dicts(data: dict, binname: str, wp: str, wp_VSe: str, flag=False) -> dict:
        bin_data = {}
        wp_data = {}
        wp_VSe_data = {}
        if not flag:
            bin_data[binname] = data
        else:
            if "DM1011" in binname:
                if "PT20" in binname:
                    bin_data["DM10_PT20_40"] = data
                    bin_data["DM11_PT20_40"] = data
                elif "PT40" in binname:
                    bin_data["DM10_PT40_200"] = data
                    bin_data["DM11_PT40_200"] = data
                else:
                    bin_data["DM10"] = data
                    bin_data["DM11"] = data
            else:
                bin_data[binname] = data
        wp_VSe_data[wp_VSe] = bin_data
        wp_data[wp] = wp_VSe_data
        return wp_data
    
    all_dicts = []
    all_dicts_ES = []
    for filename in filenames:
        f = ROOT.TFile(filename)
        if f == None:
            raise Exception("[ERROR] File {} not found.".format(filename))
        wp_param = f.Get("WP")
        wp_VSe_param = f.Get("WP_VSe")
        wp_VSmu_param = f.Get("WP_VSmu")
        wp = wp_param.GetTitle()
        wp_VSe = wp_VSe_param.GetTitle()
        wp_VSmu = wp_VSmu_param.GetTitle() # Not used by tau POG.
        tree = f.Get("limit")
        if tree == None:
            raise Exception(
                "[ERROR] Tree {} not found in file {}.".format("limit", filename)
            )

        data, binname = _get_data(filename, tree, fit_name="r_EMB_", bins=sig_bins)
        data_ES, binname_ES = _get_data(filename, tree, fit_name="ES_", bins=sig_bins)
        if data is None or data_ES is None:
            print(f'[ERROR] Wrong number of results found in file {filename}. File is skipped!\n")')
            continue
        if data == {} or data_ES == {}:
            print(f'[ERROR] No results found in file {filename}. File is skipped!\n")')
            continue
            
        wp_data = _stack_dicts(data, binname, wp, wp_VSe, flag=flag_1011)
        wp_data_ES = _stack_dicts(data_ES, binname_ES, wp, wp_VSe, flag=flag_1011)
        all_dicts += (wp_data,)
        all_dicts_ES += (wp_data_ES,)
    
    if len(all_dicts) > 1 and len(all_dicts_ES) > 1:
        main_dict = {}
        main_dict_ES = {}
        for _dcit in all_dicts:
            main_dict = recursive_update(main_dict, _dcit)
        for _dcit in all_dicts_ES:
            main_dict_ES = recursive_update(main_dict_ES, _dcit)
        return main_dict, main_dict_ES
    elif len(all_dicts) == 1 and len(all_dicts_ES) == 1:
        return all_dicts[0], all_dicts_ES[0]
    else:
        return ValueError("[ERROR] No data found in files. Check your input files!")

# first a simple argparser to the the datacard directory
parser = argparse.ArgumentParser(description="Plot the tau ID SF")
# parser.add_argument("--wp", type=str, default="Tight", help="TauID WP")
# parser.add_argument("--wp_vsele", type=str, default="Tight", help="TauID WP_VsEle")
parser.add_argument("--nTuple_tags", type=str, default="", help="List of NTUPLE Tags")
parser.add_argument("--era", type=str, default="2018", help="2016, 2017 or 2018")
parser.add_argument("--channel", type=str, default="mt", help="mt, et, em, tt")
parser.add_argument("--dm_pt_input_files", type=str, default="", help="DM-Pt input_files")
parser.add_argument("--input_files", type=str, default="", help="DM input_files")
parser.add_argument("--binnames", type=str,
                    default="DM0,DM1,DM1011,DM0_PT20_40,DM1_PT20_40,DM1011_PT20_40,DM0_PT40_200,DM1_PT40_200,DM1011_PT40_200",
                    help="Binnames, no spaces allowed!")

args = parser.parse_args()
# Duplicates (from bash script) removal while preserving order, 
fitfiles = list(dict.fromkeys(args.input_files.split(","))) #+ "cmb/higgsCombine.multidim_dm_fit.MultiDimFit.mH125.root"
binnames = list(dict.fromkeys(args.binnames.split(",")))


flag_1011 = False
if "DM1011" in binnames:
    flag_1011 = True
data_dict, data_dict_ES = load_fitresults_from_files(fitfiles, binnames)

correctionset = CorrectionSet("Tau_ID_ES_SF")
correctionset.description = f"Correction for tau embedding events; embedded tau identification efficiency and embedded tau energy scale factors ( DeepTau2018v2p5VSjet, tau_energy_scale, tau_energy_scale_dm_binned). For more info, please visit https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauEmbeddingSamplesUL#TauID_and_TauES_correction and https://tau-wiki.docs.cern.ch/ (This file was created on {datetime.datetime.now().strftime('%d.%m.%Y')})."
### ID corrections:
# pt
correction_dm_pt = TauID(
    tag="tag",
    name="DeepTau2018v2p5VSjet",
    data=data_dict,
    era=args.era,outdir="/"
)
correction_dm_pt.generate_dm_pt_scheme()
# dm
correction_dm = TauID(
    tag="tag",
    name="DeepTau2018v2p5VSjet",
    data=data_dict,
    era=args.era,
    outdir="/"
)
correction_dm.generate_dm_scheme()

correctionset.add_correction(correction_dm_pt)
# breakpoint()
# Add dm correction on flag level to other correction:
correctionset.corrections[0]['data'].content.append(correction_dm.correctionset['data'].content[0])


### ES corrections:
# pt
correction_dm_pt_es = TauID(
    tag="tag",
    name="tau_energy_scale",
    data=data_dict_ES,
    era=args.era,outdir="/"
)
correction_dm_pt_es.generate_dm_pt_scheme_es()
# dm
correction_dm_es = TauID(
    tag="tag",
    name="tau_energy_scale_dm_binned",
    data=data_dict_ES,
    era=args.era,
    outdir="/"
)
correction_dm_es.generate_dm_scheme_es()


correctionset.add_correction(correction_dm_pt_es)
correctionset.add_correction(correction_dm_es)

# breakpoint()
# Add dm correction on flag level to other correction:
# correctionset.corrections[1]['data'].content.append(correction_dm_es.correctionset['data'].content[0])







# Adds dm as second correction:
# correctionset.add_correction(correction_dm)
# correctionset.write_json(
#     "Correctionlib_Tau_ID_ES_"
#     + str(args.era)
#     + "_UL_"
#     + str(args.channel)
#     + "_"
#     + str(args.nTuple_tag)
#     + ".json"
# )
correctionset.write_json(
    f"DeepTau2018v2p5_id_es_embedding{args.era}UL.json"
)
###########################
#### Plotting the fits ####

# Example: one working point and wp_VSe combination.
# Adjust these keys if needed.
wps = list(data_dict.keys())
wp_VSes = list(dict.fromkeys([keys for vals in data_dict.values() for keys in vals]))

# Create subplots, one for each DM category
def summary_SFs(data: dict, wpTuple: Tuple, tag, ntuple, era=args.era, channel=args.channel,
                id_es="ID") -> None:
    # List of DM categories in data_dict, e.g. ['DM0', 'DM1', 'DM1011']
    wp_list = list(data[wpTuple[0]][wpTuple[1]].keys())
    desired_order = ['DM0', 'DM1', 'DM1011']
    dm_bins = sorted({_dm.split('_')[0] for _dm in wp_list},
                     key=lambda dm: desired_order.index(dm) if dm in desired_order else 999)
    # DM10 and DM11 are combined into DM1011
    flag_1011 = False
    if "DM10" in dm_bins:
        dm_bins.remove("DM10")
        flag_1011 = True
    if "DM11" in dm_bins:
        dm_bins.remove("DM11")
        flag_1011 = True
    if flag_1011:
        dm_bins.append("DM1011")
    
    if flag_1011:
        new_keys = {}
        for key, value in data[wpTuple[0]][wpTuple[1]].items():
            if "DM10" in key or "DM11" in key:
                new_key = key.replace("DM10", "DM1011").replace("DM11", "DM1011")
                new_keys[new_key] = value
            else:
                new_keys[key] = value
        data[wpTuple[0]][wpTuple[1]] = new_keys       
    
    
    x_labels = ['Incl.', 'PT20 to 40', 'PT40 to 200']
    x_list=[0.25, 0.5, 0.75]
    fig, axes = plt.subplots(nrows=len(dm_bins), ncols=1, sharex=True,
                             figsize=(9, 10))
    if len(dm_bins) == 1:
        axes = [axes]

    for ax, dm in zip(axes, dm_bins):
        # dm_dict = {}
        up_errs = [None, None, None]
        fit_vals = [None, None, None]
        down_errs = [None, None, None]
        for key, _data in data[wpTuple[0]][wpTuple[1]].items():
            if key == dm or key.startswith(dm + "_"):
                if "PT20_40" in key:
                    if len(_data[20])==3:
                        fit_vals[1] = _data[20]["r"]
                        up_errs[1] = _data[20]["u"] - _data[20]["r"]
                        down_errs[1] = _data[20]["r"] - _data[20]["d"]
                    else:
                        fit_vals[1] = _data[20][20]["r"]
                        up_errs[1] = _data[20][20]["u"] - _data[20][20]["r"]
                        down_errs[1] = _data[20][20]["r"] - _data[20][20]["d"]
                elif "PT40_200" in key:
                    if len(_data[40])==3:
                        fit_vals[2] = _data[40]["r"]
                        up_errs[2] = _data[40]["u"] - _data[40]["r"]
                        down_errs[2] = _data[40]["r"] - _data[40]["d"]
                    else:
                        fit_vals[2] = _data[40][40]["r"]
                        up_errs[2] = _data[40][40]["u"] - _data[40][40]["r"]
                        down_errs[2] = _data[40][40]["r"] - _data[40][40]["d"]
                elif "PT" not in key:
                    fit_vals[0] = _data["r"]
                    up_errs[0] = _data["u"] - _data["r"]
                    down_errs[0] = _data["r"] - _data["d"]
                else:
                    print(f"[WARNING] Unexpected key: {key}. Skipping.")
                    breakpoint()
            else:
                continue
        none_index=[]
        if None in fit_vals or None in up_errs or None in down_errs:
            for i in range(3):
                if fit_vals[i] is None and up_errs[i] is None and down_errs[i] is None:
                    none_index.append(i)
                elif fit_vals[i] is None or up_errs[i] is None or down_errs[i] is None:
                    print(f"[WARNING] Broken {dm} bin {i}. Investigate!")
                    none_index.append(i)
                else:
                    continue
            if len(none_index) == 3:
                print(f"[ERROR] All fit values for {dm} bin are None. Skipping this bin.")
                continue 
            elif len(none_index) > 0:
                for i in none_index:
                    fit_vals[i] = 1.0 if id_es == "ID" else 0.0
                    up_errs[i] = 0.0
                    down_errs[i] = 0.0
                print(f"[WARNING] Broken {dm} bin {none_index}. Setting to nominal value.")
        
        print(f'fits:{fit_vals}',f'Upper errs {up_errs}', f'Lower errs {down_errs}')
        # Plot ID points with error bars.
        for i in range(3):
            ax.errorbar(x_list[i], fit_vals[i], yerr=[[down_errs[i]], [up_errs[i]]],
                        fmt='o',
                        color='b' if i not in none_index else 'r',
                        label=f"{id_es} fits")
        ax.set_xlim(0, 1)
        ax.axhline(y=1 if id_es == "ID" else 0, color='black', linestyle='--',
                   label="Nominal")
        # ax.set_title(f"{dm} bins")
        ax.set_ylabel(f"{dm}".replace("DM", "DM ").replace("1011", "10+11"), fontsize=18)
        
        ax.grid(True)
    axes[0].legend(loc='upper right', fontsize=16)
    axes[0].set_xticks(x_list, x_labels, fontsize=18)
    axes[0].tick_params(labelbottom=True, top=True, labeltop=True)  # Show ticks at the top
    axes[0].xaxis.set_label_position('top')
    axes[0].xaxis.tick_top()
    # Hide xtick labels on the subplots below
    for ax in axes[1:]:
        ax.tick_params(labelbottom=False)
    
    fig.suptitle(f'Corrections {era}(UL) ({wpTuple[0]} vsJets) ({wpTuple[1]} vsEle) T{id_es}', fontsize=18)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    # plt.title(f'Corrections {era} UL {wpTuple[0]}vsJets {wpTuple[1]}vsEle Tau{id_es} {channel}', loc='center', fontsize=14)
    # plt.tight_layout()
    plt.savefig(f"Tau{id_es}_{channel}_{wpTuple[0]}_{wpTuple[1]}_{tag}_{ntuple}.pdf")
    plt.savefig(f"Tau{id_es}_{channel}_{wpTuple[0]}_{wpTuple[1]}_{tag}_{ntuple}.png")
    plt.close(fig)


ntuple_tag_list=args.nTuple_tags.split(" ")
iter_tags = [(ntuple_tag_list[::2][i],ntuple_tag_list[1::2][i]) for i in range(len(ntuple_tag_list[::2]))]
cross_wps = [(x, y) for x in wps for y in wp_VSes]

for i in range(len(iter_tags)):
    iter_tags[i] += (cross_wps[i],)

print(f"\nGenerating summary plots for {wps} vsJets, \n{wp_VSes} vsEle, \nnTuple_tags: {ntuple_tag_list}:\n")
# breakpoint()
for tag,ntuple,wp_tuple in iter_tags:
    print(f"\nGenerating summary plots for {wp_tuple} (vsJets,vsEle), tag: {tag}, ntuple: {ntuple}")
    summary_SFs(data_dict, wp_tuple, tag, ntuple, id_es="ID")
    summary_SFs(data_dict_ES, wp_tuple, tag, ntuple, id_es="ES")
