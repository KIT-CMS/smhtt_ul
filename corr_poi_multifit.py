#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
import numpy as np
from array import array
import matplotlib.pyplot as plt
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gStyle.SetPaintTextFormat(".2f")
import sys

ROOT.gROOT.SetBatch()



def SetTDRStyle():
    """Sets the PubComm recommended style
    Just a copy of <http://ghm.web.cern.ch/ghm/plots/MacroExample/tdrstyle.C>
    @sa ModTDRStyle() to use this style with some additional customisation.
    """
    # For the canvas:
    ROOT.gStyle.SetCanvasBorderMode(0)
    ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
    ROOT.gStyle.SetCanvasDefH(600)  # Height of canvas
    ROOT.gStyle.SetCanvasDefW(600)  # Width of canvas
    ROOT.gStyle.SetCanvasDefX(0)    # POsition on screen
    ROOT.gStyle.SetCanvasDefY(0)

    # For the Pad:
    ROOT.gStyle.SetPadBorderMode(0)
    ROOT.gStyle.SetPadColor(ROOT.kWhite)
    ROOT.gStyle.SetPadGridX(False)
    ROOT.gStyle.SetPadGridY(False)
    ROOT.gStyle.SetGridColor(0)
    ROOT.gStyle.SetGridStyle(3)
    ROOT.gStyle.SetGridWidth(1)

    # For the frame:
    ROOT.gStyle.SetFrameBorderMode(0)
    ROOT.gStyle.SetFrameBorderSize(1)
    ROOT.gStyle.SetFrameFillColor(0)
    ROOT.gStyle.SetFrameFillStyle(0)
    ROOT.gStyle.SetFrameLineColor(1)
    ROOT.gStyle.SetFrameLineStyle(1)
    ROOT.gStyle.SetFrameLineWidth(1)

    # For the histo:

    ROOT.gStyle.SetHistLineColor(1)
    ROOT.gStyle.SetHistLineStyle(0)
    ROOT.gStyle.SetHistLineWidth(1)


    ROOT.gStyle.SetEndErrorSize(2)


    ROOT.gStyle.SetMarkerStyle(20)

    # For the fit/function:
    ROOT.gStyle.SetOptFit(1)
    ROOT.gStyle.SetFitFormat('5.4g')
    ROOT.gStyle.SetFuncColor(2)
    ROOT.gStyle.SetFuncStyle(1)
    ROOT.gStyle.SetFuncWidth(1)

    # For the date:
    ROOT.gStyle.SetOptDate(0)


    # For the statistics box:
    ROOT.gStyle.SetOptFile(0)
    ROOT.gStyle.SetOptStat(0)
    # To display the mean and RMS:   SetOptStat('mr')
    ROOT.gStyle.SetStatColor(ROOT.kWhite)
    ROOT.gStyle.SetStatFont(42)
    ROOT.gStyle.SetStatFontSize(0.025)
    ROOT.gStyle.SetStatTextColor(1)
    ROOT.gStyle.SetStatFormat('6.4g')
    ROOT.gStyle.SetStatBorderSize(1)
    ROOT.gStyle.SetStatH(0.1)
    ROOT.gStyle.SetStatW(0.15)


    # Margins:
    ROOT.gStyle.SetPadTopMargin(0.06)
    ROOT.gStyle.SetPadBottomMargin(0.20)
    ROOT.gStyle.SetPadLeftMargin(0.30)
    ROOT.gStyle.SetPadRightMargin(0.11)

    # For the Global title:
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleColor(1)
    ROOT.gStyle.SetTitleTextColor(1)
    ROOT.gStyle.SetTitleFillColor(10)
    ROOT.gStyle.SetTitleFontSize(0.05)


    # For the axis titles:
    ROOT.gStyle.SetTitleColor(1, 'XYZ')
    ROOT.gStyle.SetTitleFont(42, 'XYZ')
    ROOT.gStyle.SetTitleSize(0.06, 'XYZ')
    # Another way to set the size?

    ROOT.gStyle.SetTitleXOffset(0.9)
    ROOT.gStyle.SetTitleYOffset(1.25)
    # ROOT.gStyle.SetTitleOffset(1.1, 'Y'); # Another way to set the Offset

    # For the axis labels:

    ROOT.gStyle.SetLabelColor(1, 'XYZ')
    ROOT.gStyle.SetLabelFont(42, 'XYZ')
    ROOT.gStyle.SetLabelOffset(0.007, 'XYZ')
    ROOT.gStyle.SetLabelSize(0.025, 'XYZ')

    # For the axis:

    ROOT.gStyle.SetAxisColor(1, 'XYZ')
    ROOT.gStyle.SetStripDecimals(True)
    ROOT.gStyle.SetTickLength(0.03, 'XYZ')
    ROOT.gStyle.SetNdivisions(510, 'XYZ')
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)

    # Change for log plots:
    ROOT.gStyle.SetOptLogx(0)
    ROOT.gStyle.SetOptLogy(0)
    ROOT.gStyle.SetOptLogz(0)

    # Postscript options:
    ROOT.gStyle.SetPaperSize(20., 20.)

    ROOT.gStyle.SetHatchesLineWidth(5)
    ROOT.gStyle.SetHatchesSpacing(0.05)

