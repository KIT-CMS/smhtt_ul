#!/bin/bash
set -e

ERA=$1

#### ERA specific part. If a sample is not available comment it out here.
# Samples Run2016
basedir="/ceph/mburkart/Run2Legacy/ntuples/MSSM_Legacy/MSSM_2020_04_27_UseOfSMLegacy"
ARTUS_OUTPUTS_2016="$basedir/2016/ntuples/"
SVFit_Friends_2016="$basedir/2016/friends/SVFit/"
FF_Friends_2016="$basedir/2016/friends/FakeFactors/"
EMQCD_Friends_2016="$basedir/2016/friends/EMQCDWeights/"

# Samples Run2017
ARTUS_OUTPUTS_2017="$basedir/2017/ntuples/"
SVFit_Friends_2017="$basedir/2017/friends/SVFit/"
FF_Friends_2017="$basedir/2017/friends/FakeFactors/"
EMQCD_Friends_2017="$basedir/2017/friends/EMQCDWeights/"

# Samples Run2018
ARTUS_OUTPUTS_2018="$basedir/2018/ntuples/"
SVFit_Friends_2018="$basedir/2018/friends/SVFit/"
FF_Friends_2018="$basedir/2018/friends/FakeFactors/"
EMQCD_Friends_2018="$basedir/2018/friends/EMQCDWeights/"


# ERA handling
if [[ $ERA == *"2016"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2016
    SVFit_Friends=$SVFit_Friends_2016
    FF_Friends=$FF_Friends_2016
    EMQCD_Friends=$EMQCD_Friends_2016
elif [[ $ERA == *"2017"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2017
    SVFit_Friends=$SVFit_Friends_2017
    FF_Friends=$FF_Friends_2017
    EMQCD_Friends=$EMQCD_Friends_2017
elif [[ $ERA == *"2018"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2018
    SVFit_Friends=$SVFit_Friends_2018
    FF_Friends=$FF_Friends_2018
    EMQCD_Friends=$EMQCD_Friends_2018
fi

### channels specific friend tree.
# Used for example to process the event channel without including the fakefactor friends
ARTUS_FRIENDS_EM="$SVFit_Friends $EMQCD_Friends"
ARTUS_FRIENDS_ET="$SVFit_Friends"
ARTUS_FRIENDS_MT="$SVFit_Friends"
ARTUS_FRIENDS_TT="$SVFit_Friends"
ARTUS_FRIENDS="$SVFit_Friends"
ARTUS_FRIENDS_FAKE_FACTOR=$FF_Friends
