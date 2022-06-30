source utils/setup_root.sh
export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4

VARIABLES="pt_1,pt_2,eta_1,eta_2,m_vis,jpt_1,jpt_2,jeta_1,jeta_2,mjj,njets,nbtag,bpt_1,bpt_2,mt_1,mt_2,pt_tt,met"

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

shape_output_folder=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
# if the output folder does not exist, create it
if [ ! -d "$shape_output_folder" ]; then
    mkdir -p $shape_output_folder
fi

python shapes/produce_shapes.py --channels $CHANNEL \
    --directory $shape_input_ntuple_dir \
    --${CHANNEL}-friend-directory $xsec_friends_dir  \
    --era $ERA --num-processes 4 --num-threads 4 \
    --optimization-level 1 --control-plots \
    --control-plot-set ${VARIABLES} --skip-systematic-variations \
    --output-file $shape_output_folder

echo "##############################################################################################"
echo "#      Additional estimations                                      #"
echo "##############################################################################################"

bash ./shapes/do_estimations.sh 2018 ${shape_output_folder}.root 1


echo "##############################################################################################"
echo "#     plotting                                      #"
echo "##############################################################################################"

python3 plotting/plot_shapes_control.py -l --era Run${ERA} --input ${shape_output_folder}.root --variables ${VARIABLES} --channels ${CHANNEL} --embedding