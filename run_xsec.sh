#!/bin/sh
# Startet den bestehenden XSEC-Block zum Erzeugen/Pruefen der XSEC-Friends.
set -e

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

CHANNELS="mm,mt"
ERA="2024"
NTUPLETAG="tauid_2024C_mt_all_revised_v2"
TAG="Second_try_Run3_2024C"

# WP-, ES- und Binning-Argumente belegen die festen Argumentpositionen des
# Hauptskripts. Der XSEC-Block verwendet sie nicht fuer die Friend-Produktion.
# Der Pfad zur Dataset-Datenbank bleibt im bestehenden XSEC-Block festgelegt.
exec bash tau_id_es_measurement/emb_tau_id_sfs_ul.sh \
    "$CHANNELS" \
    "$ERA" \
    "$NTUPLETAG" \
    "$TAG" \
    XSEC \
    Tight \
    VVLoose \
    Tight \
    0.0 \
    0.0 \
    None_ext_up \
    None_ext_down \
    "$TAG" \
    0.1
