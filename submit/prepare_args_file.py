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
    parser.add_argument("--pack-multiple-pipelines", default=None, type=int,
                        help="Run given number of pipelines in one job.")
    return parser.parse_args()


def write_file(output_dir, graph_file, job_nums, workdir):
    tmp_string = "{directory} {job_num} {file}\n"
    with open(os.path.join(output_dir, "arguments.txt"), "w") as f:
        for job_num in job_nums:
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


def prepare_multigraph_jobs(graph_inds, group_size):
    # Get loop index representing number of jobs after grouping minus one.
    num_jobs = len(graph_inds) // group_size
    grouped_inds = []
    for i in range(num_jobs):
        grouped_inds.append("{}-{}".format(graph_inds[i*group_size],
                                           graph_inds[i*group_size+group_size-1]
                                           ))
    # Check if only one graph remains. If more than one job remains
    if (len(graph_inds) % group_size) == 0:
        pass
    elif (len(graph_inds) % group_size) == 1:
        grouped_inds.append("{}".format(graph_inds[-1]))
    else:
        grouped_inds.append("{}-{}".format(graph_inds[(num_jobs)*group_size],
                                           graph_inds[-1]
                                           ))
    return grouped_inds


def main(args):
    with open(args.graph_file, "rb") as f:
        graphs = pickle.load(f)
    workdir = os.getcwd()
    num_singles, num_multi = split_multicore_jobs(graphs)
    if args.pack_multiple_pipelines is None:
        pass
    else:
        num_singles = prepare_multigraph_jobs(list(num_singles), args.pack_multiple_pipelines)
    write_file(args.output_dir, args.graph_file, num_singles, workdir)
    write_file_multicore(args.output_dir, args.graph_file, num_multi, workdir)
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
