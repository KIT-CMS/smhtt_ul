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
        for job_num in num_jobs:
            f.write(tmp_string.format(file=graph_file,
                                      job_num=job_num,
                                      directory=workdir))
    return


def write_file_multicore(output_dir, graph_file, num_jobs, workdir):
    tmp_string = "{directory} {job_num} 8 {file}\n"
    with open(os.path.join(output_dir, "arguments_multicore.txt"), "w") as f:
        for job_num in num_jobs:
            f.write(tmp_string.format(file=graph_file,
                                      job_num=job_num,
                                      directory=workdir))
    return


def split_multicore_jobs(graphs):
    # Split jobs in mulitcore and singlecore jobs in dependence of their number of children
    max_indices = {}
    for i, graph in enumerate(graphs):
        # Check if dataset has already been parsed
        if graph.name in max_indices:
            # Check if number of children is largest processed so far.
            if len(graph.children) > max_indices[graph.name]["val"]:
                max_indices[graph.name]["index"] = i
                max_indices[graph.name]["val"] = len(graph.children)
        else:
            max_indices[graph.name] = {"index": i, "val": len(graph.children)}
    mult_ind = [ind_dict["index"] for ind_dict in max_indices.values()]
    single_ind = set(range(len(graphs))) - set(mult_ind)
    return single_ind, mult_ind



def main(args):
    with open(args.graph_file, "rb") as f:
        graphs = pickle.load(f)
    workdir = os.getcwd()
    num_singles, num_multi = split_multicore_jobs(graphs)
    write_file(args.output_dir, args.graph_file, num_singles, workdir)
    write_file_multicore(args.output_dir, args.graph_file, num_multi, workdir)
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
