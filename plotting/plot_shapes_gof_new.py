import uproot
import argparse
import mplhep as hep
import yaml
import numpy as np
from copy import deepcopy
import pathlib

from CODE.PLOT import ControlShapeBkgProcesses, plot_single_quantity, ShapesParser

hep.style.use("CMS")

bkg_processes = ControlShapeBkgProcesses(embedding=True, fake_factor=True, channel="mt", )()


argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("--input-file", type=str)

argument_parser.add_argument("--era", type=str, default="2018")
argument_parser.add_argument("--channel", type=str, default="mt")

argument_parser.add_argument("--variable", type=str, default="pt_2")

argument_parser.add_argument("--embedding", action="store_true")
argument_parser.add_argument("--fake-factor", action="store_true")
argument_parser.add_argument("--gof-binning-config", type=str, default="gof_binning_config.yaml")

argument_parser.add_argument("--output-folder", type=str)
argument_parser.add_argument("--suffix", type=str, default="")
argument_parser.add_argument("--region", type=str, default="Nominal")
argument_parser.add_argument("--replace-close-to-zero-with-zero", action="store_true")
argument_parser.add_argument("--ratio-ylim", nargs=2, type=float, default=(0.5, 1.5))

if __name__ == "__main__":
    args = argument_parser.parse_args()

    pathlib.Path(args.output_folder).mkdir(parents=True, exist_ok=True)

    bkg_processes = ControlShapeBkgProcesses(
        embedding=args.embedding,
        fake_factor=args.fake_factor,
        channel=args.channel,
    )()
    sig_processes = ["qqH_htt", "ggH_htt"]

    category=f"htt_{args.channel}_300_{args.era}{args.suffix}"

    shapes = ShapesParser.from_combine_shapes_file(args.input_file, category=category)
    shapes.add_systematic_uncertainties(uproot_file=args.input_file)

    with open(args.gof_binning_config) as f:
        gof_binning = yaml.safe_load(f)

    def replacement_function(obj, eps=1e-8):
        if isinstance(obj, dict):
            return {
                k: (v if k == "edges" else replacement_function(v, eps))
                for k, v in obj.items()
            }

        if isinstance(obj, np.ndarray):
            out = obj.copy()
            out[np.abs(out) < eps] = 0.0
            return out

        if isinstance(obj, tuple):
            return tuple(replacement_function(v, eps) for v in obj)

        return obj
    
    func = replacement_function if args.replace_close_to_zero_with_zero else lambda x: x

    plot_single_quantity(
        variable=args.variable,
        **{
            **func(shapes.get_histograms(key_prefix="bkg", processes=bkg_processes, uncertainty_type="total")),
            **func(shapes.get_histograms(key_prefix="data", processes="data_obs")),
            **func(shapes.get_histograms(key_prefix="sig", processes=sig_processes)),
        },
        ylim=(1e-2, 1e3 + 1, None),
        yscale="linear+log",
        figsize=(13, 10),
        legend_ncol=4,
        is_2d_gof=True,
        ratio_ylim=args.ratio_ylim,
        draw_2d_slice_guides=True,
        slice_binning_dict=gof_binning,
        slice_guide_options={
            "include_secondary_axis": True,
            "label_fontsize": 10,
            "label_color": "black",
            "line_alpha": 0.6,
            "line_width": 1.1,
            "line_style": "--",
            "line_color": "black",
            "ratio_vlines_full_height": True,
        },
        path=[
            pathlib.Path(args.output_folder) / f"{args.era}_{args.channel}_{args.variable}{args.suffix}.pdf",
            pathlib.Path(args.output_folder) / f"{args.era}_{args.channel}_{args.variable}{args.suffix}.png",
        ],
        ratio_legend=False,
        trim_edges=True,
        add_fraction=False,
    )
