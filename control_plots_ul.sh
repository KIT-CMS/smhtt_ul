source utils/setup_root.sh
export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5

# Basic variables
# VARIABLES="pt_1,pt_2,eta_1,eta_2,m_vis,pzetamissvis,deltaR_ditaupair,phi_1,phi_2,mt_1,mt_2,pt_vis,iso_1,iso_2"

# Extended variables
# VARIABLES="pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,m_vis,iso_1,iso_2,jpt_1,jpt_2,jeta_1,jeta_2,jphi_1,jphi_2,mt_tot,mjj,njets,nbtag,mt_1,mt_2,mt_1_pf,mt_2_pf,pfmet,met,pzetamissvis,metphi,pt_dijet,deltaR_ditaupair,tau_decaymode_2,jet_hemisphere,pt_vis"


VARS_TAUS="iso_1,iso_2,mass_1,mass_2,pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,tau_decaymode_1,tau_decaymode_2"
VARS_TAU_PAIR="m_vis,mt_1,mt_2,mt_1_pf,mt_2_pf,pfmet,met,pzetamissvis,metphi,deltaR_ditaupair,pt_vis,mtt_coll_approx"
VARS_JETS="jpt_1,jpt_2,jeta_1,jeta_2,jphi_1,jphi_2,mjj,njets,pt_dijet,jet_hemisphere"
VARS_BJETS="nbtag,bpair_pt_1,bpair_pt_2,bpair_eta_1,bpair_eta_2,bpair_phi_1,bpair_phi_2,bpair_btag_value_1,bpair_btag_value_2,bpair_m_inv,bpair_pt_dijet,bpair_deltaR"
# VARS_DISTANCES="deltaPhi_met_tau1,deltaPhi_met_tau2,deltaPhi_met_fatjet,deltaPhi_met_bjet1,deltaPhi_met_bjet2,deltaR_tau1_fatjet,deltaR_tau2_fatjet,balance_pT_fatjet_Z,deltaR_bjet1_fatjet,deltaR_bjet2_fatjet,deltaR_tau1_bjet1,deltaR_tau1_bjet2,deltaR_tau2_bjet1,deltaR_tau2_bjet2"
VARS_BBTT="mt_tot,pt_tautaubb,mass_tautaubb"
# VARS_KINFIT="kinfit_mX,kinfit_mY,kinfit_chi2,kinfit_convergence,kinfit_mX_YToBB,kinfit_mY_YToBB,kinfit_chi2_YToBB,kinfit_convergence_YToBB,kinfit_mX_YToTauTau,kinfit_mY_YToTauTau,kinfit_chi2_YToTauTau,kinfit_convergence_YToTauTau"
VARS_FASTMTT="m_fastmtt,pt_fastmtt,eta_fastmtt,phi_fastmtt"

VARIABLES="q_1,${VARS_TAUS},${VARS_TAU_PAIR},${VARS_JETS},${VARS_BJETS},${VARS_BBTT},${VARS_FASTMTT}"

ulimit -s unlimited
export COLUMNS=$(tput cols)
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
        --${CHANNEL}-friend-directory $XSEC_FRIENDS $FASTMTT_FRIENDS \
        --era $ERA --num-processes 4 --num-threads 12 \
        --optimization-level 1 --control-plots \
        --control-plot-set ${VARIABLES} --skip-systematic-variations \
        --output-file $shapes_output \
        --xrootd --validation-tag $TAG \
        --vs-jet-wp "Medium" --vs-ele-wp "VVLoose" --collect-config-only

    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"

    python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-qcd

fi

if [[ $MODE == "PLOT" ]]; then
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"

    # python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --embedding --fake-factor
    # python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --embedding --tag ${TAG}
    python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --add-signals
    # python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --fake-factor

    # python2 ~/tools/webgallery/gallery.py Run${ERA}_plots_emb_classic/
fi
