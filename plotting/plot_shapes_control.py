#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import copy
import itertools as itt
import logging
import os
from multiprocessing import Pool, Process

import ROOT
import yaml
from process_ordering import ControlShapeBkgProcesses

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser_ntuple_processor_inputshapes as rootfile_parser
import Dumbledraw.styles as styles
from config.logging_setup_configs import setup_logging


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Plot categories using Dumbledraw from shapes produced by shape-producer module."
    )
    parser.add_argument(
        "-l", "--linear", action="store_true", help="Enable linear x-axis")
    parser.add_argument("-e", "--era", type=str, required=True, help="Era")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="ROOT file with shapes of processes")
    parser.add_argument(
        "--variables",
        type=str,
        default=None,
        help="Enable control plotting for given variable")
    parser.add_argument(
        "--category-postfix",
        type=str,
        default=None,
        help="Enable control plotting for given category_postfix. Structure of a category: <variable>_<postfix>")
    parser.add_argument(
        "--channels",
        type=str,
        default=None,
        help="Enable control plotting for given variable")
    parser.add_argument(
        "--normalize-by-bin-width",
        action="store_true",
        help="Normelize plots by bin width")
    parser.add_argument(
        "--fake-factor",
        action="store_true",
        help="Fake factor estimation method used")
    parser.add_argument(
        "--embedding",
        action="store_true",
        help="Fake factor estimation method used")
    parser.add_argument(
        "--nlo",
        action="store_true",
        help="Use NLO DY and Wjets MC")
    parser.add_argument(
        "--add-signals",
        action="store_true",
        help="Draw also signal processes and not only backgrounds")
    parser.add_argument(
        "--draw-jet-fake-variation",
        type=str,
        default=None,
        help="Draw variation of jetFakes or QCD in derivation region.")
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Plot a special category instead of nominal")
    parser.add_argument(
        "--selection-option",
        type=str,
        choices=["CR", "DR;ff;wjet", "DR;ff;qcd", "DR;ff;ttbar"],
        default="CR",
        help="Selection option for the plot",
    )
    parser.add_argument(
        "--tag",
        type=str,
        default="",
        help="Tag that is added to the output file"
    )

    return parser.parse_args()


