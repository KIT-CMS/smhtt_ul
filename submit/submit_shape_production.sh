#!/bin/bash

ERA=$1
CHANNEL=$2
PROCESSES=$3
SUBMIT_MODE=$4
TAG=$5
CONTROL=$6

[[ ! -z $1 && ! -z $2 && ! -z $3 && ! -z $4  && ! -z $5 ]] || ( echo "[ERROR] Number of given parameters is too small."; exit 1 )
[[ ! -z $6 ]] || CONTROL=0
CONTROL_ARG=""
if [[ $CONTROL == 1 ]]
then
    CONTROL_ARG="--control-plots"
fi

source utils/setup_susy_samples.sh $ERA
source utils/setup_samples.sh $ERA
source utils/setup_root.sh
source utils/bashFunctionCollection.sh

IFS="," read -a PROCS_ARR <<< $PROCESSES
PROCESSES=""
for PROC in ${PROCS_ARR[@]};
do
    if [[ "$PROC" =~ "backgrounds" ]]
    then
        BKG_PROCS="data,emb,ztt,zl,zj,ttt,ttl,ttj,vvt,vvl,vvj,w"
        PROCESSES="$PROCESSES,$BKG_PROCS"
    elif [[ "$PROC" =~ "sm_signals" ]]
    then
        SIG_PROCS="ggh,qqh,zh,wh,tth,gghww,qqhww,whww,zhww"
        PROCESSES="$PROCESSES,$SIG_PROCS"
    elif [[ "$PROC" =~ "mssm_ggh_split1" ]]
    then
        PROCESSES="$PROCESSES,$GGH_SAMPLES_SPLIT1"
    elif [[ "$PROC" =~ "mssm_ggh_split2" ]]
    then
        PROCESSES="$PROCESSES,$GGH_SAMPLES_SPLIT2"
    elif [[ "$PROC" =~ "mssm_ggh_split3" ]]
    then
        PROCESSES="$PROCESSES,$GGH_SAMPLES_SPLIT3"
    elif [[ "$PROC" =~ "mssm_bbh_split1" ]]
    then
        PROCESSES="$PROCESSES,$BBH_SAMPLES_SPLIT1"
    elif [[ "$PROC" =~ "mssm_bbh_split2" ]]
    then
        PROCESSES="$PROCESSES,$BBH_SAMPLES_SPLIT2"
    else
        echo "[INFO] Add selection of single process $PROC"
        PROCESSES="$PROCESSES,$PROC"
    fi
