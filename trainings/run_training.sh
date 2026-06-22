#!/bin/bash

source /work/sgiappic/MiniForge/bin/activate
conda activate uncertainty-training

export PYTHONPATH=$PWD:$PYTHONPATH
law index -v

worker="2"
cuda_device="0,1" #"-2" 

channels=(mt tt et) #et

train_tag="260608"

tasks=(
    # BuildCENNTCombinedModelsTask
    RunAllCENNTConfusionMatrixWorkflow
    # BuildCENNTConfusionMatrixTask
)


for channel in "${channels[@]}"; do
    echo "Processing channel: ${channel}"
    tag="${train_tag}_grouped_${channel}"
    
    for task in "${tasks[@]}"; do
        law run "${task}" --workers ${worker} --local-scheduler --version "${tag}" --log-level INFO \
            --no-lock --use-grouped-DNN --batch-size 100000 --cuda-device "${cuda_device}" \
            --dataset-directory="/ceph/sgiappic/Htt_training/${train_tag}_train/dataset/${channel}/folds/" \
            --dataset-config-file="/ceph/sgiappic/Htt_training/${train_tag}_train/dataset/${channel}/folds/config.yaml" \
            --base-config-file="/work/sgiappic/smhtt_ul/trainings/uncertainty-aware-training/datasets/smhtt/run3-coarse/smhtt_${channel}.yaml"
    done
done