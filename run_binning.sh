#!/bin/sh
# Startet den bestehenden BINNING-Block fuer die dort angeforderten Kategorien.
set -e

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

CHANNELS="mm,mt"
ERA="2024"
NTUPLETAG="tauid_2024C_mt_all_revised_v2"
TAG="Second_try_Run3_2024C"
BIN_TAG="Second_try_Run3_2024C"
WP="Tight"
WP_VSe="VVLoose"
WP_VSmu="Tight"

# Die Working Points bestimmen die fuer das Binning ausgewaehlten Ereignisse.
# ES-Grenzen und Praezision werden als Positionsargumente mitgegeben, vom
# BINNING-Block aber nicht ausgewertet. Kanaele/Kategorien stehen im Block.
exec bash tau_id_es_measurement/emb_tau_id_sfs_ul.sh \
    "$CHANNELS" \
    "$ERA" \
    "$NTUPLETAG" \
    "$TAG" \
    BINNING \
    "$WP" \
    "$WP_VSe" \
    "$WP_VSmu" \
    0.0 \
    0.0 \
    None_ext_up \
    None_ext_down \
    "$BIN_TAG" \
    0.1
