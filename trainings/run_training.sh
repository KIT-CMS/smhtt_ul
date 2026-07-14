#!/bin/bash

source /work/sgiappic/MiniForge/bin/activate
conda activate uncertainty-training

export PYTHONPATH=$PWD:$PYTHONPATH
law index -v

worker="1"
cuda_device="0" #"-2"  1

channels=(mt) #et tt

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
            --no-lock --cuda-device "${cuda_device}" --batch-size 100000 --use-grouped-DNN \
            --dataset-directory="/ceph/sgiappic/Htt_training/${train_tag}_train/dataset/${channel}/folds/" \
            --dataset-config-file="/ceph/sgiappic/Htt_training/${train_tag}_train/dataset/${channel}/folds/config.yaml" \
            --base-config-file="/work/sgiappic/smhtt_ul/trainings/uncertainty-aware-training/datasets/smhtt/run3-coarse/smhtt_${channel}.yaml"
    done
done
