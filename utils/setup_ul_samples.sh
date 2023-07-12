#!/bin/bash
set -e
NTUPLETAG=$1
ERA=$2

KINGMAKER_BASEDIR="/store/user/olavoryk/CROWN_17_16/ntuples/${NTUPLETAG}/CROWNRun/"
KINGMAKER_BASEDIR_XROOTD="root://cmsxrootd-kit.gridka.de/${KINGMAKER_BASEDIR}"
XSEC_FRIENDS="/store/user/olavoryk/CROWN_17_16/ntuples/${NTUPLETAG}/CROWNFriends/xsec/"

if [[ $ERA == *"2016"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2017"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2018"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
fi