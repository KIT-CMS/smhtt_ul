#!/bin/bash
set -e
NTUPLETAG=$1
ERA=$2

KINGMAKER_BASEDIR="/storage/gridka-nrg/sbrommer/CROWN/ntuples/${NTUPLETAG}/CROWNRun/"
KINGMAKER_BASEDIR_XROOTD="root://cmsxrootd-kit.gridka.de//store/user/sbrommer/CROWN/ntuples/${NTUPLETAG}/CROWNRun/"

# BASEFOLDER="/storage/9/sbrommer/smhtt_ul/${NTUPLETAG}"
BASEFOLDER="/ceph/sbrommer/smhtt_ul/${NTUPLETAG}"
BASEDIR="$BASEFOLDER/ntuples/"
NTUPLES_2016="$BASEDIR/ntuples/"
# SVFit_Friends_2016="$BASEDIR/2016/friends/SVFit/"
# FF_Friends_2016="$BASEDIR/2016/friends/FakeFactors_v5/"
# NLOReweighting_Friends_2016="$BASEDIR/2016/friends/NLOReweighting/"

# # Samples Run2017
NTUPLES_2017="$BASEFOLDER/ntuples/"
# SVFit_Friends_2017="$BASEDIR/2017/friends/SVFit/"
# FF_Friends_2017="$BASEDIR/2017/friends/FakeFactors_v5/"
# NLOReweighting_Friends_2017="$BASEDIR/2017/friends/NLOReweighting/"

# Samples Run2018
NTUPLES_2018="$BASEFOLDER/ntuples/"
# XSEC_FRIENDS_2018="/ceph/sbrommer/smhtt_ul/${NTUPLETAG}/friends/xsec"
# FF_FRIENDS_2018="/ceph/sbrommer/smhtt_ul/${NTUPLETAG}/friends/FakeFactors"
XSEC_FRIENDS_2018="$BASEFOLDER/friends/xsec"
FF_FRIENDS_2018="$BASEFOLDER/friends/FakeFactors"
FASTMTT_FRIENDS_2018="$BASEFOLDER/friends/FastMTT"
# SVFit_Friends_2018="$BASEDIR/2018/friends/SVFit/"
# FF_Friends_2018="$BASEDIR/2018/friends/FakeFactors_v5/"
# NLOReweighting_Friends_2018="$BASEDIR/2018/friends/NLOReweighting/"

# ERA handling
if [[ $ERA == *"2016"* ]]; then
    NTUPLES=$NTUPLES_2016
    # SVFit_Friends=$SVFit_Friends_2016
    # FF_Friends=$FF_Friends_2016
    # NLOReweighting_Friends=$NLOReweighting_Friends_2016
elif [[ $ERA == *"2017"* ]]; then
    NTUPLES=$NTUPLES_2017
    # SVFit_Friends=$SVFit_Friends_2017
    # FF_Friends=$FF_Friends_2017
    # NLOReweighting_Friends=$NLOReweighting_Friends_2017
elif [[ $ERA == *"2018"* ]]; then
    NTUPLES=$NTUPLES_2018
    XSEC_FRIENDS=$XSEC_FRIENDS_2018
    FASTMTT_FRIENDS=$FASTMTT_FRIENDS_2018
    # SVFit_Friends=$SVFit_Friends_2018
    FF_FRIENDS=$FF_FRIENDS_2018
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
FRIENDS="$XSEC_FRIENDS $FF_FRIENDS"
