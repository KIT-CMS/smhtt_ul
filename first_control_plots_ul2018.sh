source utils/setup_root.sh
export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4

# VARIABLES="pt_1,pt_2,eta_1,eta_2,m_vis,jpt_1,jpt_2,jeta_1,jeta_2,mjj,njets,nbtag,bpt_1,bpt_2,mt_1,mt_2,pt_tt,pt_tt_pf,iso_1,pfmet,mt_1_pf,mt_2_pf,met,pzetamissvis,pzetamissvis_pf,metphi,pfmetphi"
# VARIABLES="m_vis"
VARIABLES="m_fastmtt,pt_fastmtt,eta_fastmtt,phi_fastmtt"
# VARIABLES="pt_1,pt_2,m_vis,njets,nbtag,jpt_1,jpt_2,jeta_1,jeta_2,m_fastmtt,pt_vis,mjj,deltaR_ditaupair,pt_tt",
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
echo "XSEC_FRIENDS: ${XSEC_FRIENDS}"

echo "##############################################################################################"
echo "#      Copy sample to ceph, it not there yet                                                     #"
echo "##############################################################################################"

# if the xsec friends directory does not exist, create it
if [ ! -d "$BASEDIR/$ERA" ]; then
    mkdir -p $BASEDIR/$ERA
fi
if [ "$(ls -A $BASEDIR/$ERA)" ]; then
    echo "Ntuples already copied to ceph"
else
    echo "Copying ntuples to ceph"
    rsync -avhPl $KINGMAKER_BASEDIR/$ERA/ $BASEDIR/$ERA/
fi
echo "##############################################################################################"
echo "#      Checking xsec friends directory                                                       #"
echo "##############################################################################################"

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
    python3 friends/build_friend_tree.py --basepath $BASEDIR --outputpath $XSEC_FRIENDS --nthreads 20 --xrootd
fi
echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
echo "##############################################################################################"

# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
fi

python shapes/produce_shapes.py --channels $CHANNEL \
    --directory $NTUPLES \
    --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS $FASTMTT_FRIENDS \
    --era $ERA --num-processes 4 --num-threads 2 \
    --optimization-level 1 --control-plots \
    --control-plot-set ${VARIABLES} --skip-systematic-variations \
    --output-file $shapes_output

echo "##############################################################################################"
echo "#      Additional estimations                                      #"
echo "##############################################################################################"

python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-ff --do-qcd

# bash ./shapes/do_estimations.sh 2018 ${shapes_output}.root 1

echo "##############################################################################################"
echo "#     plotting                                      #"
echo "##############################################################################################"

python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --embedding --fake-factor
python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --embedding
python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL}
python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --fake-factor

# python2 ~/tools/webgallery/gallery.py Run${ERA}_plots_emb_classic/
