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

datacard_output="datacards_test_pt_v3/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_dm="datacards_es_4_0_29Apr_morph_v1/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

datacard_output_incl="datacards_incl_test_v3/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

impact_path="impacts_test_v3"

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
# dm_categories=("DM0")
printf -v categories_string '%s,' "${categories[@]}"
echo "Using Cateogires ${categories_string%,}"

es_shifts=("embminus2p5" "embminus2p4" "embminus2p3" "embminus2p2" "embminus2p1" "embminus2p0" "embminus1p9" "embminus1p8" "embminus1p7" "embminus1p6" "embminus1p5" "embminus1p4" "embminus1p3"\
 "embminus1p2" "embminus1p1" "embminus1p0" "embminus0p9" "embminus0p8" "embminus0p7" "embminus0p6" "embminus0p5" "embminus0p4" "embminus0p3" "embminus0p2" "embminus0p1" "emb0p0" "emb0p1"\
  "emb0p2" "emb0p3" "emb0p4" "emb0p5" "emb0p6" "emb0p7" "emb0p8" "emb0p9" "emb1p0" "emb1p1" "emb1p2" "emb1p3" "emb1p4" "emb1p5" "emb1p6"\
   "emb1p7" "emb1p8" "emb1p9" "emb2p0" "emb2p1" "emb2p2" "emb2p3" "emb2p4" "emb2p5")

# es_shifts=("embminus2p5" "embminus2p4" "embminus2p3")
es_shifts4_0=("embminus4p0" "embminus3p9" "embminus3p8" "embminus3p7" "embminus3p6" "embminus3p5" "embminus3p4" "embminus3p3"\
 "embminus3p2" "embminus3p1" "embminus3p0" "embminus2p9" "embminus2p8" "embminus2p7" "embminus2p6" "embminus2p5" "embminus2p4"\ 
 "embminus2p3" "embminus2p2" "embminus2p1" "embminus2p0" "embminus1p9" "embminus1p8" "embminus1p7" "embminus1p6" "embminus1p5"\
  "embminus1p4" "embminus1p3" "embminus1p2" "embminus1p1" "embminus1p0" "embminus0p9" "embminus0p8" "embminus0p7" "embminus0p6"\
   "embminus0p5" "embminus0p4" "embminus0p3" "embminus0p2" "embminus0p1" "emb0p0" "emb0p1" "emb0p2" "emb0p3" "emb0p4" "emb0p5" "emb0p6"\
    "emb0p7" "emb0p8" "emb0p9" "emb1p0" "emb1p1" "emb1p2" "emb1p3" "emb1p4" "emb1p5" "emb1p6" "emb1p7" "emb1p8" "emb1p9" "emb2p0" "emb2p1"\
     "emb2p2" "emb2p3" "emb2p4" "emb2p5" "emb2p6" "emb2p7" "emb2p8" "emb2p9" "emb3p0" "emb3p1" "emb3p2" "emb3p3" "emb3p4" "emb3p5" "emb3p6"\
      "emb3p7" "emb3p8" "emb3p9" "emb4p0")
VS_ELE_WP="vvloose"


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

min_id_dm0=0.8
max_id_dm0=1.2
min_es_dm0=-2
max_es_dm0=2
id_dm0=0.95
es_dm0=-1


min_id_dm1=0.9
max_id_dm1=1.2
min_es_dm1=-3.8
max_es_dm1=0.5
id_dm1=1.12
es_dm1=-1.4


min_id_dm10_11=0.9
max_id_dm10_11=1.2
min_es_dm10_11=-3
max_es_dm10_11=1.5
id_dm10_11=1.02
es_dm10_11=-1

min_id_sep=0
max_id_sep=0

min_es_sep=0
max_es_sep=0

cent_id_sep=0
cent_es_sep=0

id_fit_stri=""
map_str=''

mH=126

# dm_categories_sep=("DM0" "DM1" "DM10_11")
dm_categories_sep=("DM1")

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



min_id_sep_pf=0
max_id_sep_pf=0

min_es_sep_pf=0
max_es_sep_pf=0

cent_id_sep_pf=0
cent_es_sep_pf=0

id_var=""

