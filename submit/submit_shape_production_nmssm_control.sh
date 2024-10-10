#!/bin/bash

ERA=$1
CHANNEL=$2
SUBMIT_MODE=$3
TAG=$4
CONTROL=$5
BOOSTED=$6
NTUPLETAG=$7
OUTPUT=$8
MASSX=$9
MASSY=${10}
VARIABLES=${11}

[[ ! -z $1 && ! -z $2 && ! -z $3 && ! -z $4 && ! -z $5 ]] || (
    echo "[ERROR] Number of given parameters is too small."
    exit 1
)
[[ ! -z $6 ]] || CONTROL=0
CONTROL_ARG=""
if [[ $CONTROL == 1 ]]; then
    CONTROL_ARG="--gof-inputs --control-plot-set ${VARIABLES}"
    echo "[INFO] Control plots will be produced. Argument: ${CONTROL_ARG}"
fi

source utils/setup_ul_samples.sh $NTUPLETAG $ERA
source utils/setup_root.sh
# source utils/bashFunctionCollection.sh

if [[ "$SUBMIT_MODE" == "multigraph" ]]; then
    echo "[ERROR] Not implemented yet."
    exit 1
elif [[ "$SUBMIT_MODE" == "singlegraph" ]]; then
    echo "[INFO] Preparing graph for submission..."
    echo "[INFO] Using tag $TAG"
    echo "[INFO] Using friends $FF_FRIENDS $RECO_FRIENDS"
    [[ ! -d $OUTPUT ]] && mkdir -p $OUTPUT

    if [[ $BOOSTED == 0 ]]; then
        python shapes/produce_shapes.py --channels $CHANNEL \
            --directory $NTUPLES \
            --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS $KINFIT_RES_FRIENDS $FASTMTT_FRIENDS \
            --era $ERA --xrootd \
            --optimization-level 1 \
            --only-create-graphs \
            --graph-dir $OUTPUT \
            --output-file dummy.root --boosted-b-analysis \
            --massX $MASSX --massY $MASSY \
            --validation-tag $TAG \
            $CONTROL_ARG
    
        # Set output graph file name produced during graph creation.
        GRAPH_FILE_FULL_NAME=${OUTPUT}/analysis_unit_graphs-${ERA}-${CHANNEL}-${MASSX}-${MASSY}.pkl
        GRAPH_FILE=${OUTPUT}/analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}-${MASSX}-${MASSY}.pkl
        if [[ $CONTROL == 1 ]]; then
            GRAPH_FILE_FULL_NAME=${OUTPUT}/control_unit_graphs-${ERA}-${CHANNEL}-${MASSX}-${MASSY}.pkl
            GRAPH_FILE=${OUTPUT}/control_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}.pkl
        fi
        # rename the graph file to a shorter name
        mv $GRAPH_FILE_FULL_NAME $GRAPH_FILE

        # Prepare the jdl file for single core jobs.
        echo "[INFO] Creating the logging direcory for the jobs..."
        GF_NAME=$(basename $GRAPH_FILE)
        if [[ ! -d log/condorShapes/${GF_NAME%.pkl}/ ]]; then
            mkdir -p log/condorShapes/${GF_NAME%.pkl}/
        fi
        if [[ ! -d log/${GF_NAME%.pkl}/ ]]; then
            mkdir -p log/${GF_NAME%.pkl}/
        fi

        echo "[INFO] Preparing submission file for resolved tautau single core jobs for variation pipelines..."
        cp submit/produce_shapes_cc7.jdl $OUTPUT
        echo "output = log/condorShapes/${GF_NAME%.pkl}/\$(cluster).\$(Process).out" >>$OUTPUT/produce_shapes_cc7.jdl
        echo "error = log/condorShapes/${GF_NAME%.pkl}/\$(cluster).\$(Process).err" >>$OUTPUT/produce_shapes_cc7.jdl
        echo "log = log/condorShapes/${GF_NAME%.pkl}/\$(cluster).\$(Process).log" >>$OUTPUT/produce_shapes_cc7.jdl
        echo "queue a3,a2,a1 from $OUTPUT/arguments.txt" >>$OUTPUT/produce_shapes_cc7.jdl
        echo "JobBatchName = Shapes_${CHANNEL}_${ERA}_${MASSX}_${MASSY}" >>$OUTPUT/produce_shapes_cc7.jdl

        # Prepare the multicore jdl.
        echo "[INFO] Preparing submission file for resolved tautau multi core jobs for nominal pipeline..."
        cp submit/produce_shapes_cc7.jdl $OUTPUT/produce_shapes_cc7_multicore.jdl
        # Replace the values in the config which differ for multicore jobs.
        sed -i '/^+RequestWalltime/c\+RequestWalltime = 10800' $OUTPUT/produce_shapes_cc7_multicore.jdl
        if [[ $CONTROL == 1 ]]; then
            sed -i '/^RequestMemory/c\RequestMemory = 24000' $OUTPUT/produce_shapes_cc7_multicore.jdl
        else
            sed -i '/^RequestMemory/c\RequestMemory = 8000' $OUTPUT/produce_shapes_cc7_multicore.jdl
        fi
        sed -i '/^RequestCpus/c\RequestCpus = 4' $OUTPUT/produce_shapes_cc7_multicore.jdl
        sed -i '/^arguments/c\arguments = $(Proxy_path) $(a1) $(a2) $(a3) $(a4)' ${OUTPUT}/produce_shapes_cc7_multicore.jdl
        # Add log file locations to output file.
        echo "output = log/condorShapes/${GF_NAME%.pkl}/multicore.\$(cluster).\$(Process).out" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
        echo "error = log/condorShapes/${GF_NAME%.pkl}/multicore.\$(cluster).\$(Process).err" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
        echo "log = log/condorShapes/${GF_NAME%.pkl}/multicore.\$(cluster).\$(Process).log" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
        echo "JobBatchName = Shapes_${CHANNEL}_${ERA}_${MASSX}_${MASSY}" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
        echo "queue a3,a2,a4,a1 from $OUTPUT/arguments_multicore.txt" >>$OUTPUT/produce_shapes_cc7_multicore.jdl

        # Assemble the arguments.txt file used in the submission
        python submit/prepare_args_file.py --graph-file $GRAPH_FILE --output-dir $OUTPUT --pack-multiple-pipelines 10
        echo "[INFO] Submit shape production with 'condor_submit $OUTPUT/produce_shapes_cc7.jdl' and 'condor_submit $OUTPUT/produce_shapes_cc7_multicore.jdl'"
        condor_submit $OUTPUT/produce_shapes_cc7.jdl
        condor_submit $OUTPUT/produce_shapes_cc7_multicore.jdl

    elif [[ $BOOSTED == 1 ]]; then
        python shapes/produce_shapes.py --channels $CHANNEL \
            --directory $NTUPLES \
            --${CHANNEL}-friend-directory $XSEC_FRIENDS $FF_FRIENDS $KINFIT_BOOST_FRIENDS $FASTMTT_FRIENDS \
            --era $ERA --xrootd \
            --optimization-level 1 \
            --only-create-graphs \
            --graph-dir $OUTPUT \
            --output-file dummy_boosted.root --boosted-b-analysis --boosted-tau-analysis \
            --massX $MASSX --massY $MASSY \
            --validation-tag $TAG \
            $CONTROL_ARG

        # Set output graph file name produced during graph creation.
        GRAPH_FILE_FULL_NAME_BOOSTED=${OUTPUT}/boosted_analysis_unit_graphs-${ERA}-${CHANNEL}-${MASSX}-${MASSY}.pkl
        GRAPH_FILE_BOOSTED=${OUTPUT}/boosted_analysis_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}-${MASSX}-${MASSY}.pkl
        if [[ $CONTROL == 1 ]]; then
            GRAPH_FILE_FULL_NAME_BOOSTED=${OUTPUT}/boosted_control_unit_graphs-${ERA}-${CHANNEL}-${MASSX}-${MASSY}.pkl
            GRAPH_FILE_BOOSTED=${OUTPUT}/boosted_control_unit_graphs-${ERA}-${CHANNEL}-${NTUPLETAG}-${TAG}.pkl
        fi
        # rename the graph file to a shorter name
        mv $GRAPH_FILE_FULL_NAME_BOOSTED $GRAPH_FILE_BOOSTED

        # Prepare the jdl file for single core jobs.
        echo "[INFO] Creating the logging direcory for the jobs..."
        GF_NAME_BOOSTED=$(basename $GRAPH_FILE_BOOSTED)
        if [[ ! -d log/condorShapes/${GF_NAME_BOOSTED%.pkl}/ ]]; then
            mkdir -p log/condorShapes/${GF_NAME_BOOSTED%.pkl}/
        fi
        if [[ ! -d log/${GF_NAME_BOOSTED%.pkl}/ ]]; then
            mkdir -p log/${GF_NAME_BOOSTED%.pkl}/
        fi

        echo "[INFO] Preparing submission file for boosted tautau single core jobs for variation pipelines..."
        cp submit/produce_shapes_cc7.jdl $OUTPUT
        echo "output = log/condorShapes/${GF_NAME_BOOSTED%.pkl}/\$(cluster).\$(Process).out" >>$OUTPUT/produce_shapes_cc7.jdl
        echo "error = log/condorShapes/${GF_NAME_BOOSTED%.pkl}/\$(cluster).\$(Process).err" >>$OUTPUT/produce_shapes_cc7.jdl
        echo "log = log/condorShapes/${GF_NAME_BOOSTED%.pkl}/\$(cluster).\$(Process).log" >>$OUTPUT/produce_shapes_cc7.jdl
        echo "queue a3,a2,a1 from $OUTPUT/arguments.txt" >>$OUTPUT/produce_shapes_cc7.jdl
        echo "JobBatchName = Boosted_shapes_${CHANNEL}_${ERA}_${MASSX}_${MASSY}" >>$OUTPUT/produce_shapes_cc7.jdl

        # Prepare the multicore jdl.
        echo "[INFO] Preparing submission file for boosted tautau multi core jobs for nominal pipeline..."
        cp submit/produce_shapes_cc7.jdl $OUTPUT/produce_shapes_cc7_multicore.jdl
        # Replace the values in the config which differ for multicore jobs.
        sed -i '/^+RequestWalltime/c\+RequestWalltime = 10800' $OUTPUT/produce_shapes_cc7_multicore.jdl
        if [[ $CONTROL == 1 ]]; then
            sed -i '/^RequestMemory/c\RequestMemory = 24000' $OUTPUT/produce_shapes_cc7_multicore.jdl
        else
            sed -i '/^RequestMemory/c\RequestMemory = 8000' $OUTPUT/produce_shapes_cc7_multicore.jdl
        fi
        sed -i '/^RequestCpus/c\RequestCpus = 4' $OUTPUT/produce_shapes_cc7_multicore.jdl
        sed -i '/^arguments/c\arguments = $(Proxy_path) $(a1) $(a2) $(a3) $(a4)' ${OUTPUT}/produce_shapes_cc7_multicore.jdl
        # Add log file locations to output file.
        echo "output = log/condorShapes/${GF_NAME_BOOSTED%.pkl}/multicore.\$(cluster).\$(Process).out" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
        echo "error = log/condorShapes/${GF_NAME_BOOSTED%.pkl}/multicore.\$(cluster).\$(Process).err" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
        echo "log = log/condorShapes/${GF_NAME_BOOSTED%.pkl}/multicore.\$(cluster).\$(Process).log" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
        echo "JobBatchName = Boosted_shapes_${CHANNEL}_${ERA}_${MASSX}_${MASSY}" >>$OUTPUT/produce_shapes_cc7_multicore.jdl
        echo "queue a3,a2,a4,a1 from $OUTPUT/arguments_multicore.txt" >>$OUTPUT/produce_shapes_cc7_multicore.jdl

        # Assemble the arguments.txt file used in the submission
        python submit/prepare_args_file.py --graph-file $GRAPH_FILE_BOOSTED --output-dir $OUTPUT --pack-multiple-pipelines 10
        echo "[INFO] Submit boosted shape production with 'condor_submit $OUTPUT/produce_shapes_cc7.jdl' and 'condor_submit $OUTPUT/produce_shapes_cc7_multicore.jdl'"
        condor_submit $OUTPUT/produce_shapes_cc7.jdl
        condor_submit $OUTPUT/produce_shapes_cc7_multicore.jdl
    else
        echo "[ERROR] Given boosted bool $BOOSTED is not supported. Aborting..."
        exit 1
    fi
else
    echo "[ERROR] Given mode $SUBMIT_MODE is not supported. Aborting..."
    exit 1
fi