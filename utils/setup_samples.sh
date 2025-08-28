#!/bin/bash
set -e

E=$1

#### ERA specific part. If a sample is not available comment it out here.
# Samples Run2016
basedir="/ceph/htautau/Run2Legacy_MSSM"
ARTUS_OUTPUTS_2016="$basedir/2016/ntuples/"
SVFit_Friends_2016="$basedir/2016/friends/SVFit/"
FF_Friends_2016="$basedir/2016/friends/FakeFactors_v5/"
NLOReweighting_Friends_2016="$basedir/2016/friends/NLOReweighting/"

# Samples Run2017
ARTUS_OUTPUTS_2017="$basedir/2017/ntuples/"
SVFit_Friends_2017="$basedir/2017/friends/SVFit/"
FF_Friends_2017="$basedir/2017/friends/FakeFactors_v5/"
NLOReweighting_Friends_2017="$basedir/2017/friends/NLOReweighting/"

# Samples Run2018
ARTUS_OUTPUTS_2018="$basedir/2018/ntuples/"
SVFit_Friends_2018="$basedir/2018/friends/SVFit/"
FF_Friends_2018="$basedir/2018/friends/FakeFactors_v5/"
NLOReweighting_Friends_2018="$basedir/2018/friends/NLOReweighting/"

# Samples Run2022preEE
ARTUS_OUTPUTS_2022preEE="$basedir/2022preEE/ntuples/"
SVFit_Friends_2022preEE="$basedir/2022preEE/friends/SVFit/"
#FF_Friends_2022preEE="$basedir/2022preEE/friends/FakeFactors_v5/"
NLOReweighting_Friends_2022preEE="$basedir/2022preEE/friends/NLOReweighting/"

# Samples Run2022postEE
ARTUS_OUTPUTS_2022postEE="$basedir/2022postEE/ntuples/"
SVFit_Friends_2022postEE="$basedir/2022postEE/friends/SVFit/"
#FF_Friends_2022postEE="$basedir/2022postEE/friends/FakeFactors_v5/"
NLOReweighting_Friends_2022postEE="$basedir/2022postEE/friends/NLOReweighting/"

# Samples Run2023preBPix
ARTUS_OUTPUTS_2023preBPix="$basedir/2023preBPix/ntuples/"
SVFit_Friends_2023preBPix="$basedir/2023preBPix/friends/SVFit/"
#FF_Friends_2023preBPix="$basedir/2023preBPix/friends/FakeFactors_v5/"
NLOReweighting_Friends_2023preBPix="$basedir/2023preBPix/friends/NLOReweighting/"

# Samples Run2023postBPix
ARTUS_OUTPUTS_2023postBPix="$basedir/2023postBPix/ntuples/"
SVFit_Friends_2023postBPix="$basedir/2023postBPix/friends/SVFit/"
#FF_Friends_2023postBPix="$basedir/2023postBPix/friends/FakeFactors_v5/"
NLOReweighting_Friends_2023postBPix="$basedir/2023postBPix/friends/NLOReweighting/"

# Samples Run2024
ARTUS_OUTPUTS_2024="$basedir/2024/ntuples/"
SVFit_Friends_2024="$basedir/2024/friends/SVFit/"
#FF_Friends_2024="$basedir/2024/friends/FakeFactors_v5/"
NLOReweighting_Friends_2024="$basedir/2024/friends/NLOReweighting/"

# ERA handling
if [[ $E == *"2016"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2016
    SVFit_Friends=$SVFit_Friends_2016
    FF_Friends=$FF_Friends_2016
    NLOReweighting_Friends=$NLOReweighting_Friends_2016
elif [[ $E == *"2017"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2017
    SVFit_Friends=$SVFit_Friends_2017
    FF_Friends=$FF_Friends_2017
    NLOReweighting_Friends=$NLOReweighting_Friends_2017
elif [[ $E == *"2018"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2018
    SVFit_Friends=$SVFit_Friends_2018
    FF_Friends=$FF_Friends_2018
    NLOReweighting_Friends=$NLOReweighting_Friends_2018
elif [[ $E == *"2022preEE"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2022preEE
    SVFit_Friends=$SVFit_Friends_2022preEE
    #FF_Friends=$FF_Friends_2022preEE
    NLOReweighting_Friends=$NLOReweighting_Friends_2022preEE
elif [[ $E == *"2022postEE"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2022postEE
    SVFit_Friends=$SVFit_Friends_2022postEE
    #FF_Friends=$FF_Friends_2022postEE
    NLOReweighting_Friends=$NLOReweighting_Friends_2022postEE
elif [[ $E == *"2023preBPix"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2023preBPix
    SVFit_Friends=$SVFit_Friends_2023preBPix
    #FF_Friends=$FF_Friends_2023preBPix
    NLOReweighting_Friends=$NLOReweighting_Friends_2023preBPix
elif [[ $E == *"2023postBPix"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2023postBPix
    SVFit_Friends=$SVFit_Friends_2023postBPix
    #FF_Friends=$FF_Friends_2023postBPix
    NLOReweighting_Friends=$NLOReweighting_Friends_2023postBPix
elif [[ $E == *"2024"* ]]
then
    ARTUS_OUTPUTS=$ARTUS_OUTPUTS_2024
    SVFit_Friends=$SVFit_Friends_2024
    #FF_Friends=$FF_Friends_2024
    NLOReweighting_Friends=$NLOReweighting_Friends_2024
fi

### channels specific friend tree.
# Used for example to process the event channel without including the fakefactor friends
ARTUS_FRIENDS_EM="$SVFit_Friends $NLOReweighting_Friends"
ARTUS_FRIENDS_ET="$SVFit_Friends $NLOReweighting_Friends"
ARTUS_FRIENDS_MT="$SVFit_Friends $NLOReweighting_Friends"
ARTUS_FRIENDS_TT="$SVFit_Friends $NLOReweighting_Friends"
ARTUS_FRIENDS="$SVFit_Friends $NLOReweighting_Friends"
ARTUS_FRIENDS_FAKE_FACTOR=$FF_Friends
