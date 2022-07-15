source utils/setup_root.sh
export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4

VARIABLES="m_vis"

# ntuple_dir="/ceph/sbrommer/smhtt_ul/ntuples/${NTUPLETAG}/ntuples/${ERA}/"
ntuple_dir="/storage/gridka-nrg/sbrommer/CROWN/ntuples/${NTUPLETAG}/CROWNRun/${ERA}/"
shape_input_ntuple_dir="/storage/gridka-nrg/sbrommer/CROWN/ntuples/${NTUPLETAG}/CROWNRun/"
output_shapes="control_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
xsec_friends_dir="/ceph/sbrommer/smhtt_ul/${NTUPLETAG}/friends/xsec"

# print the paths to be used
echo "ntuple_dir: ${ntuple_dir}"
echo "output_shapes: ${output_shapes}"
echo "xsec_friends_dir: ${xsec_friends_dir}"

# echo "##############################################################################################"
# echo "#      unset multicore bit                                                          #"
# echo "##############################################################################################"

# python3 unset_rootbit.py --basepath ${ntuple_dir}

categories=( "Pt20to25" "Pt25to30" "Pt30to35" "Pt35to40" "Pt40to50" "Pt50to70" "PtGt70" "DM0" "DM1" "DM10" "DM11" "Inclusive" )
printf -v categories_string '%s,' "${categories[@]}"
echo "Using Cateogires ${categories_string%,}"

echo "##############################################################################################"
echo "#      Checking xsec friends directory                                                       #"
echo "##############################################################################################"

# if the xsec friends directory does not exist, create it
if [ ! -d "$xsec_friends_dir" ]; then
    mkdir -p $xsec_friends_dir
fi
# if th xsec friends dir is empty, run the xsec friends script
if [ "$(ls -A $xsec_friends_dir)" ]; then
    echo "xsec friends dir is not empty"
else
    echo "xsec friends dir is empty"
    echo "running xsec friends script"
    python3 friends/build_friend_tree.py --basepath $ntuple_dir --outputpath $xsec_friends_dir --nthreads 20 --xrootd
fi

echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
echo "##############################################################################################"

shape_output_folder=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
# if the output folder does not exist, create it
if [ ! -d "$shape_output_folder" ]; then
    mkdir -p $shape_output_folder
fi

python shapes/produce_shapes_tauID.py --channels $CHANNEL \
    --directory $shape_input_ntuple_dir \
    --${CHANNEL}-friend-directory $xsec_friends_dir  \
    --era $ERA --num-processes 4 --num-threads 4 \
    --optimization-level 1 \
    --control-plot-set ${VARIABLES} \
    --output-file $shape_output_folder

# echo "##############################################################################################"
# echo "#      Additional estimations                                      #"
# echo "##############################################################################################"

# bash ./shapes/do_estimations.sh 2018 ${shape_output_folder}.root 1


# echo "##############################################################################################"
# echo "#     plotting                                      #"
# echo "##############################################################################################"

# python3 plotting/plot_shapes_tauID.py -l --era Run${ERA} --input ${shape_output_folder}.root --variables ${VARIABLES} --channels ${CHANNEL} --embedding --categories ${categories_string%,}

# echo "##############################################################################################"
# echo "#     synced shapes                                      #"
# echo "##############################################################################################"

# python shapes/convert_to_synced_shapes.py -e $ERA \
#     -i output/shapes/${ERA}-${CHANNEL}-analysis-shapes-${TAG}/shapes-analysis-${ERA}-${CHANNEL}-${PROC}.root \
#     -o output/shapes/${ERA}-${CHANNEL}-${TAG}-synced_shapes_${VARIABLE}-${PROC} \
#     --variable-selection ${VARIABLE} \
#     -n 12