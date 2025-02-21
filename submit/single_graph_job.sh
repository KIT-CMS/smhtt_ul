#!/bin/bash
ulimit -s unlimited

source /cvmfs/grid.cern.ch/alma9-ui-test/etc/profile.d/setup-alma9-test.sh

export X509_USER_PROXY=$1
INPUT=$2
GRAPH=$3
PROC_DIR=$4
THREAD_ARG="--num-threads 1"
[[ -z $5 ]] || THREAD_ARG="--num-threads $5"

echo "INPUT: $INPUT"
echo "GRAPH: $GRAPH"
echo "PROC_DIR: $PROC_DIR"
echo "THREAD_ARG: $THREAD_ARG"

pushd $PROC_DIR

INP_BASE=$(basename $INPUT)
if [[ ! -d output/shapes/${INP_BASE%.pkl} ]]
then
    mkdir -p output/shapes/${INP_BASE%.pkl}
fi

source utils/setup_root.sh

echo "Running 'python submit/single_graph_job.py --input $INPUT --graph-number $GRAPH $THREAD_ARG'"
python submit/single_graph_job.py --input $INPUT --graph-number $GRAPH $THREAD_ARG
