#!/bin/bash
set -e
NTUPLETAG=$1
ERA=$2

KINGMAKER_BASEDIR="/store/user/sbrommer/CROWN/ntuples/${NTUPLETAG}/CROWNRun/"
KINGMAKER_BASEDIR_XROOTD="root://cmsxrootd-kit.gridka.de/${KINGMAKER_BASEDIR}"
XSEC_FRIENDS="/store/user/sbrommer/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/xsec/"

if [[ $ERA == *"2016"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2017"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2018"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
fi