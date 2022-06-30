source utils/setup_root.sh
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4

VARIABLES=(pt_1 pt_2 eta_1 eta_2 m_vis jpt_1 jpt_2 jeta_1 jeta_2 dijetpt jdeta mjj njets nbtag bpt_1 bpt_2 mt_1 mt_2 ptvis pt_tt met)

ntuple_dir="/ceph/sbrommer/smhtt_ul/ntuples/${NTUPLETAG}/ntuples/${ERA}/"
shape_input_ntuple_dir="/ceph/sbrommer/smhtt_ul/ntuples/${NTUPLETAG}/ntuples/"
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
    python3 friends/build_friend_tree.py --basepath $ntuple_dir --outputpath $xsec_friends_dir --nthreads 10
fi

echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
echo "##############################################################################################"



python shapes/produce_shapes.py --channels $CHANNEL \
    --output-file ${output_shapes} \
    --directory $shape_input_ntuple_dir \
    --${CHANNEL}-friend-directory $xsec_friends_dir  \
    --era $ERA --num-processes 1 --num-threads 1 \
    --optimization-level 1 --control-plots --control-plot-set m_vis --skip-systematic-variations