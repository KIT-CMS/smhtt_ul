"""Sample configuration for Run 3, 2024C data and 2024 MC (NanoAOD v15). for mm and mt channel

Source: KIT-CMS/KingMaker_sample_database, nanoAOD_v15/2024,
commit 33c257b4e72ae423f3f171978d6058c37fab3b5f (checked 2026-10-07).
See file_names_2024C.md for the sample mapping and unresolved production issues.

The era key is "2024", matching the database and CROWN directory convention.
Only data are explicitly restricted to period C. The two available embedding
samples are only Run2024C as confirmed by Christian

Values are database nicknames / CROWN sample directories, without .json/.root.
This separate configuration is not yet imported by the production scripts.
"""

# Common MC for 2024; normalize to the luminosity of the selected 2024C data.
common_files_2024 = {
    # nicht alle genommen aus der Kingmaker datenbank, da sich  smaples überschneiden können  https://github.com/KIT-CMS/KingMaker_sample_database/tree/main/nanoAOD_v15/2024/dyjets_amcatnlo
    "DY": [
        #Für Elektronen das 10-50 GeV sample genommen für über 50 nur das inklusive sample und nicht 0,1,2, J Sample
        "DYto2E-2Jets_Bin-MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "DYto2E-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v4",
        # Für mu das 10-50 sample genommen, für über 50 das inklusive und nicht 0,1,2, J Samples
        "DYto2Mu-2Jets_Bin-MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "DYto2Mu-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v6",
        #Für tau alle aus Datenbank genommen, da es keine Überschneidungen gibt
        "DYto2Tau-2Jets_Bin-0J-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v4",
        "DYto2Tau-2Jets_Bin-1J-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "DYto2Tau-2Jets_Bin-2J-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "DYto2Tau-2Jets_Bin-MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
    ],
    # Dileptonic, fully hadronic and semileptonic top-pair decays. Hier alle genommen, gibt auch nur 3 !!!!!!!!!!!!!!!!!!!!
    "TT": [
        "TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3",
        "TTto4Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
    ],
        #Single top channel https://github.com/KIT-CMS/KingMaker_sample_database/tree/main/nanoAOD_v15/2024/singletop wir verwwenden wie in Run2 nur den t Kanal
    "ST": [
        #t Kanal, mit 1 W 
        "TBbarQto2Q-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "TBbarQtoLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "TbarBQto2Q-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "TbarBQtoLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        # hier 2 W 
        "TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "TWminusto4Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "TWminustoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "TbarWplusto4Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "TbarWplustoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
    ],
    # Inclusive WW/WZ/ZZ; https://github.com/KIT-CMS/KingMaker_sample_database/tree/main/nanoAOD_v15/2024/diboson und nicht die spezifischen mit powheg-pythia
    "VV": [
        "WW_TuneCP5_13p6TeV_pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "WZ_TuneCP5_13p6TeV_pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "ZZ_TuneCP5_13p6TeV_pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
    ],
    # NLO W+jets split into electron, muon and tau decays. https://github.com/KIT-CMS/KingMaker_sample_database/tree/main/nanoAOD_v15/2024/wjets , wir nehmen nicht d
    "W": [
        "WtoENu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3",
        "WtoMuNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3",
        "WtoTauNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3",
    ],
}
 #https://github.com/KIT-CMS/KingMaker_sample_database/tree/main/nanoAOD_v15/2024/data 
files = {
    "2024": {
        "mt": dict(
            {
                "data": [
                    "Muon0_Run2024C-MINIv6NANOv15-v1",
                    "Muon1_Run2024C-MINIv6NANOv15-v1",
                ],
                # Period C coverage is NOT confirmed by the database.
                "EMB": ["Run2024_MuTauEmbedding"], # hat Christian produziert https://github.com/KIT-CMS/KingMaker_sample_database/tree/main/nanoAOD_v15/2024/embedding
            },
            **common_files_2024
        ),
        "mm": dict(
            {
                "data": [
                    "Muon0_Run2024C-MINIv6NANOv15-v1",
                    "Muon1_Run2024C-MINIv6NANOv15-v1",
                ],
                # Period C coverage is NOT confirmed by the database. https://github.com/KIT-CMS/KingMaker_sample_database/tree/main/nanoAOD_v15/2024/embedding
                "EMB": ["Run2024_MuMuEmbedding"],
            },
            **common_files_2024
        ),
    },
}
