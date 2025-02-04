# #!/bin/bash

# ### Setup of CMSSW release
# CMSSW=CMSSW_12_6_5

# export SCRAM_ARCH=slc7_amd64_gcc1000
# export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
# source $VO_CMS_SW_DIR/cmsset_default.sh

# scramv1 project $CMSSW; pushd $CMSSW/src
# eval `scramv1 runtime -sh`


# git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit


# # CombineHarvester 
# git clone git@github.com:cms-analysis/CombineHarvester.git CombineHarvester

# # SM analysis specific code
# git clone git@github.com:KIT-CMS/SMRun2Legacy.git CombineHarvester/SMRun2Legacy -b ul

# # Tau ID measurement repository
# git clone git@github.com:conformist89/TauIDSFMeasurement.git CombineHarvester/TauIDSFMeasurement -b combined-fit

# # compile everything
# # Build
# scram b clean
# scram b -j 24

# Nikitas porposal:
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

CMSSW=CMSSW_11_3_4
cmsrel $CMSSW
cd $CMSSW/src/
cmsenv
git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit/
git fetch origin
git checkout v9.2.1
scramv1 b clean; scramv1 b -j 8
cd ../..
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester
git checkout v2.1.0
scram b -j 8
git clone git@github.com:KIT-CMS/SMRun2Legacy.git -b ul
git clone git@github.com:conformist89/TauIDSFMeasurement.git -b combined-fit
scram b -j 8