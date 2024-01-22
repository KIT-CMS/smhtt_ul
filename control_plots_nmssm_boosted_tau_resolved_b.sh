source utils/setup_root.sh
export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5

VARIABLES="boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,boosted_mass_2,boosted_m_vis,boosted_iso_1,boosted_tau_decaymode_2,boosted_deltaR_ditaupair,boosted_pt_vis,boosted_mt_1,boosted_mt_2,met_boosted,metphi_boosted,njets_boosted,nbtag_boosted,bpair_pt_1_boosted,bpair_pt_2_boosted,bpair_eta_1_boosted,bpair_eta_2_boosted,bpair_phi_1_boosted,bpair_phi_2_boosted,bpair_btag_value_1_boosted,bpair_btag_value_2_boosted,bpair_m_inv_boosted,bpair_pt_dijet_boosted,bpair_deltaR_boosted,boosted_pt_tautaubb,boosted_mass_tautaubb" #,boosted_m_fastmtt,boosted_pt_fastmtt,boosted_eta_fastmtt,boosted_phi_fastmtt,kinfit_mX_boosted,kinfit_mY_boosted,kinfit_chi2_boosted,kinfit_convergence_boosted,kinfit_mX_YToBB_boosted,kinfit_mY_YToBB_boosted,kinfit_chi2_YToBB_boosted,kinfit_mX_YToTauTau_boosted,kinfit_mY_YToTauTau_boosted,kinfit_chi2_YToTauTau_boosted"
# VARIABLES="deltaR_b2_mu,deltaR_b1_tau,deltaR_b1_mu,deltaR_b2_tau,deltaR_b1_addtau,deltaR_b2_addtau,deltaR_mu_addtau,deltaR_tau_addtau,deltaPT_tau_addtau,deltaPT_mu_addtau"

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
    python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsxrootd-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
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
        --xrootd --validation-tag $TAG --boosted-tau-analysis

    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"

    python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-qcd --do-ff
fi

if [[ $MODE == "PLOT" ]]; then
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"

    python3 plotting/plot_shapes_control_nmssm.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --add-signals --embedding --fake-factor
    python3 plotting/plot_shapes_control_nmssm.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --add-signals --embedding
    python3 plotting/plot_shapes_control_nmssm.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --add-signals
    python3 plotting/plot_shapes_control_nmssm.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --add-signals --fake-factor
fi
