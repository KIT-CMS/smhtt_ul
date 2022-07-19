#!/bin/bash
set -e
NTUPLETAG=$1
ERA=$2


basedir="/storage/gridka-nrg/sbrommer/CROWN/ntuples/${NTUPLETAG}/CROWNRun/"
NTUPLES_2016="$basedir"
# SVFit_Friends_2016="$basedir/2016/friends/SVFit/"
# FF_Friends_2016="$basedir/2016/friends/FakeFactors_v5/"
# NLOReweighting_Friends_2016="$basedir/2016/friends/NLOReweighting/"

# # Samples Run2017
NTUPLES_2017="$basedir"
# SVFit_Friends_2017="$basedir/2017/friends/SVFit/"
# FF_Friends_2017="$basedir/2017/friends/FakeFactors_v5/"
# NLOReweighting_Friends_2017="$basedir/2017/friends/NLOReweighting/"

# Samples Run2018
NTUPLES_2018="$basedir"
xsec_friends_2018="/ceph/sbrommer/smhtt_ul/${NTUPLETAG}/friends/xsec"
# SVFit_Friends_2018="$basedir/2018/friends/SVFit/"
# FF_Friends_2018="$basedir/2018/friends/FakeFactors_v5/"
# NLOReweighting_Friends_2018="$basedir/2018/friends/NLOReweighting/"


# ERA handling
if [[ $ERA == *"2016"* ]]
then
    NTUPLES=$NTUPLES_2016
    # SVFit_Friends=$SVFit_Friends_2016
    # FF_Friends=$FF_Friends_2016
    # NLOReweighting_Friends=$NLOReweighting_Friends_2016
elif [[ $ERA == *"2017"* ]]
then
    NTUPLES=$NTUPLES_2017
    # SVFit_Friends=$SVFit_Friends_2017
    # FF_Friends=$FF_Friends_2017
    # NLOReweighting_Friends=$NLOReweighting_Friends_2017
elif [[ $ERA == *"2018"* ]]
then
    NTUPLES=$NTUPLES_2018
    XSEC_FRIENDS=$xsec_friends_2018
    # SVFit_Friends=$SVFit_Friends_2018
    # FF_Friends=$FF_Friends_2018
    # NLOReweighting_Friends=$NLOReweighting_Friends_2018
fi

### channels specific friend tree.
# Used for example to process the event channel without including the fakefactor friends
# ARTUS_FRIENDS_EM="$SVFit_Friends $NLOReweighting_Friends"
# ARTUS_FRIENDS_ET="$SVFit_Friends $NLOReweighting_Friends"
# ARTUS_FRIENDS_MT="$SVFit_Friends $NLOReweighting_Friends"
# ARTUS_FRIENDS_TT="$SVFit_Friends $NLOReweighting_Friends"
# ARTUS_FRIENDS="$SVFit_Friends $NLOReweighting_Friends"
# ARTUS_FRIENDS_FAKE_FACTOR=$FF_Friends
FRIENDS="$XSEC_FRIENDS"