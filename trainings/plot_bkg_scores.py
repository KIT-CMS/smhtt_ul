#!/usr/bin/env python
"""
Background NN score distributions — CMS style via Dumbledraw (ROOT).

Reads fold*_bkg_scores.npz written by train_multiclass_nn.py and produces
one CMS-style stacked MC + data plot per background class output node.

Run from smhtt_ul/:
    python trainings/plot_bkg_scores.py \\
        --input /ceph/.../models/mt/fold0_bkg_scores.npz \\
        --output-dir /web/.../plots/ \\
        --era Run2022-23 \\
        --linear
"""

import argparse
import copy
import sys
from pathlib import Path

import numpy as np

# ── Dumbledraw / ROOT path ────────────────────────────────────────────────
_here = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_here))

import Dumbledraw.dumbledraw as dd
import Dumbledraw.styles as styles
import ROOT

ROOT.gROOT.SetBatch(True)

# ── CMS colour / label maps (from Dumbledraw/colors.yaml palette) ────────
_CLASS_COLORS = {
    "is_dyjets":          "#ffa90e",   # ZTT (amber)
    "is_dy_ztt":          "#ffa90e",
    "is_dy_zl":           "#ffcc66",   # Z→ll (light amber)
    "is_jetfakes":        "#94a4a2",   # jetFakes (grey)
    "is_background_rest": "#832db6",   # TTbar / rest (purple)
    "is_wjets":           "#e76300",   # W+jets (orange)
    "is_ttbar":           "#832db6",
    "is_embedding":       "#ffa90e",
    # signal colours for score overlay
    "is_ggh":             "#e31a1c",   # ggH (red)
    "is_vbf":             "#1f78b4",   # VBF (blue)
}

_CLASS_LABELS = {
    "is_dyjets":          "DY (Z#rightarrow#tau#tau)",
    "is_dy_zl":           "DY (Z#rightarrowll)",
    "is_jetfakes":        "Jet#rightarrowFake",
    "is_background_rest": "t#bar{t}, VV, W+jets",
    "is_wjets":           "W+jets",
    "is_ttbar":           "t#bar{t}",
    "is_embedding":       "Embedded",
    "is_ggh_htautau":     "ggH",
    "is_vbf_htautau":     "VBF",
}

_CHANNEL_LABELS = {
    "et": "#font[42]{#scale[0.85]{e}}#tau_{#font[42]{h}}",
    "mt": "#mu#tau_{#font[42]{h}}",
    "tt": "#tau_{#font[42]{h}}#tau_{#font[42]{h}}",
}


def _root_color(hex_str):
    return ROOT.TColor.GetColor(hex_str)


def _get_color(name):
    low = name.lower()
    for k, v in _CLASS_COLORS.items():
        if k in low:
            return _root_color(v)
    return ROOT.kGray + 2


def _get_label(name):
    low = name.lower()
    for k, v in _CLASS_LABELS.items():
        if k in low:
            return v
    return name.replace("is_", "")


def _np_to_th1(values, weights, nbins, name):
    """Build a TH1F from numpy arrays using vectorised histogram + Sumw2."""
    counts, _ = np.histogram(values, bins=nbins, range=(0.0, 1.0), weights=weights)
    w2, _     = np.histogram(values, bins=nbins, range=(0.0, 1.0), weights=weights ** 2)
    h = ROOT.TH1F(name, name, nbins, 0.0, 1.0)
    for i in range(nbins):
        h.SetBinContent(i + 1, float(counts[i]))
        h.SetBinError(i + 1, float(np.sqrt(w2[i])))
    return h