done
# Remove introduced leading comma again.
PROCESSES=$(sort_string ${PROCESSES#,})

if [[ "$SUBMIT_MODE" == "multigraph" ]]
then
    echo "[ERROR] Not implemented yet."
    exit 1
elif [[ "$SUBMIT_MODE" == "singlegraph" ]]
then
    echo "[INFO] Preparing graph for processes $PROCESSES for submission..."
    OUTPUT=output/submit_files/${ERA}-${CHANNEL}-${PROCESSES}-${TAG}
    [[ ! -d $OUTPUT ]] && mkdir -p $OUTPUT
    python shapes/produce_shapes.py --channels $CHANNEL \
        			    --output-file dummy.root \
        			    --directory $ARTUS_OUTPUTS \
                                    --et-friend-directory $ARTUS_FRIENDS_ET $ARTUS_FRIENDS_FAKE_FACTOR \
                                    --mt-friend-directory $ARTUS_FRIENDS_MT $ARTUS_FRIENDS_FAKE_FACTOR \
                                    --tt-friend-directory $ARTUS_FRIENDS_TT $ARTUS_FRIENDS_FAKE_FACTOR \
                                    --em-friend-directory $ARTUS_FRIENDS_EM \
                                    --era $ERA \
                                    --optimization-level 1 \
                                    --process-selection $PROCESSES \
                                    --only-create-graphs \
                                    --graph-dir $OUTPUT \
                                    $CONTROL_ARG
    # Set output graph file name produced during graph creation.
    GRAPH_FILE=${OUTPUT}/analysis_unit_graphs-${ERA}-${CHANNEL}-${PROCESSES}.pkl
    [[ $CONTROL == 1 ]] && GRAPH_FILE=${OUTPUT}/control_unit_graphs-${ERA}-${CHANNEL}-${PROCESSES}.pkl
    # Prepare the jdl file for single core jobs.
    echo "[INFO] Creating the logging direcory for the jobs..."
    GF_NAME=$(basename $GRAPH_FILE)
    if [[ ! -d log/condorShapes/${GF_NAME%.pkl}/ ]]
    then
        mkdir -p log/condorShapes/${GF_NAME%.pkl}/
    fi
    if [[ ! -d log/${GF_NAME%.pkl}/ ]]
    then
        mkdir -p log/${GF_NAME%.pkl}/
    fi

    echo "[INFO] Preparing submission file for single core jobs for variation pipelines..."
    cp submit/produce_shapes_cc7.jdl $OUTPUT
    echo "output = log/condorShapes/${GF_NAME%.pkl}/\$(cluster).\$(Process).out" >> $OUTPUT/produce_shapes_cc7.jdl
    echo "error = log/condorShapes/${GF_NAME%.pkl}/\$(cluster).\$(Process).err" >> $OUTPUT/produce_shapes_cc7.jdl
    echo "log = log/condorShapes/${GF_NAME%.pkl}/\$(cluster).\$(Process).log" >> $OUTPUT/produce_shapes_cc7.jdl
    echo "queue a3,a2,a1 from $OUTPUT/arguments.txt" >> $OUTPUT/produce_shapes_cc7.jdl
    
    # Prepare the multicore jdl.
    echo "[INFO] Preparing submission file for multi core jobs for nominal pipeline..."
    cp submit/produce_shapes_cc7.jdl $OUTPUT/produce_shapes_cc7_multicore.jdl
    # Replace the values in the config which differ for multicore jobs.
    sed -i '/^RequestMemory/c\RequestMemory = 10000' $OUTPUT/produce_shapes_cc7_multicore.jdl
    sed -i '/^RequestCpus/c\RequestCpus = 8' $OUTPUT/produce_shapes_cc7_multicore.jdl
    sed -i '/^arguments/c\arguments = $(a1) $(a2) $(a3) $(a4)' ${OUTPUT}/produce_shapes_cc7_multicore.jdl
    # Add log file locations to output file.
    echo "output = log/condorShapes/${GF_NAME%.pkl}/multicore.\$(cluster).\$(Process).out" >> $OUTPUT/produce_shapes_cc7_multicore.jdl
    echo "error = log/condorShapes/${GF_NAME%.pkl}/multicore.\$(cluster).\$(Process).err" >> $OUTPUT/produce_shapes_cc7_multicore.jdl
    echo "log = log/condorShapes/${GF_NAME%.pkl}/multicore.\$(cluster).\$(Process).log" >> $OUTPUT/produce_shapes_cc7_multicore.jdl
    echo "queue a3,a2,a4,a1 from $OUTPUT/arguments_multicore.txt" >> $OUTPUT/produce_shapes_cc7_multicore.jdl

    # Assemble the arguments.txt file used in the submission
    python submit/prepare_args_file.py --graph-file $GRAPH_FILE --output-dir $OUTPUT --pack-multiple-pipelines 10
    echo "[INFO] Submit shape production with 'condor_submit $OUTPUT/produce_shapes_cc7.jdl' and 'condor_submit $OUTPUT/produce_shapes_cc7_multicore.jdl'"
    condor_submit $OUTPUT/produce_shapes_cc7.jdl
    condor_submit $OUTPUT/produce_shapes_cc7_multicore.jdl
else
    echo "[ERROR] Given mode $SUBMIT_MODE is not supported. Aborting..."
    exit 1
fi
