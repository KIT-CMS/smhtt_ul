#!/usr/bin/env python

import os
import argparse
import pickle
import logging

from ntuple_processor import RunManager
from shapes.produce_shapes import setup_logging

logger = logging.getLogger("")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Input file containing the pickled graphs")
    parser.add_argument("-g", "--graph-number", type=int, help="Number of the graph to be processed.")
    parser.add_argument("-n", "--num-threads", type=int, default=1,
                        help="Number of threads to run on.")
    return parser.parse_args()


def main(args):

    with open(args.input, "rb") as f:
        graphs = pickle.load(f)
        graph_to_process = graphs[args.graph_number]
    logger.info("Processing graph number {} out of {} graphs.".format(args.graph_number, len(graphs)))

    logger.info(graphs[args.graph_number])
    output_file = os.path.join("output/shapes", os.path.basename(args.input).replace(".pkl", ""), "output-single_graph_job-{}-{}.root".format(
                            os.path.basename(args.input.replace(".pkl", "")),
                            args.graph_number))

    # Step 3: convert to RDataFrame and run the event loop
    r_manager = RunManager([graph_to_process])
    r_manager.run_locally(output_file, 1, args.num_threads)

    return

if __name__ == "__main__":
    args = parse_args()
    pathname = "log/{id}/".format(
        id=os.path.basename(args.input).replace(".pkl", ""))
    setup_logging(os.path.join(pathname, "single_graph_job-{id}-{num}.log".format(
                                        id=pathname,
                                        num=args.graph_number)),
                  level=logging.INFO)
    main(args)