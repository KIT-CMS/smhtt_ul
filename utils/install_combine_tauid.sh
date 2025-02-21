#!/bin/bash

### Setup of CMSSW release
export SCRAM_ARCH=el9_amd64_gcc12
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

CMSSW=CMSSW_14_1_0_pre4
cmsrel $CMSSW
cd $CMSSW/src/
cmsenv
git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit/
git fetch origin
git checkout v10.0.2
scramv1 b clean; scramv1 b -j 8
cd ../..
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester
git checkout v3.0.0
scram b -j 8
git clone git@github.com:KIT-CMS/SMRun2Legacy.git -b ul
git clone git@github.com:conformist89/TauIDSFMeasurement.git -b combined-fit
scram b -j 8
cd ../../..