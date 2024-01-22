#!/bin/bash
set -e
NTUPLETAG=$1
ERA=$2

KINGMAKER_BASEDIR="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNRun/"
KINGMAKER_BASEDIR_XROOTD="root://cmsxrootd-kit-disk.gridka.de/${KINGMAKER_BASEDIR}"
XSEC_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/xsec/"
FF_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/fake_factors_v1/"
RECO_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/mass_reco_v1/"

if [[ $ERA == *"2016"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2017"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2018"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
fi