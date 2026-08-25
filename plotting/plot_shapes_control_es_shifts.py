#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser_ntuple_processor_inputshapes as rootfile_parser
import Dumbledraw.styles as styles
import ROOT

import argparse
import copy
import yaml
import os

import logging

from plotting.plot_shapes_combined import plot
logger = logging.getLogger("")
from multiprocessing import Pool
from multiprocessing import Process

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Plot categories using Dumbledraw from shapes produced by shape-producer module."
    )
    parser.add_argument("-l", "--linear", action="store_true", help="Enable linear x-axis")
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
        "--category",
        type=str,
        default=None,
        help="Enable control plotting for given category")
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
        "--draw-jet-fake-variation",
        type=str,
        default=None,
        help="Draw variation of jetFakes or QCD in derivation region.")
    parser.add_argument(
        "--vs-jet-wp",
        type=str,
        default=None,
        help="Working point for tau ID vs Jets.")
    parser.add_argument(
        "--vs-ele-wp",
        type=str,
        default=None,
        help="Working point for tau ID.")
    parser.add_argument(
        "--energy_scale",
        action="store_true",
        help="Include energy scale variation in the plot.")
    parser.add_argument(
        "--es_family_plot",
        default=[],
        help="List of energy scale variations to put in one plot additionaly to the nominal one.")
    parser.add_argument(
        "--es_shift",
        type=str,
        default="EMB",
        help="The value of the energy scale shift in %. EMB is nominal.")
    parser.add_argument(
        "--es_up",
        type=float,
        default=None,
        help="Upper bound of the energy scale shift in %.")
    parser.add_argument(
        "--es_down",
        type=float,
        default=None,
        help="Lower bound of the energy scale shift in %.")
    parser.add_argument(
        "--tag",
        type=str,
        default=None,
        help="SFs user tag.")
    parser.add_argument(
        "--tes_precision",
        type=float,
        default=0.1,
        help="Precision of the TES variation.")

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


