#!/bin/bash

export PYTHONPATH=$PWD:$PYTHONPATH
law index -v

worker="2"
cuda_device="0,1"

channels=(mt tt) #et

train_tag="260507"

tasks=(
    # BuildCENNTCombinedModelsTask
    RunAllCENNTConfusionMatrixWorkflow
    # BuildCENNTConfusionMatrixTask
)


for channel in "${channels[@]}"; do
    echo "Processing channel: ${channel}"
    tag="${train_tag}_${channel}"
    
    for task in "${tasks[@]}"; do
        law run "${task}" --workers ${worker} --local-scheduler --version "${tag}" --log-level INFO \
            --cuda-device "${cuda_device}" --no-lock \
            --dataset-directory="/ceph/sgiappic/Htt_training/cennt_folds/coarse/${channel}/" \
            --base-config-file="/work/sgiappic/smhtt_ul/trainings/uncertainty-aware-training/datasets/smhtt/run3-coarse/smhtt_${channel}.yaml"
    done
done