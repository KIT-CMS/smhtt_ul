#!/usr/bin/env python3
"""
combine_to_cennt_folds.py

Combines per-process feather fold files (produced by create_training_dataset.py)
into per-channel fold files compatible with the uncertainty-aware-training framework
(uncertainty-aware-training/) running in CE-only mode (data-type="SMHtt").

The per-process files are expected to be named:
    __{fold_name}__{channel}_{era}_{process}_{subprocess}.feather

Output per channel:
    {output_dir}/{channel}/
        fold0_training.feather
        fold0_validation.feather
        fold1_training.feather
        fold1_validation.feather
        config.yaml

Era weight equalization:
    For each era flag (is_2022preEE, is_2023preBPix, …), the nominal weights
    of events belonging to that era are rescaled so that mean(|w|) = 1.
    This prevents high-luminosity eras from dominating training.

Usage:
    python combine_to_cennt_folds.py \\
        --folds-dir /path/to/_folds \\
        --output-dir /path/to/cennt_folds \\
        --channel mt \\
        --setup-config setup.yaml
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column key helpers — must match the 5-level MultiIndex used by the pipeline
# ---------------------------------------------------------------------------
_COL_LEN = 5


def _col(*parts, length=_COL_LEN):
    return tuple(list(parts) + [""] * (length - len(parts)))


NOMINAL = "Nominal"
LABELS = "Labels"
VARIABLES = "variables"
WEIGHT = "weight"
CLASS_WEIGHT = "class_weight"
CUT = "cut"
ANTI_ISO_CUT = "anti_iso_cut"

# All recognised era flags (ordered from most recent to oldest)
ERA_FLAGS = [
    "is_2025",
    "is_2024",
    "is_2023postBPix",
    "is_2023preBPix",
    "is_2022postEE",
    "is_2022preEE",
]

FOLD_NAMES = [
    "fold0",
    "fold1",
    "fold0_training",
    "fold0_validation",
    "fold1_training",
    "fold1_validation",
]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(
        description="Combine per-process feather folds into per-channel CENNT-compatible files"
    )
    p.add_argument(
        "--folds-dir",
        type=str,
        required=True,
        help="Directory containing __{fold}__{ch}_*.feather per-process files",
    )
    p.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Root output directory; a sub-directory per channel will be created",
    )
    p.add_argument(
        "--channel",
        type=str,
        required=True,
        choices=["mt", "et", "tt"],
        help="Decay channel to combine (mt, et, or tt)",
    )
    p.add_argument(
        "--setup-config",
        type=str,
        default="setup.yaml",
        help="Path to setup.yaml (provides training_variables and renaming_map). Default: setup.yaml",
    )
    p.add_argument(
        "--equalise-era-weights",
        action="store_true",
        default=True,
        help="Normalise weights per era so each era has mean|w|=1 (default: enabled)",
    )
    p.add_argument(
        "--no-equalise-era-weights",
        dest="equalise_era_weights",
        action="store_false",
    )
    p.add_argument(
        "--add-class-weights",
        action="store_true",
        default=True,
        help="Compute and store per-event class weights (default: enabled)",
    )
    p.add_argument(
        "--no-add-class-weights",
        dest="add_class_weights",
        action="store_false",
    )
    p.add_argument(
        "--nominal-only",
        action="store_true",
        default=False,
        help=(
            "Keep only events with cut=True (nominal SR). "
            "By default both nominal and anti-iso events are kept so the "
            "framework can use both regions during training."
        ),
    )
    p.add_argument(
        "--signal-mode",
        type=str,
        choices=["fine", "coarse"],
        default="fine",
        help=(
            "Signal class granularity. "
            "'fine'  : STXS stage-1.2 bins (is_ggh_htautau_bin*, is_vbf_htautau_bin*) as signal; "
            "          inclusive is_ggh_htautau / is_vbf_htautau go to background. "
            "'coarse': inclusive is_ggh_htautau and is_vbf_htautau as signal; "
            "          all STXS bin labels are merged back into them and the bin columns are dropped. "
            "Default: fine"
        ),
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Era weight equalization
# ---------------------------------------------------------------------------
def equalise_era_weights(df: pd.DataFrame, era_flags: list) -> pd.DataFrame:
    """
    Rescale the nominal weight of events per era so that mean(|w|) = 1 for
    every era. Events not assigned to any recognised era flag are left unchanged.
    """
    w_col = _col(NOMINAL, WEIGHT)
    if w_col not in df.columns:
        logger.warning("Weight column %s not found — skipping era weight equalisation.", w_col)
        return df

    df = df.copy()
    weights = df[w_col].values.astype(np.float64)

    found_any = False
    unassigned = np.ones(len(df), dtype=bool)

    for era in era_flags:
        era_col = _col(NOMINAL, VARIABLES, era)
        if era_col not in df.columns:
            continue
        mask = df[era_col].values.astype(bool)
        if mask.sum() == 0:
            continue
        found_any = True
        unassigned &= ~mask
        mean_abs_w = np.abs(weights[mask]).mean()
        if mean_abs_w > 0:
            scale = 1.0 / mean_abs_w
            weights[mask] *= scale
            logger.info(
                "Era %-20s | %7d events | mean|w|=%.4g → scale=%.4g",
                era, mask.sum(), mean_abs_w, scale,
            )
        else:
            logger.warning("Era %s: mean|w|=0, skipping.", era)

    if not found_any:
        logger.warning("No era flag columns found in dataframe — skipping era weight equalisation.")
    elif unassigned.sum() > 0:
        logger.warning(
            "%d events not covered by any era flag — their weights are unchanged.",
            unassigned.sum(),
        )

    df[w_col] = weights.astype(np.float32)
    return df


# ---------------------------------------------------------------------------
# Class weight computation — mirrors the CENNT framework's get_class_weights:
#   scale[class] = Σw / Σw_class
#   class_weight[event] = scale[class] * w[event]   (class_weighted=True)
# ---------------------------------------------------------------------------
def compute_class_weights(
    weights: np.ndarray,
    Y_argmax: np.ndarray,
) -> np.ndarray:
    w = weights.astype(np.float64)
    total_w = w.sum()
    scales = np.zeros(len(w), dtype=np.float64)
    classes = np.unique(Y_argmax)
    for c in classes:
        mask = Y_argmax == c
        class_sum = w[mask].sum()
        if class_sum != 0:
            scales[mask] = total_w / class_sum
    return (scales * w).astype(np.float32)


# ---------------------------------------------------------------------------
# Coarse mode: collapse STXS bin labels into inclusive ggH / VBF columns
# ---------------------------------------------------------------------------
def collapse_stxs_to_inclusive(df: pd.DataFrame, renaming_map: dict) -> pd.DataFrame:
    """
    For coarse signal mode: OR all is_ggh_htautau_bin* columns into
    is_ggh_htautau, and all is_vbf_htautau_bin* into is_vbf_htautau,
    then drop the individual bin columns.
    """
    df = df.copy()
    stxs_bins = [n for n in renaming_map if "ggh_htautau_bin" in n or "vbf_htautau_bin" in n]

    for parent, prefix in [("is_ggh_htautau", "ggh_htautau_bin"), ("is_vbf_htautau", "vbf_htautau_bin")]:
        parent_col = _col(LABELS, parent)
        bin_cols = [_col(LABELS, n) for n in stxs_bins if prefix in n and _col(LABELS, n) in df.columns]
        if not bin_cols:
            continue
        # Any event that was assigned to a bin gets absorbed into the inclusive column
        bin_mask = df[bin_cols].astype(bool).any(axis=1)
        if parent_col in df.columns:
            df[parent_col] = (df[parent_col].astype(bool) | bin_mask).astype(np.float32)
        else:
            df[parent_col] = bin_mask.astype(np.float32)
        df = df.drop(columns=bin_cols)
        logger.info("Collapsed %d STXS bin columns into %s (%d events)", len(bin_cols), parent, bin_mask.sum())

    return df


# ---------------------------------------------------------------------------
# Cut column: ensure (Nominal, cut) exists (needed by the SMHtt loader)
# ---------------------------------------------------------------------------
def ensure_cut_column(df: pd.DataFrame) -> pd.DataFrame:
    cut_col = _col(NOMINAL, CUT)
    if cut_col not in df.columns:
        df = df.copy()
        df[cut_col] = np.ones(len(df), dtype=np.int32)
        logger.info("Added missing (Nominal, cut) column (all ones).")
    return df


# ---------------------------------------------------------------------------

def load_and_align(files: list, all_label_cols: list) -> pd.DataFrame:
    """
    Read all per-process feather files, restore MultiIndex columns,
    fill missing label columns with zeros, then concatenate.
    """
    dfs = []
    for f in tqdm(files, desc="Loading files"):
        df = pd.read_feather(f)
        # Restore MultiIndex (feather stores tuple columns as strings)
        if not isinstance(df.columns, pd.MultiIndex):
            df.columns = pd.MultiIndex.from_tuples(df.columns)
        # Fill any label columns that are absent in this per-process file
        for col in all_label_cols:
            if col not in df.columns:
                df[col] = np.zeros(len(df), dtype=np.float32)
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    return combined


# ---------------------------------------------------------------------------
# Build dataset config YAML for the CENNT framework
# ---------------------------------------------------------------------------
def build_config(
    renaming_map: dict,
    physics_vars: list,
    era_vars: list,
    signal_mode: str = "fine",
) -> dict:
    """
    Build the dataset config dict that the uncertainty-aware-training SMHtt
    data loader expects.

    signal_mode='fine'  : STXS bin labels as signal, inclusive ggH/VBF in background.
    signal_mode='coarse': inclusive is_ggh_htautau / is_vbf_htautau as signal,
                          all STXS bin columns are excluded from the class list
                          (they are merged back by collapse_stxs_to_inclusive before writing).
    """
    all_labels = list(renaming_map.keys())
    stxs_bins = [n for n in all_labels if "ggh_htautau_bin" in n or "vbf_htautau_bin" in n]
    inclusive_signal = ["is_ggh_htautau", "is_vbf_htautau"]
    pure_backgrounds = [n for n in all_labels if n not in stxs_bins and n not in inclusive_signal]

    if signal_mode == "fine":
        signal_classes     = stxs_bins
        background_classes = inclusive_signal + pure_backgrounds
    else:  # coarse
        signal_classes     = [n for n in inclusive_signal if n in all_labels]
        background_classes = pure_backgrounds

    # Network inputs = physics variables + era flags (unscaled)
    training_vars = physics_vars + era_vars

    return {
        "multiclassification": True,
        "signal_mode": signal_mode,
        "training_variables": training_vars,
        "scaled_training_variables": physics_vars,   # only physics vars are scaled
        "training_variables_latex": {v: v for v in training_vars},
        "classes": signal_classes + background_classes,
        "signal_classes": signal_classes,
        "background_classes": background_classes,
        "signal_class_names": signal_classes,
        "background_class_names": background_classes,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    args = parse_args()

    # ── Load setup config ────────────────────────────────────────────────
    with open(args.setup_config, "r") as f:
        setup_cfg = yaml.safe_load(f)

    renaming_map = (
        setup_cfg
        .get("dataset_modifications", {})
        .get("labels", {})
        .get("renaming_map", {})
    )
    if not renaming_map:
        logger.error(
            "dataset_modifications.labels.renaming_map not found in %s",
            args.setup_config,
        )
        sys.exit(1)

    all_training_vars = setup_cfg.get("training_variables", [])
    physics_vars = [v for v in all_training_vars if not v.startswith("is_")]
    era_vars     = [v for v in all_training_vars if v.startswith("is_20")]

    logger.info("Physics vars (%d): %s", len(physics_vars), physics_vars)
    logger.info("Era vars     (%d): %s", len(era_vars), era_vars)

    all_label_names = list(renaming_map.keys())
    all_label_cols  = [_col(LABELS, n) for n in all_label_names]

    folds_dir = Path(args.folds_dir)
    out_dir   = Path(args.output_dir) / args.channel
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Write dataset config YAML once ──────────────────────────────────
    cfg = build_config(renaming_map, physics_vars, era_vars, signal_mode=args.signal_mode)
    config_path = out_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, default_flow_style=False)
    logger.info("Wrote dataset config: %s", config_path)
    logger.info(
        "  Signal classes     (%d): %s", len(cfg["signal_classes"]), cfg["signal_classes"]
    )
    logger.info(
        "  Background classes (%d): %s", len(cfg["background_classes"]), cfg["background_classes"]
    )

    # ── Process each fold ────────────────────────────────────────────────
    for fold_name in FOLD_NAMES:
        pattern = f"__{fold_name}__{args.channel}_*.feather"
        files = sorted(folds_dir.glob(pattern))

        if not files:
            logger.debug("No files found for pattern: %s", folds_dir / pattern)
            continue

        logger.info("")
        logger.info("═" * 60)
        logger.info("Fold: %s  |  %d input files", fold_name, len(files))
        logger.info("═" * 60)

        # ── Load & concatenate ───────────────────────────────────────────
        combined = load_and_align(files, all_label_cols)
        logger.info("Combined shape: %s", combined.shape)

        # ── Optionally drop anti-iso events ─────────────────────────────
        if args.nominal_only:
            cut_col = _col(NOMINAL, CUT)
            if cut_col in combined.columns:
                before = len(combined)
                combined = combined[combined[cut_col].astype(bool)].reset_index(drop=True)
                logger.info(
                    "--nominal-only: kept %d / %d events (cut=True)", len(combined), before
                )
            else:
                logger.warning("--nominal-only requested but no cut column found; keeping all events.")

        # ── Era weight equalisation ──────────────────────────────────────
        if args.equalise_era_weights:
            combined = equalise_era_weights(combined, ERA_FLAGS)

        # ── Ensure cut column exists ─────────────────────────────────────
        combined = ensure_cut_column(combined)

        # ── Coarse mode: collapse STXS bins into inclusive signal columns ─
        if args.signal_mode == "coarse":
            combined = collapse_stxs_to_inclusive(combined, renaming_map)

        # ── Class weights — recompute after any collapse ──────────────────
        active_label_names = cfg["classes"]  # already filtered for the chosen mode
        active_label_cols  = [_col(LABELS, n) for n in active_label_names if _col(LABELS, n) in combined.columns]

        if args.add_class_weights:
            if active_label_cols:
                Y_mat    = combined[active_label_cols].values.astype(np.float32)
                Y_argmax = Y_mat.argmax(axis=1)
                w_col    = _col(NOMINAL, WEIGHT)
                weights  = combined[w_col].values.astype(np.float32)
                cw       = compute_class_weights(weights, Y_argmax)
                combined[_col(NOMINAL, CLASS_WEIGHT)] = cw
                logger.info(
                    "Class weights: min=%.4g  max=%.4g  mean=%.4g",
                    cw.min(), cw.max(), cw.mean(),
                )
                unique, counts = np.unique(Y_argmax, return_counts=True)
                for cls_idx, cnt in zip(unique, counts):
                    lname = active_label_names[cls_idx] if cls_idx < len(active_label_names) else str(cls_idx)
                    logger.info("  class %-40s : %7d events", lname, cnt)

        # ── Handle fold output ──────────────────────────────────────────────
        # Each fold variant (fold0, fold0_training, fold0_validation, etc.)
        # is written with its own filename
        out_path = out_dir / f"{fold_name}.feather"
        combined.reset_index(drop=True).to_feather(out_path)
        logger.info("Wrote %s  (%d events, %d columns)", out_path, len(combined), len(combined.columns))

    logger.info("")
    logger.info("Done. Output in %s", out_dir)


if __name__ == "__main__":
    main()
