#!/bin/bash
set -e

INPUT_FILE="$1"
if [ -z "$INPUT_FILE" ]; then
    echo "Error: Please provide an input file."
    exit 1
fi

NUM_WORKERS=1

USER=$(whoami)
ANALYSISPATH=$(pwd)
FOLDER="split_graph_processing"

SUBMIT_DIR="$FOLDER/condor_jobs"
JOB_LOG="$SUBMIT_DIR/workflow.log"

source utils/setup_root.sh

mkdir -p "$SUBMIT_DIR"

PROXY_PATH="/home/$USER/.globus/x509up"

RUN_SH_SCRIPT="$SUBMIT_DIR/run.sh"
RUN_SH_TEMPLATE=$(cat << EOF

    #!/bin/bash
    PROCESS=\$1
    INDEX=\$2

    cd "$ANALYSISPATH"

    source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
    export PYTHONPATH=\$PWD:\$PYTHONPATH

    export X509_USER_PROXY=\${_CONDOR_JOB_IWD}/x509up

    python3 "$FOLDER"/procedure.py --input "$INPUT_FILE" --process \$PROCESS --index \$INDEX --mode run --numworkers $NUM_WORKERS

EOF
)

JDL_TEMPLATE=$(cat << EOF

Universe = docker
docker_image = cverstege/alma9-gridjob

executable =  $SUBMIT_DIR/run.sh

use_x509userproxy = True
x509userproxy = $PROXY_PATH

request_cpus = $NUM_WORKERS
request_memory = 10000
request_disk = 10000
+RequestWalltime = 7200

Output = $SUBMIT_DIR/job_\$(Cluster)_\$(Process).out
Error  = $SUBMIT_DIR/job_\$(Cluster)_\$(Process).err
Log  = $SUBMIT_DIR/workflow.log

requirements = TARGET.ProvidesEKPResources

accounting_group = cms.higgs

transfer_input_files =  $SUBMIT_DIR/run.sh,$PROXY_PATH

EOF
)

echo "$RUN_SH_TEMPLATE" > "$RUN_SH_SCRIPT"
chmod +x "$RUN_SH_SCRIPT"

TEMP_JDL=$(mktemp /tmp/job_XXXXXX.jdl)
trap "rm -f '$TEMP_JDL'" EXIT

while true; do
    echo "--------------------------------------------------"
    echo "Running setup procedure to generate argument list..."

    ARG_LIST=$(python3 $FOLDER/procedure.py --input "$INPUT_FILE" --mode setup)
    if [ -z "$ARG_LIST" ]; then
        echo "Setup complete. No more jobs to run."
        break
    fi

    echo "Cleaning up previous log file: $JOB_LOG"
    rm -f "$JOB_LOG"

    echo "$JDL_TEMPLATE" > "$TEMP_JDL"
    echo "" >> "$TEMP_JDL"
    echo "queue arguments from (" >> "$TEMP_JDL"
    echo "$ARG_LIST" >> "$TEMP_JDL"
    echo ")" >> "$TEMP_JDL"

    echo "Submitting jobs from generated argument list..."

    SUBMIT_OUTPUT=$(condor_submit "$TEMP_JDL")
    CLUSTER_ID=$(echo "$SUBMIT_OUTPUT" | grep -oE 'submitted to cluster [0-9]+' | grep -oE '[0-9]+')
    
    if [ -z "$CLUSTER_ID" ]; then
        echo "Error: Failed to submit jobs or could not parse Cluster ID from condor_submit."
        echo "Submit output: $SUBMIT_OUTPUT"
        exit 1
    fi
    echo "Successfully submitted cluster $CLUSTER_ID"

    cp "$TEMP_JDL" "$SUBMIT_DIR/job_${CLUSTER_ID}.jdl"
    echo "Saved JDL with embedded arguments to: $SUBMIT_DIR/job_${CLUSTER_ID}.jdl"

    echo "Waiting for all jobs in cluster $CLUSTER_ID to finish..."
    condor_wait "$JOB_LOG"

    if [ $? -ne 0 ]; then
        echo "Error: condor_wait failed. The job cluster may have failed or been held."
        echo "Check job status with 'condor_q $CLUSTER_ID' and review logs in '$SUBMIT_DIR'."
        exit 1
    fi
    
    echo "Cluster $CLUSTER_ID finished successfully."
done

echo "--------------------------------------------------"
echo "All job batches have completed."

python3 $FOLDER/procedure.py --input "$INPUT_FILE" --output "combined.root" --mode hadd

