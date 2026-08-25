#!/bin/bash


# if [[ $(hostname) =~ centos7 ]]; then
#     source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc11-opt/setup.sh
# elif [[ $(hostname) =~ bms || $(hostname) =~ portal1 || $(hostname) =~ deepthought ]]; then
#     source /cvmfs/sft.cern.ch/lcg/views/LCG_108/x86_64-el9-gcc15-opt/setup.sh
# else
#     echo "Unknown host, not sourcing any LCG environment"
#     exit 0
# fi

LCG_SETUP="/cvmfs/sft.cern.ch/lcg/views/LCG_108/x86_64-el9-gcc15-opt/setup.sh"

echo "[INFO] Trying to source LCG stack: ${LCG_SETUP}"

if [ ! -f "${LCG_SETUP}" ]; then
    echo "[ERROR] LCG setup file does not exist: ${LCG_SETUP}"
    echo "[ERROR] Exiting with code 0 to avoid failed Condor job."
    exit 0
fi

source "${LCG_SETUP}"
SOURCE_STATUS=$?

if [ ${SOURCE_STATUS} -ne 0 ]; then
    echo "[ERROR] Failed to source LCG stack: ${LCG_SETUP}"
    echo "[ERROR] source returned status ${SOURCE_STATUS}"
    echo "[ERROR] Exiting with code 0 to avoid failed Condor job."
    exit 0
fi

echo "[INFO] Successfully sourced LCG stack."

export PYTHONPATH=$PWD:$PYTHONPATH
