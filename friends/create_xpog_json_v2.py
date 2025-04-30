from unicodedata import category
import correctionlib._core as core
import correctionlib.schemav2 as schema
import correctionlib.JSONEncoder as JSONEncoder
import ROOT
import json
import argparse
import glob
import os
from typing import Union
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser


class CorrectionSet(object):
    def __init__(self, name):
        self.name = name
        self.corrections = []

    def add_correction_file(self, correction_file):
        with open(correction_file) as file:
            data = json.load(file)
            corr = schema.Correction.parse_obj(data)
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
            "DM11_PT20_40": 20,
            "DM0_PT40_200": 40,
            "DM1_PT40_200": 40,
            "DM10_PT40_200": 40,
            "DM11_PT40_200": 40,
        }
        self.dm_binning = {
            "DM0": 0,
            "DM1": 1,
            "DM10": 10,
            "DM11": 11,
        }
        # self.pt_to_dm = {
        #     "DM0_PT20_40": 0,
        #     "DM1_PT20_40": 1,
        #     "DM10_PT20_40": 10,
        #     "DM11_PT20_40": 11,
        #     "DM0_PT40_200": 0,
        #     "DM1_PT40_200": 1,
        #     "DM10_PT40_200": 10,
        #     "DM11_PT40_200": 11,
        # }
        
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
                "description": "DeepTau2017v2p1VSjet working point: VVVLoose-VVTight"
                },
                { "name": "wp_VSe",
                "type": "string",
                "description": "DeepTau2017v2p1VSe working point: VVLoose,Tight"
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
                "description": "pT-dependent scale factor",
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
                        "input": "vsele_wp",
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
                                                    {"key": "nom", "value": self.get_tauID_sf(pt, "nom", isPt=True, wp=wp, wp_VSe=wp_VSe, dm=dm)},
                                                    {"key": "up", "value": self.get_tauID_sf(pt, "up", isPt=True, wp=wp, wp_VSe=wp_VSe, dm=dm)},
                                                    {"key": "down", "value": self.get_tauID_sf(pt, "down", isPt=True, wp=wp, wp_VSe=wp_VSe, dm=dm)},
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
        return schema.Category.parse_obj(data)


    def setup_dm_scheme(self):
        self.correctionset = {
            "version": 0,
            "name": self.name,
            "description": "dm-dependent tau ID scale factor for tau embedded samples",
            "inputs": [
                # Not needed here, right ???
                # { "name": "pt",
                # "type": "real",
                # "description": "Reconstructed tau pT"
                # },
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
                "description": "DeepTau2017v2p1VSjet working point: VVVLoose-VVTight"
                },
                { "name": "wp_VSe",
                "type": "string",
                "description": "DeepTau2017v2p1VSe working point: VVLoose,Tight"
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
                                                "nodetype": "category",
                                                "input": "syst",
                                                "content": [
                                                    {"key": "nom","value": self.get_tauID_sf(dm,"nom",isDM=True, wp=wp, wp_VSe=wp_VSe)},
                                                    {"key": "up","value": self.get_tauID_sf(dm, "up", isDM=True, wp=wp, wp_VSe=wp_VSe)},
                                                    {"key": "down","value": self.get_tauID_sf(dm, "down", isDM=True, wp=wp, wp_VSe=wp_VSe)},
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
        
        return schema.Category.parse_obj(data)

    def get_tauID_sf(self, variable: Union[str,int], variation: str, isPt=False, isDM=False, dm=9000, wp="Medium", wp_VSe="VVLoose"):
        if isPt:
            if variable == 20:
                dm_pt = f"DM{dm}_PT{variable}_40"
            elif variable == 40:
                dm_pt = f"DM{dm}_PT{variable}_200"
            data = self.data[wp][wp_VSe]
            for bin in data[dm_pt].keys():
                if variable == bin:
                    if variation == "nom":
                        return data[dm_pt][bin]["r"]
                    elif variation == "up":
                        return data[dm_pt][bin]["u"]
                    elif variation == "down":
                        return data[dm_pt][bin]["d"]
                    else:
                        raise ValueError(f"Invalid variation: {variation}")
        elif isDM:
            data = self.data[wp][wp_VSe]
            for bin in data.keys():
                if variable == bin:
                    if variation == "nom":
                        return data[bin]["r"]
                    elif variation == "up":
                        return data[bin]["u"]
                    elif variation == "down":
                        return data[bin]["d"]
                    else:
                        raise ValueError(f"Invalid variation: {variation}")
        else:
            raise ValueError("Invalid argument")

    def generate_dm_pt_scheme(self):
        self.parse_config()
        self.setup_dm_pt_scheme()
        self.correctionset["data"] = self.generate_dm_pt_sfs()
        output_corr = schema.Correction.parse_obj(self.correctionset)
        self.correction = output_corr
        # print(JSONEncoder.dumps(self.correction))

    def generate_dm_scheme(self):
        self.parse_config()
        self.setup_dm_scheme()
        self.correctionset["data"] = self.generate_dm_sfs()
        output_corr = schema.Correction.parse_obj(self.correctionset)
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
    
    all_dicts = []
    
    for filename in filenames:
        f = ROOT.TFile(filename)
        if f == None:
            raise Exception("[ERROR] File {} not found.".format(filename))
        wp_param = f.Get("WP")
        wp_VSe_param = f.Get("WP_VSe")
        wp = wp_param.GetTitle()
        wp_VSe = wp_VSe_param.GetTitle()
        tree = f.Get("limit")
        if tree == None:
            raise Exception(
                "[ERROR] Tree {} not found in file {}.".format("limit", filename)
            )

        indices = {}
        count = 1
        results = {}
        binname = []
        for key in tree.GetListOfBranches():
            name = key.GetName()
            for sig_bin in sig_bins:
                if name == "r_EMB_" + sig_bin:
                    indices[name] = count
                    count += 2
                    results[name] = [-999, -999, -999]
                    binname += (sig_bin,)
                    break
            if binname:
                break
        
        if not binname:
            print(f"[ERROR] Nothing found in file {filename}.")
            continue
        
        values_lst = []
        for i, row in enumerate(tree):
            for name in indices:
                values_lst.append(getattr(row, name))

        if len(values_lst) != 5:
            print(f'[ERROR] Wrong number of results found in file {filename}: {len(values_lst)} instead of 5. File is skipped!\n")')
            continue
            
        data = {}
        results_list = values_lst[2:].copy()
        if results_list[1] <= results_list[0] <= results_list[2]: 
            data["r"] = results_list[0]
            data["d"] = results_list[1]
            data["u"] = results_list[2]
        else:
            print('[ERROR] Ordering is wrong. Investigate! Errors with float precision possible.')
            breakpoint()
        
        bin_data = {}
        wp_data = {}
        wp_VSe_data = {}
        
        bin_data[binname[0]] = data
        wp_VSe_data[wp_VSe] = bin_data
        wp_data[wp] = wp_VSe_data
        all_dicts += (wp_data,)
    
    if len(all_dicts) > 1:
        main_dict = {}
        for _dcit in all_dicts:
            main_dict = recursive_update(main_dict, _dcit)
        return main_dict
    elif len(all_dicts) == 1:
        return all_dicts[0]
    else:
        return ValueError("Creation of ")

# first a simple argparser to the the datacard directory
parser = argparse.ArgumentParser(description="Plot the tau ID SF")
# parser.add_argument("--wp", type=str, default="Tight", help="TauID WP")
# parser.add_argument("--wp_vsele", type=str, default="Tight", help="TauID WP_VsEle")
parser.add_argument("--user_out_tag", type=str, default="", help="Tag")
parser.add_argument("--era", type=str, default="2018", help="2016, 2017 or 2018")
parser.add_argument("--channel", type=str, default="mt", help="mt, et, em, tt")
parser.add_argument("--dm_pt_input_files", type=str, default="", help="DM-Pt input_files")
parser.add_argument("--input_files", type=str, default="", help="DM input_files")
parser.add_argument("--binnames", type=str, default="DM0,DM1,DM10_11,DM10,DM11,DM0_PT20_40,DM1_PT20_40,DM10_PT20_40,DM11_PT20_40,DM0_PT40_200,DM1_PT40_200,DM10_PT40_200,DM11_PT40_200", help="Binnames, no spaces allowed!")

args = parser.parse_args()

fitfiles = args.input_files.split(",") #+ "cmb/higgsCombine.multidim_dm_fit.MultiDimFit.mH125.root"
binnames = args.binnames.split(",")



data_dict = load_fitresults_from_files(fitfiles, binnames)

correctionset = CorrectionSet("TauID_SF")

# pt
correction_dm_pt = TauID(
    tag="tag",
    name="TauID_deeptau2p1_sf_emb_ptbinned",
    data=data_dict,
    era=args.era,outdir="/"
)

correction_dm_pt.generate_dm_pt_scheme()
# dm
correction_dm = TauID(
    tag="tag",
    name="TauID_deeptau2p1_sf_emb_dmbinned",
    data=data_dict,
    era=args.era,
    outdir="/"
)

correction_dm.generate_dm_scheme()

correctionset.add_correction(correction_dm_pt)
correctionset.add_correction(correction_dm)
correctionset.write_json(
    "TauID_"
    + str(args.era)
    + "_UL_"
    + str(args.channel)
    + "_"
    + str(args.user_out_tag)
    + ".json"
)
