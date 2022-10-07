export PYTHONPATH=$PYTHONPATH:$PWD/Dumbledraw
CHANNEL=$1
ERA=$2
NTUPLETAG=$3
TAG=$4
MODE=$5
# full set
VARIABLES="pt_1,pt_2,eta_1,eta_2,m_vis,jpt_1,jpt_2,jeta_1,jeta_2,mjj,njets,nbtag,bpt_1,bpt_2,mt_1,mt_2,mt_1_pf,mt_2_pf,pt_tt,pfmet,met,pzetamissvis,metphi,m_fastmtt,pt_fastmtt,eta_fastmtt,phi_fastmtt,pt_dijet,deltaR_ditaupair,decaymode_2,mt_tot,jet_hemisphere,pt_vis"
# used in training
VARIABLES="pt_1,pt_2,m_vis,njets,nbtag,jpt_1,jpt_2,jeta_1,jeta_2,m_fastmtt,mjj,pt_vis,deltaR_ditaupair,pt_dijet"
# VARIABLES="pt_2,jpt_2"
POSTFIX="-ML"
ulimit -s unlimited
source utils/setup_ul_samples.sh $NTUPLETAG $ERA

output_shapes="gof_shapes-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}"
CONDOR_OUTPUT=output/condor_shapes/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}
shapes_output=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/${output_shapes}
shapes_output_synced=output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/synced
shapes_rootfile=${shapes_output}.root
shapes_rootfile_synced=${shapes_output_synced}_synced.root

# if the output folder does not exist, create it
if [ ! -d "$shapes_output" ]; then
    mkdir -p $shapes_output
fi

# print the paths to be used
echo "KINGMAKER_BASEDIR: $KINGMAKER_BASEDIR"
echo "BASEDIR: ${BASEDIR}"
echo "output_shapes: ${output_shapes}"
echo "FRIENDS: ${FRIENDS}"
echo "###################################"
echo "#           Mode ${MODE}          #"
echo "###################################"

if [[ $MODE == "XSEC" ]]; then
    source utils/setup_root.sh
    python3 friends/build_friend_tree.py --basepath $BASEDIR --outputpath $XSEC_FRIENDS --nthreads 20
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
        python3 friends/build_friend_tree.py --basepath $BASEDIR --outputpath $XSEC_FRIENDS --nthreads 20
    fi
    exit 0
fi

if [[ $MODE == "GOF-BINNING" ]]; then
    source utils/setup_root.sh
    ./gof/create_gof_binning.sh $CHANNEL $ERA $NTUPLETAG $VARIABLES
fi

