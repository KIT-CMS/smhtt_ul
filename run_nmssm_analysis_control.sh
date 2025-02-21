export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MASSX=$5
MASSY=$6
MODE=$7

POSTFIX="-${MASSX}_${MASSY}"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Datacard Setup
datacard_output="datacards/${NTUPLETAG}-${TAG}/${ERA}"

output_shapes="nmssm_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
output_shapes_boosted="nmssm_boosted_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_boosted=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes_boosted}
shapes_output_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_output_boosted_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/boosted_synced
shapes_output_all_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/all_synced
shapes_rootfile=${shapes_output}${POSTFIX}.root
shapes_rootfile_boosted=${shapes_output_boosted}${POSTFIX}.root
shapes_rootfile_synced=${shapes_output_synced}${POSTFIX}_synced.root


VARIABLES="iso_1,mass_1,mass_2,pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,tau_decaymode_1,tau_decaymode_2"

# VARS_TAUS="iso_1,mass_1,mass_2,pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,tau_decaymode_1,tau_decaymode_2"
# VARS_TAU_PAIR="m_vis,mt_1,mt_2,mt_1_pf,mt_2_pf,pfmet,met,pzetamissvis,metphi,deltaR_ditaupair,pt_vis"
# VARS_JETS="jpt_1,jpt_2,jeta_1,jeta_2,jphi_1,jphi_2,mjj,njets,pt_dijet,jet_hemisphere"
# VARS_BJETS="nbtag,bpair_pt_1,bpair_pt_2,bpair_eta_1,bpair_eta_2,bpair_phi_1,bpair_phi_2,bpair_btag_value_1,bpair_btag_value_2,bpair_m_inv,bpair_pt_dijet,bpair_deltaR"
# VARS_FATJETS="nfatjets,fj_Xbb_pt,fj_Xbb_eta,fj_Xbb_phi,fj_Xbb_mass,fj_Xbb_particleNet_XbbvsQCD,fj_Xbb_nsubjettiness_3over2,fj_Xbb_nsubjettiness_2over1,fj_Xbb_msoftdrop"
# VARS_DISTANCES="deltaPhi_met_tau1,deltaPhi_met_tau2,deltaPhi_met_fatjet,deltaPhi_met_bjet1,deltaPhi_met_bjet2,deltaR_tau1_fatjet,deltaR_tau2_fatjet,balance_pT_fatjet_Z,deltaR_bjet1_fatjet,deltaR_bjet2_fatjet,deltaR_tau1_bjet1,deltaR_tau1_bjet2,deltaR_tau2_bjet1,deltaR_tau2_bjet2"
# VARS_BBTT="mt_tot,pt_tautaubb,mass_tautaubb"
# VARS_KINFIT="kinfit_mX,kinfit_mY,kinfit_chi2,kinfit_convergence,kinfit_mX_YToBB,kinfit_mY_YToBB,kinfit_chi2_YToBB,kinfit_convergence_YToBB,kinfit_mX_YToTauTau,kinfit_mY_YToTauTau,kinfit_chi2_YToTauTau,kinfit_convergence_YToTauTau"
# VARS_FASTMTT="m_fastmtt,pt_fastmtt,eta_fastmtt,phi_fastmtt"

