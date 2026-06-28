#!/usr/bin/env python3
import argparse
import pathlib
import logging
import mplhep as hep


parser = argparse.ArgumentParser(description="Plot NN output from Combine shapes.")
parser.add_argument("--base-path", type=pathlib.Path, required=True, help="Base path to output directory (e.g. $PWD/output)")
parser.add_argument("--era", type=str, default="2018", help="Data-taking era")
parser.add_argument("--channel", type=str, default="mt", help="Decay channel")
parser.add_argument("--ntupletag", type=str, required=True, help="Ntuple tag")
parser.add_argument("--tag", type=str, required=True, help="Job run tag")
parser.add_argument("--save-path", type=pathlib.Path, default=None, help="Explicit output path for plots")
parser.add_argument("--stage0", action="store_true", help="Use STXS stage 0 signals and categories instead of stage 1.2")
    
BKG_CATEGORIES = (
    (10, r"$\tau$ embedded"),
    (11, r"Jet $\to \tau_{h}$"),
    (12, r"$t\bar{t}(\ell\tau)$"),
    (13, r"$Z\to\ell\ell$"),
    (14, r"Diboson ($\ell\tau$)"),
)

STAGES = {
    "stage1p2": {
        "sig_processes": (
            "qqH125-vbf_htautau_bin201to210_selection125",
            "ggH125-ggh_htautau_bin101to104_selection125",
            "ggH125-ggh_htautau_bin105to106_selection125",
            "ggH125-ggh_htautau_bin107to109_selection125",
            "ggH125-ggh_htautau_bin110to116_selection125",
        ),
        # (cat_id, label, ratio_ylim)
        "signal_categories": (
            (100, r"VBF", (0.5, 2.0)),
            (101, r"ggH: $p_T^H \geq 200 GeV$", (0.5, 1.5)),
            (102, r"ggH: $N_{jets} = 0$", (0.5, 1.5)),
            (103, r"ggH: $N_{jets} = 1$", (0.5, 1.5)),
            (104, r"ggH: $N_{jets} \geq 2$", (0.5, 1.5)),
        ),
    },
    "stage0": {
        "sig_processes": (
            "qqH125-vbf_htautau_bin201to210_selection125",
            "ggH125-ggh_htautau_bin101to116_selection125",
        ),
        "signal_categories": (
            (100, r"VBF", (0.5, 2.0)),
            (101, r"ggH", (0.5, 1.5)),
        ),
    },
}


def main(args):
    folder_name = f"{args.era}-{args.channel}-{args.ntupletag}-{args.tag}"
    ntuple_dir = args.base_path / folder_name
    
    input_root = ntuple_dir / "datacards.for_plotting" / args.channel / "common" / f"htt_input_{args.era}.root"
    shapes_root = ntuple_dir / "datacards.for_plotting" / args.channel / "125" / "shapes" / "datacard-shapes-prefit.root"
    
    if args.save_path:
        save_path = args.save_path
    else:
        save_path = ntuple_dir / "datacards.for_plotting" / args.channel / "125" / "shapes" / "plots"
        
    save_path.mkdir(parents=True, exist_ok=True)

    try:
        from CODE.PLOT import ControlShapeBkgProcesses, plot_nn_output_from_combine_shapes_file
        import CODE.LOGGING as log
    except ImportError as e:
        raise ImportError("Could not import CODE.PLOT components. Verify PYTHONPATH environment variable.") from e

    hep.style.use("CMS")

    logger = log.setup_logging(logger=logging.getLogger(__name__))
    logger.debug(f"Called state and defined variables: {locals()}")

    stage = STAGES["stage0" if args.stage0 else "stage1p2"]
    category = lambda cat_id: f"htt_{args.channel}_{cat_id}_{args.era}"

    category_to_name = tuple(
        (category(cat_id), label) for cat_id, label, _ in stage["signal_categories"]
    ) + tuple(
        (category(cat_id), label) for cat_id, label in BKG_CATEGORIES
    )

    override = {
        category(cat_id): {"add_fraction": True, "ratio_ylim": rylim}
        for cat_id, _, rylim in stage["signal_categories"]
    }
    override.update({category(cat_id): {"ratio_ylim": (0.5, 1.5)} for cat_id, _ in BKG_CATEGORIES})

    plot_nn_output_from_combine_shapes_file(
        input_root,
        shapes_root,
        bkg_processes=ControlShapeBkgProcesses(embedding=True, fake_factor=True, channel=args.channel)(),
        sig_processes=stage["sig_processes"],
        category_to_name=category_to_name,
        per_category_plotting_kwargs_override=override,
        save_path=str(save_path),
        show=False,
    )
    logger.info(f"Plots successfully generated and saved to: {save_path}")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
