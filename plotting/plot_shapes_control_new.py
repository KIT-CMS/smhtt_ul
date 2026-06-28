#!/usr/bin/env python3

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import mplhep as hep

import CODE.PLOT as plot_helper
from CODE.PLOT import plot_single_quantity, ShapesParser
from process_ordering import ControlShapeBkgProcesses

hep.style.use("CMS")

SIGNAL_PROCESSES = ["ggH125", "qqH125"]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot control shapes with the new plotting backend."
    )
    parser.add_argument("-l", "--linear", action="store_true", help="Enable linear y-axis")
    parser.add_argument("-e", "--era", type=str, required=True, help="Era")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ROOT file with shapes of processes",
    )
    parser.add_argument(
        "--variables",
        type=str,
        required=True,
        help="Comma-separated list of variables",
    )
    parser.add_argument(
        "--channels",
        type=str,
        required=True,
        help="Comma-separated list of channels",
    )
    parser.add_argument("--fake-factor", action="store_true", help="Use fake factor")
    parser.add_argument("--embedding", action="store_true", help="Use embedding")
    parser.add_argument("--nlo", action="store_true", help="Use NLO DY and Wjets MC")
    parser.add_argument(
        "--add-signals",
        action="store_true",
        help="Draw signal processes in addition to backgrounds",
    )
    parser.add_argument(
        "--draw-jet-fake-variation",
        type=str,
        default=None,
        help="Draw variation of jetFakes or QCD in derivation region.",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Plot a special category instead of nominal",
    )
    parser.add_argument(
        "--selection-option",
        type=str,
        choices=["CR", "DR;ff;wjet", "DR;ff;qcd", "DR;ff;ttbar"],
        default="CR",
        help="Selection option for the plot",
    )
    parser.add_argument(
        "--region",
        type=str,
        default="Nominal",
        help="Region for the plot",
    )
    parser.add_argument(
        "--tag",
        type=str,
        default="",
        help="Tag that is added to the output file",
    )

    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    variables = [v.strip() for v in args.variables.split(",") if v.strip()]
    channels = [c.strip() for c in args.channels.split(",") if c.strip()]

    if not variables:
        raise ValueError("No variables provided")
    if not channels:
        raise ValueError("No channels provided")

    sig_processes = SIGNAL_PROCESSES if args.add_signals else None

    for channel in channels:
        bkg_processes = ControlShapeBkgProcesses(
            embedding=args.embedding,
            fake_factor=args.fake_factor,
            channel=channel,
            nlo=args.nlo,
            selection_option=args.selection_option,
            draw_jet_fake_variation=args.draw_jet_fake_variation,
        )()

        shapes = ShapesParser.from_uproot_file(
            args.input,
            channel=channel,
            region=args.region,
            category=args.category,
        )

        for variable in variables:
            plot_helper.X_LABELS.setdefault(variable, variable)

            _bkg = shapes.get_histograms(variable=variable, processes=bkg_processes, key_prefix="bkg")
            _data = shapes.get_histograms(variable=variable, processes="data_obs", key_prefix="data")

            _sig = {}
            if sig_processes:
                try:
                    _sig = shapes.get_histograms(variable=variable, processes=sig_processes, key_prefix="sig")
                except ValueError:
                    _sig = shapes.get_histograms(
                        variable=variable,
                        processes=[
                            "qqH125-vbf_htautau_bin201to210_selection",
                            "ggH125-ggh_htautau_bin101to104_selection",
                            "ggH125-ggh_htautau_bin105to106_selection",
                            "ggH125-ggh_htautau_bin107to109_selection",
                            "ggH125-ggh_htautau_bin110to116_selection",
                        ],
                        key_prefix="sig",
                    )

            if args.linear:
                yscale, ylim = "linear", (0.0, None)
            else:
                yscale, ylim = "linear+log", (0.1, 1e2, None)

            output_dir = Path(f"{args.era}_plots_{args.postfix}_{args.tag}") / channel
            output_dir.mkdir(parents=True, exist_ok=True)
            category_label = args.category or ""
            output_base = f"{args.era}_{channel}_{category_label}_{variable}"

            plot_single_quantity(
                variable=variable,
                **{**_bkg, **_data, **_sig},
                ratio_ylim=(0.8, 1.2),
                yscale=yscale,
                ylim=ylim,
                figsize=(10, 10),
                legend_ncol=3,
                path=[
                    output_dir / f"{output_base}.pdf",
                    output_dir / f"{output_base}.png",
                ],
                # ratio_legend=True,
                ratio_legend=False,
                trim_edges=variable not in ["tau_decaymode_2", "q_1"],
                add_fraction=False,
                bkg_unct_label="Bkg. Unct. (stat.)"
            )


if __name__ == "__main__":
    args = parse_arguments()

    if not args.embedding and not args.fake_factor:
        postfix = "fully_classic"
    else:
        a = "emb" if args.embedding else "classic"
        b = "ff" if args.fake_factor else "classic"
        postfix = f"{a}_{b}"
    if args.nlo:
        postfix = f"{postfix}_nlo"
    if args.draw_jet_fake_variation is not None:
        postfix = f"{postfix}_{args.draw_jet_fake_variation}"

    args.postfix = postfix

    main(args)
