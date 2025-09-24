#!/bin/bash

export SCRAM_ARCH=el9_amd64_gcc12
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

# pushd CMSSW_14_1_9/src
pushd CMSSW_14_1_9/src
eval `scramv1 runtime -sh`
popd
