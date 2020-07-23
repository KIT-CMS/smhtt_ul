#!/usr/bin/env python

import os
import argparse
import pickle


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--graph-file",
                        help="The input file containing the graphs to be produced.")
    parser.add_argument("-o", "--output-dir",
                        help="The output directory the arguments file is written to.")
    return parser.parse_args()


def write_file(output_dir, graph_file, num_jobs, workdir):
    tmp_string = "{directory} {job_num} {file}\n"
    with open(os.path.join(output_dir, "arguments.txt"), "w") as f:
        for job_num in range(num_jobs):
            f.write(tmp_string.format(file=graph_file,
                                      job_num=job_num,
                                      directory=workdir))
    return


def main(args):
    with open(args.graph_file, "rb") as f:
        num_jobs = len(pickle.load(f))
    workdir = os.getcwd()
    write_file(args.output_dir, args.graph_file, num_jobs, workdir)
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
