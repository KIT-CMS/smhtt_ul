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


def calculate_range(range_str):
    ran = list(map(int, range_str.split("_")))
    ran[-1] += 1
    return ran


def check_output_files(era, channel, process_string, control_arg):
    out_graph_ranges = list(fi.split("-")[-1].split(".root")[0]
                                for fi in os.listdir(
                                    os.path.join(
                                                 "output/shapes",
                                                 "{}_unit_graphs-{}-{}-{}".format(
                                                     control_arg,
                                                     era,
                                                     channel,
                                                     process_string))))
    out_nums = [list(range(*calculate_range(out_graphs)))
                        if "_" in out_graphs else int(out_graphs)
                        for out_graphs in out_graph_ranges]
    # Flatten the ouput list
    output_nums = []
    for entry in out_nums:
        if isinstance(entry, list):
            output_nums.extend(entry)
        else:
            output_nums.append(entry)
    return len(output_nums), set(output_nums)


def main(args):
    proc_dict = {
            "bkg": ["data,emb,ttj,ttl,ttt,vvj,vvl,vvt,w,zj,zl,ztt,ggh,gghww,qqh,qqhww,tth,wh,whww,zh,zhww"],
            "mssm_bbh": [os.environ["BBH_SAMPLES_SPLIT{}".format(i)] for i in range(1,3)],
            "mssm_ggh": [os.environ["GGH_SAMPLES_SPLIT{}".format(i)] for i in range(1,4)],
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
                                       "{}-{}-{}-{}-{}".format(args.era, ch, proc_str, 1 if args.control else 0, args.tag),
                                       "{}_unit_graphs-{}-{}-{}.pkl".format(c_arg, args.era, ch, proc_str)),
                          "rb") as f:
                    num_graphs = len(pickle.load(f))
                # Check number of output files.
                num_outputs, output_nums = check_output_files(args.era, ch, proc_str, c_arg)

                print("[INFO] Checking outputs for channel {} and processes {}"
                        .format( ch, proc_str))
                if num_graphs != num_outputs:
                    print("\033[93m[WARNING] Outputs missing for channel {}"
                          " and processes {}\033[0m".format(ch, proc_str))
                    # For deviations check which graphs are missing.
                    print("Missing outputs are {}".format(sorted(set(range(num_graphs)) - output_nums)))
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