def SetCorrMatrixPalette():
    ROOT.TColor.CreateGradientColorTable(3,
                                      array("d",[0.00, 0.50, 1.00]),
                                      array("d",[0.00, 1.00, 1.00]),
                                      array("d",[0.00, 1.00, 0.00]),
                                      array("d",[1.00, 1.00, 0.00]),
                                      10000,  1.0)

if __name__ == "__main__":
    SetTDRStyle()
    SetCorrMatrixPalette()
    #print cp
    #ROOT.gStyle.SetPalette(cp) #kBlueGreenYellow kCoffee
    #ROOT.TColor.InvertPalette()
    label_dict = {
        "r_EMB_Pt20to25" : "EMB_Pt20to25", 
        "r_EMB_Pt25to30" : "EMB_Pt25to30", 
        "r_EMB_Pt30to35" : "EMB_Pt30to35", 
        "r_EMB_Pt35to40" : "EMB_Pt35to40", 
        "r_EMB_PtGt40"   : "EMB_PtGt40",
    }
    label_list = [
         "EMB_Pt20to25",
         "EMB_Pt25to30",
         "EMB_Pt30to35",
         "EMB_Pt35to40",
         "EMB_PtGt40",
    ]

    era = sys.argv[1]
    print("[INFO] Plot for era {}.".format(era))

    filename = sys.argv[2]
    print("[INFO] Plot POI correlations from file {}.".format(filename))
    f = ROOT.TFile(filename)
    if f == None:
        raise Exception("[ERROR] File {} not found.".format(filename))

    result = f.Get("fit_s")
    if result == None:
        raise Exception("[ERROR] Failed to load fit_s from file {}.".format(filename))

    params = result.floatParsInit()
    pois = []
    for i in range(params.getSize()):
        name = params[i].GetName()
        if name.startswith("r"):
            pois.append(name)
    print("[INFO] Identified POIs with names {}.".format(pois))


    num_pois = len(pois)
    m = ROOT.TH2D("h", "h", num_pois, 0, num_pois, num_pois, 0, num_pois)
    for i in range(num_pois):
        for j in range(num_pois):
            val = result.correlation(params.find(pois[i]), params.find(pois[j]))
            m.SetBinContent(i+1, j+1, val)

    m.SetTitle("")
    for i in range(num_pois):
        m.GetXaxis().SetBinLabel(i+1, "")
        m.GetYaxis().SetBinLabel(i+1, label_dict[pois[i]])
    m.GetXaxis().LabelsOption("v")
    m.SetMinimum(-1)
    m.SetMaximum(1)

    c = ROOT.TCanvas("c", "c", 600, 600)
    c.SetGrid(1)
    m.SetContour(10000)
    m.Draw("colz text")

    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetLineWidth(2)
    tex.SetTextAlign(11)
    tex.SetTextFont(43)
    tex.SetTextSize(25)
    tex.SetTextFont(43)
    tex.DrawLatex(0.30, 0.955, "CMS")
    tex.DrawLatex(0.65, 0.955, "59.8 fb^{-1} (13 TeV)")
    tex.SetTextFont(53)
    tex.DrawLatex(0.40, 0.955, "Internal")
    for i in range(num_pois):
        texlabel = ROOT.TLatex()
        texlabel.SetTextAngle(30)
        texlabel.SetTextFont(42)
        texlabel.SetTextAlign(32)
        texlabel.SetTextSize(0.02)
        texlabel.DrawLatex(i+0.6,-0.19,label_dict[pois[i]])


    lineh = ROOT.TLine(0.0,7.0,13.0,7.0)
    lineh.SetLineWidth(2)
    lineh.Draw()
    linev = ROOT.TLine(7.0,0.0,7.0,13.0)
    linev.SetLineWidth(2)
    linev.Draw()

    c.Update()

    # c.SaveAs("{}_plot_poi_correlation_stage-0.pdf".format(era))
    c.SaveAs("{}_plot_poi_correlation_Medium_Vs_Jet_Medium_Vs_Ele.png".format(era))
