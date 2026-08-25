#!/bin/bash
set -e
CHANNEL=${1}
ERA=${2}
NTUPLETAG=${3}
TAG=${4}
MODE=${5}
WP=${6}
WP_VSe=${7}

# output_shapes="tauid_shapes-${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/shapes_condor/${NTUPLETAG}/${ERA}-${TAG}/${WP}/${WP_VSe}/${CHANNEL}
shapes_output_ctrl=output/shapes_ctrl/${NTUPLETAG}/${ERA}-${TAG}/${WP}/${WP_VSe}/${CHANNEL}
shapes_output="output/shapes/${NTUPLETAG}/${ERA}-${TAG}/${WP}/${WP_VSe}/${CHANNEL}"
shapes_output_synced="output/shapes_synced/${NTUPLETAG}/${ERA}-${TAG}/${WP}/${WP_VSe}/${CHANNEL}"
shapes_rootfile_ctrl=${shapes_output_ctrl}/m_vis.root
shapes_rootfile=${shapes_output}/m_vis.root

echo "My condor output path is: ${CONDOR_OUTPUT}"
echo "My control output path is: ${shapes_output_ctrl}"
echo "My out path is: ${shapes_output}"
echo "My synchpath is ${shapes_output_synced}"

if [ ! -d "${shapes_output_ctrl}" ]; then
    mkdir -p ${shapes_output_ctrl}
fi
if [ ! -d "${shapes_output}" ]; then
    mkdir -p ${shapes_output}
fi