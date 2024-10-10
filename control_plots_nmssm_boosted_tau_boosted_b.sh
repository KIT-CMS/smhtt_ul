source utils/setup_root.sh
export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5

VARS_TAUS="boosted_iso_1,boosted_mass_1,boosted_mass_2,boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,boosted_tau_decaymode_1,boosted_tau_decaymode_2"
VARS_TAU_PAIR="boosted_m_vis,boosted_mt_1,boosted_mt_2,met_boosted,metphi_boosted,boosted_deltaR_ditaupair,boosted_pt_vis"
VARS_BJETS="njets_boosted,nbtag_boosted,bpair_pt_1_boosted,bpair_pt_2_boosted,bpair_eta_1_boosted,bpair_eta_2_boosted,bpair_phi_1_boosted,bpair_phi_2_boosted,bpair_btag_value_1_boosted,bpair_btag_value_2_boosted,bpair_m_inv_boosted,bpair_pt_dijet_boosted,bpair_deltaR_boosted"
VARS_FATJETS="nfatjets_boosted,fj_Xbb_pt_boosted,fj_Xbb_eta_boosted,fj_Xbb_phi_boosted,fj_Xbb_mass_boosted,fj_Xbb_particleNet_XbbvsQCD_boosted,fj_Xbb_nsubjettiness_3over2_boosted,fj_Xbb_nsubjettiness_2over1_boosted,fj_Xbb_msoftdrop_boosted"
VARS_BBTT="boosted_pt_tautaubb,boosted_mass_tautaubb"
VARS_KINFIT="kinfit_mX_boosted,kinfit_mY_boosted,kinfit_chi2_boosted,kinfit_convergence_boosted,kinfit_mX_YToBB_boosted,kinfit_mY_YToBB_boosted,kinfit_chi2_YToBB_boosted,kinfit_convergence_YToBB_boosted,kinfit_mX_YToTauTau_boosted,kinfit_mY_YToTauTau_boosted,kinfit_chi2_YToTauTau_boosted,kinfit_convergence_YToTauTau_boosted"
VARS_FASTMTT="boosted_m_fastmtt,boosted_pt_fastmtt,boosted_eta_fastmtt,boosted_phi_fastmtt"
# sqrt_pt1_met,cos_deltaPhi_met_tau1,sqrt_pt2_met,cos_deltaPhi_met_tau2,deltaPhi_met_jet1,deltaPhi_jet1_fatjet,deltaR_jet1_fatjet,deltaR_jet2_fatjet,deltaR_jet1_jet2,deltaR_tau1_jet1,deltaR_tau2_jet1,deltaR_tau1_jet2,deltaR_tau2_jet2,deltaPhi_jet1_jet2,deltaEta_jet1_jet2,deltaPT_jet1_jet2,deltaPhi_tau1_jet1,deltaEta_tau1_jet1,

if [[ $CHANNEL == "et" ]]; then
    VARS_TAUS="boosted_iso_1,boosted_mass_2,boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,boosted_tau_decaymode_2"
    VARIABLES="${VARS_TAUS},${VARS_TAU_PAIR},${VARS_BJETS},${VARS_FATJETS},${VARS_BBTT}"
fi
if [[ $CHANNEL == "mt" ]]; then
    VARS_TAUS="boosted_iso_1,boosted_mass_2,boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,boosted_tau_decaymode_2"
    VARIABLES="${VARS_TAUS},${VARS_TAU_PAIR},${VARS_BJETS},${VARS_FATJETS},${VARS_BBTT}"
fi
if [[ $CHANNEL == "tt" ]]; then
    VARS_TAUS="boosted_mass_1,boosted_mass_2,boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,boosted_tau_decaymode_1,boosted_tau_decaymode_2"
    VARIABLES="${VARS_TAUS},${VARS_TAU_PAIR},${VARS_BJETS},${VARS_FATJETS},${VARS_BBTT}"
fi

VARIABLES="${VARS_FATJETS},${VARS_TAUS},${VARS_BJETS}"

ulimit -s unlimited
source utils/setup_root.sh
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

output_shapes="control_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shape_rootfile=${shapes_output}.root
# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"

if [[ $MODE == "XSEC" ]]; then

    echo "##############################################################################################"
    echo "#      Checking xsec friends directory                                                       #"
    echo "##############################################################################################"

    echo "running xsec friends script"
    echo "XSEC_FRIENDS: ${XSEC_FRIENDS}"
    python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsdcache-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
fi

if [[ $MODE == "SHAPES" ]]; then
    echo "##############################################################################################"
    echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
    echo "##############################################################################################"

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output" ]; then
        mkdir -p $shapes_output
    fi

    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS \
        --era $ERA --num-processes 4 --num-threads 12 \
        --optimization-level 1 --control-plots \
        --control-plot-set ${VARIABLES} --skip-systematic-variations \
        --output-file $shapes_output \
        --xrootd --validation-tag $TAG --boosted-tau-analysis --boosted-b-analysis --massX 800 --massY 250

    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"

    python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-qcd --do-ff
fi

if [[ $MODE == "PLOT" ]]; then
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"

    python3 plotting/plot_shapes_control_nmssm.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --control-plots --add-signals --embedding --fake-factor
    python3 plotting/plot_shapes_control_nmssm.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --control-plots --add-signals --embedding
    python3 plotting/plot_shapes_control_nmssm.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --control-plots --add-signals
    python3 plotting/plot_shapes_control_nmssm.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --control-plots --add-signals --fake-factor
fi
