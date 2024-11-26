source utils/setup_root.sh
export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5

VARIABLES="phi_2,phi_1,q_1,mjj,iso_2,iso_1,mjj,pt_dijet,pt_tt,pt_vis,mt_2,mt_1,tau_decaymode_1,tau_decaymode_2,nbtag,njets,jphi_2,jphi_1,jeta_2,jeta_1,jpt_2,jpt_1,eta_1,eta_2,pt_2,pt_1,mt_tot,met,metphi,m_vis,deltaR_ditaupair,pzetamissvis"
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
    nice -n 19 python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsdcache-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
fi

if [[ $MODE == "SHAPES" ]]; then
    echo "##############################################################################################"
    echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
    echo "##############################################################################################"

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output" ]; then
        mkdir -p $shapes_output
    fi
    
    nice -n 19 python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS \
        --era $ERA --num-processes 25 --num-threads 50 \
        --optimization-level 1 --control-plots \
        --control-plot-set ${VARIABLES} --skip-systematic-variations \
        --output-file $shapes_output \
        --xrootd --validation-tag $TAG \
        --vs-jet-wp "Tight" --vs-ele-wp "VVLoose"

    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"
    if [[ $CHANNEL == "mm" ]]; then
        nice -n 19 python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-qcd
    else
        nice -n 19 python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-qcd --do-ff
    fi
fi

if [[ $MODE == "PLOT" ]]; then
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"

    nice -n 19 python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --tag ${TAG} --embedding --fake-factor
    nice -n 19 python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --tag ${TAG} --embedding
    nice -n 19 python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --tag ${TAG} --fake-factor
    nice -n 19 python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --tag ${TAG}

    # python2 ~/tools/webgallery/gallery.py Run${ERA}_plots_emb_classic/
fi
