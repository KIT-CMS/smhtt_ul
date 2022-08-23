#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser as rootfile_parser
import Dumbledraw.styles as styles
import ROOT

import argparse
import copy
import yaml
import distutils.util
import logging

logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Plot categories using Dumbledraw from shapes produced by shape-producer module."
    )
    parser.add_argument(
        "-l", "--linear", action="store_true", help="Enable linear x-axis"
    )
    parser.add_argument(
        "-c", "--channel", nargs="+", type=str, required=True, help="Channels"
    )
    parser.add_argument("-e", "--era", type=str, required=True, help="Era")
    parser.add_argument(
        "-o", "--outputfolder", type=str, required=True, help="...yourself"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ROOT file with shapes of processes",
    )
    parser.add_argument(
        "--gof-variable",
        type=str,
        default=None,
        help="Enable plotting goodness of fit shapes for given variable",
    )
    parser.add_argument("--png", action="store_true", help="Save plots in png format")
    parser.add_argument(
        "--categories",
        type=str,
        required=True,
        choices=[
            "inclusive",
            "stxs_stage0",
            "stxs_stage1p1",
            "stxs_stage1p1cut",
            "stxs_stage1p1_15node",
            "None",
        ],
        help="Select categorization.",
    )
    parser.add_argument(
        "--single-category", type=str, default="", help="Plot single category"
    )
    parser.add_argument(
        "--normalize-by-bin-width",
        action="store_true",
        help="Normelize plots by bin width",
    )
    parser.add_argument(
        "--fake-factor", action="store_true", help="Fake factor estimation method used"
    )
    parser.add_argument(
        "--embedding", action="store_true", help="Fake factor estimation method used"
    )
    parser.add_argument(
        "--train-emb",
        type=lambda x: bool(distutils.util.strtobool(x)),
        default=True,
        help="Use fake factor training category",
    )
    parser.add_argument(
        "--train-ff",
        type=lambda x: bool(distutils.util.strtobool(x)),
        default=True,
        help="Use fake factor training category",
    )

    parser.add_argument(
        "--chi2test",
        action="store_true",
        help="Print chi2/ndf result in upper-right of subplot",
    )

    parser.add_argument(
        "--blind-data",
        action="store_true",
        help="if set, data is not plotted in signal categories above 0.5",
    )

    parser.add_argument(
        "--blinded-shapes",
        action="store_true",
        help="if set, plotting blinded shapes with no entries above threshold in  signal categories",
    )
    parser.add_argument(
        "--prefit", action="store_true", help="If set, use prefit shapes"
    )
    return parser.parse_args()


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def main(args):
    # plot signals
    logger.debug("Arguments: {}".format(args))
    if args.gof_variable is not None:
        channel_categories = {
            "et": ["300"],
            "mt": ["300"],
            "tt": ["300"],
            "em": ["300"],
        }
    else:
        channel_categories = {
            "mt": ["1", "2", "3", "4", "5", "6", "7"],
            "mt": [ "6", "7", "8", "10", "11"],
        }

        signalcats = []
        for channel in ["mt"]:
            channel_categories[channel] += signalcats
    channel_dict = {
        "ee": "ee",
        "em": "e#mu",
        "et": "e#tau_{h}",
        "mm": "#mu#mu",
        "mt": "#mu#tau_{h}",
        "tt": "#tau_{h}#tau_{h}",
    }
    # bkgs+stage1
    category_dict = {
        "1": "Pt20to25",
        "2": "Pt25to30",
        "3": "Pt30to35",
        "4": "Pt35to40",
        "5": "PtGt40",
        "6": "Inclusive",
        "7": "DM0",
        "8": "DM1",
        "9": "DM10_11",
        "10": "DM10",
        "11": "DM11",
        "100": "Control Region"
    }
    if args.linear:
        split_value = 0
    else:
        if args.normalize_by_bin_width:
            split_value = 10001
        else:
            split_value = 101

    split_dict = {c: split_value for c in ["et", "mt", "tt", "em", "mm"]}

    bkg_processes = ["VVL", "TTL", "ZL", "jetFakes", "EMB"]
    if not args.fake_factor and args.embedding:
        bkg_processes = ["QCD", "VVJ", "VVL", "W", "TTJ", "TTL", "ZJ", "ZL", "EMB"]
    if not args.embedding and args.fake_factor:
        bkg_processes = ["VVT", "VVJ", "TTT", "TTJ", "ZJ", "ZL", "jetFakes", "ZTT"]
    if not args.embedding and not args.fake_factor:
        bkg_processes = [
            "QCD",
            "VVT",
            "VVL",
            "VVJ",
            "W",
            "TTT",
            "TTL",
            "TTJ",
            "ZJ",
            "ZL",
            "ZTT",
        ]
    # bkg_processes = ["QCD", "VVJ", "VVL", "W", "TTJ", "TTL", "ZJ", "ZL", "EMB"]
    all_bkg_processes = [b for b in bkg_processes]
    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    if "2016" in args.era:
        era = "Run2016"
    elif "2017" in args.era:
        era = "Run2017"
    elif "2018" in args.era:
        era = "Run2018"
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception
    logger.debug("Channel Categories: {}".format(channel_categories))
    plots = []
    channel = args.channel[0]
    categories = []
    if args.single_category != "":
        logger.debug(f"channel {channel}")
        logger.warning("Selected category: {}".format(args.single_category))
        logger.warning("Available categories: {}".format(category_dict))
        catname = args.single_category.replace("htt_mt_", "")
        if catname in category_dict.values():
            categories = list(category_dict.keys())[
                list(category_dict.values()).index(catname)
            ]
        if catname == "100" and channel == "mm":
            categories =["100"]
        # categories = set(channel_categories[channel]).intersection(
        #     set([args.single_category])
        # )
    else:
        categories = channel_categories[channel]
    logger.warning("Categories: {}".format(categories))
    if not isinstance(categories, list):
        categories = [categories]
    for category in categories:
        rootfile = rootfile_parser.Rootfile_parser(args.input, prefit=args.prefit)
        if channel == "em" and args.embedding:
            bkg_processes = ["VVL", "W", "TTL", "ZL", "QCD", "EMB"]
        elif channel == "em" and not args.embedding:
            bkg_processes = ["VVL", "W", "TTL", "ZL", "QCD", "ZTT"]
        elif channel == "mm":
            bkg_processes = ["VVL", "W", "TTL", "ZL"]
        else:
            bkg_processes = [b for b in all_bkg_processes]
        legend_bkg_processes = copy.deepcopy(bkg_processes)
        legend_bkg_processes.reverse()
        # create plot
        width = 600
        if args.linear:
            plot = dd.Plot([0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)
        else:
            plot = dd.Plot([0.5, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)

        # get background histograms
        for process in bkg_processes:
            try:
                plot.add_hist(
                    rootfile.get(era, channel, category, process), process, "bkg"
                )
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict[process]
                )
            except BaseException:
                pass
        data_obs = rootfile.get(era, channel, category, "data_obs")
        plot.add_hist(data_obs, "data_obs")

        total_bkg = rootfile.get(era, channel, category, "TotalBkg")
        plot.add_hist(total_bkg, "total_bkg")

        total_sig = rootfile.get(era, channel, category, "TotalSig")
        plot.add_hist(total_sig, "total_sig")

        model_total = plot.subplot(2).get_hist("total_bkg")
        model_total.Add(plot.subplot(2).get_hist("total_sig"))
        plot.add_hist(model_total, "model_total")
        plot.subplot(0).setGraphStyle("data_obs", "e0")
        plot.setGraphStyle(
            "model_total",
            "e2",
            markersize=0,
            fillcolor=styles.color_dict["unc"],
            linecolor=0,
        )

        plot.subplot(2).normalize(
            [
                "model_total",
                "data_obs",
            ],
            "model_total",
        )

        # stack background processes
        plot.create_stack(bkg_processes, "stack")

        # normalize stacks by bin-width
        if args.normalize_by_bin_width:
            plot.subplot(0).normalizeByBinWidth()
            plot.subplot(1).normalizeByBinWidth()

        # set axes limits and labels
        plot.subplot(0).setYlims(
            split_dict[channel],
            max(
                2 * plot.subplot(0).get_hist("data_obs").GetMaximum(),
                split_dict[channel] * 2,
            ),
        )

        plot.subplot(2).setYlims(0.75, 1.25)

        if not args.linear:
            plot.subplot(1).setYlims(0.1, split_dict[channel])
            plot.subplot(1).setLogY()
            plot.subplot(1).setYlabel(
                ""
            )  # otherwise number labels are not drawn on axis
        plot.subplot(0).setYlabel("N_{events}")
        plot.subplot(2).setXlabel("m_{vis} [GeV]")
        plot.subplot(2).setYlabel("Ratio")
        # plot.scaleXLabelSize(0.8)
        # plot.scaleYTitleSize(0.8)
        plot.scaleYLabelSize(0.8)
        # plot.scaleXLabelOffset(2.0)
        plot.scaleYTitleOffset(1.1)
        plot.subplot(2).setNYdivisions(3, 5)
        plot.subplot(2).setNXdivisions(5, 3)
        # if not channel == "tt" and category in ["11", "12", "13", "14", "15", "16"]:
        #    plot.subplot(2).changeXLabels(["0.2", "0.4", "0.6", "0.8", "1.0"])

        # draw subplots. Argument contains names of objects to be drawn in
        # corresponding order.

        procs_to_draw_0 = (
            ["stack", "model_total", "data_obs"]
            if args.linear
            else ["stack", "model_total", "data_obs"]
        )
        procs_to_draw_1 = ["stack", "model_total", "data_obs"]
        procs_to_draw_2 = [
            "model_total",
            "data_obs",
        ]
        plot.subplot(0).Draw(procs_to_draw_0)
        if not args.linear:
            plot.subplot(1).Draw(procs_to_draw_1)
        plot.subplot(2).Draw(procs_to_draw_2)
        # create legends
        for i in range(2):
            plot.add_legend(width=0.6, height=0.15)
            for process in legend_bkg_processes:
                try:
                    plot.legend(i).add_entry(
                        0,
                        process,
                        styles.legend_label_dict[
                            process.replace("TTL", "TT").replace("VVL", "VV")
                        ],
                        "f",
                    )
                except BaseException:
                    pass
            plot.legend(i).add_entry(0, "total_bkg", "Bkg. unc.", "f")
            plot.legend(i).add_entry(0, "data_obs", "Data", "PE")
            plot.legend(i).setNColumns(3)
        plot.legend(0).Draw()
        plot.legend(1).setAlpha(0.0)
        plot.legend(1).Draw()

        if args.chi2test:
            f = ROOT.TFile(args.input, "read")
            background = f.Get(
                "htt_{}_{}_Run{}_{}/TotalBkg".format(
                    channel,
                    category,
                    args.era,
                    "prefit" if "prefit" in args.input else "postfit",
                )
            )
            data = f.Get(
                "htt_{}_{}_Run{}_{}/data_obs".format(
                    channel,
                    category,
                    args.era,
                    "prefit" if "prefit" in args.input else "postfit",
                )
            )
            chi2 = data.Chi2Test(background, "UW CHI2/NDF")
            plot.DrawText(0.7, 0.3, "\chi^{2}/ndf = " + str(round(chi2, 3)))

        for i in range(2):
            plot.add_legend(reference_subplot=2, pos=1, width=0.5, height=0.03)
            plot.legend(i + 2).add_entry(0, "data_obs", "Data", "PE")
            plot.legend(i + 2).add_entry(0, "total_bkg", "Bkg. unc.", "f")
            plot.legend(i + 2).setNColumns(4)
        plot.legend(2).Draw()
        plot.legend(3).setAlpha(0.0)
        plot.legend(3).Draw()

        # draw additional labels
        plot.DrawCMS()
        if "2016" in args.era:
            plot.DrawLumi("35.9 fb^{-1} (2016, 13 TeV)", textsize=0.5)
        elif "2017" in args.era:
            plot.DrawLumi("41.5 fb^{-1} (2017, 13 TeV)", textsize=0.5)
        elif "2018" in args.era:
            plot.DrawLumi("59.8 fb^{-1} (2018, 13 TeV)", textsize=0.5)
        elif "all" in args.era:
            plot.DrawLumi(
                "(35.9 + 41.5 + 59.7) fb^{-1} (2016+2017+2018, 13 TeV)",
                textsize=0.5,
            )
        else:
            logger.critical("Era {} is not implemented.".format(args.era))
            raise Exception

        plot.DrawChannelCategoryLabel(
            "%s, %s" % (channel_dict[channel], category_dict[category]),
            begin_left=None,
            textsize=0.032,
        )

        # save plot
        postfix = "prefit" if args.prefit else "postfit"
        plot.save(
            "%s/%s_%s_%s_%s.%s"
            % (
                args.outputfolder,
                args.era,
                channel,
                args.gof_variable if args.gof_variable is not None else category,
                postfix,
                "png",
            )
        )
        plot.save(
            "%s/%s_%s_%s_%s.%s"
            % (
                args.outputfolder,
                args.era,
                channel,
                args.gof_variable if args.gof_variable is not None else category,
                postfix,
                "pdf",
            )
        )
        # work around to have clean up seg faults only at the end of the
        # script
        plots.append(plot)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes.log".format(args.era), logging.DEBUG)
    main(args)
