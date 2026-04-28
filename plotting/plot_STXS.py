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
DIR_PLOTS = '/web/sgiappic/public_html/CMS_HTT/Run2022preEE/STXS/' 
LOGY = False

#now you can list all the histograms that you want to plot
VARIABLES_LIST = [
  "HTXS_stage1_2_cat_pTjet25GeV",
  "HTXS_stage1_2_cat_pTjet30GeV",
  "HTXS_stage1_2_fine_cat_pTjet25GeV",
  "HTXS_stage1_2_fine_cat_pTjet30GeV",
]

era = [
    "2022preEE",
    #"2022postEE",
    #"2023preBPix",
    #"2023postBPix",
    #"2024",
    #"2025",
]

tag = [
    "STXS_ggH",
    "STXS_vbf"
]

channel = [
    "et",
    "mt",
    "tt",
]

scolors = {
    "2022preEE":ROOT.kAzure+6,
    "2022postEE":ROOT.kAzure-8,
    "2023preBPix":ROOT.kTeal-8,
    "2023postBPix":ROOT.kTeal-6,
    "2024CDE":ROOT.kViolet-9,
    "2024FGHI":ROOT.kBlue-9,
    "2025":ROOT.kPink+1,
    "STXS_ggH":ROOT.kAzure-5,
    "STXS_vbf":ROOT.kOrange+7,
}

slegend = {
    "2022preEE":"2022preEE data",
    "2022postEE":"2022postEE data",
    "2023preBPix":"2023preBPix data",
    "2023postBPix":"2023postBPix data",
    "2024CDE":"2024CDE data",
    "2024FGHI":"2024FGHI data",
    "2025":"2025 data",
}

LOGY = True

for ch in channel:
    for s in era:
        for t in tag:
            for variable in VARIABLES_LIST:

                canvas = ROOT.TCanvas("", "", 1200, 800)

                nsig = len(era) 

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
            
                if s=="2024":
                    fin_ll = f"{DIRECTORY}/{s}-{ch}-htt_260116_2024-25-260116_{t}/control_shapes-{s}-{ch}-htt_260116_2024-25-260116_{t}.root"
                    tf_ll = ROOT.TFile.Open(fin_ll, 'READ')
                    h = tf_ll.Get(f"data#{ch}#Nominal#{variable}")
                    hh = copy.deepcopy(h)
                    hh.SetDirectory(0)
                    if hh.Integral()>0:
                        hh.Scale(35.96)
                    histos.append(hh)
                    colors.append(scolors[s+t])
                    leg.AddEntry(histos[-1], slegend[s+t], "l")
                else:
                    ntuple_tag = "htt_260116_2022-23_v2"
                    histo_tag = t
                    if s=="2025":
                        ntuple_tag = "htt_260116_2024-25"
                        histo_tag = "260116_CDEF"
                    fin_ll = f"{DIRECTORY}/{s}-{ch}-{ntuple_tag}-{histo_tag}/control_shapes-{s}-{ch}-{ntuple_tag}-{histo_tag}.root"
                    print(fin_ll)
                    tf_ll = ROOT.TFile.Open(fin_ll, 'READ')
                    sample = "ggH" if "ggH" in t else "qqH"
                    print(f"{sample}#{ch}-{sample}125#Nominal#{variable}")
                    h = tf_ll.Get(f"{sample}#{ch}-{sample}125#Nominal#{variable}")
                    hh = copy.deepcopy(h)
                    hh.SetDirectory(0)
                    if hh.Integral()>0:
                        #hh.Scale(8052912 / (3.26 * 7.86e3)) if "ggH" in t else hh.Scale(5088809 * (0.25 * 7.86e3))
                        hh.Scale(35.96)
                    histos.append(hh)
                    colors.append(scolors[t])
                    #leg.AddEntry(histos[-1], slegend[s], "l")

                nsig = len(histos)
                    
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
                    h.Sumw2()
                    h.SetMarkerStyle(20)
                    h.SetMarkerColor(colors[i])
                    if i == 0:
                        h.Draw("E")
                        h.GetYaxis().SetTitle("ggH Yields" if "ggH" in t else "VBF Yields")
                        h.GetYaxis().SetTitleSize(0.05)
                        h.GetYaxis().SetLabelSize(0.048)
                        h.GetYaxis().SetTitleOffset(1.2)
                        h.GetXaxis().SetTitle(variable)
                        
                        #h.GetXaxis().SetTitleOffset(1.2)
                        if LOGY==True :
                            if "ggH" in t:
                                h.SetMinimum(1e-1)
                                h.SetMaximum(1e5)
                            else:
                                h.SetMinimum(1e-1)
                                h.SetMaximum(1e5)
                        else:
                            h.GetYaxis().SetRangeUser(0, max*2)
                        h.SetTitle("")
                        h.SetStats(0)
                    else: 
                        h.Draw("E SAME")
                
                # Draw leftText on the main canvas before saving
                #leg.Draw()

                #labels around the plot
                rightText = f'#sqrt{{s}} = 13.6 TeV, L = 286.97 fb^{{-1}}'

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

                # Set Logarithmic scales for both x and y axes
                if LOGY == True:
                    canvas.SetLogy()

                canvas.SetTicks(1, 1)
                canvas.SetLeftMargin(0.14)
                canvas.SetRightMargin(0.08)
                canvas.GetFrame().SetBorderSize(12)
                canvas.SetGridx(0)            
                canvas.SetGridy(1)

                canvas.RedrawAxis()
                canvas.Modified()
                canvas.Update()

                dir = DIR_PLOTS + ch +  "/" 
                make_dir_if_not_exists(dir)

                if (LOGY == True):
                    canvas.SaveAs(dir + variable + "_" + t + "_log.png")
                    canvas.SaveAs(dir + variable + "_" + t + "_log.pdf")
                else:
                    canvas.SaveAs(dir + variable + "_" + t + ".png")
                    canvas.SaveAs(dir + variable + "_" + t + ".pdf")