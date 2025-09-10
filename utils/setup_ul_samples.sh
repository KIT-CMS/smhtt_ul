#!/bin/bash
set -e
NTUPLETAG=$1
ERA=$2

KINGMAKER_BASEDIR="/store/user/${USER}/CROWN/ntuples/${NTUPLETAG}/CROWNRun/"
KINGMAKER_BASEDIR_XROOTD="root://cmsdcache-kit-disk.gridka.de/${KINGMAKER_BASEDIR}"
# BASEDIR="/ceph/sdaigler/CROWN/${NTUPLETAG}/CROWNRun/"

FRIENDS_BASE_DIR="/store/user/${USER}/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/"
MULTI_FRIENDS_BASE_DIR="/store/user/${USER}/CROWN/ntuples/${NTUPLETAG}/CROWNMultiFriends/"
XSEC_FRIENDS="${FRIENDS_BASE_DIR}xsec/"
FASTMTT_FRIENDS="${FRIENDS_BASE_DIR}fastmtt/"
NN_FRIENDS_EQUAL_EVENTS="${MULTI_FRIENDS_BASE_DIR}ml_equal_events/"
NN_FRIENDS_EQUAL_WEIGHTS="${MULTI_FRIENDS_BASE_DIR}ml_equal_weights/"
# FF_FRIENDS="/store/user/${USER}/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/ff_2018UL_mt_et_tt__2024-11-21_v2/"

if [[ $ERA == *"2016"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2017"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2018"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
fi