if [[ $MODE == "CONTROL" ]]; then
    source utils/setup_root.sh
    # python shapes/produce_shapes.py --channels $CHANNEL $NNSCORE_FRIENDS \
    #     --directory $NTUPLES \
    #     --${CHANNEL}-friend-directory $FRIENDS \
    #     --era $ERA --num-processes 4 --num-threads 6 \
    #     --optimization-level 1 --skip-systematic-variations \
    #     --output-file $shapes_output

    # python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-ff --do-qcd

    # now plot the shapes by looping over the categories
    for category in "ggh" "qqh" "ztt" "tt" "ff" "misc" "xxh"; do
        python3 plotting/plot_ml_shapes_control.py -l --era Run${ERA} --input ${shapes_output}.root --channel ${CHANNEL} --embedding --fake-factor --category ${category} --output-dir output/${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/controlplots --normalize-by-bin-width
    done
fi

if [[ $MODE == "LOCAL" ]]; then
    source utils/setup_root.sh
    python shapes/produce_shapes.py --channels $CHANNEL \
        --directory $NTUPLES \
        --${CHANNEL}-friend-directory $FRIENDS \
        --era $ERA --num-processes 4 --num-threads 12 \
        --optimization-level 1 --gof-inputs \
        --control-plot-set ${VARIABLES} \
        --output-file $shapes_output
fi

if [[ $MODE == "CONDOR" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Running on Condor"
    echo "[INFO] Condor output folder: ${CONDOR_OUTPUT}"
    bash submit/submit_shape_production_ul.sh $ERA $CHANNEL \
        "singlegraph" $TAG 1 $NTUPLETAG $CONDOR_OUTPUT ${VARIABLES} $NNSCORE_FRIENDS
    echo "[INFO] Jobs submitted"
fi
if [[ $MODE == "MERGE" ]]; then
    source utils/setup_root.sh
    echo "[INFO] Merging outputs located in ${CONDOR_OUTPUT}"
    hadd -j 5 -n 600 -f $shapes_rootfile ${CONDOR_OUTPUT}/../control_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}/*.root
fi

if [[ $MODE == "SYNC" ]]; then
    source utils/setup_root.sh
    python shapes/do_estimations.py -e $ERA -i ${shapes_output}.root --do-emb-tt --do-ff --do-qcd

    # if the output folder does not exist, create it
    if [ ! -d "$shapes_output_synced" ]; then
        mkdir -p $shapes_output_synced
    fi

    python shapes/convert_to_synced_shapes.py -e $ERA \
        -i ${shapes_rootfile} \
        -o ${shapes_output_synced} \
        -n 1 --gof

    inputfile="htt_${CHANNEL}.inputs-sm-Run${ERA}${POSTFIX}.root"
    hadd -f $shapes_output_synced/$inputfile $shapes_output_synced/${ERA}-${CHANNEL}*.root

    exit 0
fi

if [[ $MODE == "DATACARD" ]]; then
    source utils/setup_cmssw.sh
    # Datacard Setup
    for VARIABLE in ${VARIABLES//,/ }; do
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}_${VARIABLE}"
        GOF_CATEGORY_NAME=${CHANNEL}_${VARIABLE}
        ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
            --base_path=$PWD \
            --input_folder_mt=$shapes_output_synced \
            --input_folder_tt=$shapes_output_synced \
            --input_folder_et=$shapes_output_synced \
            --input_folder_em=$shapes_output_synced \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=1 \
            --embedding=1 \
            --postfix="-ML" \
            --channel=${CHANNEL} \
            --auto_rebin=false \
            --rebin_categories=false \
            --stxs_signals="stxs_stage0" \
            --categories="gof" \
            --era=${ERA} \
            --gof_category_name=$GOF_CATEGORY_NAME \
            --output=$datacard_output \
            --train_ff=1 \
            --train_stage0=1 --train_emb=1
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd $datacard_output/${CHANNEL}
        for FILE in */*.txt; do
            sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
        done
        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -o workspace.root -i $datacard_output/${CHANNEL}/125 --channel-masks
    done
    exit 0
fi

if [[ $MODE == "DATACARD-MC" ]]; then
    source utils/setup_cmssw.sh
    # Datacard Setup
    for VARIABLE in ${VARIABLES//,/ }; do
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ERA}_${CHANNEL}_${VARIABLE}"
        GOF_CATEGORY_NAME=${CHANNEL}_${VARIABLE}
        ${CMSSW_BASE}/bin/slc7_amd64_gcc700/MorphingSMRun2Legacy \
            --base_path=$PWD \
            --input_folder_mt=$shapes_output_synced \
            --input_folder_tt=$shapes_output_synced \
            --input_folder_et=$shapes_output_synced \
            --input_folder_em=$shapes_output_synced \
            --real_data=true \
            --classic_bbb=false \
            --binomial_bbb=false \
            --jetfakes=1 \
            --embedding=0 \
            --postfix="-ML" \
            --channel=${CHANNEL} \
            --auto_rebin=false \
            --rebin_categories=false \
            --stxs_signals="stxs_stage0" \
            --categories="gof" \
            --era=${ERA} \
            --gof_category_name=$GOF_CATEGORY_NAME \
            --output=$datacard_output \
            --train_ff=1 \
            --train_stage0=1 --train_emb=1
        THIS_PWD=${PWD}
        echo $THIS_PWD
        cd $datacard_output/${CHANNEL}
        for FILE in */*.txt; do
            sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
        done
        cd $THIS_PWD

        echo "[INFO] Create Workspace for datacard"
        combineTool.py -M T2W -o workspace.root -i $datacard_output/${CHANNEL}/125 --channel-masks
    done
    exit 0
fi

if [[ $MODE == "GOF" ]]; then
    source utils/setup_cmssw.sh
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        WORKSPACE=$datacard_output/${CHANNEL}/125/workspace.root
        MASS=125
        NUM_TOYS=100 # multiply x10
        for ALGO in "saturated" "KS" "AD"; do
            # Get test statistic value
            if [[ "$ALGO" == "saturated" ]]; then
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE --fixedSignalStrength=0 -v 1
            else
                combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE --plots --fixedSignalStrength=0
            fi

            # Throw toys
            TOYSOPT=""
            if [[ "$ALGO" == "saturated" ]]; then
                TOYSOPT="--toysFreq"
            fi

            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1230 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1231 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1232 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1233 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1234 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1235 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1236 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1237 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1238 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            combine -M GoodnessOfFit -n Test.${ID} --algo=$ALGO -m $MASS -d $WORKSPACE -s 1239 -t $NUM_TOYS $TOYSOPT --fixedSignalStrength=0 >/dev/null &
            wait
            # Collect results
            combineTool.py -M CollectGoodnessOfFit --input \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1230.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1231.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1232.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1233.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1234.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1235.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1236.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1237.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1238.root \
                higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.1239.root \
                --output output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json

            mv higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.123?.root output/gof/${NTUPLETAG}-${TAG}/${ID}/
            if [[ "$ALGO" == "saturated" ]]; then
                mv output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json output/gof/${NTUPLETAG}-${TAG}/${ID}/gof.json
            fi

            # Plot
            if [[ "$ALGO" != "saturated" ]]; then
                plotGof.py --statistic $ALGO --mass $MASS.0 --output gof_${ALGO} output/gof/${NTUPLETAG}-${TAG}/${ID}/gof_${ALGO}.json
                mv htt_${CHANNEL}_300_${ERA}gof_${ALGO}.p{df,ng} output/gof/${NTUPLETAG}-${TAG}/${ID}/
                python2 plotting/gof/plot_gof_metrics.py -e $ERA -g $ALGO -o output/gof/${NTUPLETAG}-${TAG}/${ID}/ -i output/gof/${NTUPLETAG}-${TAG}/${ID}/higgsCombineTest.${ID}.GoodnessOfFit.mH$MASS.root
            else
                plotGof.py --statistic $ALGO --mass $MASS.0 --output output/gof/${NTUPLETAG}-${TAG}/${ID}/gof output/gof/${NTUPLETAG}-${TAG}/${ID}/gof.json
            fi
        done
    done
    source utils/setup_root.sh
    python3 gof/plot_gof_summary.py --variables $VARIABLES --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL
    exit 0
fi

if [[ $MODE == "GOF-SUMMARY" ]]; then
    source utils/setup_root.sh
    python3 gof/plot_gof_summary.py --variables $VARIABLES --path output/gof/${NTUPLETAG}-${TAG}/ --era $ERA --channel $CHANNEL

fi

if [[ $MODE == "POSTFIT" ]]; then
    source utils/setup_cmssw.sh
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        WORKSPACE=$datacard_output/${CHANNEL}/125/workspace.root
        combine \
            -M FitDiagnostics \
            -m 125 -d $WORKSPACE \
            --robustFit 1 -v1 \
            --robustHesse 1 \
            -n .$ID \
            --setParameters r=0 --freezeParameters r \
            --X-rtd MINIMIZER_analytic \
            --cminDefaultMinimizerStrategy 0 |
            tee $LOGFILE
        FITFILE=${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root
        mv fitDiagnostics.${ID}.root $FITFILE
        #python combine/check_mlfit.py fitDiagnostics${ERA}.root
        # root -l $FITFILE <<< "fit_b->Print(); fit_s->Print()"

        python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
            ${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root -a \
            -f html >${datacard_output}/nuisances.html
        PostFitShapesFromWorkspace -m 125 -w $WORKSPACE \
            -o ${datacard_output}/${ID}-datacard-shapes-prefit.root \
            -d ${datacard_output}/cmb/125/htt_${CHANNEL}_300_${ERA}.txt

        PostFitShapesFromWorkspace -m 125 -w $WORKSPACE \
            -o ${datacard_output}/${ID}-datacard-shapes-postfit-b.root \
            -f ${datacard_output}/fitDiagnostics.${ID}.MultiDimFit.mH125.root:fit_b --postfit --sampling \
            -d ${datacard_output}/cmb/125/htt_${CHANNEL}_300_${ERA}.txt
    done
    exit 0

fi

if [[ $MODE == "PLOT-POSTFIT" ]]; then
    source utils/setup_root.sh
    SUMMARYFOLDER=output/gof/${NTUPLETAG}-${TAG}/plots
    [ -d $SUMMARYFOLDER ] || mkdir -p $SUMMARYFOLDER
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        PLOTDIR=${datacard_output}/plots
        PREFITFILE=${datacard_output}/${ID}-datacard-shapes-prefit.root
        POSTFITFILE=${datacard_output}/${ID}-datacard-shapes-postfit-b.root
        [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
        echo "[INFO] Using postfitshapes from $FILE"
        # python3 plotting/plot_shapes.py -i $FILE -o $PLOTDIR \
        #         -c ${channel} -e $ERA --categories $CATEGORIES \
        #         --fake-factor --embedding --normalize-by-bin-width \
        #         -l --train-ff True --train-emb True
        # CATEGORIES="stxs_stage0"

        # python3 plotting/plot_shapes_combined.py -i $FILE -o $PLOTDIR -c ${CHANNEL} -e $ERA --categories "None" --fake-factor --embedding -l --train-ff True --train-emb True --combine-backgrounds
        # python3 plotting/plot_shapes_combined.py -i $FILE -o $PLOTDIR -c ${CHANNEL} -e $ERA --categories "None" --fake-factor --embedding -l --train-ff True --train-emb True --combine-backgrounds
        for OPTION in "" "--png"; do
            python3 gof/plot_shapes_gof.py -i $PREFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor --embedding \
                --gof-variable $VARIABLE -o ${PLOTDIR}
            python3 gof/plot_shapes_gof.py -i $POSTFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor --embedding \
                --gof-variable $VARIABLE -o ${PLOTDIR}
        done
        cp ${PLOTDIR}/*.p{df,ng} $SUMMARYFOLDER
    done
    exit 0
fi

if [[ $MODE == "PLOT-POSTFIT-MC" ]]; then
    source utils/setup_root.sh
    SUMMARYFOLDER=output/gof/${NTUPLETAG}-${TAG}/plots
    [ -d $SUMMARYFOLDER ] || mkdir -p $SUMMARYFOLDER
    for VARIABLE in ${VARIABLES//,/ }; do
        ID=${ERA}_${CHANNEL}_${VARIABLE}
        datacard_output="output/gof/${NTUPLETAG}-${TAG}/${ID}"
        PLOTDIR=${datacard_output}/plots
        PREFITFILE=${datacard_output}/${ID}-datacard-shapes-prefit.root
        POSTFITFILE=${datacard_output}/${ID}-datacard-shapes-postfit-b.root
        [ -d $PLOTDIR ] || mkdir -p $PLOTDIR
        echo "[INFO] Using postfitshapes from $FILE"
        for OPTION in "" "--png"; do
            python3 gof/plot_shapes_gof.py -i $PREFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor \
                --gof-variable $VARIABLE -o ${PLOTDIR}
            python3 gof/plot_shapes_gof.py -i $POSTFITFILE -c $CHANNEL -e $ERA $OPTION \
                --categories 'None' --fake-factor \
                --gof-variable $VARIABLE -o ${PLOTDIR}
        done
        cp ${PLOTDIR}/*.p{df,ng} $SUMMARYFOLDER
    done
    exit 0
fi

if [[ $MODE == "IMPACTS" ]]; then
    source utils/setup_cmssw.sh
    WORKSPACE=output/$datacard_output/mt/125/workspace.root
    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --doInitialFit --robustFit 1 \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --robustFit 1 --doFits \
        --parallel 16

    combineTool.py -M Impacts -d $WORKSPACE -m 125 -o sm_${ERA}_${CHANNEL}.json
    plotImpacts.py -i sm_${ERA}_${CHANNEL}.json -o sm_${ERA}_${CHANNEL}_impacts
    # cleanup the fit files
    rm higgsCombine*.root
    exit 0
fi
