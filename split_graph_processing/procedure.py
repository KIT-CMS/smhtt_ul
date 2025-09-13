import argparse
import logging
import os
import pathlib
import pickle
import socket
import time
from contextlib import nullcontext
from copy import deepcopy
from itertools import islice
from typing import Callable, Dict, Iterable, List, Set, Tuple, Union

from config.logging_setup_configs import setup_logging
from ntuple_processor import RunManager

logger = setup_logging(logger=logging.getLogger(__name__))

input_arg_parser = argparse.ArgumentParser()
input_arg_parser.add_argument("-i", "--input", type=str, help="Input file containing the pickled graphs")
input_arg_parser.add_argument("-o", "--output", type=str, default=None, help="Output directory for the produced root files")
input_arg_parser.add_argument("-m", "--mode", type=str, help="setup|run|hadd|combine_daemon - working modes")
input_arg_parser.add_argument("-p", "--process", type=str, default=None, help="process to run")
input_arg_parser.add_argument("-idx", "--index", type=int, default=None, help="index of the unit block to process")
input_arg_parser.add_argument("-n", "--numworkers", type=int, default=1, help="Number of workers to use")
input_arg_parser.add_argument("-a", "--argument-file", type=str, default=None, help="File to write argument list to")

def _batched(iterable, n):
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        yield batch

class GraphProcessor:
    def __init__(
        self,
        graphs_path: str,
        output_path: str = pathlib.Path(__file__).parent / "tmp" / "_output",
        processed_path: str = pathlib.Path(__file__).parent / "tmp" / "processed.archive",
    ) -> None:
        self.graphs_path = graphs_path
        self.output_path = output_path
        self.processed_path = processed_path

        self._graphs = None
        self._all_files = None

    @property
    def graphs(self) -> List[Callable]:
        if self._graphs is None:
            with open(self.graphs_path, "rb") as f:
                self._graphs = pickle.load(f)
        return self._graphs

    @property
    def all_files(self) -> Set[pathlib.Path]:
        if self._all_files is None:
            self._all_files = {
                self.output_path / graph.name / f"{idx}.root"
                for graph in self.graphs
                for idx in range(len(graph.unit_block.ntuples))
            }
        return self._all_files

    @property
    def processed(self) -> Set[pathlib.Path]:
        if not self.processed_path.exists():
            return set()
        with open(self.processed_path, "r") as f:
            return {pathlib.Path(line.strip()) for line in f}

    def add_processed(self, files: Union[pathlib.Path, str, Iterable[Union[pathlib.Path, str]]]) -> None:
        if isinstance(files, (str, pathlib.Path)):
            files = [files]
        with open(self.processed_path, "a") as f:
            for file in files:
                f.write(str(file) + "\n")

    def argument_list(self, argument_file: Union[str, None] = None) -> list[str]:
        with open(argument_file, "w") if argument_file is not None else nullcontext() as f:
            for file in sorted(list(set(self.all_files) - set(self.processed))):
                if file.exists() or str(file) in self.processed:
                    continue
                
                process, idx = file.parent.name, int(file.stem)
                
                if argument_file is not None:
                    f.write(f"{process} {idx}\n")
                else:
                    print(f"{process} {idx}")
    
    def subgraph(self, process: str, idx: int) -> List[Callable]:
        for graph in self.graphs:
            if graph.name == process:
                _graph = deepcopy(graph)
                _graph.unit_block.ntuples = [deepcopy(graph.unit_block.ntuples[idx])]
                return [_graph]
    
    def run_subgraph(self, process: str, idx: int, numworkers: int = 1) -> None:
        subgraph = self.subgraph(process, idx)

        output_path = self.output_path / process / f"{idx}.root"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        r_manager = RunManager(subgraph)
        r_manager.run_locally(str(output_path), numworkers, numworkers * 4)

    def incremental_hadd(self, output_file: str, older_than: int = 60, batch_size: int = 50) -> None:
        output_file = pathlib.Path(output_file)
        currently_processed = self.processed

        to_add_files = [
            _file
            for _file in (pathlib.Path(__file__).parent / "tmp" / "_output").glob("**/*.root")
            if time.time() - _file.stat().st_mtime >= older_than and _file not in currently_processed
        ]

        for files_batch in _batched(to_add_files, batch_size):
            logger.info(f"Adding files: {files_batch}")

            if not output_file.exists():
                tmp_output = None
                cmd = f"hadd -f {output_file} {' '.join(map(str, files_batch))}"
            else:
                tmp_output = output_file.with_suffix(".tmp.root")
                cmd = f"hadd -f {tmp_output} {output_file} {' '.join(map(str, files_batch))}"
            
            logger.info(f"Running command: {cmd}")
            result = os.system(cmd)

            if result == 0:
                if tmp_output is not None:
                    tmp_output.replace(output_file)
                self.add_processed(files_batch)
                for file in files_batch:
                    os.remove(file)
            else:
                logger.error(f"Command failed with exit code {result}: {cmd}")

    def incremental_hadd_daemon(self, output_file: str, wait: int = 60, interval: int = 120) -> None:
        while True:
            if self.all_files.issubset(self.processed):
                logger.info("All files processed. Exiting daemon.")
                break
            self.incremental_hadd(output_file, wait)
            time.sleep(interval)


if __name__ == "__main__":
    args = input_arg_parser.parse_args()
    graphs_manager = GraphProcessor(args.input)

    with open(args.input, "rb") as f:
        graphs = pickle.load(f)

    if args.mode == "setup":
        graphs_manager.argument_list(argument_file=args.argument_file)
    
    if args.mode == "run":
        assert args.process is not None, "Please provide a process to run"
        assert args.index is not None, "Please provide an index to run"
        (pathlib.Path(__file__).parent / "condor_jobs/").mkdir(parents=True, exist_ok=True)
        graphs_manager.run_subgraph(args.process, args.index, args.numworkers)
    

    if args.mode == "combine_daemon":
        if args.output is None:
            raise ValueError("Please provide an output file when using combine_daemon mode")
        graphs_manager.incremental_hadd_daemon(args.output)
