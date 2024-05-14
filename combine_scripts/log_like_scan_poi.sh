source utils/setup_cmssw_tauid.sh
source utils/bashFunctionCollection.sh

TAG=$1
NTUPLETAG=$2
ERA=$3
CHANNEL=$4
WP=$5
WP_ELE=$6



categories=("DM0" "DM1" "DM10_11")


tag_folder="medium_vs_ele_es_4_0"


fix_es=0
fix_id=0

datacard_output_dm="datacards_es_4_0_29Apr_morph_v1/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"


for dm_cat in ${categories[@]}; do

    if [[ ! -d lscan_/${tag_folder}/${ERA}/${CHANNEL}/${TAG}/${dm_cat}/ ]]
    then
        mkdir -p lscan/${tag_folder}/${ERA}/${CHANNEL}/${WP}/${dm_cat}/
        mkdir -p lscan/${tag_folder}/${ERA}/${CHANNEL}/${WP}/${dm_cat}/
    fi

    
    if [[ $dm_cat == "DM0" ]]; then
        fix_es=-0.999
        fix_id=0.994
    fi

    if [[ $dm_cat == "DM1" ]]; then
        fix_es=-1.399 
        fix_id=1.089
    fi

    if [[ $dm_cat == "DM10_11" ]]; then
        fix_es=-1.193
        fix_id=1.060
    fi

                                                   
    fit_name=nominal_${dm_cat}_check_poi
   
    
    combineTool.py -M MultiDimFit -n .nominal_${dm_cat}_check_poi -d output/$datacard_output_dm/htt_mt_${dm_cat}/ws_scan_${dm_cat}.root \
    --setParameters ES_${dm_cat}=${fix_es},r=${fix_id} --setParameterRanges r=0.5,1.5:ES_${dm_cat}=-4.0,4.0 \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_${dm_cat},r \
    --floatOtherPOIs=1 --points=400 --algo grid -v 2 -m 127
    
    
    python3  plot1DScan.py  higgsCombine.${fit_name}.MultiDimFit.mH127.root --POI r \
    --y-max 12 --output ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}_r_${dm_cat}
    python3  plot1DScan.py  higgsCombine.${fit_name}.MultiDimFit.mH127.root --POI ES_${dm_cat} \
     --y-max 12 --output ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}_es_${dm_cat}
    mv ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}*  /work/olavoryk/tau_pog_tau_sfs/tau_id_es_main/smhtt_ul/lscan/${tag_folder}/${ERA}/${CHANNEL}/${WP}/${dm_cat}/

done
# exit 0

