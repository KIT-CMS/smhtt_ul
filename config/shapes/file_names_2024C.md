# Sample-Auswahl für Run 3 / 2024C

Die separate Konfiguration `file_names_2024C.py` verwendet dieselbe Struktur wie
`file_names.py`: `files[era][channel][process]`. Der Era-Schlüssel bleibt `"2024"`,
passend zum `era`-Feld der Datenbank. Die Datensamples sind auf **2024C** begrenzt;
die MC-Samples stammen aus der gemeinsamen 2024-Produktion.

Quelle: [KingMaker_sample_database, NanoAOD v15 / 2024](https://github.com/KIT-CMS/KingMaker_sample_database/tree/33c257b4e72ae423f3f171978d6058c37fab3b5f/nanoAOD_v15/2024),
Commit `33c257b4e72ae423f3f171978d6058c37fab3b5f`, geprüft am 07.10.2026.
Die ursprüngliche Auswahl von 34 Sample-Namen wurde gegen `nick`, `era`, `nfiles`
und die nichtleeren `filelist`-Einträge der jeweiligen JSON-Datei geprüft.
Am 08.10.2026 wurde DY auf zwölf Samples umgestellt: für jeden Leptonflavour
0J/1J/2J oberhalb 50 GeV und ein Sample für 10–50 GeV. Die vollständigen Namen
einschließlich Versionssuffixen wurden gegen den bereits abgerufenen
Datenbankbaum des obigen Commits geprüft. Die sechs neu aufgenommenen E-/Mu-Jet-Bin-
Einträge wurden dabei nicht erneut auf JSON-Inhalt oder Dateiverfügbarkeit geprüft.
Die Erreichbarkeit der ROOT-Dateien und bereits produzierter CROWN-Ntuples wurde
nicht geprüft. Die JSON-Dateilisten enthalten NanoAOD-Eingaben; die Shape-Produktion
benötigt daraus erzeugte CROWN-Ntuples mit diesen Sample-Namen.

## Zuordnung der Samples

| Gruppe | Auswahl für 2024 | Unterschied zur aktiven 2018-Konfiguration |
| --- | --- | --- |
| `DY` | 12 amcatnloFXFX-Samples | Jeweils `DYto2E`, `DYto2Mu`, `DYto2Tau` mit 0J/1J/2J oberhalb 50 GeV sowie einem Sample für 10–50 GeV |
| `TT` | `TTto2L2Nu`, `TTto4Q`, `TTtoLNu2Q` | Entsprechen dileptonischen, hadronischen und semileptonischen Zerfällen |
| `ST` | 4 t-Kanal- und 6 tW-Samples | Top/Antitop und Zerfallsmodi getrennt; s-Kanal wie in der aktiven 2018-Auswahl ausgelassen |
| `VV` | Inklusive `WW`, `WZ`, `ZZ` | Verfügbare exklusive Zerfalls-Samples werden nicht zusätzlich aufgenommen |
| `W` | `WtoENu`, `WtoMuNu`, `WtoTauNu`, jeweils amcatnloFXFX | Drei Flavour-Samples ersetzen das gemeinsame `WJetsToLNu` |
| Daten `mt`, `mm` | `Muon0` und `Muon1`, jeweils Run2024C | Ersetzen die `SingleMuon`-Sample-Auswahl |
| Daten `et`, `em`, `ee` | `EGamma0` und `EGamma1`, jeweils Run2024C | Analog zur EGamma-Auswahl der bisherigen Konfiguration |
| Daten `tt` | `Tau_Run2024C-MINIv6NANOv15-v1` | Nur Periode C |

Die Datenstream-Zuordnung folgt der bisherigen Kanalstruktur. Die tatsächlichen
Run-3-Trigger und gegebenenfalls die Behandlung von Ereignisüberschneidungen
müssen zur Selektion der neuen Analyse passen.

## Gefundene Lücken und offene Punkte

1. **Kein inklusives NLO-DY→ττ-Sample für MLL > 50 GeV im Snapshot.**
   In `dyjets_amcatnlo` sind stattdessen `Bin-0J-MLL-50`, `Bin-1J-MLL-50` und
   `Bin-2J-MLL-50` vorhanden. Diese Jet-Bins sind jetzt für alle drei Flavours ausgewählt. Ihre Kombination
   und Normierung müssen zu den FXFX-Metadaten und den verwendeten Gewichten
   passen. Die inklusiven MLL-50-Samples für Elektronen und Myonen wurden ersetzt.
   Für Myon-1J wird Standard-NanoAOD v15 verwendet, nicht die zusätzliche JMENano-Variante.
   Ein inklusives LO-`DYto2Tau-4Jets_Bin-MLL-50` existiert in `dyjets_madgraph`,
   wird aber nicht mit den NLO-Samples gemischt.
2. **Embedding ist nicht ausdrücklich als 2024C ausgewiesen.**
   Die einzigen Einträge sind `Run2024_MuTauEmbedding` und
   `Run2024_MuMuEmbedding`, aufgenommen für `mt` bzw. `mm`.
   Beide haben `era: 2024`, `dbs: /sample/not/published` und jeweils 182 Dateien
   unter `/store/user/cwinter/run3_embedding/2024/MuTau/nanoaod/` bzw.
   `/store/user/cwinter/run3_embedding/2024/MuMu/nanoaod/`.
   Weder die Metadaten noch die Pfade bestätigen die Beschränkung auf C.
   Vor dem Vergleich mit 2024C-Daten muss die Abdeckung bestätigt oder die
   passende Run-/Lumisection-Selektion angewendet werden.
3. **Embedding für `et`, `tt`, `em`, `ee` fehlt in dieser Datenbank.**
   Die entsprechenden `EMB`-Listen sind ausdrücklich leer. Das sind Platzhalter,
   keine vollständigen Konfigurationen für eine Embedding-Messung dieser Kanäle.
4. **Die bestehende Produktionspipeline ist noch auf Run 2 ausgelegt.**
   Die neue Datei wird noch nicht automatisch importiert. Unter anderem müssen
   `utils/setup_ul_samples.sh`, die Luminosität in
   `config/shapes/process_selection.py`, Kanal-/Triggerselektionen, Korrekturen
   und Systematiken für 2024 bzw. die Periode C angepasst werden.
   Nur ein Importwechsel macht die Produktion daher noch nicht lauffähig.

Zum separaten Einlesen der Auswahl:

```python
from config.shapes.file_names_2024C import files

samples_mt = files["2024"]["mt"]
samples_mm = files["2024"]["mm"]
```
