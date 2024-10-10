#!/bin/bash
set -e
NTUPLETAG=$1
ERA=$2

KINGMAKER_BASEDIR="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNRun/"
KINGMAKER_BASEDIR_XROOTD="root://cmsdcache-kit-disk.gridka.de/${KINGMAKER_BASEDIR}"
BASEDIR="/ceph/nshadskiy/CROWN/${NTUPLETAG}/CROWNRun/"
XSEC_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/xsec/"
# FF_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/ffs_pNet_flv_v4/"
FF_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/fake_factors_v8/"
KINFIT_RES_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/kinfit_resolved_v1/"
KINFIT_BOOST_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/kinfit_boosted_v1/"
FASTMTT_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNFriends/fastmtt_v2/"
# NN_RES_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNMultiFriends/pnn_resolved_v4/"
# NN_BOOST_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNMultiFriends/pnn_boosted_v1/"
NN_RES_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNMultiFriends/pnn_resolved_lowmass_v1/"
NN_BOOST_FRIENDS="/store/user/nshadskiy/CROWN/ntuples/${NTUPLETAG}/CROWNMultiFriends/pnn_boosted_lowmass_v1/"

if [[ $ERA == *"2016"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2017"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
elif [[ $ERA == *"2018"* ]]; then
    NTUPLES=$KINGMAKER_BASEDIR
fi