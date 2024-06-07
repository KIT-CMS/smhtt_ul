source utils/setup_cmssw_tauid.sh
source utils/bashFunctionCollection.sh


CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
WP=$5

categories=("DM0" "DM1" "DM10_11")



fix_es=0
fix_id=0

id_min=0
id_max=0

es_min=0
es_max=0

datacard_output_dm="datacards_dm_sim_fit_${TAG}/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"

mH=127

. combine_scripts/fit_id_es.sh 
for dm_cat in ${categories[@]}; do

    if [[ ! -d lscan_/${TAG}/${ERA}/${CHANNEL}/${TAG}/${dm_cat}/ ]]
    then
        mkdir -p lscan/${TAG}/${ERA}/${CHANNEL}/${WP}/${dm_cat}/
        mkdir -p lscan/${TAG}/${ERA}/${CHANNEL}/${WP}/${dm_cat}/
    fi

    
    if [[ $dm_cat == "DM0" ]]; then
        fix_es=${fix_es_dm0}
        fix_id=${fix_id_dm0}

        id_min=${min_id_dm0}
        id_max=${max_id_dm0}
        es_min=${min_es_dm0}
        es_max=${max_es_dm0}
    fi

    if [[ $dm_cat == "DM1" ]]; then
        fix_es=${fix_es_dm1}
        fix_id=${fix_id_dm1}

        id_min=${min_id_dm1}
        id_max=${max_id_dm1}
        es_min=${min_es_dm1}
        es_max=${max_es_dm1}
    fi

    if [[ $dm_cat == "DM10_11" ]]; then
        fix_es=${fix_es_dm10_11}
        fix_id=${fix_id_dm10_11}

        id_min=${min_id_dm10_11}
        id_max=${max_id_dm10_11}
        es_min=${min_es_dm10_11}
        es_max=${max_es_dm10_11}
    fi

                                                   
    fit_name_id=nominal_${dm_cat}_check_poi_id
    fit_name_es=nominal_${dm_cat}_check_poi_es
   

    combineTool.py -M MultiDimFit -n .${fit_name_id} -d output/$datacard_output_dm/htt_mt_${dm_cat}/ws_scan_${dm_cat}.root \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs r \
    --setParameterRanges r=${id_min},${id_max} --setParameters r=${fix_id},ES_${dm_cat}=${fix_es} \
    --floatOtherPOIs=1 --points=400 --algo grid -v 2 -m ${mH}

    combineTool.py -M MultiDimFit -n .${fit_name_es} -d output/$datacard_output_dm/htt_mt_${dm_cat}/ws_scan_${dm_cat}.root \
    --robustFit=1 --setRobustFitAlgo=Minuit2  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP \
    --cminFallbackAlgo Minuit2,Migrad,0:0.001 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminPreScan \
    --redefineSignalPOIs ES_${dm_cat} \
    --setParameterRanges ES_${dm_cat}=${es_min},${es_max} --setParameters ES_${dm_cat}=${fix_es},r=${fix_id} \
    --floatOtherPOIs=1 --points=400 --algo grid -v 2 -m ${mH}
    
    # moving the output (tau ID) to the correct folder
    python3  tau_id_es_measurement/plot1DScan_comb.py  higgsCombine.${fit_name_id}.MultiDimFit.mH${mH}.root --POI r \
    --y-max 12 --output ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}_r_${dm_cat}
    mv ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}*  lscan/${TAG}/${ERA}/${CHANNEL}/${WP}/${dm_cat}/
    mv higgsCombine.${fit_name_id}.MultiDimFit.mH${mH}.root lscan/${TAG}/${ERA}/${CHANNEL}/${WP}/${dm_cat}/

    # moving the output (tau ES) to the correct folder
    python3  tau_id_es_measurement/plot1DScan_comb.py  higgsCombine.${fit_name_es}.MultiDimFit.mH${mH}.root --POI ES_${dm_cat} \
    --y-max 12 --output ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}_es_${dm_cat}
    mv ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}_es_${dm_cat}*  lscan/${TAG}/${ERA}/${CHANNEL}/${WP}/${dm_cat}/
    mv higgsCombine.${fit_name_es}.MultiDimFit.mH${mH}.root lscan/${TAG}/${ERA}/${CHANNEL}/${WP}/${dm_cat}/
done
# exit 0

