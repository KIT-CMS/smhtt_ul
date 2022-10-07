source utils/setup_cmssw.sh
datacard_output=$1
ERA=$2
CHANNEL=$3
IS_MC=$4
STXS_FIT=$5
DATACARD=output/$datacard_output/$CHANNEL/125/combined.txt.cmb
# add the default unc groups from fitting/groups_emb.txt if they are not already there
# this can be check by checking if "theory group" can be found in the card. If not, add the groups
if ! grep -q "theory group" $DATACARD; then

    if [[ $IS_MC == "1" ]]; then
        echo "Adding MC unc groups to datacard"
        cat fitting/groups_mc.txt >> $DATACARD
    else
        echo "Adding EMB unc groups to datacard"
        cat fitting/groups_emb.txt >> $DATACARD
    fi
fi
if [[ $STXS_FIT == "inclusive" ]]; then

    combineTool.py -M T2W -o workspace.root -i $DATACARD --parallel 4 -m 125 \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH_htt.?$:r[1,0,2]"' \
        --PO '"map=^.*/qqH_htt.?$:r[1,0,2]"'
    POIS=("r")
    RESULTFOLDER=output/$datacard_output/$CHANNEL/results/inclusive
else
    combineTool.py -M T2W -o workspace.root -i $DATACARD --parallel 4 -m 125 \
        -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
        --PO '"map=^.*/ggH_htt.?$:r_ggH[1,0,2]"' \
        --PO '"map=^.*/qqH_htt.?$:r_qqH[1,0,2]"'
    POIS=("r_ggH r_qqH")
    RESULTFOLDER=output/$datacard_output/$CHANNEL/results/stage0
fi
mkdir -p $RESULTFOLDER
echo "Will run fit for POIs: ${POIS[@]}"
# loop though the POIs and run the fit
for POI in ${POIS[@]}; do
    combine -M MultiDimFit output/$datacard_output/mt/125/workspace.root -n .snapshot -m 125 --saveWorkspace --redefineSignalPOIs $POI

    combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH125.root -n .nominal -m 125 --algo grid --snapshotName MultiDimFit --redefineSignalPOIs $POI --points 100

    combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH125.root -n .freezebbb -m 125 --algo grid --freezeNuisanceGroups autoMCStats --snapshotName MultiDimFit --redefineSignalPOIs $POI --points 100

    combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH125.root -n .freezesyst -m 125 --algo grid --freezeNuisanceGroups autoMCStats,syst --snapshotName MultiDimFit --redefineSignalPOIs $POI --points 100

    combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH125.root -n .freezetheory -m 125 --algo grid --freezeNuisanceGroups syst,theory,autoMCStats --snapshotName MultiDimFit --redefineSignalPOIs $POI --points 100

    combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH125.root -n .freezeall -m 125 --algo grid --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit --redefineSignalPOIs $POI --points 100
    if [[ $IS_MC == "1" ]]; then
        outputname=freeze_${POI}_mc
    else
        outputname=freeze_${POI}_emb
    fi
    fitting/plot1DScan.py --main higgsCombine.nominal.MultiDimFit.mH125.root --POI $POI --others higgsCombine.freezebbb.MultiDimFit.mH125.root:"freeze bbb":4 higgsCombine.freezesyst.MultiDimFit.mH125.root:"freeze bbb + syst":6 higgsCombine.freezetheory.MultiDimFit.mH125.root:"freeze bbb + syst + theo":7 higgsCombine.freezeall.MultiDimFit.mH125.root:"Stat. only":2 -o ${outputname} --breakdown bbb,syst,theory,rest,stat --y-max 4 --json $outputname.json --x-range 0,2


    # move all output files to the result folder
    echo "Moving output files to $RESULTFOLDER"
    mv higgsCombine* $RESULTFOLDER
    mv ${outputname}.pdf $RESULTFOLDER
    mv ${outputname}.json $RESULTFOLDER
    mv ${outputname}.png $RESULTFOLDER
    mv ${outputname}.root $RESULTFOLDER
done
