"""Sample configuration for Run 3, 2024C data and 2024 MC (NanoAOD v15). for mm and mt channel

Source: KIT-CMS/KingMaker_sample_database, nanoAOD_v15/2024,
commit 33c257b4e72ae423f3f171978d6058c37fab3b5f (checked 2026-10-07).
Revised VV selection: ten POWHEG decay samples supplied by Moritz.
Other sample groups match file_names_2024C.py.

The era key is "2024", matching the database and CROWN directory convention.
Only data are explicitly restricted to period C. The two available embedding
samples are only Run2024C as confirmed by Christian

Values are database nicknames / CROWN sample directories, without .json/.root.
This separate configuration is not yet imported by the production scripts.
"""

# Common MC for 2024; normalize to the luminosity of the selected 2024C data.
common_files_2024 = {
    # aMC@NLO: pro Leptonflavour 0J/1J/2J fuer MLL > 50 GeV sowie MLL 10-50 GeV.
    # Keine zusaetzlichen inklusiven MLL-50-Samples oder JMENano-Varianten.
    # Kombination und Normierung der FXFX-Jet-Bins vor der Produktion pruefen.
    "DY": [
        # Elektronen
        "DYto2E-2Jets_Bin-0J-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "DYto2E-2Jets_Bin-1J-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3",
        "DYto2E-2Jets_Bin-2J-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "DYto2E-2Jets_Bin-MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        # Myonen (Standard-NanoAOD v15)
        "DYto2Mu-2Jets_Bin-0J-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3",
        "DYto2Mu-2Jets_Bin-1J-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v1",
        "DYto2Mu-2Jets_Bin-2J-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3",
        "DYto2Mu-2Jets_Bin-MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        # Taus
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
    # Exclusive WW/WZ/ZZ decay samples (POWHEG + Pythia8), supplied by Moritz.
    "VV": [
        "WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "WWtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "WWto4Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "WZtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "ZZto4L_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
        "ZZto2Nu2Q_TuneCP5_13p6TeV_powheg-pythia8_RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2",
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