# if [[ $CHANNEL == "et" ]]; then
#     VARS_TAUS="iso_1,mass_2,pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,tau_decaymode_2"
#     BOOST_VARS_TAUS="boosted_iso_1,boosted_mass_2,boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,boosted_tau_decaymode_2"
#     VARIABLES="${VARS_TAUS},${VARS_TAU_PAIR},${VARS_JETS},${VARS_BJETS},${VARS_FATJETS},${VARS_DISTANCES},${VARS_BBTT},${VARS_KINFIT},${VARS_FASTMTT}"
#     BOOST_VARIABLES="${BOOST_VARS_TAUS},${BOOST_VARS_TAU_PAIR},${BOOST_VARS_BJETS},${BOOST_VARS_FATJETS},${BOOST_VARS_DISTANCES},${BOOST_VARS_BBTT},${BOOST_VARS_KINFIT},${BOOST_VARS_FASTMTT}"
# fi
# if [[ $CHANNEL == "mt" ]]; then
#     VARS_TAUS="iso_1,mass_2,pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,tau_decaymode_2"
#     BOOST_VARS_TAUS="boosted_iso_1,boosted_mass_2,boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,boosted_tau_decaymode_2"
#     VARIABLES="${VARS_TAUS},${VARS_TAU_PAIR},${VARS_JETS},${VARS_BJETS},${VARS_FATJETS},${VARS_DISTANCES},${VARS_BBTT},${VARS_KINFIT},${VARS_FASTMTT}"
#     BOOST_VARIABLES="${BOOST_VARS_TAUS},${BOOST_VARS_TAU_PAIR},${BOOST_VARS_BJETS},${BOOST_VARS_FATJETS},${BOOST_VARS_DISTANCES},${BOOST_VARS_BBTT},${BOOST_VARS_KINFIT},${BOOST_VARS_FASTMTT}"
# fi
# if [[ $CHANNEL == "tt" ]]; then
#     VARS_TAUS="mass_1,mass_2,pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,tau_decaymode_1,tau_decaymode_2"
#     BOOST_VARS_TAUS="boosted_mass_1,boosted_mass_2,boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,boosted_tau_decaymode_1,boosted_tau_decaymode_2"
#     VARIABLES="${VARS_TAUS},${VARS_TAU_PAIR},${VARS_JETS},${VARS_BJETS},${VARS_FATJETS},${VARS_DISTANCES},${VARS_BBTT},${VARS_KINFIT},${VARS_FASTMTT}"
#     BOOST_VARIABLES="${BOOST_VARS_TAUS},${BOOST_VARS_TAU_PAIR},${BOOST_VARS_BJETS},${BOOST_VARS_FATJETS},${BOOST_VARS_DISTANCES},${BOOST_VARS_BBTT},${BOOST_VARS_KINFIT},${BOOST_VARS_FASTMTT}"
# fi

# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
fi

# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "output_shapes_boosted: ${output_shapes_boosted}"
echo "XSEC_FRIENDS: ${XSEC_FRIENDS}"
echo "FF_FRIENDS: ${FF_FRIENDS}"
echo "NN_FRIENDS: ${NN_FRIENDS}"
echo "###################################"
echo "#           Mode ${MODE}          #"
echo "###################################"

if [[ $MODE == "COPY" ]]; then
    source utils/setup_root.sh

    # if the xsec friends directory does not exist, create it
    if [ ! -d "$BASEDIR/$ERA" ]; then
        mkdir -p $BASEDIR/$ERA
    fi
    if [ "$(ls -A $BASEDIR/$ERA)" ]; then
        echo "Ntuples already copied to ceph"
    else
        echo "Copying ntuples to ceph"
        rsync -avhPl $KINGMAKER_BASEDIR$ERA/ $BASEDIR$ERA/
    fi
    exit 0
