export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
# VARIABLES=$4

GOF_VARIABLES="njets,nbtag,nfatjets,pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,bpair_pt_1,bpair_pt_2,bpair_eta_1,bpair_eta_2,bpair_phi_1,bpair_phi_2,bpair_btag_value_1,bpair_btag_value_2,deltaR_ditaupair,m_vis,bpair_m_inv,bpair_deltaR,bpair_pt_dijet,fj_Xbb_pt,fj_Xbb_eta,fj_Xbb_phi,fj_Xbb_msoftdrop,fj_Xbb_nsubjettiness_2over1,met,metphi,mt_1,m_fastmtt,pt_fastmtt,eta_fastmtt,phi_fastmtt,kinfit_mX,kinfit_mY,kinfit_chi2"
# GOF_VARIABLES="njets_boosted,nbtag_boosted,nfatjets_boosted,boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,bpair_pt_1_boosted,bpair_pt_2_boosted,bpair_eta_1_boosted,bpair_eta_2_boosted,bpair_phi_1_boosted,bpair_phi_2_boosted,bpair_btag_value_1_boosted,bpair_btag_value_2_boosted,boosted_deltaR_ditaupair,boosted_m_vis,bpair_m_inv_boosted,bpair_deltaR_boosted,bpair_pt_dijet_boosted,fj_Xbb_pt_boosted,fj_Xbb_eta_boosted,fj_Xbb_phi_boosted,fj_Xbb_msoftdrop_boosted,fj_Xbb_nsubjettiness_2over1_boosted,met_boosted,metphi_boosted,boosted_mt_1,boosted_m_fastmtt,boosted_pt_fastmtt,boosted_eta_fastmtt,boosted_phi_fastmtt,kinfit_mX_boosted,kinfit_mY_boosted,kinfit_chi2_boosted"

ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA
source utils/setup_root.sh

python3 gof/build_binning.py --channel $CHANNEL \
    --directory $NTUPLES \
    --era $ERA --variables ${GOF_VARIABLES} --${CHANNEL}-friend-directory $KINFIT_BOOST_FRIENDS $FASTMTT_FRIENDS \
    --output-folder "config/gof_binning" --xrootd --validation-tag $TAG --boosted-tau-analysis --boosted-b-analysis

# --boosted-tau-analysis