def main(info):
    args = info["args"]
    variable = info["variable"]
    channel = info["channel"]
    channel_dict = {
        "ee": "#font[42]{#scale[0.85]{ee}}",
        "em": "#scale[0.85]{e}#mu",
        "et": "#font[42]{#scale[0.85]{e}}#tau_{#font[42]{h}}",
        "mm": "#mu#mu",
        "mt": "#mu#tau_{#font[42]{h}}",
        "tt": "#tau_{#font[42]{h}}#tau_{#font[42]{h}}"
    }
    if args.linear:
        split_value = 0.1
    else:
        if args.normalize_by_bin_width:
            split_value = 10001
        else:
            split_value = 101

    split_dict = {c: split_value for c in ["et", "mt", "tt", "em", "mm", "ee"]}

    bkg_processes = ControlShapeBkgProcesses(
        embedding=args.embedding,
        fake_factor=args.fake_factor,
        channel=channel,
        nlo=args.nlo,
        selection_option=args.selection_option,
        draw_jet_fake_variation=args.draw_jet_fake_variation,
    )()

    if "2016postVFP" in args.era:
        era = "Run2016postVFP"
    elif "2016preVFP" in args.era:
        era = "Run2016preVFP"
    elif "2017" in args.era:
        era = "Run2017"
    elif "2018" in args.era:
        era = "Run2018"
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    rootfile = rootfile_parser.Rootfile_parser(args.input, variable, )

    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    # create plot
    width = 600
    if args.linear:
        plot = dd.Plot(
            [0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)
    else:
        plot = dd.Plot(
            [0.5, [0.3, 0.28]], "ModTDR", r=0.04, l=0.14, width=width)

    # get background histograms
    total_bkg = None
    if args.category is None:
        stype = "Nominal"
        cat = None
    else:
        stype = "Nominal"
        cat = args.category

    for index, process in enumerate(bkg_processes):
        _hist = rootfile.get(channel, process, category=cat, shape_type=stype).Clone()

        if index == 0:
            total_bkg = _hist
        else:
            total_bkg.Add(_hist)

        plot.add_hist(_hist, process, "bkg")
        plot.setGraphStyle(process, "hist", fillcolor=styles.color_dict[process])

    plot.add_hist(total_bkg, "total_bkg")
    plot.setGraphStyle(
        "total_bkg",
        "e2",
        markersize=0,
        fillcolor=styles.color_dict["unc"],
        linecolor=0)

    plot.add_hist(rootfile.get(channel, "data", category=cat, shape_type=stype), "data_obs")
    data_norm = plot.subplot(0).get_hist("data_obs").Integral()
    plot.subplot(0).get_hist("data_obs").GetXaxis().SetMaxDigits(4)
    plot.subplot(0).setGraphStyle("data_obs", "e0")
    plot.subplot(0).setGraphStyle("data_obs", "e0")
    if args.linear:
        pass
    else:
        plot.subplot(1).setGraphStyle("data_obs", "e0")

    # get signal histograms
    plot_idx_to_add_signal = [0,2] if args.linear else [1,2]
    if args.add_signals:
        for i in plot_idx_to_add_signal:
            ggH = rootfile.get(channel, "ggH125",category=cat).Clone()
            qqH = rootfile.get(channel, "qqH125",category=cat).Clone()
            # VH = rootfile.get(channel, "VH125").Clone()
            # ttH = rootfile.get(channel, "ttH125").Clone()
            # HWW = rootfile.get(channel, "HWW").Clone()
            if ggH.Integral() > 0:
                ggH_scale = 10
            else:
                ggH_scale = 0.0
            if qqH.Integral() > 0:
                qqH_scale = 10
            else:
                qqH_scale = 0.0
            # if VH.Integral() > 0:
            #     VH_scale = 10
            # else:
            #     VH_scale = 0.0
            # if ttH.Integral() > 0:
            #     ttH_scale = 10
            # else:
            #     ttH_scale = 0.0
            # if HWW.Integral() > 0:
            #     HWW_scale = 10
            # else:
            #     HWW_scale = 0

            if i in [0,1]:
                ggH.Scale(ggH_scale)
                qqH.Scale(qqH_scale)
                # VH.Scale(VH_scale)
                # ttH.Scale(ttH_scale)
                # HWW.Scale(HWW_scale)
            plot.subplot(i).add_hist(ggH, "ggH")
            plot.subplot(i).add_hist(ggH, "ggH_top")
            plot.subplot(i).add_hist(qqH, "qqH")
            plot.subplot(i).add_hist(qqH, "qqH_top")
            # plot.subplot(i).add_hist(VH, "VH")
            # plot.subplot(i).add_hist(VH, "VH_top")
            # plot.subplot(i).add_hist(ttH, "ttH")
            # plot.subplot(i).add_hist(ttH, "ttH_top")
            # plot.subplot(i).add_hist(HWW, "HWW")
            # plot.subplot(i).add_hist(HWW, "HWW_top")

        plot.subplot(0 if args.linear else 1).setGraphStyle(
            "ggH", "hist", linecolor=styles.color_dict["ggH"], linewidth=3)
        plot.subplot(0 if args.linear else 1).setGraphStyle("ggH_top", "hist", linecolor=0)
        plot.subplot(0 if args.linear else 1).setGraphStyle(
            "qqH", "hist", linecolor=styles.color_dict["qqH"], linewidth=3)
        plot.subplot(0 if args.linear else 1).setGraphStyle("qqH_top", "hist", linecolor=0)
        # plot.subplot(0 if args.linear else 1).setGraphStyle(
        #     "VH", "hist", linecolor=styles.color_dict["VH"], linewidth=3)
        # plot.subplot(0 if args.linear else 1).setGraphStyle("VH_top", "hist", linecolor=0)
        # plot.subplot(0 if args.linear else 1).setGraphStyle(
        #     "ttH", "hist", linecolor=styles.color_dict["ttH"], linewidth=3)
        # plot.subplot(0 if args.linear else 1).setGraphStyle("ttH_top", "hist", linecolor=0)
        # plot.subplot(0 if args.linear else 1).setGraphStyle(
        #     "HWW", "hist", linecolor=styles.color_dict["HWW"], linewidth=3)
        # plot.subplot(0 if args.linear else 1).setGraphStyle("HWW_top", "hist", linecolor=0)


        # assemble ratio
        bkg_ggH = plot.subplot(2).get_hist("ggH")
        bkg_qqH = plot.subplot(2).get_hist("qqH")
        bkg_ggH.Add(plot.subplot(2).get_hist("total_bkg"))
        bkg_qqH.Add(plot.subplot(2).get_hist("total_bkg"))
        plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH")
        plot.subplot(2).add_hist(bkg_ggH, "bkg_ggH_top")
        plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH")
        plot.subplot(2).add_hist(bkg_qqH, "bkg_qqH_top")
        plot.subplot(2).setGraphStyle(
            "bkg_ggH",
            "hist",
            linecolor=styles.color_dict["ggH"],
            linewidth=3)
        plot.subplot(2).setGraphStyle("bkg_ggH_top", "hist", linecolor=0)
        plot.subplot(2).setGraphStyle(
            "bkg_qqH",
            "hist",
            linecolor=styles.color_dict["qqH"],
            linewidth=3)
        plot.subplot(2).setGraphStyle("bkg_qqH_top", "hist", linecolor=0)

    if args.add_signals:
        to_draw = [
            "total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH",
            "bkg_qqH_top", "data_obs"
        ]
    else:
        to_draw = [
            "total_bkg", "data_obs"
        ]
    plot.subplot(2).normalize(to_draw, "total_bkg")

    # stack background processes
    plot.create_stack(bkg_processes, "stack")

    # normalize stacks by bin-width
    if args.normalize_by_bin_width:
        plot.subplot(0).normalizeByBinWidth()
        plot.subplot(1).normalizeByBinWidth()

    # set axes limits and labels
    plot.subplot(0).setYlims(
        split_dict[channel],
        max(1.6 * plot.subplot(0).get_hist("data_obs").GetMaximum(),
            split_dict[channel] * 2))

    log_quantities = ["ME_ggh", "ME_vbf", "ME_z2j_1", "ME_z2j_2", "ME_q2v1", "ME_q2v2", "ME_vbf_vs_ggh", "ME_ggh_vs_Z"]

    # log_quantities += variables

    if variable in log_quantities:
        plot.subplot(0).setLogY()
        plot.subplot(0).setYlims(
            1.0,
            1000 * plot.subplot(0).get_hist("data_obs").GetMaximum())

    plot.subplot(2).setYlims(0.75, 1.45)
    # if channel == "mm":
    #     plot.subplot(0).setLogY()
    #     plot.subplot(0).setYlims(1, 10**10)

    if args.linear != True:
        plot.subplot(1).setYlims(0.1, split_dict[channel])
        plot.subplot(1).setYlabel(
            "")  # otherwise number labels are not drawn on axis
        plot.subplot(1).setLogY()
    # Check if variables should be plotted with log x axis
    log_x_variables = ["puppimet"]
    if variable in log_x_variables:
        plot.subplot(0).setLogX()
        plot.subplot(1).setLogX()
        plot.subplot(2).setLogX()
    if variable != None:
        if variable in styles.x_label_dict[channel]:
            x_label = styles.x_label_dict[channel][
                variable]
        else:
            x_label = variable
        plot.subplot(2).setXlabel(x_label)
    else:
        plot.subplot(2).setXlabel("NN output")
    if args.normalize_by_bin_width:
        plot.subplot(0).setYlabel("dN/d(NN output)")
    else:
        plot.subplot(0).setYlabel("N_{events}")

    plot.subplot(2).setYlabel("")
    plot.subplot(2).setGrid()
    plot.scaleYLabelSize(0.8)
    plot.scaleYTitleOffset(1.1)

    category = ""
    if not channel == "tt" and category in ["11", "12", "13", "14", "15", "16"]:
        plot.subplot(2).changeXLabels(["0.2", "0.4", "0.6", "0.8", "1.0"])

    # draw subplots. Argument contains names of objects to be drawn in corresponding order.
    # procs_to_draw = ["stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top", "VH", "VH_top", "ttH", "ttH_top", "data_obs"] if args.linear else ["stack", "total_bkg", "data_obs"]
    if args.add_signals:
        procs_to_draw = ["stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top", "data_obs"] if args.linear else ["stack", "total_bkg", "data_obs"]
    else:
        procs_to_draw = ["stack", "total_bkg", "data_obs"] if args.linear else ["stack", "total_bkg", "data_obs"]
    if args.draw_jet_fake_variation is not None:
        procs_to_draw = ["stack", "total_bkg", "data_obs"]
    plot.subplot(0).Draw(procs_to_draw)
    if args.linear != True:
        # plot.subplot(1).Draw([
        #     "stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top",
        #     "VH", "VH_top", "ttH", "ttH_top", "HWW", "HWW_top", "data_obs"
        # ])
        if args.add_signals:
            plot.subplot(1).Draw([
                "stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top",
                "data_obs"
            ])
        else:
            plot.subplot(1).Draw([
                "stack", "total_bkg", "data_obs"
            ])
    if args.draw_jet_fake_variation is None:
        plot.subplot(2).Draw([
            "total_bkg", "bkg_ggH", "bkg_ggH_top", "bkg_qqH",
            "bkg_qqH_top", "data_obs"
        ])
    else:
        plot.subplot(2).Draw([
            "total_bkg", "data_obs"
        ])

    # create legends
    suffix = ["", "_top"]
    for i in range(2):

        plot.add_legend(width=0.6, height=0.15)
        for process in legend_bkg_processes:
            if "mm" in channel and process == "EMB":
                plot.legend(i).add_entry(
                0,
                process,
                "#mu#rightarrow#mu embedded",
                'f',
                )
            else:
                plot.legend(i).add_entry(
                0,
                process,
                styles.legend_label_dict[process.replace("TTL", "TT").replace("VVL", "VV").replace("_NLO","")],
                'f'
                )
        plot.legend(i).add_entry(0, "total_bkg", "Bkg. stat. unc.", 'f')
        if args.add_signals:
            plot.legend(i).add_entry(0 if args.linear else 1, "ggH%s" % suffix[i], "%s #times gg#rightarrowH"%str(int(ggH_scale)), 'l')
            plot.legend(i).add_entry(0 if args.linear else 1, "qqH%s" % suffix[i], "%s #times qq#rightarrowH"%str(int(qqH_scale)), 'l')
            # plot.legend(i).add_entry(0 if args.linear else 1, "VH%s" % suffix[i], "%s #times V(lep)H"%str(int(VH_scale)), 'l')
            # plot.legend(i).add_entry(0 if args.linear else 1, "ttH%s" % suffix[i], "%s #times ttH"%str(int(ttH_scale)), 'l')
            # # plot.legend(i).add_entry(0 if args.linear else 1, "HWW%s" % suffix[i], "%s #times H#rightarrowWW"%str(int(HWW_scale)), 'l')
        plot.legend(i).add_entry(0, "data_obs", "Observed", 'PE2L')
        plot.legend(i).setNColumns(3)
    plot.legend(0).Draw()
    plot.legend(1).setAlpha(0.0)
    plot.legend(1).Draw()

    for i in range(2):
        plot.add_legend(
            reference_subplot=2, pos=1, width=0.6, height=0.03)
        plot.legend(i + 2).add_entry(0, "data_obs", "Observed", 'PE2L')
        if "mm" not in channel and "ee" not in channel and args.draw_jet_fake_variation is None and args.add_signals:
            plot.legend(i + 2).add_entry(0 if args.linear else 1, "ggH%s" % suffix[i],
                                         "ggH+bkg.", 'l')
            plot.legend(i + 2).add_entry(0 if args.linear else 1, "qqH%s" % suffix[i],
                                         "qqH+bkg.", 'l')
        plot.legend(i + 2).add_entry(0, "total_bkg", "Bkg. stat. unc.", 'f')
        plot.legend(i + 2).setNColumns(4)
    plot.legend(2).Draw()
    plot.legend(3).setAlpha(0.0)
    plot.legend(3).Draw()

    # draw additional labels
    plot.DrawCMS()
    if "2016postVFP" in args.era:
        plot.DrawLumi("16.8 fb^{-1} (2016UL postVFP, 13 TeV)")
    elif "2016preVFP" in args.era:
        plot.DrawLumi("19.5 fb^{-1} (2016UL preVFP, 13 TeV)")
    elif "2017" in args.era:
        plot.DrawLumi("41.5 fb^{-1} (2017, 13 TeV)")
    elif "2018" in args.era:
        plot.DrawLumi("59.8 fb^{-1} (2018, 13 TeV)")
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception

    posChannelCategoryLabelLeft = None
    plot.DrawChannelCategoryLabel(
        "%s, %s" % (channel_dict[channel], "inclusive"),
        begin_left=posChannelCategoryLabelLeft)

    print("Trying to save the created plot")
    _path = os.path.join(f"{args.era}_plots_{postfix}_{args.tag}", channel)
    if not os.path.exists(_path):
        os.makedirs(_path, exist_ok=True)
    for _ext in ["pdf", "png"]:
        plot.save(os.path.join(_path, f"{args.era}_{channel}_{args.category or ''}_{variable}.{_ext}"))


if __name__ == "__main__":
    args = parse_arguments()
    logger = setup_logging(logger=logging.getLogger(__name__))
    variables, channels = args.variables.split(","), args.channels.split(",")

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

    infolist = [{"args": args, "channel": ch, "variable": v} for ch, v in itt.product(channels, variables)]
    for info in infolist:
        main(info)
