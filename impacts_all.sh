export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5
WP=$6
VS_ELE_WP=$7
DEEP_TAU=$8

VARIABLES="m_vis"
POSTFIX="-ML"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

# Datacard Setup
# WP="medium"
datacard_output="datacards/${NTUPLETAG}-${TAG}/${ERA}_tauid_${WP}"


output_shapes="tauid_shapes-${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_synced=output/${WP}-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_rootfile=${shapes_output}.root
shapes_rootfile_mm=${shapes_output}_mm.root
shapes_rootfile_synced=${shapes_output_synced}_synced.root


# categories=("Pt20to25" "Pt25to30" "Pt30to35" "Pt35to40" "PtGt40" "DM0" "DM1" "DM10_11" "Inclusive")
categories=("Pt20to25")

out_impacts=impacts_output

printf -v categories_string '%s,' "${categories[@]}"

if [[ $MODE == "IMPACTS" ]]; then
    source utils/setup_cmssw.sh
    
    if [ ! -d "$out_impacts/${ERA}/${CHANNEL}/${WP}" ]; then
        mkdir -p  $out_impacts/${ERA}/${CHANNEL}/${WP}
    fi

    
    for WSP in ${categories[@]}; do

        if [[ ! -d "/work/olavoryk/tauID_SF_ES/smhtt_ul/$out_impacts/${ERA}/${CHANNEL}/${WP}/${WSP}" ]]; then

            mkdir -p /work/olavoryk/tauID_SF_ES/smhtt_ul/$out_impacts/${ERA}/${CHANNEL}/${WP}/${WSP}
        fi


        WORKSPACE=output/$datacard_output/htt_mt_${WSP}/workspace.root
        echo "My current workspace is" $WORKSPACE
        combineTool.py -M Impacts -d $WORKSPACE -m 125 \
                    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
                    --doInitialFit --robustFit 1 -v 3 \
                    --setParameterRanges r=0.8,1.2  \
                    --setParameters r=1.00 \
                    --parallel 16 \
                    --job-mode script

        bash job_combine_task_0.sh
        mv job_combine_task_0.sh /work/olavoryk/tauID_SF_ES/smhtt_ul/$out_impacts/${ERA}/${CHANNEL}/${WP}/${WSP}/initial_fit.sh

        combineTool.py -M Impacts -d $WORKSPACE -m 125 \
                    --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
                    --robustFit 1 --doFits \
                    --setParameterRanges r=0.8,1.2 \
                    --setParameters r=1.00 \
                    --parallel 16 \
                    --job-mode script
                    
        mv job_combine_task_*.sh /work/olavoryk/tauID_SF_ES/smhtt_ul/$out_impacts/${ERA}/${CHANNEL}/${WP}/${WSP}/


        combineTool.py -M Impacts -d $WORKSPACE -m 125 \
            --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
            --robustFit 1 --doFits \
            --setParameterRanges r=0.8,1.2 \
            --setParameters r=1.00 \
            --parallel 16 

        combineTool.py -M Impacts -d $WORKSPACE -m 125 -o /work/olavoryk/tauID_SF_ES/smhtt_ul/$out_impacts/${ERA}/${CHANNEL}/${WP}/${WSP}/tauid_${ERA}_${CHANNEL}_${WP}_${TAG}_${WSP}_impacts.json
        plotImpacts.py -i /work/olavoryk/tauID_SF_ES/smhtt_ul/$out_impacts/${ERA}/${CHANNEL}/${WP}/${WSP}/tauid_${ERA}_${CHANNEL}_${WP}_${TAG}_${WSP}_impacts.json -o tauid_${ERA}_${CHANNEL}_${WP}_${TAG}_impacts_${WSP}
        mv tauid_${ERA}_${CHANNEL}_${WP}_${TAG}_impacts_${WSP}.pdf /work/olavoryk/tauID_SF_ES/smhtt_ul/$out_impacts/${ERA}/${CHANNEL}/${WP}/${WSP}/

        # move the fit files
        mv higgsCombine*.root /work/olavoryk/tauID_SF_ES/smhtt_ul/${out_impacts}/${ERA}/${CHANNEL}/${WP}/${WSP}/

    done
   exit 0
fi