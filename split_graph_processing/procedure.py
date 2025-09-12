import logging
import pathlib
import argparse
import os
import pickle
import socket
from copy import deepcopy
from contextlib import nullcontext

from config.logging_setup_configs import setup_logging

from ntuple_processor import RunManager

logger = setup_logging(logger=logging.getLogger(__name__))

input_arg_parser = argparse.ArgumentParser()
input_arg_parser.add_argument("-i", "--input", type=str, help="Input file containing the pickled graphs")
input_arg_parser.add_argument("-o", "--output", type=str, default=None, help="Output directory for the produced root files")
input_arg_parser.add_argument("-m", "--mode", type=str, help="setup|run|hadd - working modes")
input_arg_parser.add_argument("-p", "--process", type=str, default=None, help="process to run")
input_arg_parser.add_argument("-idx", "--index", type=int, default=None, help="index of the unit block to process")
input_arg_parser.add_argument("-n", "--numworkers", type=int, default=1, help="Number of workers to use")


def create_argument_list(
    graphs,
    argument_file: str = pathlib.Path(__file__).parent / "argument_list.txt",
    output_path: str = pathlib.Path(__file__).parent / "tmp" / "_output",
    to_file: bool = False,
):
    with open(argument_file, "w") if to_file else nullcontext() as f:
        for graph in graphs:
            if graph.name != "EMB":
                continue
            for idx in range(len(graph.unit_block.ntuples)):
                if output_path is not None:
                    _output_path = output_path / graph.name / f"{idx}.root"
                    if _output_path.exists():
                        continue

                if to_file:
                    f.write(f"{graph.name} {idx}\n")
                else:
                    print(f"{graph.name} {idx}")
                if idx == 2:
                    break
            break


def get_subgraph(graphs, process, idx):
    for graph in graphs:
        if graph.name == process:
            _graph = deepcopy(graph)
            _graph.unit_block.ntuples = [deepcopy(graph.unit_block.ntuples[idx])]
            return [_graph]


def hadd(output_file):
    for file in pathlib.Path(__file__).parent / "tmp" / "_output".glob("**/*.root"):
        os.system(f"hadd -f {output_file} {file}")


if __name__ == "__main__":
    args = input_arg_parser.parse_args()

    with open(args.input, "rb") as f:
        graphs = pickle.load(f)

    if args.mode == "setup":
        create_argument_list(graphs)

    if args.mode == "run":
        (pathlib.Path(__file__).parent / "condor_jobs/").mkdir(parents=True, exist_ok=True)

        output_path = pathlib.Path(__file__).parent / "tmp" / "_output" / args.process / f"{args.index}.root"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logs_path = pathlib.Path(__file__).parent / "tmp" / "_logs" / args.process / f"{args.index}.log"
        logs_path.parent.mkdir(parents=True, exist_ok=True)

        logger = setup_logging(logger=logging.getLogger(f"{socket.gethostname()}.{__name__}"), output_file=logs_path)
        subgraph = get_subgraph(graphs, args.process, args.index)

        if not output_path.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)

            r_manager = RunManager(subgraph)
            r_manager.run_locally(str(output_path), args.numworkers, args.numworkers * 4)

    if args.mode == "hadd":
        hadd(args.output)
