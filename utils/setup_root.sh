#!/bin/bash


if [[ $(hostname) =~ centos7 ]]; then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc11-opt/setup.sh
elif [[ $(hostname) =~ bms || $(hostname) =~ portal1 || $(hostname) =~ deepthought ]]; then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_108/x86_64-el9-gcc15-opt/setup.sh
else
    echo "Unknown host, not sourcing any LCG environment"
    exit 0
fi

export PYTHONPATH=$PWD:$PYTHONPATH
