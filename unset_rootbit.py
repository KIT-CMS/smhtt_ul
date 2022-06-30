import ROOT
import glob
import argparse
import os
from rich.progress import Progress

parser = argparse.ArgumentParser()
parser.add_argument("--basepath", type=str, required=True)
parser.add_argument("--check", action="store_true")
args = parser.parse_args()

# base_path = "ntuples/2018/*/*/*.root"
# dataset = yaml.load(open("datasets.yaml"), Loader=yaml.Loader)
base_path = os.path.join(args.basepath, "*/*/*.root")
ntuples = glob.glob(base_path)
with Progress() as progress:
    task = progress.add_task("Updating Statusbit...", total=len(ntuples))
    for ntuple in ntuples:
        # filename = os.path.basename(ntuple)
        # open the ntuple
        if args.check:
            # do a chort check if it worked
            print("Checking", ntuple)
            rfile = ROOT.TFile(ntuple, "READ")
            t = rfile.Get("ntuple")
            if t.TestBit(ROOT.TTree.EStatusBits.kEntriesReshuffled):
                print("kEntriesReshuffled bit is true")
            else:
                print("kEntriesReshuffled bit is false")
            rfile.Close()
        else:
            print("Updating {}".format(ntuple))
            rfile = ROOT.TFile(ntuple, "UPDATE")
            if "ntuple" not in [x.GetTitle() for x in rfile.GetListOfKeys()]:
                print("ntuple tree not found, continueing")
                rfile.Close()
                continue
            t = rfile.Get("ntuple")
            if t.TestBit(ROOT.TTree.EStatusBits.kEntriesReshuffled):
                print("Bit is set, resetting....")
                t.ResetBit(ROOT.TTree.EStatusBits.kEntriesReshuffled)
            rfile.Write()
            rfile.Close()
        progress.update(task, advance=1)
