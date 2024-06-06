export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5
WP=$6


echo $NTUPLETAG
echo $WP

VARIABLES="m_vis"
POSTFIX="-ML"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Datacard Setup

datacard_output="datacards_pt_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_dm="datacards_dm_sim_fit_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_incl="datacards_incl_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

impact_path="impacts_${TAG}"

output_shapes="tauid_shapes-${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_synced=output/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_rootfile=${shapes_output}.root
shapes_rootfile_mm=${shapes_output}_mm.root
shapes_rootfile_synced=${shapes_output_synced}_synced.root

echo "MY WP is: " ${WP}
echo "My out path is: ${shapes_output}"
echo "My synchpath is ${shapes_output_synced}"

# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "FRIENDS: ${FRIENDS}"
echo "XSEC: ${XSEC_FRIENDS}"

categories=("Pt20to25" "Pt25to30" "Pt30to35" "PtGt40" "DM0" "DM1" "DM10_11" "Inclusive")
dm_categories=("DM0" "DM1" "DM10_11")
printf -v categories_string '%s,' "${categories[@]}"
echo "Using Cateogires ${categories_string%,}"


es_shifts4_0=("embminus4p0" "embminus3p9" "embminus3p8" "embminus3p7" "embminus3p6" "embminus3p5" "embminus3p4" "embminus3p3"\
 "embminus3p2" "embminus3p1" "embminus3p0" "embminus2p9" "embminus2p8" "embminus2p7" "embminus2p6" "embminus2p5" "embminus2p4"\ 
 "embminus2p3" "embminus2p2" "embminus2p1" "embminus2p0" "embminus1p9" "embminus1p8" "embminus1p7" "embminus1p6" "embminus1p5"\
  "embminus1p4" "embminus1p3" "embminus1p2" "embminus1p1" "embminus1p0" "embminus0p9" "embminus0p8" "embminus0p7" "embminus0p6"\
   "embminus0p5" "embminus0p4" "embminus0p3" "embminus0p2" "embminus0p1" "emb0p0" "emb0p1" "emb0p2" "emb0p3" "emb0p4" "emb0p5" "emb0p6"\
    "emb0p7" "emb0p8" "emb0p9" "emb1p0" "emb1p1" "emb1p2" "emb1p3" "emb1p4" "emb1p5" "emb1p6" "emb1p7" "emb1p8" "emb1p9" "emb2p0" "emb2p1"\
     "emb2p2" "emb2p3" "emb2p4" "emb2p5" "emb2p6" "emb2p7" "emb2p8" "emb2p9" "emb3p0" "emb3p1" "emb3p2" "emb3p3" "emb3p4" "emb3p5" "emb3p6"\
      "emb3p7" "emb3p8" "emb3p9" "emb4p0")
VS_ELE_WP="VVLoose"


if [[ $MODE == "COPY" ]]; then
    source utils/setup_root.sh
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
        rsync -avhPl $KINGMAKER_BASEDIR$ERA/ $BASEDIR$ERA/
    fi
    exit 0
