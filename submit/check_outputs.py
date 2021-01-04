#!/usr/bin/env python

import os
import argparse
import pickle

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--era", required=True, help="Submitted era.")
    parser.add_argument("-c", "--channels", default=["et", "mt", "tt", "em"],
                        nargs="*", help="Channels that have been submitted.")
    parser.add_argument("-t", "--tag", type=str, required=True,
                        help="Given tag of the submission.")
    parser.add_argument("--control", action="store_true", help="Check for control plots")
    return parser.parse_args()


def main(args):
    proc_dict = {
            "bkg": ["data,emb,ttj,ttl,ttt,vvj,vvl,vvt,w,zj,zl,ztt"],
            "sm_signals": ["ggh,gghww,qqh,qqhww,tth,wh,whww,zh,zhww"],
            "mssm_bbh": [os.environ["BBH_SAMPLES_SPLIT{}".format(i)] for i in range(1,3)],
            "mssm_ggh": [os.environ["GGH_SAMPLES_SPLIT{}".format(i)] for i in range(1,6)],
    }
    for ch in args.channels:
        for proc, proc_splits in proc_dict.items():
            if args.control and proc in ["mssm_bbh", "mssm_ggh"]:
                continue
            # Read number of graphs that should have been processed from pickled graph list.
            c_arg = "control" if args.control else "analysis"
            for proc_str in proc_splits:
                # Sort proc string for correct matching
                proc_str = ",".join(sorted(proc_str.split(",")))
                with open(os.path.join("output/submit_files",
                                       "{}-{}-{}-0-{}".format(args.era, ch, proc_str, args.tag),
                                       "{}_unit_graphs-{}-{}-{}.pkl".format(c_arg, args.era, ch, proc_str)),
                          "rb") as f:
                    num_graphs = len(pickle.load(f))
                # Check number of output files.
                num_outputs = len(
                        os.listdir(
                            os.path.join("output/shapes",
                                         "{}_unit_graphs-{}-{}-{}".format(
                                                                        c_arg,
                                                                        args.era,
                                                                        ch,
                                                                        proc_str)
                                         )))
                print("[INFO] Checking outputs for channel {} and processes {}"
                        .format( ch, proc_str))
                if num_graphs != num_outputs:
                    print("\033[93m[WARNING] Outputs missing for channel {}"
                          " and processes {}\033[0m".format(ch, proc_str))
                    # For deviations check which graphs are missing.
                    output_nums = set(
                            fi.split("-")[-1].split(".root")[0]
                                for fi in os.listdir(
                                    os.path.join(
                                                 "output/shapes",
                                                 "{}_unit_graphs-{}-{}-{}".format(
                                                     c_arg,
                                                     args.era,
                                                     ch,
                                                     proc_str))))
                    print("Missing outputs are {}".format(sorted(set(map(str, range(num_graphs))) - output_nums)))
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
