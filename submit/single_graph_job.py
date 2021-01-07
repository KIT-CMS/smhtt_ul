#!/usr/bin/env python

import os
import argparse
import pickle
import logging

from ntuple_processor import RunManager

logger = logging.getLogger("")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Input file containing the pickled graphs")
    parser.add_argument("-g", "--graph-number", type=str, help="Number of the graph to be processed.")
    parser.add_argument("-n", "--num-threads", type=int, default=1,
                        help="Number of threads to run on.")
    parser.add_argument("--output", type=str, default=None,
                        help="Alternative output root file for test purposes.")
    return parser.parse_args()


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def main(args):

    with open(args.input, "rb") as f:
        graphs = pickle.load(f)
        if "-" in args.graph_number:
            graph_ind = list(map(int, args.graph_number.split("-")))
            graph_to_process = graphs[graph_ind[0]:graph_ind[1]+1]
        else:
            graph_to_process = [graphs[int(args.graph_number)]]
    logger.info("Processing graph number {} out of {} graphs.".format(args.graph_number, len(graphs)))

    if "-" in args.graph_number:
        logger.info(graphs[graph_ind[0]:graph_ind[1]+1])
    else:
        logger.info(graphs[int(args.graph_number)])
    if args.output is None:
        output_file = os.path.join("output/shapes", os.path.basename(args.input).replace(".pkl", ""), "output-single_graph_job-{}-{}.root".format(
                                os.path.basename(args.input.replace(".pkl", "")),
                                args.graph_number.replace("-", "_")))
    else:
        output_file = args.output

    # Step 3: convert to RDataFrame and run the event loop
    r_manager = RunManager(graph_to_process)
    r_manager.run_locally(output_file, 1, args.num_threads)

    return

if __name__ == "__main__":
    args = parse_args()
    pathname = "log/{id}/".format(
        id=os.path.basename(args.input).replace(".pkl", ""))
    setup_logging(os.path.join(pathname, "single_graph_job-{id}-{num}.log".format(
                                        id=os.path.basename(args.input).replace(".pkl", ""),
                                        num=args.graph_number)),
                  level=logging.INFO)
    main(args)