elif [[ $MODE == "COPY_XROOTD" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Copy sample to ceph, it not there yet                                                     #"
    echo "##############################################################################################"
    echo "[INFO] Copying ntuples to ceph via xrootd"
    echo "xrdcp -r $KINGMAKER_BASEDIR_XROOTD$ERA/ $BASEDIR$ERA/"
    if [ ! -d "$BASEDIR/$ERA" ]; then
        mkdir -p $BASEDIR/$ERA
    fi
    xrdcp -r $KINGMAKER_BASEDIR_XROOTD$ERA $BASEDIR
    exit 0
fi

if [[ $MODE == "XSEC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Checking xsec friends directory                                                       #"
    echo "##############################################################################################"
    python3 friends/build_friend_tree.py --basepath $KINGMAKER_BASEDIR_XROOTD --outputpath root://cmsdcache-kit-disk.gridka.de/$XSEC_FRIENDS --nthreads 20
    exit 0
fi


echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
echo "##############################################################################################"
echo "##############################################################################################"
echo "#      Producing shapes for ${CHANNEL}-${ERA}-${NTUPLETAG}                                         #"
echo "##############################################################################################"

# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
    mkdir -p "${shapes_output}_mm"
fi

echo "${shapes_output}_mm"

if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes_tauid_es.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 3 --num-threads 9 \
        --vs-jet-wp $WP \
        --vs-ele-wp ${VS_ELE_WP} \
        --optimization-level 1 --skip-systematic-variations \
        --special-analysis "TauID" \
        --control-plot-set ${VARIABLES} \
        --output-file $shapes_output  --xrootd  --validation-tag $TAG 
fi

if [[ $MODE == "CONTROLREGION" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes_tauid_es.py --channels mm \
        --directory $NTUPLES \
        --mm-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 3 --num-threads 9 \
        --vs-jet-wp $WP \
        --vs-ele-wp ${VS_ELE_WP} \
        --optimization-level 1 --skip-systematic-variations \
        --special-analysis "TauID" \
        --output-file "${shapes_output}_mm"  --xrootd --validation-tag $TAG
fi

PROCESSES="emb"
number="_emb_ssos"
if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes_tauid_es.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $XSEC_FRIENDS \
        --era $ERA --num-processes 3 --num-threads 9 \
        --vs-jet-wp $WP \
        --vs-ele-wp ${VS_ELE_WP} \
        --optimization-level 1 \
        --special-analysis "TauID" \
        --process-selection $PROCESSES \
        --control-plot-set ${VARIABLES} \
        --optimization-level 1 \
        --output-file $shapes_output$number --xrootd --validation-tag $TAG --es
fi

if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_ul.sh $ERA $CHANNEL \
        "singlegraph" $TAG 0 $NTUPLETAG $CONDOR_OUTPUT "TauID" "" $WP $VS_ELE_WP
    echo "[INFO] Jobs submitted"
fi

if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ "${ERA}" == "2018"  ||  "${ERA}" == "2017" ]]; then 
    datacard_era=${ERA}
elif [[ "${ERA}" == "2016postVFP"  ||  "${ERA}" == "2016preVFP" ]]; then
   datacard_era="2016"
fi


if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#      Additional estimations                                      #"
    echo "##############################################################################################"

    python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile} --do-qcd

    python shapes/do_estimations.py -e $ERA -i ${shapes_rootfile_mm} --do-qcd

    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"



    echo "##############################################################################################"
    echo "#     synced shapes                                      #"
    echo "##############################################################################################"

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python shapes/convert_to_synced_shapes.py -e ${datacard_era} \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        --variable-selection ${VARIABLES} \
        -n 1

    python shapes/convert_to_synced_shapes.py -e ${datacard_era} \
        -i "${shapes_rootfile_mm}" \
        -o "${shapes_output_synced}_mm" \
        --variable-selection ${VARIABLES} \
        -n 1

    inputfile="htt_${CHANNEL}.inputs-sm-Run${datacard_era}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${datacard_era}-${CHANNEL}*.root

    inputfile="htt_mm.inputs-sm-Run${datacard_era}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile ${shapes_output_synced}_mm/${datacard_era}-mm-*.root

    exit 0
fi

if [[ $MODE == "PLOT-CONTROL-ES" ]]; then
    source utils/setup_root.sh
    echo "##############################################################################################"
    echo "#     plotting                                      #"
    echo "##############################################################################################"

        for CATEGORY in "${dm_categories[@]}"
    do
        for es_sh in "${es_shifts4_0[@]}"
        do 
            python3 plotting/plot_shapes_control_es_shifts.py -l --era Run${ERA} --input ${shapes_rootfile} \
            --variables ${VARIABLES} --channels ${CHANNEL} --embedding --category $CATEGORY --energy_scale --es_shift $es_sh
        done
    done
fi

if [[ $MODE == "INST_COMB" ]]; then
    source utils/install_combine_tauid.sh
fi


dm_categories=("DM0" "DM1" "DM10_11")
# dm_categories=("DM10_11")
if [[ $MODE == "DATACARD_DM" ]]; then
    source utils/setup_cmssw_tauid.sh
    # # inputfile

    for dm_cat in "${dm_categories[@]}"
    do
        inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
        # # for category in "dm_binned"
        $CMSSW_BASE/bin/slc7_amd64_gcc10/MorphingTauID2017 \
            --base_path=$PWD \
            --input_folder_mt=$shapes_output_synced \
            --input_folder_mm=$shapes_output_synced \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=0 \
            --embedding=1 \
            --verbose=true \
            --postfix=$POSTFIX \
            --use_control_region=true \
            --auto_rebin=true \
            --categories=${dm_cat} \
            --era=$datacard_era \
            --output=$datacard_output_dm
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd output/$datacard_output_dm/
    
        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -i output/$datacard_output_dm/htt_mt_${dm_cat}/ -o workspace_dm.root --parallel 4 -m 125
    done

    exit 0
fi

#  2D likelihood scan for tau ID + ES, we vary ID from 0.5 to 1.5 abd ES from -4.0 % to +4.0%

# That's reflected in min/max_id and min/max_es parameters that have corresponding ranges


min_id=0
max_id=0
min_es=0
max_es=0

mH=120

scan_2D_plot_path="scan_2D_"${TAG}

if [[ $MODE == "SCAN_2D" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create 2D scan"

        for dm_cat in "${dm_categories[@]}"
    do
    
        combineTool.py -M T2W -i output/$datacard_output_dm/htt_mt_${dm_cat}/ -o ws_scan_${dm_cat}.root

        if [[ $dm_cat == "DM0" ]]; then
            min_id=0.5
            max_id=1.5
            min_es=-4.0
            max_es=4.0
        fi

        if [[ $dm_cat == "DM1" ]]; then
            min_id=0.5
            max_id=1.5
            min_es=-4.0
            max_es=4.0
        fi

        if [[ $dm_cat == "DM10_11" ]]; then
            min_id=0.5
            max_id=1.5
            min_es=-4.0
            max_es=4.0
        fi

            combineTool.py -M MultiDimFit -n .scan_2D_${dm_cat} -d output/$datacard_output_dm/htt_mt_${dm_cat}/ws_scan_${dm_cat}.root \
            --setParameters ES_${dm_cat}=0.2,r=0.9 --setParameterRanges r=${min_id},${max_id}:ES_${dm_cat}=${min_es},${max_es} \
            --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
            --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
            --redefineSignalPOIs ES_${dm_cat},r \
            --floatOtherPOIs=1 --points=400 --algo grid -m ${mH}

        echo "[INFO] Moving scan file to datacard folder ..."
        mv higgsCombine.scan_2D_${dm_cat}.MultiDimFit.mH${mH}.root output/$datacard_output_dm/htt_mt_${dm_cat}/

        echo "[INFO] Plotting 2D scan ..."
        echo "[INFO] Input file: " output/$datacard_output_dm/htt_mt_${dm_cat}/higgsCombine.scan_2D_${dm_cat}.MultiDimFit.mH${mH}.root
        echo "But before we create a folder for 2D scans"

        if [ ! -d "${scan_2D_plot_path}" ]; then
            mkdir -p  ${scan_2D_plot_path}
        fi

        python3 tau_id_es_measurement/plot_2D_scan.py --name scan_2D_${dm_cat} --in-path output/$datacard_output_dm/htt_mt_${dm_cat}/ \
         --tau-id-poi ${dm_cat} --tau-es-poi ES_${dm_cat} --outname ${dm_cat}
        mv scan_2D_${dm_cat}* ${scan_2D_plot_path}
    done

fi


fix_es=-1.4
fix_id=1.097

probl_nuisance="ES_DM1"

probl_dm_categories=("DM1")

if [[ $MODE == "PROBL_NUIS_SCAN" ]]; then

    source utils/setup_cmssw_tauid.sh

   echo "[INFO] Create 1D scan for problematic nuisance parameter ${probl_nuisance}"

           for dm_cat in "${probl_dm_categories[@]}"
    do

    combineTool.py -M MultiDimFit -n .scan_2D${dm_cat}_check_poi -d output/$datacard_output_dm/htt_mt_${dm_cat}/ws_scan_${dm_cat}.root \
    --setParameters ES_${dm_cat}=${fix_es},r=${fix_id} --setParameterRanges r=0.5,1.5:ES_${dm_cat}=-4.0,4.0 \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ${probl_nuisance} \
    --floatOtherPOIs=1 --points=400 --algo grid -v 2

    echo "[INFO] Moving scan with problematic nuisance parameter file to datacard folder ..."

    mv higgsCombine.nominal_${dm_cat}_check_poi.MultiDimFit.mH120.root output/$datacard_output_dm/htt_mt_${dm_cat}/

    echo "[INFO] Plotting 1D scan ..."

    python3 plot1DScan.py  output/$datacard_output_dm/htt_mt_${dm_cat}/higgsCombine.nominal_${dm_cat}_check_poi.MultiDimFit.mH120.root \
     --POI $probl_nuisance --y-max 12 --output ${TAG}_${ERA}_${CHANNEL}_${WP}_${dm_cat}_${probl_nuisance}_scan

    mv ${TAG}_${ERA}_${CHANNEL}_${WP}_${dm_cat}_${probl_nuisance}_scan.* output/$datacard_output_dm/htt_mt_${dm_cat}/
    done
fi


. tau_id_es_measurement/tau_id_es_sim_fit_conf.sh

if [[ $MODE == "MULTIFIT" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create Workspace for all the datacards"
    combineTool.py -M T2W -i output/$datacard_output_dm/cmb \
                -o out_multidim_dm.root \
                --parallel 8 -m 125 \
                -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
                --PO '"map=^.*/EMB_DM0:r_EMB_DM_0[1,${min_id_dm0},${max_id_dm0}]"' \
                --PO '"map=^.*/EMB_DM1:r_EMB_DM_1[1,${min_id_dm1},${max_id_dm1}]"' \
                --PO '"map=^.*/EMB_DM10_11:r_EMB_DM_10_11[1,${min_id_dm10_11},${max_id_dm10_11}]"'  

    combineTool.py -M MultiDimFit -n .comb_dm_fit -d output/$datacard_output_dm/cmb/out_multidim_dm.root \
    --setParameters ES_DM0=${es_dm0},ES_DM1=${es_dm1},ES_DM10_11=${es_dm10_11},r_EMB_DM_0=${id_dm0},r_EMB_DM_1=${id_dm1},r_EMB_DM_10_11=${id_dm10_11} \
    --setParameterRanges r_EMB_DM_0=${min_id_dm0},${max_id_dm0}:r_EMB_DM_1=${min_id_dm1},${max_id_dm1}:r_EMB_DM_10_11=${min_id_dm10_11},${max_id_dm10_11}:ES_DM0=${min_es_dm0},${max_es_dm0}:ES_DM1=${min_es_dm1},${max_es_dm1}:ES_DM10_11=${min_es_dm10_11},${max_es_dm10_11} \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_DM0,ES_DM1,ES_DM10_11,r_EMB_DM_0,r_EMB_DM_1,r_EMB_DM_10_11 --floatOtherPOIs=1 \
    --points=400 --algo singles

    mv higgsCombine.comb_dm_fit.MultiDimFit.mH120.root output/$datacard_output_dm/cmb/

fi

min_id_sep=0
max_id_sep=0

min_es_sep=0
max_es_sep=0

cent_id_sep=0
cent_es_sep=0

id_fit_stri=""
map_str=''

dm_categories_sep=("DM0" "DM1" "DM10_11")
if [[ $MODE == "MULTIFIT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh

    echo "[INFO] Create Workspace for all the datacards (fitting separately in every DM category)"    

        for dm_cat in "${dm_categories_sep[@]}"
    do

        if [[ $dm_cat == "DM0" ]]; then

            min_id_sep=$min_id_dm0
            max_id_sep=$max_id_dm0

            min_es_sep=$min_es_dm0
            max_es_sep=$max_es_dm0

            cent_id_sep=$id_dm0
            cent_es_sep=$es_dm0

            id_fit_stri='DM_0'
            map_str='"map=^.*/EMB_${dm_cat}:r_EMB_DM_0[1,${min_id_sep},${max_id_sep}]"'
        fi

        if [[ $dm_cat == "DM1" ]]; then

            min_id_sep=$min_id_dm1
            max_id_sep=$max_id_dm1

            min_es_sep=$min_es_dm1
            max_es_sep=$max_es_dm1

            cent_id_sep=$id_dm1
            cent_es_sep=$es_dm1

            id_fit_stri=DM_1
            map_str='"map=^.*/EMB_${dm_cat}:r_EMB_DM_1[1,${min_id_sep},${max_id_sep}]"'
        fi

        if [[ $dm_cat == "DM10_11" ]]; then

            min_id_sep=$min_id_dm10_11
            max_id_sep=$max_id_dm10_11

            min_es_sep=$min_es_dm10_11
            max_es_sep=$max_es_dm10_11

            cent_id_sep=$id_dm10_11
            cent_es_sep=$es_dm10_11

            id_fit_stri=DM_10_11
            map_str='"map=^.*/EMB_${dm_cat}:r_EMB_DM_10_11[1,${min_id_sep},${max_id_sep}]"'
        fi
    echo "My values"
    echo ${id_fit_stri}
    echo ${min_id_sep}, ${max_id_sep}

    combineTool.py -M T2W -i output/$datacard_output_dm/htt_mt_${dm_cat} \
        -o out_multidim_dm_${dm_cat}_sep_cat.root \
        --parallel 8 -m ${mH} \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO ${map_str} \

    combineTool.py -M MultiDimFit -n .comb_dm_sep_fit_${dm_cat} -d output/$datacard_output_dm/htt_mt_${dm_cat}/out_multidim_dm_${dm_cat}_sep_cat.root \
    --setParameters ES_${dm_cat}=${cent_es_sep},r_EMB_${id_fit_stri}=${cent_id_sep} \
    --setParameterRanges r_EMB_${id_fit_stri}=${min_id_sep},${max_id_sep}:ES_${dm_cat}=${min_es_sep},${max_es_sep} \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_${dm_cat},r_EMB_${id_fit_stri} --floatOtherPOIs=1 \
    --points=400 --algo singles -m ${mH}

    mv higgsCombine.comb_dm_sep_fit_${dm_cat}.MultiDimFit.mH${mH}.root output/$datacard_output_dm/htt_mt_${dm_cat}/
 done
fi


if [[ $MODE == "POSTFIT_MULT" ]]; then
    source utils/setup_cmssw_tauid.sh

    WORKSPACE=output/$datacard_output_dm/cmb/out_multidim_dm.root
    echo "[INFO] Printing fit result for category $(basename $RESDIR)"
    FILE=output/$datacard_output_dm/cmb/postfitshape.root
    FITFILE=output/$datacard_output_dm/cmb/fitDiagnostics.${ERA}.root
   
    combineTool.py -M FitDiagnostics  -d ${WORKSPACE} -m ${mH} \
    --setParameters ES_DM0=${es_dm0},ES_DM1=${es_dm1},ES_DM10_11=${es_dm10_11},r_EMB_DM_0=${id_dm0},r_EMB_DM_1=${id_dm1},r_EMB_DM_10_11=${id_dm10_11} \
    --setParameterRanges r_EMB_DM_0=${min_id_dm0},${max_id_dm0}:r_EMB_DM_1=${min_id_dm1},${max_id_dm1}:r_EMB_DM_10_11=${min_id_dm10_11},${max_id_dm10_11}:ES_DM0=${min_es_dm0},${max_es_dm0}:ES_DM1=${min_es_dm1},${max_es_dm1}:ES_DM10_11=${min_es_dm10_11},${max_es_dm10_11} \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_DM0,ES_DM1,ES_DM10_11,r_EMB_DM_0,r_EMB_DM_1,r_EMB_DM_10_11  \
    --parallel 16   -v2 --robustHesse 1 --saveShapes --saveWithUncertainties
    mv fitDiagnostics.Test.root $FITFILE
    mv higgsCombine.Test.FitDiagnostics.mH${mH}.root output/$datacard_output_dm/cmb/
    echo "[INFO] Already built Prefit/Postfit shapes"

    exit 0
fi

if [[ $MODE == "PLOT-MULTIPOSTFIT_DM" ]]; then
    source utils/setup_root.sh

    fit_categories=("DM0" "DM1" "DM10_11")



    for RESDIR in "${fit_categories[@]}" 
      do
        
        WORKSPACE=output/$datacard_output_dm/cmb/out_multidim_dm.root


        CATEGORY=$RESDIR
        
        FILE=output/$datacard_output_dm/cmb/postfitshape.root

        # create output folder if it does not exist
        if [ ! -d "output/postfitplots_emb_${TAG}_multifit/" ]; then
            mkdir -p output/postfitplots_emb_${TAG}_multifit/${WP}
        fi
        echo "[INFO] Postfits plots for category $CATEGORY"
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category $CATEGORY --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP} --prefit
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel ${CHANNEL} --embedding --single-category $CATEGORY --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP}
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category 100 --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP} --prefit
        python3 plotting/plot_shapes_tauID_postfit.py -l --era ${ERA} --input ${FILE} --channel mm --embedding --single-category 100 --categories "None" -o output/postfitplots_emb_${TAG}_multifit/${WP}
    done
    exit 0
fi

if [[ $MODE == "POI_CORRELATION" ]]; then
    source utils/setup_root.sh
    FITFILE=output/$datacard_output_dm/cmb/fitDiagnostics.${ERA}.root
    
    # python corr_plot.py $ERA $FITFILE
    python tau_id_es_measurement/poi_correlation.py $ERA $FITFILE

fi


min_id_sep_imp=0
max_id_sep_imp=0

min_es_sep_imp=0
max_es_sep_imp=0

cent_id_sep_imp=0
cent_es_sep_imp=0

id_var_imp=""

if [[ $MODE == "IMPACTS_ALL" ]]; then
    source utils/setup_cmssw_tauid.sh

    if [ ! -d "$impact_path/${ERA}/${CHANNEL}/${WP}" ]; then
        mkdir -p  $impact_path/${ERA}/${CHANNEL}/${WP}
    fi
    

    fit_categories_imp=("DM0" "DM1" "DM10_11")
            for dm_cat in "${fit_categories_imp[@]}"
    do
      WORKSPACE_IMP=output/$datacard_output_dm/htt_mt_${dm_cat}/out_multidim_dm_${dm_cat}_sep_cat.root

        if [[ $dm_cat == "DM0" ]]; then

            min_id_sep_imp=$min_id_dm0
            max_id_sep_imp=$max_id_dm0

            min_es_sep_imp=$min_es_dm0
            max_es_sep_imp=$max_es_dm0

            cent_id_sep_imp=$id_dm0
            cent_es_sep_imp=$es_dm0

            id_var_imp="DM_0"

        fi

        if [[ $dm_cat == "DM1" ]]; then

            min_id_sep_imp=$min_id_dm1
            max_id_sep_imp=$max_id_dm1

            min_es_sep_imp=$min_es_dm1
            max_es_sep_imp=$max_es_dm1

            cent_id_sep_imp=$id_dm1
            cent_es_sep_imp=$es_dm1

            id_var_imp="DM_1"

        fi

        if [[ $dm_cat == "DM10_11" ]]; then

            min_id_sep_imp=$min_id_dm10_11
            max_id_sep_imp=$max_id_dm10_11

            min_es_sep_imp=$min_es_dm10_11
            max_es_sep_imp=$max_es_dm10_11

            cent_id_sep_imp=$id_dm10_11
            cent_es_sep_imp=$es_dm10_11

            id_var_imp="DM_10_11"


        fi

    combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 123 \
        --setParameters ES_${dm_cat}=${cent_es_sep_imp},r_EMB_${id_var_imp}=${cent_id_sep_imp} \
        --setParameterRanges r_EMB_${id_var_imp}=${min_id_sep_imp},${max_id_sep_imp}:ES_${dm_cat}=${min_es_sep_imp},${max_es_sep_imp} \
        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
        --parallel 16 --doInitialFit 

    combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 123 \
        --setParameters ES_${dm_cat}=${cent_es_sep_imp},r_EMB_${id_var_imp}=${cent_id_sep_imp} \
        --setParameterRanges r_EMB_${id_var_imp}=${min_id_sep_imp},${max_id_sep_imp}:ES_${dm_cat}=${min_es_sep_imp},${max_es_sep_imp} \
        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
        --parallel 16 --doFits 

    combineTool.py -M Impacts -d $WORKSPACE_IMP -m 123 -o tauid_${WP}_impacts_r_${dm_cat}.json  

    plotImpacts.py -i tauid_${WP}_impacts_r_${dm_cat}.json -o tauid_${WP}_impacts_r_${dm_cat}
    # # cleanup the fit files
    rm higgsCombine_paramFit*.root
    # rm robustHesse_paramFit*.root
    mv tauid_${WP}_impacts_r_${dm_cat}* $impact_path/${ERA}/${CHANNEL}/${WP}
    done

    exit 0
fi
