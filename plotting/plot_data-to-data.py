#code adapted from FCCAnalyses/do_plots.py

import sys
import os
import os.path
import ntpath
import importlib
import copy
import re
import logging
import ROOT

# Set ROOT to batch mode so it doesn't open all the plots
ROOT.gROOT.SetBatch(True)

def sorted_dict_values(dic: dict) -> list:
    ''''
    Sort values in the dictionary.
    '''
    keys = sorted(dic)
    return [dic[key] for key in keys]

def make_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.system("cp /web/sgiappic/public_html/index.php {}".format(directory)) #copy index to show plots in web page automatically
        print(f"Directory created successfully.")
    else:
        print(f"Directory already exists.")

def file_exists(file_path):
    return os.path.isfile(file_path)

# directory with final stage files
DIRECTORY = "/work/sgiappic/smhtt_ul/output/"

#directory where you want your plots to go
DIR_PLOTS = '/web/sgiappic/public_html/CMS_HTT/Run2024/data-to-data/' 
LOGY = False

#now you can list all the histograms that you want to plot
VARIABLES_LIST = [
    "pt_1", "eta_1", "phi_1", "tau_decaymode_1", "mt_1", "iso_1", "mass_1",
    "pt_2", "eta_2", "phi_2", "tau_decaymode_2", "mt_2", "iso_2", "mass_2",
    "jpt_1", "jeta_1", "jphi_1",
    "jpt_2", "jeta_2", "jphi_2",
    "bpt_1", "beta_1", "bphi_1", "btag_value_1",
    "bpt_2", "beta_2", "bphi_2", "btag_value_2",
    "pt_tt", "pt_tt", "pt_vis", "pt_dijet", "pt_ttjj",
    "mjj", "mt_tot", "m_vis",
    "met", "metphi", "mTdileptonMET", "metSumEt",
    "nbtag", "njets",
    "q_1", "pzetamissvis", "jet_hemisphere",
    "deltaR_ditaupair",
]

era = [
    "2024",
    "2025"
]

tag = [
    "CDE",
    "FGHI",
]

channel = [
    "et",
    "mt",
    "tt",
]

scolors = {
    "2024CDE":ROOT.kViolet-9,
    "2024FGHI":ROOT.kAzure+6,
    "2025":ROOT.kTeal+5,
}

slegend = {
    "2024CDE":"2024CDE data",
    "2024FGHI":"2024FGHI data",
    "2025":"2025 data",
}