def add_es_family_plots(args, channel, cat, rootfile, plot, other_bkg):
    added_plots_info = []
    if args.es_family_plot:
        es_variations = args.es_family_plot.split(",") if isinstance(args.es_family_plot, str) else args.es_family_plot
        # Define some colors for the variations
        # colors = [632, 600, 418, 616, 432, 800] # kRed, kBlue, kGreen+2, kMagenta, kCyan, kOrange
        colors = [ROOT.kRed - 3, ROOT.kRed - 7, ROOT.kBlue - 7, ROOT.kBlue - 3]
        
        for i, var in enumerate(es_variations):
            # Using the retrieval method you mentioned works for you
            emb_var = rootfile.get(channel, var, cat, shape_type="Nominal")
            
            if emb_var:
                total_var = emb_var.Clone()
                if other_bkg:
                    total_var.Add(other_bkg)
                
                plot_name = f"total_bkg_{var}"
                plot.add_hist(total_var, plot_name)
                
                color = colors[i % len(colors)]
                plot.setGraphStyle(plot_name, "hist", linecolor=color, linewidth=2, linestyle=2,fillstyle=0)
                
                # Parse label
                # Example: emb0p4 -> EMB +0.4%, embminus0p4 -> EMB -0.4%
                label_str = var.replace("emb", "")
                if "minus" in label_str:
                    sign = "-"
                    label_str = label_str.replace("minus", "")
                else:
                    sign = "+"
                val = label_str.replace("p", ".")
                short_val = val.split(".")[0] if "." in val else val
                # label = f"TES {sign}{short_val}%"
                label = f"TES {sign}{val}%"
                
                added_plots_info.append((plot_name, label))
    return added_plots_info


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
    category_dict_plot = {
        "DM0": "DM 0",
        "DM1": "DM 1",
        "DM10": "DM 10",
        "DM11": "DM 11",
        "DM1011": "DM 10+11",     
        "DM0_PT20_40": "DM 0 (PT20 to 40)",
        "DM1_PT20_40": "DM 1 (PT20 to 40)",
        "DM10_PT20_40": "DM 10 (PT20 to 40)",
        "DM11_PT20_40": "DM 11 (PT20 to 40)",
        "DM1011_PT20_40": "DM 10+11 (PT20 to 40)",
        "DM0_PT40_200": "DM 0 (PT40 to 200)",
        "DM1_PT40_200": "DM 1 (PT40 to 200)",
        "DM10_PT40_200": "DM 10 (PT40 to 200)",
        "DM11_PT40_200": "DM 11 (PT40 to 200)",
        "DM1011_PT40_200": "DM 10+11 (PT40 to 200)",
        "control_region": "Control Region",
        "Inclusive": "Inclusive",
    }
    if args.linear == True:
        split_value = 0.1
    else:
        if args.normalize_by_bin_width:
            split_value = 10001
        else:
            split_value = 101

    split_dict = {c: split_value for c in ["et", "mt", "tt", "em", "mm"]}

    bkg_processes = [
        "VVL", "TTL", "ZL", "jetFakesEMB", "EMB"
    ]
    if not args.fake_factor and args.embedding and not args.energy_scale:
        # bkg_processes = [
        #     "QCDEMB", "VVL", "VVJ", "W", "TTL", "TTJ", "ZJ", "ZL", "EMB"
        # ]
        bkg_processes = [ # Ordered for AN_dict:
            "QCDEMB", "VVJ", "TTJ", "ZJ", "W", "VVL", "TTL", "ZL", "EMB"
        ]
    if not args.fake_factor and args.embedding and args.energy_scale:
        bkg_processes = [
            "QCD", "VVL", "VVJ", "W", "TTL", "TTJ", "ZJ", "ZL", args.es_shift
        ]
    if not args.embedding and args.fake_factor:
        bkg_processes = [
            "VVT", "VVL", "TTT", "TTL", "ZL", "jetFakes", "ZTT"
        ]
    if not args.embedding and not args.fake_factor:
        bkg_processes = [
            "QCD", "VVT", "VVL", "VVJ", "W", "TTT", "TTL", "TTJ", "ZJ", "ZL", "ZTT"
        ]
    if args.draw_jet_fake_variation is not None:
        bkg_processes = [
            "VVL", "TTL", "ZL", "EMB"
        ]
        if not args.fake_factor and args.embedding and not args.energy_scale:
            bkg_processes = [
                "VVL", "VVJ", "W", "TTL", "TTJ", "ZJ", "ZL", "EMB"
            ]
        if not args.fake_factor and args.embedding and args.energy_scale:
            bkg_processes = [
                "VVL", "VVJ", "W", "TTL", "TTJ", "ZJ", "ZL", args.es_shift,
            ]
        if not args.embedding and args.fake_factor:
            bkg_processes = [
                "VVT", "VVL", "TTT", "TTL", "ZL", "ZTT"
            ]
        if not args.embedding and not args.fake_factor:
            bkg_processes = [
                "VVT", "VVL", "VVJ", "W", "TTT", "TTL", "TTJ", "ZJ", "ZL", "ZTT"
            ]

    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()
    # breakpoint()
    if args.energy_scale:
        rootfile = rootfile_parser.Rootfile_parser(args.input, variable, [args.es_down, args.es_up], args.tes_precision, channel=channel)
    else:
        rootfile = rootfile_parser.Rootfile_parser(args.input, variable, [None, None],  channel=channel)

    if "em" in channel:
        if not args.embedding:
            bkg_processes = [
                "QCD", "VVT", "VVL", "W", "TTT", "TTL", "ZL", "ZTT"
            ]
        if args.embedding:
            bkg_processes = [
                "QCDEMB", "VVL", "W", "TTL", "ZL", "EMB"
            ]
        if args.draw_jet_fake_variation is not None:
            if not args.embedding:
                bkg_processes = [
                    "VVT", "VVL", "W", "TTT", "TTL", "ZL", "ZTT"
                ]
            if args.embedding:
                bkg_processes = [
                    "VVL", "W", "TTL", "ZL", "EMB"
                ]

    if "mm" in channel:
        if not args.embedding:
            bkg_processes = ["ZL", "QCD","W", "VVL", "TTL", "STL"]
        elif args.embedding:
            bkg_processes = [
                "QCD", "W", "EMB"
            ]

    legend_bkg_processes = copy.deepcopy(bkg_processes)
    legend_bkg_processes.reverse()

    AN_dict ={
    "jetFData": ["QCD", "QCDEMB"],
    "jetFMC": ["VVJ", "TTJ", "ZJ", "W"],
    "lepF": ["VVL", "TTL", "ZL"],
    "true_tautau": ["ZTT", "TTT", "VVT"]
    }
    
    # create plot
    width = 800
    if args.linear == True:
        plot = dd.Plot(
            [0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.18, width=width)
    else:
        plot = dd.Plot(
            [0.5, [0.3, 0.28]], "ModTDR", r=0.04, l=0.18, width=width)
        
    # get category histograms
    cat = args.category
    scale_max = 1.0
    # # If ratio plot range is not large enough:
    if cat is not None and "40_200" in cat:
        scale_max = 1.75
    # get background histograms
    total_bkg = None
    other_bkg = None
    if args.draw_jet_fake_variation is None:
        stype = "Nominal"
    else:
        stype = args.draw_jet_fake_variation
    # print(bkg_processes, variable)
    # breakpoint()
    for index,process in enumerate(bkg_processes):
        if index == 0:
            total_bkg = rootfile.get(channel, process, cat, shape_type=stype).Clone()
            if process != "EMB":
                other_bkg = rootfile.get(channel, process, cat, shape_type=stype).Clone()
        else:
            total_bkg.Add(rootfile.get(channel, process, cat, shape_type=stype))
            if process != "EMB":
                if other_bkg is None:
                    other_bkg = rootfile.get(channel, process, cat, shape_type=stype).Clone()
                else:
                    other_bkg.Add(rootfile.get(channel, process, cat, shape_type=stype))
        
        if process in ["jetFakesEMB", "jetFakes"] and channel == "tt":
            total_bkg.Add(rootfile.get(channel, "wFakes",cat, shape_type=stype))
            if process != "EMB":
                if other_bkg is None:
                    other_bkg = rootfile.get(channel, "wFakes",cat, shape_type=stype).Clone()
                else:
                    other_bkg.Add(rootfile.get(channel, "wFakes",cat, shape_type=stype))
            
            jetfakes_hist = rootfile.get(channel, process, cat, shape_type=stype)
            jetfakes_hist.Add(
                rootfile.get(channel, "wFakes", cat, shape_type=stype))
            plot.add_hist(
                jetfakes_hist, process, "bkg")
        else:
            plot.add_hist(
                rootfile.get(channel, process, cat, shape_type=stype), process, "bkg")
        if process == "EMB" or process.startswith("emb"):
            if channel != "mm":
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict["EMB"])
            else:
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict["MUEMB"])
        else:
            if channel == "mm":
                plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict[process])
            else:
                if process in AN_dict["jetFData"]:
                    plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict["QCD"])
                elif process in AN_dict["jetFMC"]:
                    plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict["jetFakesQCD"])
                elif process in AN_dict["lepF"]:
                    plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict["ZL"])
                elif process in AN_dict["true_tautau"]:
                    if process in ["ZTT", "ZTT_NLO"]:
                        plot.setGraphStyle(
                        process, "hist", fillcolor=styles.color_dict["ZTT"])
                    elif process == "TTT":
                        plot.setGraphStyle(
                        process, "hist", fillcolor=styles.color_dict["TTT"])
                    elif process == "VVT":
                        plot.setGraphStyle(
                        process, "hist", fillcolor=styles.color_dict["VVT"])


    plot.add_hist(total_bkg, "total_bkg")
    plot.setGraphStyle(
        "total_bkg",
        "e2",
        markersize=0,
        fillcolor=styles.color_dict["unc"],
        linecolor=0)

    plot.add_hist(rootfile.get(channel, "data", cat, shape_type=stype), "data_obs")
    data_norm = plot.subplot(0).get_hist("data_obs").Integral()
    plot.subplot(0).get_hist("data_obs").GetXaxis().SetMaxDigits(4)
    plot.subplot(0).setGraphStyle("data_obs", "e0")
    plot.subplot(0).setGraphStyle("data_obs", "e0")
    if args.linear:
        pass
    else:
        plot.subplot(1).setGraphStyle("data_obs", "e0")


    # Add ES variations of EMB into the plot, if argument given
    es_family_plots_info = add_es_family_plots(args, channel, cat, rootfile, plot, other_bkg)
    es_family_plots = [x[0] for x in es_family_plots_info]
    
    procs_to_normalize = ["total_bkg", "data_obs"]
    if es_family_plots:
        procs_to_normalize.extend(es_family_plots)
    
    plot.subplot(2).normalize(procs_to_normalize, "total_bkg")

    # stack background processes
    plot.create_stack(bkg_processes, "stack")  
    # normalize stacks by bin-width
    if args.normalize_by_bin_width:
        plot.subplot(0).normalizeByBinWidth()
        plot.subplot(1).normalizeByBinWidth()

    # set axes limits and labels
    plot.subplot(0).setYlims(
        split_dict[channel],
        max(2.0 * plot.subplot(0).get_hist("data_obs").GetMaximum(),
            split_dict[channel] * 2) * scale_max )

    log_quantities = ["ME_ggh", "ME_vbf", "ME_z2j_1", "ME_z2j_2", "ME_q2v1", "ME_q2v2", "ME_vbf_vs_ggh", "ME_ggh_vs_Z"]
    if variable in log_quantities:
        plot.subplot(0).setLogY()
        plot.subplot(0).setYlims(
            1.0,
            1000 * plot.subplot(0).get_hist("data_obs").GetMaximum())
    
    plot.subplot(2).setYlims(0.45/(scale_max**3), 1.75 * scale_max)
    if channel == "mm":
        # plot.subplot(0).setLogY()
        # plot.subplot(0).setYlims(1, 10**10)
        pass

    if args.linear != True:
        plot.subplot(1).setYlims(0.1, split_dict[channel])
        plot.subplot(1).setYlabel("")  # otherwise number labels are not drawn on axis
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
        # plot.subplot(0).setYlabel("N_{events} / bin width")
        plot.subplot(0).setYlabel("#frac{d N_{events}}{d m_{vis}} #left[GeV^{-1}#right]")
    else:
        plot.subplot(0).setYlabel("N_{events}")

    plot.subplot(2).setYlabel("")
    plot.subplot(2).setGrid()
    plot.scaleYLabelSize(0.7)
    plot.scaleYTitleOffset(0.8)
    

    category = ""
    if not channel == "tt" and category in ["11", "12", "13", "14", "15", "16"]:
        plot.subplot(2).changeXLabels(["0.2", "0.4", "0.6", "0.8", "1.0"])

    # draw subplots. Argument contains names of objects to be drawn in corresponding order.
    if "mm" not in channel:
        procs_to_draw = ["stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top", "data_obs"] if args.linear else ["stack", "total_bkg", "data_obs"]
        if args.draw_jet_fake_variation is not None:
            procs_to_draw = ["stack", "total_bkg", "data_obs"]
        
        # Add ES family plots to drawing list
        if es_family_plots:
             if "data_obs" in procs_to_draw:
                 idx = procs_to_draw.index("data_obs")
                 procs_to_draw[idx:idx] = es_family_plots
             else:
                 procs_to_draw.extend(es_family_plots)
        
        plot.subplot(0).Draw(procs_to_draw)
        if args.linear != True:

            plot.subplot(1).Draw([
                "stack", "total_bkg", "ggH", "ggH_top", "qqH", "qqH_top",
                "data_obs"
            ])
        if args.draw_jet_fake_variation is None:
            ratio_procs = ["total_bkg", "data_obs"]
            if es_family_plots:
                ratio_procs.extend(es_family_plots)  # Add ES family plots to ratio plot
            plot.subplot(2).Draw(ratio_procs)
        else:
            plot.subplot(2).Draw([
                "total_bkg", "data_obs"
            ])
    else:
        procs_to_draw = ["stack", "total_bkg", "data_obs"] if args.linear else ["stack", "total_bkg", "data_obs"]
        plot.subplot(0).Draw(procs_to_draw)
        if args.linear != True:
            plot.subplot(1).Draw([
                "stack", "total_bkg", "data_obs"
            ])
        plot.subplot(2).Draw([
            "total_bkg", "data_obs"
        ])

    # create legends
    suffix = ["", "_top"]
    for i in range(2):
        jetFData = False
        jetFMC = False
        lepF = False
        z_tt = False
        tt_t = False
        vv_t = False
        plot.add_legend(width=0.7, height=0.15)
        for process in legend_bkg_processes:
            if "emb" in process:
                if channel != "mm":
                    tes_variation = process.split("emb")[1].replace("minus", "-").replace("p", ".")
                    emb_label = f"#tau embedded {tes_variation}%"
                    plot.legend(i).add_entry(
                        0, process, emb_label, 'f')
                else:
                    emb_label = f"#mu embedded"
                    plot.legend(i).add_entry(
                        0, process, emb_label, 'f')
            else:
                if channel == "mm":
                    if "EMB" in process:
                        emb_label = f"#mu embedded"
                        plot.legend(i).add_entry(
                            0, process, emb_label, 'f')
                    else:
                        # plot.legend(i).add_entry(
                        #     0, process, styles.legend_label_dict[process.replace("TTL", "TT").replace("VVL", "VV").replace("NLO","")], 'f')
                        plot.legend(i).add_entry(
                            0, process, styles.legend_label_dict[process], 'f')
                elif "EMB" in process:
                    plot.legend(i).add_entry(
                        0, process, styles.legend_label_dict[process], 'f')
                else:
                    if process in AN_dict["jetFData"] and not jetFData:
                        plot.legend(i).add_entry(
                            0, process, styles.legend_label_dict["jetFakesData"], 'f')
                        jetFData = True
                    elif process in AN_dict["jetFMC"] and not jetFMC:
                        plot.legend(i).add_entry(
                            0, process, styles.legend_label_dict["jetFakesMC"], 'f')
                        jetFMC = True
                    elif process in AN_dict["lepF"] and not lepF:
                        plot.legend(i).add_entry(
                            0, process, styles.legend_label_dict["lepFakes"], 'f')
                        lepF = True
                    elif process in AN_dict["true_tautau"]:
                        if process == "ZTT" and not z_tt:
                            plot.legend(i).add_entry(
                                0, process, styles.legend_label_dict["ZTT"], 'f')
                            z_tt = True
                        elif process == "TTT" and not tt_t:
                            plot.legend(i).add_entry(
                                0, process, styles.legend_label_dict["TTT"], 'f')
                            tt_t = True
                        elif process == "VVT" and not vv_t:
                            plot.legend(i).add_entry(
                                0, process, styles.legend_label_dict["VVT"], 'f')
                            vv_t = True
                    
                    else:
                        if process in AN_dict["lepF"] + AN_dict["jetFMC"] + AN_dict["jetFData"] + AN_dict["true_tautau"]:
                            continue
                        else:
                            print(f"Legend entry for process:{process} had a problem.")
                            breakpoint()
        # Add es_family to legend (assuming legend 0 exists)
        if es_family_plots_info:
            for name, label in es_family_plots_info:
                plot.legend(i).add_entry(0, name, label, 'l')   
        plot.legend(i).add_entry(0, "total_bkg", "Bkg. stat. unc.", 'f')
        plot.legend(i).add_entry(0, "data_obs", "Observed", 'PE2L')
        plot.legend(i).setNColumns(4)
    plot.legend(0).Draw()
    plot.legend(1).setAlpha(0.0)
    plot.legend(1).Draw()

    # for i in range(2):
    #     plot.add_legend(
    #         reference_subplot=2, pos=1, width=0.6, height=0.04)
    #     plot.legend(i + 2).add_entry(0, "data_obs", "Observed", 'PE2L')
    #     plot.legend(i + 2).add_entry(0, "total_bkg", "Bkg. stat. unc.", 'f')
    #     if es_family_plots_info:
    #         for name, label in es_family_plots_info:
    #             plot.legend(i + 2).add_entry(0, name, label, 'l')
    #     # plot.legend(i + 2).setEntrySeparation(0.02)
    #     plot.legend(i + 2).setNColumns(4)
    # plot.add_legend(
    #         reference_subplot=2, pos=1, width=0.6, height=0.04)
    # plot.legend(2).Draw()
    # plot.legend(3).setAlpha(0.0)
    # plot.legend(3).Draw()

    # draw additional labels
    # plot.DrawCMS() Not in AN plots !!!
    if "2016postVFP" in args.era:
            plot.DrawLumi("16.8 fb^{-1} (2016postVFP, 13 TeV)")
    elif "2016preVFP" in args.era:
            plot.DrawLumi("19.5 fb^{-1} (2016preVFP, 13 TeV)")
    elif "2017" in args.era:
        plot.DrawLumi("41.5 fb^{-1} (2017, 13 TeV)")
    elif "2018" in args.era:
        plot.DrawLumi("59.7 fb^{-1} (2018, 13 TeV)")
    else:
        logger.critical(f"Era {args.era} is not implemented.")
        raise Exception

    posChannelCategoryLabelLeft = None
    if cat is None:
        cat_str = "Inclusive"
    else:
        cat_str = cat
    plot.DrawChannelCategoryLabel(
        "%s, %s" % (channel_dict[channel], category_dict_plot[cat_str]),
        begin_left=posChannelCategoryLabelLeft)

    # save plot
    if not args.embedding and not args.fake_factor:
        postfix = "fully_classic"
    if args.embedding and not args.fake_factor:
        postfix = "emb_classic"
    if not args.embedding and args.fake_factor:
        postfix = "classic_ff"
    if args.embedding and args.fake_factor:
        postfix = "emb_ff"
    if args.draw_jet_fake_variation is not None:
        postfix = postfix + "_" + args.draw_jet_fake_variation
    if "ctrl" in args.input:
        shape_type = "_ctrl"
    else:
        shape_type = ""
    os.makedirs(f"output/plots/{args.tag}/shapes{shape_type}", exist_ok=True)
    os.makedirs(f"output/plots/{args.tag}/shapes{shape_type}/{args.vs_jet_wp}/{args.vs_ele_wp}",exist_ok=True)
    savepath=f"output/plots/{args.tag}/shapes{shape_type}/{args.vs_jet_wp}/{args.vs_ele_wp}"
    for i in range(len(bkg_processes)):
        if "emb" in bkg_processes[i]:
            shiftanme = bkg_processes[i]
        else:
            shiftanme = ""
    print("Trying to save the created plot")
    plot.save(f"{savepath}/{postfix}_{cat_str}_{variable}{shiftanme}.pdf")
    plot.save(f"{savepath}/{postfix}_{cat_str}_{variable}{shiftanme}.png")


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes.log".format(args.era), logging.DEBUG)
    variables = args.variables.split(",")
    channels = args.channels.split(",")
    infolist = []
    print(f"Variables: {variables}")
    
    if not args.embedding and not args.fake_factor:
        postfix = "fully_classic"
    if args.embedding and not args.fake_factor:
        postfix = "emb_classic"
    if not args.embedding and args.fake_factor:
        postfix = "classic_ff"
    if args.embedding and args.fake_factor:
        postfix = "emb_ff"

    # if not os.path.exists(f"{args.era}_plots_{postfix}_{args.tag}"):
    #     os.mkdir(f"{args.era}_plots_{postfix}_{args.tag}")
    for ch in channels:
        # if not os.path.exists(f"{args.era}_plots_{postfix}_{args.tag}/{ch}"):
        #     os.mkdir(f"{args.era}_plots_{postfix}_{args.tag}/{ch}")
        for v in variables:
            infolist.append({"args" : args, "channel" : ch, "variable" : v})
    # with Pool(3) as pool:
    #     pool.map(main, infolist)
    for i in range(len(infolist)):
        main(infolist[i])
