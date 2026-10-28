#!/bin/sh
# Startet den bestehenden CONTROL-Block: Shapes, QCD-Schaetzung und Kontrollplots.
set -e

# Das Hauptskript erwartet relative Pfade aus dem smhtt_ul-Verzeichnis.
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

CHANNELS="mm,mt"
ERA="2024"
NTUPLETAG="tauid_2024C_mt_all_revised_v2"
TAG="Second_try_Run3_2024C_allSyst_ESscan"
BIN_TAG="Second_try_Run3_2024C"
WP="Tight"
WP_VSe="VVLoose"
WP_VSmu="Tight"
ES_UP="20.0"
ES_DOWN="-20.0"
TES_PRECISION="0.1"

# ES_UP=ES_DOWN=0.0 erzeugt nur den nominalen Energiepunkt.
# Systematik-Schalter und Hintergrundschaetzungen bleiben im CONTROL-Block
# von emb_tau_id_sfs_ul.sh festgelegt; dieser Starter dupliziert sie nicht.
# Bash wird fuer Arrays, [[ ... ]] und source im Hauptskript benoetigt.
exec bash tau_id_es_measurement/emb_tau_id_sfs_ul.sh \
    "$CHANNELS" \
    "$ERA" \
    "$NTUPLETAG" \
    "$TAG" \
    CONTROL \
    "$WP" \
    "$WP_VSe" \
    "$WP_VSmu" \
    "$ES_UP" \
    "$ES_DOWN" \
    None_ext_up \
    None_ext_down \
    "$BIN_TAG" \
    "$TES_PRECISION"
