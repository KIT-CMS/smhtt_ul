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
import math

logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Plot categories using Dumbledraw from shapes produced by shape-producer module."
    )
    parser.add_argument(
        "-l", "--linear", action="store_true", help="Enable linear x-axis"
    )
    parser.add_argument(
        "-c", "--channel", type=str, required=True, help="Channels"
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
    parser.add_argument(
        "--binning-tag",
        type=str,
        default="default",
        help="Binning the shapes are based on.",
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
    # if args.gof_variable is not None:
    #     channel_categories = {
    #         "et": ["300"],
    #         "mt": ["300"],
    #         "tt": ["300"],
    #         "em": ["300"],
    #     }
    # else:
    #     channel_categories = {
    #         "mt": ["1", "2", "3", "4", "5", "6", "7"],
    #     }

        # signalcats = []
        # for channel in ["mt"]:
        #     channel_categories[channel] += signalcats
    
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
        "9": "DM1011",
        "10": "DM10",
        "11": "DM11",
        "12": "DM0_PT20_40",
        "13": "DM1_PT20_40",
        "14": "DM1011_PT20_40",
        "15": "DM10_PT20_40",
        "16": "DM11_PT20_40",
        "17": "DM0_PT40_200",
        "18": "DM1_PT40_200",
        "19": "DM1011_PT40_200",
        "20": "DM10_PT40_200",
        "21": "DM11_PT40_200",
        "100": "Control Region"
    }
    category_dict_for_plot = {
        "7": "DM 0",
        "8": "DM 1",
        "9": "DM 10+11",
        "10": "DM 10",
        "11": "DM 11",
        "12": "DM 0 (PT20 to 40)",
        "13": "DM 1 (PT20 to 40)",
        "14": "DM 10+11 (PT20 to 40)",
        "15": "DM 10 (PT20 to 40)",
        "16": "DM 11 (PT20 to 40)",
        "17": "DM 0 (PT40 to 200)",
        "18": "DM 1 (PT40 to 200)",
        "19": "DM 10+11 (PT40 to 200)",
        "20": "DM 10 (PT40 to 200)",
        "21": "DM 11 (PT40 to 200)",
        "100": "Control Region"
    }
    inv_category_dict = {v: k for k, v in category_dict.items()}
    
    if args.linear:
        split_value = 0
    else:
        if args.normalize_by_bin_width:
            split_value = 10001
        else:
            split_value = 101

    split_dict = {c: split_value for c in ["et", "mt", "tt", "em", "mm"]}

    AN_dict ={
    "jetFData": ["QCD"],
    "jetFMC": ["VVJ", "TTJ", "ZJ", "W"],
    "lepF": ["VVL", "TTL", "ZL"]
    }
    
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

    if "2016" in args.era:
        if "pre" in args.era:
            era = "Run2016preVFP"
        elif "post" in args.era:
            era = "Run2016postVFP"
        else:
            era = "Run2016"
    elif "2017" in args.era:
        era = "Run2017"
    elif "2018" in args.era:
        era = "Run2018"
    else:
        logger.critical("Era {} is not implemented.".format(args.era))
        raise Exception
    # logger.debug("Channel Categories: {}".format(channel_categories))
    plots = []
    channel = args.channel
    if args.single_category in category_dict.values():
        logger.debug(f"channel {channel}")
        logger.warning("Selected category: {}".format(args.single_category))
        logger.warning("Available categories: {}".format(category_dict))            
        
        catname = args.single_category
        categories = inv_category_dict[catname]
    else:
        raise NameError("Wrong category name!\
                        \n Also multi category NOT possible atm. Only single categories are expected!")
        # categories = channel_categories[channel]
    logger.warning(f"Categories: {categories}")
    if not isinstance(categories, list):
        categories = [categories]
    binning_tag = args.binning_tag
    for category in categories:
        if channel != "mm":
            rootfile = rootfile_parser.Rootfile_parser(args.input, prefit=args.prefit, tag=binning_tag)
        else:
            rootfile = rootfile_parser.Rootfile_parser(args.input, mode="CombineHarvester", prefit=args.prefit, tag="mm")
        if channel == "em":
            if args.embedding:
                bkg_processes = ["VVL", "W", "TTL", "ZL", "QCD", "EMB"]
            else:
                bkg_processes = ["VVL", "W", "TTL", "ZL", "QCD", "ZTT"]
        elif channel == "mm":
            bkg_processes = ["W", "QCD", "MUEMB"]
        else:
            bkg_processes = ["QCD", "VVJ", "VVL", "W", "TTJ", "TTL", "ZJ", "ZL", f"EMB_{category_dict[category]}"]
        legend_bkg_processes = copy.deepcopy(bkg_processes)
        legend_bkg_processes.reverse()
        # create plot
        width = 800
        if args.linear:
            plot = dd.Plot([0.3, [0.3, 0.28]], "ModTDR", r=0.04, l=0.18, width=width)
        else:
            plot = dd.Plot([0.5, [0.3, 0.28]], "ModTDR", r=0.04, l=0.18, width=width)

        # get background histograms
        for process in bkg_processes:
            plot.add_hist(
                rootfile.get(era, channel, category, process), process, "bkg"
            )
            if "EMB_" not in process:
                if process in AN_dict["jetFData"]:
                    plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict["QCD"])

                elif process in AN_dict["jetFMC"]:
                    plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict["jetFakesQCD"])
                elif process in AN_dict["lepF"]:
                    plot.setGraphStyle(
                    process, "hist", fillcolor=styles.color_dict["ZL"])
                else:
                    plot.setGraphStyle(
                        process, "hist", fillcolor=styles.color_dict[process]
                    )
            else:
                if "EMB_" in process:
                    if channel == "mm":
                        plot.setGraphStyle(
                            process, "hist", fillcolor=styles.color_dict["MUEMB"]
                        )
                    else:
                        plot.setGraphStyle(
                            process, "hist", fillcolor=styles.color_dict["EMB"]
                        )
                
                else:
                    print(f""" \n Something went wrong in creating hist and style for process: {process} \n""")
                    
                    pass

        
        data_obs = rootfile.get(era, channel, category, "data_obs")
        plot.add_hist(data_obs, "data_obs")
        # Total bkg and sig have different naming in COMBINE!!! Other name is total_background or total_signal !!!
        # Check that if Ratio plot is not working!
        total_bkg = rootfile.get(era, channel, category, "TotalBkg")
        plot.add_hist(total_bkg, "total_bkg")
        if channel != "mm":
            total_sig = rootfile.get(era, channel, category, "TotalSig") 
            plot.add_hist(total_sig, "total_sig")
        # breakpoint()
        model_total = plot.subplot(2).get_hist("total_bkg")
        if channel != "mm":
            model_total.Add(plot.subplot(2).get_hist("total_sig"))
        plot.add_hist(model_total, "model_total")
        plot.subplot(0).setGraphStyle("data_obs", "e0")
        
        
        # print("total_bkg bins:", [plot.subplot(2).get_hist("total_bkg").GetBinContent(i) for i in range(1, model_total.GetNbinsX()+1)])
        # if channel != "mm":
            # print("total_sig bins:", [plot.subplot(2).get_hist("total_sig").GetBinContent(i) for i in range(1, model_total.GetNbinsX()+1)])
        
        try:
            n_bins = model_total.GetNbinsX()
            errors = [model_total.GetBinError(i) for i in range(1, n_bins + 1)]
            if any([math.isnan(i) for i in errors]):
                print("\n NAN in uncertainties!!! \n")
                raise ValueError("Postfit uncertainties contain NaN values.")
            plot.setGraphStyle(
            "model_total",
            "e2",
            markersize=0,
            fillcolor=styles.color_dict["unc"],
            linecolor=0,
        )
        except:
            print("\n EXCEPT \n")
            logger.warning("Postfit uncertainties appear to be faulty; skipping error band plotting.")
            plot.setGraphStyle("model_total", "hist")
        
        # print("model_total bins:", [model_total.GetBinContent(i) for i in range(1, model_total.GetNbinsX()+1)])
        # print("data_obs bins:", [data_obs.GetBinContent(i) for i in range(1, data_obs.GetNbinsX()+1)])
        
        plot.subplot(2).normalize(
            [
                "model_total",
                "data_obs",
            ],
            "model_total",
        )
        # plot.subplot(2).get_hist("data_obs").Integral()
        # stack background processes
        plot.create_stack(bkg_processes, "stack")
        # ratio_hist = plot.subplot(2).get_hist("data_obs")
        # print("ratio bins:", [ratio_hist.GetBinContent(i) for i in range(1, ratio_hist.GetNbinsX()+1)])
        # print("ratio errors:", [ratio_hist.GetBinError(i) for i in range(1, ratio_hist.GetNbinsX()+1)])

        # normalize stacks by bin-width
        # breakpoint()
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

        plot.subplot(2).setYlims(0.79, 1.41) # Larger limits for DM10_11 ???

        if not args.linear:
            plot.subplot(1).setYlims(0.1, split_dict[channel])
            plot.subplot(1).setLogY()
            plot.subplot(1).setYlabel(
                ""
            )  # otherwise number labels are not drawn on axis
        if args.normalize_by_bin_width:
            plot.subplot(0).setYlabel("#frac{d N_{events}}{d m_{vis}} #left[GeV^{-1}#right]")
        else:
            plot.subplot(0).setYlabel("N_{events}")
            # plot.subplot(0).setYlabel("#frac{d N_{events}}{d m_{vis}} #left[GeV^{-1}#right]")
        plot.subplot(2).setXlabel("m_{vis} [GeV]")
        plot.subplot(2).setYlabel("")
        plot.subplot(2).setGrid()
        # plot.scaleXLabelSize(0.8)
        # plot.scaleYTitleSize(0.8)
        plot.scaleYLabelSize(0.7)
        plot.scaleYTitleOffset(0.8)
        # plot.scaleXLabelOffset(2.0)
        plot.subplot(2).setNYdivisions(3, 5) # what does it do ???
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
            jetFData = False
            jetFMC = False
            lepF = False
            emb = False
            plot.add_legend(width=0.6, height=0.15)
            for process in legend_bkg_processes:
                if channel == "mm":
                    plot.legend(i).add_entry(
                        0,
                        process,
                        styles.legend_label_dict[
                            process.replace("TTL", "TT").replace("VVL", "VV")
                        ],
                        "f",
                    )
                elif "EMB_" in process:
                    if not emb:
                        plot.legend(i).add_entry(
                            0, process, f"#tau embedded", 'f')
                        emb = True
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
                    else:
                        if process in AN_dict["lepF"] + AN_dict["jetFMC"] + AN_dict["jetFData"]:
                            continue
                        else:
                            print(f"Legend entry for process:{process} had a problem.")
                            breakpoint()
            # if channel != "mm":
            #     plot.legend(i).add_entry(0, legend_bkg_processes[0], f"#tau embedded" , "f")
            # plot.legend(i).add_entry(0, "total_bkg", "Bkg. unc.", "f")
            plot.legend(i).add_entry(0, "model_total", "Bkg. unc.", "f")
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

        # for i in range(2):
        #     plot.add_legend(reference_subplot=2, pos=1, width=0.5, height=0.03)
        #     plot.legend(i + 2).add_entry(0, "data_obs", "Data", "PE")
        #     plot.legend(i + 2).add_entry(0, "total_bkg", "Bkg. unc.", "f")
        #     plot.legend(i + 2).setNColumns(4)
        # plot.legend(2).Draw()
        # plot.legend(3).setAlpha(0.0)
        # plot.legend(3).Draw()

        # draw additional labels
        # plot.DrawCMS(position="outside")
        if "2016postVFP" in args.era:
            plot.DrawLumi("16.8 fb^{-1} (2016UL postVFP, 13 TeV)")
        elif "2016preVFP" in args.era:
            plot.DrawLumi("19.5 fb^{-1} (2016UL preVFP, 13 TeV)")
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
        #### This drew inside the plot, bad for reading. Could be used for other stuff.
        # plot.DrawChannelCategoryLabel(
        #     "%s, %s" % (channel_dict[channel], category_dict[category]),
        #     begin_left=None,
        #     textsize=0.032,
        #     print_inside=True,
        #     legend_outside=False,
        # )
        posChannelCategoryLabelLeft = None
        plot.DrawChannelCategoryLabel(
            "%s, %s" % (channel_dict[channel], category_dict_for_plot[category]),
            begin_left=posChannelCategoryLabelLeft)

        # save plot
        postfix = "prefit" if args.prefit else "postfit"
        # plot.save(
        #     "%s/%s_%s_%s_%s.%s"
        #     % (
        #         args.outputfolder,
        #         args.era,
        #         channel,
        #         args.gof_variable if args.gof_variable is not None else category,
        #         postfix,
        #         "png",
        #     )
        # )
        s_or_b = ""
        if args.input.endswith("-b.root"):
            s_or_b = "_b"
        plot.save(
            "%s/%s_%s_%s_%s%s.%s"
            % (
                args.outputfolder,
                args.era,
                channel,
                args.gof_variable if args.gof_variable is not None else category,
                postfix,
                s_or_b,
                "pdf",
            )
        )
        # plot.save(f"output/{postfix}_{channel}_{category}.png")
        # work around to have clean up seg faults only at the end of the
        # script
        plots.append(plot)


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_plot_shapes.log".format(args.era), logging.DEBUG)
    main(args)