elif [[ $MODE == "COPY_XROOTD" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Copying ntuples to ceph via xrootd"
    echo "xrdcp -r $KINGMAKER_BASEDIR_XROOTD$ERA/ $BASEDIR$ERA/"
    if [ ! -d "$BASEDIR/$ERA" ]; then
        mkdir -p $BASEDIR/$ERA
    fi
    xrdcp -r $KINGMAKER_BASEDIR_XROOTD$ERA $BASEDIR
fi

if [[ $MODE == "XSEC" ]]; then
    source utils/setup_root.sh
    # if the xsec friends directory does not exist, create it
    if [ ! -d "$XSEC_FRIENDS" ]; then
        mkdir -p $XSEC_FRIENDS
    fi
    # if th xsec friends dir is empty, run the xsec friends script
    if [ "$(ls -A $XSEC_FRIENDS)" ]; then
        echo "xsec friends dir already exists"
    else
        echo "xsec friends dir is empty"
        echo "running xsec friends script"
        python3 friends/build_friend_tree.py --basepath $BASEDIR --outputpath $XSEC_FRIENDS --nthreads 20
    fi
    exit 0
elif [[ $MODE == "XSEC_XROOTD" ]]; then
    source utils/setup_root.sh

    echo "running xsec friends script"
    python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsdcache-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
fi

if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $FRIENDS $NNSCORE_FRIENDS  \
        --era $ERA --num-processes 4 --num-threads 6 \
        --optimization-level 1 --skip-systematic-variations \
        --output-file $shapes_output

    python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-qcd

    # now plot the shapes by looping over the categories
    for category in "ggh" "qqh" "ztt" "tt" "ff" "misc" "xxh"; do
        python3 plotting/plot_ml_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --channel ${CHANNEL} --embedding --fake-factor --category ${category} --output-dir output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/controlplots --normalize-by-bin-width
    done
fi

if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS $NN_FRIENDS \
        --era $ERA --num-processes 8 --num-threads 12 \
        --optimization-level 1 --skip-systematic-variations --xrootd \
        --output-file $shapes_output --boosted-b-analysis \
        --massX $MASSX --massY $MASSY --validation-tag $TAG
    
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS $NN_FRIENDS \
        --era $ERA --num-processes 8 --num-threads 12 \
        --optimization-level 1 --skip-systematic-variations --xrootd \
        --output-file $shapes_output_boosted --boosted-b-analysis --boosted-tau-analysis \
        --massX $MASSX --massY $MASSY --validation-tag $TAG
fi

if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_nmssm_control.sh $ERA $CHANNEL \
        "singlegraph" $TAG 1 0 $NTUPLETAG $CONDOR_OUTPUT $MASSX $MASSY $VARIABLES
    echo "[INFO] Jobs submitted"
fi

if [[ $MODE == "CONDOR_BOOSTED" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_nmssm_control.sh $ERA $CHANNEL \
        "singlegraph" $TAG 1 1 $NTUPLETAG $CONDOR_OUTPUT $MASSX $MASSY $BOOST_VARIABLES
    echo "[INFO] Jobs submitted"
fi

if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../control_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ $MODE == "MERGE_BOOSTED" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile_boosted ${CONDOR_OUTPUT}/../boosted_control_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile} --do-emb-tt --do-ff --do-qcd

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi
    if [ ! -d "$shapes_output_all_synced" ]; then
        mkdir -p $shapes_output_all_synced
    fi

    python shapes/convert_to_synced_shapes.py -e $ERA \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        -n 1 --gof

    inputfile="nmssm_${CHANNEL}.inputs-nmssm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_all_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}-synced*.root 
fi

if [[ $MODE == "SYNC_BOOSTED" ]]; then
    source utils/setup_root.sh
    python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile_boosted} --do-emb-tt --do-ff --do-qcd

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_boosted_synced" ]; then
        mkdir -p $shapes_output_boosted_synced
    fi
    if [ ! -d "$shapes_output_all_synced" ]; then
        mkdir -p $shapes_output_all_synced
    fi
    
    python shapes/convert_to_synced_shapes.py -e $ERA \
        -i ${shapes_rootfile_boosted} \
        -o ${shapes_output_boosted_synced} \
        -n 1 --gof

    inputfile_boosted="nmssm_${CHANNEL}.inputs-nmssm_boosted-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_all_synced/$inputfile_boosted $shapes_output_boosted_synced/${ERA}-${CHANNEL}-synced*.root
fi

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw14.sh
    # inputfile
    inputfile="nmssm_${CHANNEL}.inputs-nmssm-Run${ERA}${POSTFIX}.root"

    for VARIABLE in ${VARIABLES//,/ }; do
        ${CMSSW_BASE}/bin/el9_amd64_gcc12/MorphingNMSSMRun2UL \
            --base_path=$PWD \
            --input_folder_mt="${shapes_output_all_synced}/${inputfile}" \
            --input_folder_tt="${shapes_output_all_synced}/${inputfile}" \
            --input_folder_et="${shapes_output_all_synced}/${inputfile}" \
            --boosted_tt=false \
            --heavy_mass=$MASSX \
            --light_mass=$MASSY \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=1 \
            --embedding=0 \
            --postfix=${POSTFIX} \
            --chan=${CHANNEL} \
            --auto_rebin=true \
            --era=${ERA} \
            --output_folder=output/$datacard_output \
            --use_automc=true \
            --remove_empty_categories=true \
            --train_ff=1 \
            --train_emb=1 \
            --categories="gof" \
            --verbose=true \
            --gof_category_name=$VARIABLE
    done

    THIS_PWD=${PWD}
    echo $THIS_PWD
    cd output/$datacard_output
    for FILE in */${MASSX}_${MASSY}_*/*.txt; do
        sed -i '$s/$/\n * autoMCStats 10.0/' $FILE
    done
    cd $THIS_PWD
    echo "[INFO] Created datacard"

    for VARIABLE in ${VARIABLES//,/ }; do
        combineTool.py -M T2W -o "workspace.root" \
            -i output/$datacard_output/$CHANNEL/${MASSX}_${MASSY}_${VARIABLE}/ \
            -m $MASSY -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
            --PO '"map=^.*/NMSSM_Ytt:r_NMSSM_Ytt[1,-10,10]"' \
            --PO '"map=^.*/NMSSM_Ybb:r_NMSSM_Ybb[1,-10,10]"' \
            --channel-masks  
    done
    echo "[INFO] Created Workspace for datacard"
fi

if [[ $MODE == "DATACARD_BOOSTED" ]]; then
    source utils/setup_cmssw14.sh
    # inputfile
    inputfile_boosted="nmssm_${CHANNEL}.inputs-nmssm_boosted-Run${ERA}${POSTFIX}.root"

    for VARIABLE in ${BOOST_VARIABLES//,/ }; do
        ${CMSSW_BASE}/bin/el9_amd64_gcc12/MorphingNMSSMRun2UL \
            --base_path=$PWD \
            --input_folder_mt="${shapes_output_all_synced}/${inputfile_boosted}" \
            --input_folder_tt="${shapes_output_all_synced}/${inputfile_boosted}" \
            --input_folder_et="${shapes_output_all_synced}/${inputfile_boosted}" \
            --boosted_tt=true \
            --heavy_mass=$MASSX \
            --light_mass=$MASSY \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=1 \
            --embedding=0 \
            --postfix=${POSTFIX} \
            --chan=${CHANNEL} \
            --auto_rebin=true \
            --era=${ERA} \
            --output_folder=output/$datacard_output \
            --use_automc=true \
            --remove_empty_categories=true \
            --train_ff=1 \
            --train_emb=1 \
            --categories="gof" \
            --verbose=true \
            --gof_category_name=$VARIABLE
    done

    THIS_PWD=${PWD}
    echo $THIS_PWD
    cd output/$datacard_output
    for FILE in */${MASSX}_${MASSY}_*/*.txt; do
        sed -i '$s/$/\n * autoMCStats 10.0/' $FILE
    done
    cd $THIS_PWD
    echo "[INFO] Created datacard"

    for VARIABLE in ${BOOST_VARIABLES//,/ }; do
        combineTool.py -M T2W -o "workspace.root" \
            -i output/$datacard_output/$CHANNEL/${MASSX}_${MASSY}_${VARIABLE}/ \
            -m $MASSY -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
            --PO '"map=^.*/NMSSM_Ytt:r_NMSSM_Ytt[1,-10,10]"' \
            --PO '"map=^.*/NMSSM_Ybb:r_NMSSM_Ybb[1,-10,10]"' \
            --channel-masks  
    done
    echo "[INFO] Created Workspace for datacard"
fi

# GOF_VARIABLES="njets,nbtag,nfatjets,pt_1,pt_2,eta_1,eta_2,phi_1,phi_2,bpair_pt_1,bpair_pt_2,bpair_eta_1,bpair_eta_2,bpair_phi_1,bpair_phi_2,bpair_btag_value_1,bpair_btag_value_2,deltaR_ditaupair,m_vis,bpair_m_inv,bpair_deltaR,bpair_pt_dijet,fj_Xbb_pt,fj_Xbb_eta,fj_Xbb_phi,fj_Xbb_msoftdrop,fj_Xbb_nsubjettiness_2over1,met,metphi,mt_1,m_fastmtt,pt_fastmtt,eta_fastmtt,phi_fastmtt,kinfit_mX,kinfit_mY,kinfit_chi2"
GOF_VARIABLES="njets_boosted,nbtag_boosted,nfatjets_boosted,boosted_pt_1,boosted_pt_2,boosted_eta_1,boosted_eta_2,boosted_phi_1,boosted_phi_2,bpair_pt_1_boosted,bpair_pt_2_boosted,bpair_eta_1_boosted,bpair_eta_2_boosted,bpair_phi_1_boosted,bpair_phi_2_boosted,bpair_btag_value_1_boosted,bpair_btag_value_2_boosted,boosted_deltaR_ditaupair,boosted_m_vis,bpair_m_inv_boosted,bpair_deltaR_boosted,bpair_pt_dijet_boosted,fj_Xbb_pt_boosted,fj_Xbb_eta_boosted,fj_Xbb_phi_boosted,fj_Xbb_msoftdrop_boosted,fj_Xbb_nsubjettiness_2over1_boosted,met_boosted,metphi_boosted,boosted_mt_1,boosted_m_fastmtt,boosted_pt_fastmtt,boosted_eta_fastmtt,boosted_phi_fastmtt,kinfit_mX_boosted,kinfit_mY_boosted,kinfit_chi2_boosted"

if [[ $MODE == "GOF" ]]; then
    source utils/setup_cmssw14.sh
    for VARIABLE in ${GOF_VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        gof_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        WORKSPACE=output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}_${VARIABLE}/workspace.root
        MASS=${MASSY}
        NUM_TOYS=100 # multiply x10

        if [ ! -d "$gof_output" ]; then
            mkdir -p $gof_output
        fi

        for ALGO in "saturated"; do
            # Get test statistic value
            if [[ "$ALGO" == "saturated" ]]; then
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE --fixedSignalStrength=0 -v 1 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb 
            else
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE --plots --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb 
            fi

            # Throw toys
            TOYSOPT=""
            if [[ "$ALGO" == "saturated" ]]; then
                TOYSOPT="--toysFreq"
            fi

            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1230 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1231 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1232 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1233 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1234 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1235 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1236 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1237 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1238 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1239 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 --setParameters r_NMSSM_Ytt=0,r_NMSSM_Ybb=0 --freezeParameters r_NMSSM_Ytt,r_NMSSM_Ybb >/dev/null &
            wait
            # Collect results
            combineTool.py -M CollectGoodnessOfFit --input \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1230.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1231.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1232.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1233.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1234.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1235.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1236.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1237.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1238.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1239.root \
                --output output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json

            mv higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.123?.root output/gof/${NTUPLETAG}-${TAG}/${ID}/
            if [[ "$ALGO" == "saturated" ]]; then
                mv output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json output/gof/${NTUPLETAG}-${TAG}/${ID}/gof.json
            fi

            # Plot
            if [[ "$ALGO" != "saturated" ]]; then
                plotGof.py --statistic $ALGO --mass $MASS.0 --output gof_${ALGO} output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json
                mv nmssm_${CHANNEL}_300_${ERA}gof_${ALGO}.p{df,ng} output/gof/${NTUPLETAG}-${TAG}/${ID}/
                python2 plotting/gof/plot_gof_metrics.py -e $ERA -g $ALGO -o output/gof/${NTUPLETAG}-${TAG}/${ID}/ -i output/gof/${NTUPLETAG}-${TAG}/${ID}/higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root
            else
                plotGof.py --statistic $ALGO --mass $MASS.0 --output output/gof/${NTUPLETAG}-${TAG}/${ID}/gof output/gof/${NTUPLETAG}-${TAG}/${ID}/gof.json
            fi
        done
    done
fi

if [[ $MODE == "GOF-SUM" ]]; then
    source utils/setup_root.sh
    python3 gof/plot_gof_summary.py --variables $GOF_VARIABLES --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL
fi

if [[ $MODE == "PREFIT" ]]; then
    source utils/setup_cmssw14.sh
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        WORKSPACE=output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}_${VARIABLE}/workspace.root
        
        PostFitShapesFromWorkspace -m ${MASSY} -w $WORKSPACE \
            -o output/${datacard_output}/${ID}-datacard-shapes-prefit.root \
            -d output/${datacard_output}/${CHANNEL}/${MASSX}_${MASSY}_${VARIABLE}/nmssm_${CHANNEL}_300_${ERA}.txt
    done
fi

if [[ $MODE == "PREFIT_BOOSTED" ]]; then
    source utils/setup_cmssw14.sh
    for VARIABLE in ${BOOST_VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        WORKSPACE=output/$datacard_output/${CHANNEL}/${MASSX}_${MASSY}_${VARIABLE}/workspace.root

        PostFitShapesFromWorkspace -m ${MASSY} -w $WORKSPACE \
            -o output/${datacard_output}/${ID}-datacard-shapes-prefit.root \
            -d output/${datacard_output}/${CHANNEL}/${MASSX}_${MASSY}_${VARIABLE}/nmssm_${CHANNEL}_300_${ERA}.txt
    done
fi

if [[ $MODE == "PLOT-PREFIT" ]]; then
    source utils/setup_root.sh
    SUMMARYFOLDER=output/gof/${NTUPLETAG}-${TAG}/plots
    [ -d $SUMMARYFOLDER ] || mkdir -p $SUMMARYFOLDER
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        gof_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        PLOTDIR=output/${datacard_output}/plots
        PREFITFILE=output/${datacard_output}/${ID}-datacard-shapes-prefit.root
        [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
       
        for OPTION in "" "--png"; do
            python3 plotting/plot_shapes_gof.py -l -i $PREFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor \
                --gof-variable $VARIABLE -o ${PLOTDIR}
        done
        cp ${PLOTDIR}/*.p{df,ng} $SUMMARYFOLDER
    done
fi

if [[ $MODE == "PLOT-PREFIT_BOOSTED" ]]; then
    source utils/setup_root.sh
    SUMMARYFOLDER=output/gof/${NTUPLETAG}-${TAG}/plots
    [ -d $SUMMARYFOLDER ] || mkdir -p $SUMMARYFOLDER
    for VARIABLE in ${BOOST_VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        gof_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        PLOTDIR=output/${datacard_output}/plots
        PREFITFILE=output/${datacard_output}/${ID}-datacard-shapes-prefit.root
        [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
        
        for OPTION in "" "--png"; do
            python3 plotting/plot_shapes_gof.py -l -i $PREFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor --tt-boosted \
                --gof-variable $VARIABLE -o ${PLOTDIR}
        done
        cp ${PLOTDIR}/*.p{df,ng} $SUMMARYFOLDER
    done
fi