if [[ $MODE == "POSTFIT_MULT_SEP" ]]; then
    source utils/setup_cmssw_tauid.sh
    
        for dm_cat in "${dm_categories_sep[@]}"
    do

    RESDIR=output/$datacard_output_dm/htt_mt_${dm_cat}
    WORKSPACE=${RESDIR}/out_multidim_dm_${dm_cat}_sep_cat.root
    echo "[INFO] Printing fit result for category $(basename $RESDIR)"
    FITFILE=${RESDIR}/fitDiagnostics.${ERA}.root

        if [[ $dm_cat == "DM0" ]]; then

            min_id_sep_pf=$min_id_dm0
            max_id_sep_pf=$max_id_dm0

            min_es_sep_pf=$min_es_dm0
            max_es_sep_pf=$max_es_dm0

            cent_id_sep_pf=$id_dm0
            cent_es_sep_pf=$es_dm0

            id_var="DM_0"

        fi

        if [[ $dm_cat == "DM1" ]]; then

            min_id_sep_pf=$min_id_dm1
            max_id_sep_pf=$max_id_dm1

            min_es_sep_pf=$min_es_dm1
            max_es_sep_pf=$max_es_dm1

            cent_id_sep_pf=$id_dm1
            cent_es_sep_pf=$es_dm1

            id_var="DM_1"

        fi

        if [[ $dm_cat == "DM10_11" ]]; then

            min_id_sep_pf=$min_id_dm10_11
            max_id_sep_pf=$max_id_dm10_11

            min_es_sep_pf=$min_es_dm10_11
            max_es_sep_pf=$max_es_dm10_11

            cent_id_sep_pf=$id_dm10_11
            cent_es_sep_pf=$es_dm10_11

            id_var="DM_10_11"

        fi

    combineTool.py -M FitDiagnostics  -d ${WORKSPACE} -m ${mH} \
    --setParameters ES_${dm_cat}=${cent_es_sep_pf},r_EMB_${id_var}=${cent_id_sep_pf} \
    --setParameterRanges r_EMB_${id_var}=${min_id_sep_pf},${max_id_sep_pf}:ES_${dm_cat}=${min_es_sep_pf},${max_es_sep_pf} \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_${dm_cat},r_EMB_${id_var}  \
    --parallel 16   -v1 --robustHesse 1 --saveShapes --saveWithUncertainties


    mv fitDiagnostics.Test.root $FITFILE
    mv higgsCombine.Test.FitDiagnostics.mH${mH}.root output/$datacard_output_dm/htt_mt_${dm_cat}/

    done

    exit 0
fi



if [[ $MODE == "IMPACTS_ID" ]]; then
    source utils/setup_cmssw_tauid.sh
    WORKSPACE_IMP=output/$datacard_output_dm/htt_mt_DM0/out_multidim_dm_DM0_sep_cat.root

    fit_categories=("DM0" "DM1" "DM10_11")

    imp_es_dm0=-1
    
    combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 123 \
        --setParameters ES_DM0=${imp_es_dm0},r_EMB_DM_0=${id_dm0} \
        --setParameterRanges r_EMB_DM_0=${min_id_dm0},${max_id_dm0}:ES_DM0=${min_es_dm0},${max_es_dm0} \
        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
        --parallel 16 --doInitialFit 

    combineTool.py -M Impacts  -d ${WORKSPACE_IMP} -m 123 \
        --setParameters ES_DM0=${imp_es_dm0},r_EMB_DM_0=${id_dm0} \
        --setParameterRanges r_EMB_DM_0=${min_id_dm0},${max_id_dm0}:ES_DM0=${min_es_dm0},${max_es_dm0} \
        --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
        --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
        --parallel 16 --doFits 

    combineTool.py -M Impacts -d $WORKSPACE_IMP -m 123 -o tauid_${WP}_impacts_r_DM0_v4.json  

    plotImpacts.py -i tauid_${WP}_impacts_r_DM0_v4.json -o tauid_${WP}_DM0_r_impacts_v4 
    # # cleanup the fit files
    rm higgsCombine_paramFit*.root
    # rm robustHesse_paramFit*.root
    exit 0
fi