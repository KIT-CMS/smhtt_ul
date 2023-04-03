source utils/setup_cmssw.sh
source utils/bashFunctionCollection.sh

TAG=$1
NTUPLETAG=$2
ERA=$3
CHANNEL=$4
WP=$5
WP_ELE=$6

categories=("PtGt40")


# categories=("Pt20to25" "Pt25to30" "Pt30to35" "Pt35to40" "PtGt40" "DM0" "DM1" "DM10_11" "Inclusive")


tag_folder="medium_vs_ele"


poi=CMS_ExtrapSSOS_mt_Run2018



for cat in ${categories[@]}; do

    if [[ ! -d lscan_/${tag_folder}/${ERA}/${CHANNEL}/${TAG}/${cat}/${poi} ]]
    then
        mkdir -p lscan/${tag_folder}/${ERA}/${CHANNEL}/${WP}/${cat}/${poi}
        mkdir -p lscan/${tag_folder}/${ERA}/${CHANNEL}/${WP}/${cat}/${poi}
    fi

    DATACARD="/work/olavoryk/tauID_SF_ES/smhtt_ul/output/datacards/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}/htt_mt_${cat}/"
    workspace="/work/olavoryk/tauID_SF_ES/smhtt_ul/output/datacards/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}/htt_mt_${cat}/workspace.root"

                                                   
    cd $DATACARD
    # combine -M MultiDimFit $workspace -n .nominal  --algo grid  --points 100 --redefineSignalPOIs $poi,r  --setParameterRanges $poi=-2.0,2.0   --setParameters $poi=0.0,r=1
    
    combine -M MultiDimFit -n .nominal --algo grid --redefineSignalPOIs r -P $poi --floatOtherPOIs 1 --saveInactivePOI 1 --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0  --setParameterRanges $poi=-2,2 -m 125 -d $workspace --setParameters $poi=0,r=1.00 -v 2 --points 100 
    
    # combine -M MultiDimFit -n .nominal _paramFit_Test_CMS_htt_tjXsec --algo grid --redefineSignalPOIs r -P CMS_htt_tjXsec --floatOtherPOIs 1 --saveInactivePOI 1 --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 --robustFit 1 --setParameterRanges r=0.8,1.2:CMS_htt_tjXsec=-4.0,4.0 -m 125 -d $workspace --setParameters r=1.00,CMS_htt_tjXsec=0.0 
    plot1DScan.py  higgsCombine.nominal.MultiDimFit.mH125.root --POI $poi --y-max 16 --output ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}
    mv ${TAG}_${ERA}_${CHANNEL}_${WP}_${cat}*  /work/olavoryk/tauID_SF_ES/smhtt_ul/lscan/${tag_folder}/${ERA}/${CHANNEL}/${WP}/${cat}/${poi}/

done
exit 0

# /work/olavoryk/tauID_SF_ES/smhtt_ul/output/datacards/2022_07_v6-vtight_mt_2018UL_vs_ele_medium_DT21/2018_tauid_medium/htt_mt_DM10_11/
