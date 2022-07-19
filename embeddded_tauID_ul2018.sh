export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5

VARIABLES="m_vis"
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
# echo "##############################################################################################"
# echo "#      unset multicore bit                                                          #"
# echo "##############################################################################################"

# python3 unset_rootbit.py --basepath ${BASEDIR}

categories=( "Pt20to25" "Pt25to30" "Pt30to35" "Pt35to40" "Pt40to50" "Pt50to70" "PtGt70" "DM0" "DM1" "DM10" "DM11" "Inclusive" )
printf -v categories_string '%s,' "${categories[@]}"
echo "Using Cateogires ${categories_string%,}"

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

if [[ $MODE == "LOCAL" ]]
then
    python shapes/produce_shapes_tauID.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS  \
        --era $ERA --num-processes 2 --num-threads 4 \
        --optimization-level 1 \
        --control-plot-set ${VARIABLES} \
        --output-file $shapes_output
elif [[ $MODE == "CONDOR" ]]
then
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_ul.sh $ERA $CHANNEL \
       "singlegraph" $TAG 0 $NTUPLETAG $CONDOR_OUTPUT
    echo "[INFO] Jobs submitted"
elif [[ $MODE == "MERGE" ]]
then
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 $shapes_output.root ${CONDOR_OUTPUT}/*.root
else
    echo "Mode $MODE is not implemented "
fi



# echo "##############################################################################################"
# echo "#      Additional estimations                                      #"
# echo "##############################################################################################"

# bash ./shapes/do_estimations.sh 2018 ${shapes_output}.root 1


# echo "##############################################################################################"
# echo "#     plotting                                      #"
# echo "##############################################################################################"

# python3 plotting/plot_shapes_tauID.py -l --era Run${ERA} --input ${shapes_output}.root --variables ${VARIABLES} --channels ${CHANNEL} --embedding --categories ${categories_string%,}

# echo "##############################################################################################"
# echo "#     synced shapes                                      #"
# echo "##############################################################################################"

# python shapes/convert_to_synced_shapes.py -e $ERA \
#     -i output/shapes/${ERA}-${CHANNEL}-analysis-shapes-${TAG}/shapes-analysis-${ERA}-${CHANNEL}-${PROC}.root \
#     -o output/shapes/${ERA}-${CHANNEL}-${TAG}-synced_shapes_${VARIABLE}-${PROC} \
#     --variable-selection ${VARIABLE} \
#     -n 12