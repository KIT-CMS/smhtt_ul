#!/bin/bash


if [[ $(hostname) =~ centos7 ]]; then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc11-opt/setup.sh
elif [[ $(hostname) =~ bms || $(hostname) =~ portal1 ]]; then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
else
    source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
fi

export PYTHONPATH=$PWD:$PYTHONPATH
