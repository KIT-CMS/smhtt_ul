#!/bin/bash

### Setup of CMSSW release
CMSSW=CMSSW_14_1_9

export SCRAM_ARCH=el9_amd64_gcc12
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project $CMSSW; pushd $CMSSW/src
eval `scramv1 runtime -sh`

git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v10.2.1
cd -

# CombineHarvester 
git clone git@github.com:cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester
git fetch origin
git checkout v3.0.0

# SM analysis specific code
git clone git@github.com:KIT-CMS/SMRun2Legacy.git SMRun2Legacy
cd SMRun2Legacy
git fetch origin
git checkout ul

# compile everything
CORES=`grep -c ^processor /proc/cpuinfo`
scramv1 b clean; scramv1 b -j $CORES
