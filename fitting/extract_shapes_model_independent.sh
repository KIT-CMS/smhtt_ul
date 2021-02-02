#!/bin/bash

ERA=$1
FREEZE=$2
[[ -z $FREEZE ]] && FREEZE="MH=2600,r_ggH=0.002,r_bbH=0.002"
CORES=1
[[ ! -z $3 ]] && CORES=$3

source utils/setup_cmssw.sh

pushd $FITDIR


# Produce the necessary workspaces.
combineTool.py -M T2W -o "ws.root" \
               -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
               --PO '"map=^.*/ggh_(i|t|b).?$:r_ggH[0,0,200]"' --PO '"map=^.*/bbh$:r_bbH[0,0,200]"' \
               -i output_mssm/${ERA}/htt_*/ \
               -m 110 \
               --parallel $CORES

# Extract prefit shapes.
prefit_postfit_shapes_parallel.py --datacard_pattern "output_mssm/201?/htt_*/combined.txt.cmb" \
                                  --workspace_name ws.root \
                                  --freeze_arguments "--freeze $FREEZE" \
                                  --output_name prefit_shapes_${FREEZE}.root
                                  --parallel $CORES

hadd -f prefit_shapes_${FREEZE}.root output_mssm/201?/htt_*/prefit_shapes_${FREEZE}.root