def _np_to_th1_data(values, nbins, name):
    """Build a TH1F for observed data (weight=1, Poisson errors)."""
    counts, _ = np.histogram(values, bins=nbins, range=(0.0, 1.0))
    h = ROOT.TH1F(name, name, nbins, 0.0, 1.0)
    for i in range(nbins):
        h.SetBinContent(i + 1, float(counts[i]))
        h.SetBinError(i + 1, float(np.sqrt(counts[i])))
    return h


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Plot background NN scores with Dumbledraw (CMS style)"
    )
    p.add_argument("--input",      required=True, help="Path to fold*_bkg_scores.npz")
    p.add_argument("--output-dir", default=None,  help="Output directory (default: same dir as --input)")
    p.add_argument("--era",        default="",    help="Era string for CMS lumi label, e.g. 'Run2022-23'")
    p.add_argument("--nbins",      type=int, default=20, help="Number of histogram bins (default: 20)")
    p.add_argument("--linear",     action="store_true",  help="Use linear y-axis (default: log)")
    args = p.parse_args()

    # ── Load numpy arrays ────────────────────────────────────────────────
    npz = np.load(args.input, allow_pickle=True)
    scores      = npz["scores_val"]                      # (N_val, n_classes)
    true_cls    = npz["true_class_val"]                  # (N_val,)
    weights     = npz["weights_val"]                     # (N_val,)
    is_data     = npz["is_data_val"].astype(bool)        # (N_val,)
    class_names = [str(x) for x in npz["class_names"]]
    bkg_indices = [int(x) for x in npz["bkg_class_indices"]]
    bkg_names   = [str(x) for x in npz["bkg_class_names"]]
    channel     = str(npz["channel"][0])
    fold        = int(npz["fold"][0])

    out = Path(args.output_dir) if args.output_dir else Path(args.input).parent
    out.mkdir(parents=True, exist_ok=True)

    has_data    = bool(is_data.sum() > 0)
    mc_mask     = ~is_data
    # MC events whose true class is one of the background classes
    bkg_mc_mask = mc_mask & np.isin(true_cls, bkg_indices)

    ch_label = _CHANNEL_LABELS.get(channel, channel)

    print(f"Background classes : {bkg_names}")
    print(f"Data events in val : {is_data.sum()}")
    print(f"Bkg MC events      : {bkg_mc_mask.sum()}")

    # ── One canvas per background score output node ───────────────────
    for score_node_i, score_node_name in zip(bkg_indices, bkg_names):
        short = score_node_name.replace("is_", "")
        ROOT.gROOT.cd()

        # ── MC component histograms (one per background class) ────────
        mc_hists  = {}
        total_mc  = None
        for ti, tname in enumerate(bkg_names):
            cls_mask = bkg_mc_mask & (true_cls == bkg_indices[ti])
            vals = scores[cls_mask, score_node_i]
            wts  = np.abs(weights[cls_mask])
            h = _np_to_th1(vals, wts, args.nbins, f"mc_{tname}_{short}_{fold}_{ti}")
            mc_hists[tname] = h
            if total_mc is None:
                total_mc = h.Clone(f"total_mc_{short}_{fold}")
            else:
                total_mc.Add(h)

        if total_mc is None or total_mc.Integral() == 0:
            print(f"  Skipping {score_node_name}: no MC events")
            continue

        # ── Data histogram ────────────────────────────────────────────
        h_data = None
        if has_data:
            vals_data = scores[is_data, score_node_i]
            h_data = _np_to_th1_data(vals_data, args.nbins, f"data_{short}_{fold}")

        # ── Normalise to unit area (shape comparison) ─────────────────
        mc_integral = total_mc.Integral()
        for h in mc_hists.values():
            h.Scale(1.0 / mc_integral)
        total_mc.Scale(1.0 / mc_integral)

        if h_data is not None and h_data.Integral() > 0:
            h_data.Scale(1.0 / h_data.Integral())

        # ── Build Dumbledraw canvas ───────────────────────────────────
        # Layout:  log-main (subplot 0) | linear-main (subplot 1) | ratio (subplot 2)
        # For linear-only:  main (subplot 0) | ratio (subplot 2) [subplot 1 is zero-height]
        if has_data:
            split = [0.5, [0.3, 0.28]] if not args.linear else [0.3, [0.3, 0.28]]
        else:
            split = [0.3] if not args.linear else [0.3]

        plot = dd.Plot(split, "ModTDR", r=0.04, l=0.14, width=600)

        # Add MC histograms (go to ALL subplots via plot.add_hist)
        for tname in bkg_names:
            plot.add_hist(mc_hists[tname], tname, "bkg")
            plot.setGraphStyle(
                tname, "hist",
                fillcolor=_get_color(tname),
                linecolor=_get_color(tname),
            )

        # Uncertainty band on total MC
        plot.add_hist(total_mc.Clone(f"total_bkg_{short}"), "total_bkg")
        plot.setGraphStyle(
            "total_bkg", "e2", markersize=0,
            fillcolor=styles.color_dict["unc"], linecolor=0,
        )

        # Data markers
        if h_data is not None:
            plot.add_hist(h_data.Clone(f"data_obs_{short}"), "data_obs")
            # data style set per-subplot below

        # Stacked MC
        plot.create_stack(bkg_names, "stack")

        # ── Y-axis limits ─────────────────────────────────────────────
        mc_max   = total_mc.GetMaximum()
        data_max = h_data.GetMaximum() if h_data else 0.0
        y_max    = max(mc_max, data_max)

        main_idx = 0 if (args.linear or not has_data) else 1

        if not args.linear and has_data:
            # Log panel (subplot 0) shows the full dynamic range
            plot.subplot(0).setYlims(1e-4, y_max * 500)
            plot.subplot(0).setLogY()

        plot.subplot(main_idx).setYlims(0.0, y_max * 1.6)
        plot.subplot(main_idx).setYlabel("Density / bin")
        plot.subplot(main_idx).setXlabel(f"Score({short})")

        # ── Data style ────────────────────────────────────────────────
        if h_data is not None:
            plot.subplot(main_idx).setGraphStyle("data_obs", "e0")
            if not args.linear and has_data:
                plot.subplot(0).setGraphStyle("data_obs", "e0")

        # ── Ratio panel ───────────────────────────────────────────────
        if has_data:
            plot.subplot(2).normalize(["data_obs", "total_bkg"], "total_bkg")
            plot.subplot(2).setYlims(0.75, 1.45)
            plot.subplot(2).setYlabel("Obs/Exp")
            plot.subplot(2).setXlabel(f"Score({short})")
            plot.subplot(2).setGrid()

        # ── Draw ──────────────────────────────────────────────────────
        draw_main = ["stack", "total_bkg"] + (["data_obs"] if h_data else [])

        plot.subplot(main_idx).Draw(draw_main)
        if not args.linear and has_data:
            plot.subplot(0).Draw(draw_main)
        if has_data:
            plot.subplot(2).Draw(["total_bkg", "data_obs"])

        # ── Legend ────────────────────────────────────────────────────
        leg_h = 0.06 + 0.055 * len(bkg_names) + (0.055 if h_data else 0.0)
        plot.add_legend(width=0.45, height=leg_h)
        for tname in reversed(bkg_names):
            plot.legend(0).add_entry(main_idx, tname, _get_label(tname), "f")
        if h_data is not None:
            plot.legend(0).add_entry(main_idx, "data_obs", "Observed", "PE")
        plot.legend(0).Draw()

        # ── CMS header ────────────────────────────────────────────────
        plot.DrawCMS()
        if args.era:
            plot.DrawLumi(args.era)
        plot.DrawChannelCategoryLabel(f"{ch_label}  fold {fold}")

        # ── Save ──────────────────────────────────────────────────────
        for ext in ("png", "pdf"):
            fname = str(out / f"fold{fold}_bkg_score_{short}.{ext}")
            plot.save(fname)

        print(f"  Saved {out / f'fold{fold}_bkg_score_{short}.png'}")

    # ── One canvas per signal score output node (MC only, no data) ─────
    sig_indices  = [i for i, n in enumerate(class_names) if i not in bkg_indices]
    sig_names    = [class_names[i] for i in sig_indices]
    all_mc_mask  = mc_mask  # all non-data events

    print(f"Signal classes     : {sig_names}")

    for score_node_i, score_node_name in zip(sig_indices, sig_names):
        short = score_node_name.replace("is_", "")
        ROOT.gROOT.cd()

        # ── Background MC histograms ──────────────────────────────────
        mc_hists = {}
        total_mc = None
        for ti, tname in enumerate(bkg_names):
            cls_mask = all_mc_mask & (true_cls == bkg_indices[ti])
            vals = scores[cls_mask, score_node_i]
            wts  = np.abs(weights[cls_mask])
            h = _np_to_th1(vals, wts, args.nbins,
                           f"sig_mc_bkg_{tname}_{short}_{fold}_{ti}")
            mc_hists[tname] = h
            if total_mc is None:
                total_mc = h.Clone(f"sig_total_bkg_{short}_{fold}")
            else:
                total_mc.Add(h)

        # ── Signal MC histogram for this output node ──────────────────
        sig_mask = all_mc_mask & (true_cls == score_node_i)
        vals_sig = scores[sig_mask, score_node_i]
        wts_sig  = np.abs(weights[sig_mask])
        h_sig = _np_to_th1(vals_sig, wts_sig, args.nbins,
                            f"sig_mc_sig_{short}_{fold}")

        # Need at least some signal events to plot
        if h_sig.Integral() == 0 and (total_mc is None or total_mc.Integral() == 0):
            print(f"  Skipping {score_node_name}: no MC events")
            continue

        # ── Normalise signal to bkg integral (shape overlay) ──────────
        bkg_integral = total_mc.Integral() if total_mc else 0.0
        sig_integral = h_sig.Integral()
        if bkg_integral > 0 and sig_integral > 0:
            for h in mc_hists.values():
                h.Scale(1.0 / bkg_integral)
            total_mc.Scale(1.0 / bkg_integral)
            h_sig.Scale(1.0 / sig_integral)  # normalise signal independently (shape)
        elif bkg_integral > 0:
            for h in mc_hists.values():
                h.Scale(1.0 / bkg_integral)
            total_mc.Scale(1.0 / bkg_integral)

        # ── Build Dumbledraw canvas (no ratio — no data) ──────────────
        split = [0.3]
        plot  = dd.Plot(split, "ModTDR", r=0.04, l=0.14, width=600)

        for tname in bkg_names:
            plot.add_hist(mc_hists[tname], tname, "bkg")
            plot.setGraphStyle(
                tname, "hist",
                fillcolor=_get_color(tname),
                linecolor=_get_color(tname),
            )

        plot.add_hist(total_mc.Clone(f"sig_total_bkg_unc_{short}"), "total_bkg")
        plot.setGraphStyle(
            "total_bkg", "e2", markersize=0,
            fillcolor=styles.color_dict["unc"], linecolor=0,
        )

        # Signal histogram — line style, no fill
        if h_sig.Integral() > 0:
            plot.add_hist(h_sig.Clone(f"signal_{short}"), "signal")
            # determine colour from node name
            if "ggh" in score_node_name.lower():
                sig_color = _root_color("#e31a1c")
            else:
                sig_color = _root_color("#1f78b4")
            plot.setGraphStyle(
                "signal", "hist",
                linecolor=sig_color, linewidth=2,
                fillcolor=0, fillstyle=0,
            )

        plot.create_stack(bkg_names, "stack")

        mc_max  = total_mc.GetMaximum()
        sig_max = h_sig.GetMaximum() if h_sig.Integral() > 0 else 0.0
        y_max   = max(mc_max, sig_max)

        if not args.linear:
            plot.subplot(0).setYlims(1e-4, y_max * 500)
            plot.subplot(0).setLogY()
        else:
            plot.subplot(0).setYlims(0.0, y_max * 1.6)

        plot.subplot(0).setYlabel("Density / bin")
        plot.subplot(0).setXlabel(f"Score({short})")

        draw_list = ["stack", "total_bkg"]
        if h_sig.Integral() > 0:
            draw_list.append("signal")
        plot.subplot(0).Draw(draw_list)

        # Legend
        leg_h = 0.06 + 0.055 * (len(bkg_names) + 1)
        plot.add_legend(width=0.45, height=leg_h)
        for tname in reversed(bkg_names):
            plot.legend(0).add_entry(0, tname, _get_label(tname), "f")
        if h_sig.Integral() > 0:
            plot.legend(0).add_entry(0, "signal", _get_label(score_node_name), "l")
        plot.legend(0).Draw()

        plot.DrawCMS()
        if args.era:
            plot.DrawLumi(args.era)
        plot.DrawChannelCategoryLabel(f"{ch_label}  fold {fold}")

        for ext in ("png", "pdf"):
            fname = str(out / f"fold{fold}_sig_score_{short}.{ext}")
            plot.save(fname)
        print(f"  Saved {out / f'fold{fold}_sig_score_{short}.png'}")

    print(f"\nAll plots written to {out}")


if __name__ == "__main__":
    main()
