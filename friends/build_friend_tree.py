import ROOT
import argparse
import yaml
import os
import glob
import time
from tqdm import tqdm
from multiprocessing import Pool, current_process, RLock
import XRootD.client.glob_funcs as xrdglob


def args_parser():
    parser = argparse.ArgumentParser(
        description="Generate xsec friend trees for SM-HTT analysis"
    )
    parser.add_argument(
        "--basepath",
        type=str,
        required=True,
        help="Basepath",
    )
    parser.add_argument(
        "--outputpath",
        type=str,
        required=True,
        help="Path to output directory",
    )
    parser.add_argument(
        "--nthreads",
        type=int,
        default=1,
        help="Number of threads to use",
    )
    parser.add_argument(
        "--dataset-config",
        type=str,
        default="datasets/datasets.yaml",
        help="path to the datasets.yaml",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="if set, debug mode will be enabled",
    )
    return parser.parse_args()


def parse_filepath(path):
    """
    filepaths always look like this:
    /$basepath/2018/samplenick/mt/samplenick_3.root
    so the channel is the [-2] element
    """
    splitted = path.split("/")
    data = {
        "era": splitted[-4],
        "channel": splitted[-2],
        "nick": splitted[-3],
    }

    return data


def convert_to_xrootd(path):
    if path.startswith("/storage/gridka-nrg/"):
        return path.replace(
            "/storage/gridka-nrg/",
            "root://xrootd-cms.infn.it///store/user/",
        )
    elif path.startswith("/ceph"):
        return path


def job_wrapper(args):
    return friend_producer(*args)


def friend_producer(
    inputfile, output_path, dataset_proc, era, channel, debug=False
):
    # filepath = os.path.dirname(inputfile).split("/")
    output_file = os.path.join(
        output_path, era, dataset_proc["nick"], channel, os.path.basename(inputfile)
    )
    if debug:
        print(f"Processing {inputfile}")
        print(f"Outputting to {output_file}")
    # remove outputfile if it exists
    # if os.path.exists(output_path):
    #     os.remove(output_path)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    # for data and embedded, we don't need to do anything
    if (
        dataset_proc["sample_type"] == "data"
        or dataset_proc["sample_type"] == "embedding"
    ):
        return
    # check if the output file is empty
    # print(f"Checking if {inputfile} is empty")
    try:
        rootfile = ROOT.TFile.Open(inputfile, "READ")
    except OSError:
        print(f"{inputfile} is broken")
        return
    # if the ntuple tree does not exist, the file is empty, so we can skip it
    if "ntuple" not in [x.GetTitle() for x in rootfile.GetListOfKeys()]:
        print(f"{inputfile} is empty, generating empty friend tree")
        if debug:
            print("Available keys: ", [x.GetTitle() for x in rootfile.GetListOfKeys()])
        # generate empty friend tree
        # friend_tree = ROOT.TFile(output_file, "CREATE")
        # tree = ROOT.TTree("ntuple", "")
        # tree.Write()
        # friend_tree.Close()
        rootfile.Close()
        print("done")
        return
    # else:
    # print(f"{inputfile} is not empty, generating friend tree")
    rdf = ROOT.RDataFrame("ntuple", rootfile)
    numberGeneratedEventsWeight = 1 / float(dataset_proc["nevents"])
    crossSectionPerEventWeight = float(dataset_proc["xsec"])
    negative_events_fraction = float(dataset_proc["generator_weight"])
    rdf = rdf.Define(
        "numberGeneratedEventsWeight",
        "(float){ngw}".format(ngw=numberGeneratedEventsWeight),
    )
    rdf = rdf.Define(
        "crossSectionPerEventWeight",
        "(float){xsec}".format(xsec=crossSectionPerEventWeight),
    )
    rdf = rdf.Define(
        "negative_events_fraction",
        "(float){negative_events_fraction}".format(
            negative_events_fraction=negative_events_fraction
        ),
    )
    rdf.Snapshot(
        "ntuple",
        output_file,
        [
            "numberGeneratedEventsWeight",
            "crossSectionPerEventWeight",
            "negative_events_fraction",
        ],
    )
    rootfile.Close()
    return


def generate_friend_trees(dataset, ntuples, nthreads, output_path, debug):
    print("Using {} threads".format(nthreads))
    arguments = [
        (
            ntuple,
            output_path,
            dataset[parse_filepath(ntuple)["nick"]],
            parse_filepath(ntuple)["era"],
            parse_filepath(ntuple)["channel"],
            debug,
        )
        for ntuple in ntuples
    ]
    pbar = tqdm(
        total=len(arguments),
        desc="Total progress",
        position=nthreads + 1,
        dynamic_ncols=True,
        leave=True,
    )
    with Pool(nthreads, initargs=(RLock(),), initializer=tqdm.set_lock) as pool:
        for result in pool.imap_unordered(job_wrapper, arguments):
            pbar.update(1)
    pool.close()
    pbar.close()


if __name__ == "__main__":
    args = args_parser()
    base_path = os.path.join(args.basepath, "*/*/*/*.root")
    output_path = os.path.join(args.outputpath)
    dataset = yaml.safe_load(open(args.dataset_config))
    if base_path.startswith("root://"):
        ntuples = xrdglob.glob(base_path)
    else:
        ntuples = glob.glob(base_path)
    # Remove data and embedded samples from ntuple list as friends are not needed for these
    ntuples_wo_data = list(filter(lambda ntuple: dataset[parse_filepath(ntuple)["nick"]]["sample_type"] != "data" and dataset[parse_filepath(ntuple)["nick"]]["sample_type"] != "embedding", ntuples))
    nthreads = args.nthreads
    if nthreads > len(ntuples_wo_data):
        nthreads = len(ntuples_wo_data)
    generate_friend_trees(
        dataset, ntuples_wo_data, nthreads, output_path, args.debug
    )
    print("Done")