for ch in channel:
    for variable in VARIABLES_LIST:

        canvas = ROOT.TCanvas("", "", 800, 800)
        canvas.SetLeftMargin(0.14)
        canvas.SetRightMargin(0.08)
        canvas.GetFrame().SetBorderSize(12)

        pad = ROOT.TPad("", "", 0.0, 0.3, 1.0, 1.0)
        
        pad2 = ROOT.TPad("", "", 0.0, 0.0, 1.0, 0.35)

        pad.Draw()
        pad2.Draw()
        canvas.cd()
        pad.cd()

        nsig = 3

        #legend coordinates and style
        legsize = 0.04*nsig
        leg = ROOT.TLegend(0.65, 0.86 - legsize, 0.90, 0.86)
        leg.SetFillColor(0)
        leg.SetFillStyle(0)
        leg.SetLineColor(0)
        leg.SetShadowColor(0)
        leg.SetTextSize(0.025)
        leg.SetTextFont(42)

        #global arrays for histos and colors
        histos = []
        colors = []
        legend = []

        #loop over files for signals and backgrounds and assign corresponding colors and titles
        for s in era:
            if s=="2024":
                for t in tag:
                    fin_ll = f"{DIRECTORY}/{s}-{ch}-htt_251211_2024-25_v2-251211_{t}/control_shapes-{s}-{ch}-htt_251211_2024-25_v2-251211_{t}.root"
                    tf_ll = ROOT.TFile.Open(fin_ll, 'READ')
                    h = tf_ll.Get(f"data#{ch}#Nominal#{variable}")
                    hh = copy.deepcopy(h)
                    hh.SetDirectory(0)
                    if hh.Integral()>0:
                        hh.Scale(1./(hh.Integral()))
                    histos.append(hh)
                    colors.append(scolors[s+t])
                    leg.AddEntry(histos[-1], slegend[s+t], "l")
            else:
                fin_ll = f"{DIRECTORY}/{s}-{ch}-htt_251211_2024-25_v2-251211/control_shapes-{s}-{ch}-htt_251211_2024-25_v2-251211.root"
                tf_ll = ROOT.TFile.Open(fin_ll, 'READ')
                h = tf_ll.Get(f"data#{ch}#Nominal#{variable}")
                hh = copy.deepcopy(h)
                hh.SetDirectory(0)
                if hh.Integral()>0:
                    hh.Scale(1./(hh.Integral()))
                histos.append(hh)
                colors.append(scolors[s])
                leg.AddEntry(histos[-1], slegend[s], "l")
            
        # add the signal histograms
        for i in range(nsig):
            h = histos[i]
            max = 0 
            if h.GetMaximum() > max :
                max = h.GetMaximum() 
        for i in range(nsig):
            h = histos[i]
            h.SetLineWidth(3)
            h.SetLineColor(colors[i])
            #h.Rebin(2)
            if i == 0:
                h.Draw("HIST")
                h.GetYaxis().SetTitle("Normalised events")
                h.GetYaxis().SetTitleSize(0.05)
                h.GetYaxis().SetLabelSize(0.048)
                h.GetYaxis().SetTitleOffset(1.2)
                h.GetXaxis().SetTitle(variable)
                #h.GetXaxis().SetTitleOffset(1.2)
                h.GetYaxis().SetRangeUser(0, max*1.5)
                h.SetTitle("")
                h.SetStats(0)
            else: 
                h.Draw("HIST SAME")
        
        

        #leg.Draw()

        pad.SetLeftMargin(0.14)
        pad.SetRightMargin(0.08)
        pad.GetFrame().SetBorderSize(12)
        pad.SetBottomMargin(0)
        pad.SetTopMargin(0.148)
        pad.SetTicks(1, 1)

        canvas.cd()
        
        #### ratio plot ####
        pad2.cd()
 
        legend2size = 0.1*(nsig-1)
        legend2 = ROOT.TLegend(0.16, 0.90 - legend2size, 0.45, 0.90)
        legend2.SetFillColor(0)
        legend2.SetFillStyle(0)
        legend2.SetLineColor(0)
        legend2.SetShadowColor(0)
        legend2.SetTextSize(0.04)
        legend2.SetTextFont(42)

        #dummy plot
        #drawing error bar for SM sample centered at 1 (ratio with itself) but error from the full scale
        #dummy = histos[0].Clone("")
        #for i in range(dummy.GetNbinsX()):
        #    dummy.SetBinContent(i,1.0)
        dummy = histos[0].Clone("")
        dummy.Divide(histos[0])
        #for i in range(dummy.GetNbinsX()+1):
        #    dummy.SetBinContent(i,1.0)
        #    dummy.SetBinError(i, histos[0].GetBinError(i)/histos[0].GetBinContent(i))
        dummy.SetFillColor(ROOT.kGray)
        dummy.SetLineColor(0)
        #dummy.SetMarkerColor(0)
        dummy.SetLineWidth(0)
        #dummy.SetMarkerSize(0)

        dummy.GetYaxis().SetTitle("Ratio with 2024CDE")
        dummy.GetYaxis().SetTitleSize(0.093)
        dummy.GetYaxis().CenterTitle()
        #adjust the range for the ratio here
        dummy.GetYaxis().SetRangeUser(0.8,1.2)
        dummy.GetYaxis().SetLabelSize(0.095)
        dummy.GetYaxis().SetNdivisions(5)
        dummy.GetYaxis().SetTitleOffset(0.6)

        dummy.GetXaxis().SetTitle(variable)
        dummy.GetXaxis().SetTitleSize(0.1)
        dummy.GetXaxis().SetLabelSize(0.095)
        dummy.GetXaxis().SetTitleOffset(1.1)
        dummy.SetStats(0)
        dummy.Draw("e2")
            
        ratio_list = []
        for i in range(1,nsig):  
            ratio = histos[i].Clone("")
            ratio.Divide(histos[0])
            ratio.SetLineWidth(3)
            ratio.SetLineColor(colors[i])
            #print(f"{legend[i]}")
            ratio.Draw("hist same")
            ratio_list.append(ratio)
            #legend2.AddEntry(ratio, legend[i], "l")

        #legend2.Draw()
        pad2.SetLeftMargin(0.14)
        pad2.SetRightMargin(0.08)
        pad2.GetFrame().SetBorderSize(12)
        pad2.SetTopMargin(0.145)
        pad2.SetBottomMargin(0.28)
        pad2.SetFillColor(0)
        pad2.SetFillStyle(4000)
        #pad2.SetLogy()

        # Draw leftText on the main pad before saving
        canvas.cd()
        leg.Draw()

        #labels around the plot
        rightText = f'#sqrt{{s}} = 13.6 TeV'

        latex = ROOT.TLatex()
        latex.SetNDC()

        text = '#bf{#it{'+rightText+'}}'
        latex.SetTextSize(0.03)
        latex.DrawLatex(0.18, 0.84, text)

        text = '#bf{#it{' + ch + ' channel}}'
        latex.SetTextSize(0.03)
        latex.DrawLatex(0.18, 0.80, text)

        #text = '#bf{#it{' + extralab + '}}'
        #latex.SetTextSize(0.02)
        #latex.DrawLatex(0.18, 0.76, text)

        latex.SetTextAlign(31)
        latex.SetTextSize(0.03)
        latex.DrawLatex(0.92, 0.92, 'CMS'+'#bf{ Own work}')

        canvas.RedrawAxis()
        canvas.Modified()
        canvas.Update()

        dir = DIR_PLOTS + ch +  "/"
        make_dir_if_not_exists(dir)

        if (LOGY == True):
            canvas.SaveAs(dir + "log/" + variable + cut + ".png")
            canvas.SaveAs(dir + "log/" + variable + cut + ".pdf")
        else:
            canvas.SaveAs(dir + variable + ".png")
            canvas.SaveAs(dir + variable  + ".pdf")