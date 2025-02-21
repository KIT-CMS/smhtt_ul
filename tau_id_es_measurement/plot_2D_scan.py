import ROOT
from scipy.interpolate import griddata
import numpy as np

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--name',type=str, help='Name of the file')
parser.add_argument('--in-path',type=str, help='Input path to the 2D scan file') 
parser.add_argument('--tau-id-poi',type=str, help='Name of the tau ID POI')
parser.add_argument('--tau-es-poi',type=str, help='Name of the tau ES POI')
parser.add_argument('--outname',type=str, help='Name of the outputfile')
args = parser.parse_args()
title = args.outname
if "DM" in title:
    title_map = {"DM0":"DM 0", "DM1":"DM 1", "DM10_11":"DM 10+11"}
    title_name = title_map[title]
else:
    title_name = title

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

file_name = args.in_path+"higgsCombine."+args.name+".MultiDimFit.mH120.root"
f = ROOT.TFile(file_name)
t = f.Get("limit")

# Number of points in interpolation
n_points = 400
x_range = [0.5, 1.5]
y_range = [-4.0, 4]

# Number of bins in plot
n_bins = 20

x, y, deltaNLL = [], [], []
for ev in t:
    x.append(getattr(ev, "r"))
    y.append(getattr(ev, args.tau_es_poi))
    deltaNLL.append(getattr(ev, "deltaNLL"))
# print(deltaNLL, len(deltaNLL), y, len(y), x, len(x)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Do interpolation
# # Convert to numpy arrays as required for interpolation
# dnll = np.asarray(deltaNLL)
# points = np.array([x, y]).transpose()
# Set up grid
# grid_x, grid_y = np.mgrid[x_range[0] : x_range[1] : n_points * 1j, y_range[0] : y_range[1] : n_points * 1j]
# grid_vals = griddata(points, dnll, (grid_x, grid_y), "cubic")

# Remove NANS
# grid_x = grid_x[grid_vals == grid_vals]
# grid_y = grid_y[grid_vals == grid_vals]
# grid_vals = grid_vals[grid_vals == grid_vals]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define Profile2D histogram
# h2D = ROOT.TProfile2D("h", "h", n_bins, x_range[0], x_range[1], n_bins, y_range[0], y_range[1], -10, 400, "h")
h2D = ROOT.TProfile2D("h", title_name, n_bins, x_range[0], x_range[1], n_bins, y_range[0], y_range[1])

# for i in range(len(grid_vals)):
for i in range(len(deltaNLL)):
    # Factor of 2 comes from 2*NLL
    # h2D.Fill(grid_x[i], grid_y[i], 2 * grid_vals[i])
    h2D.Fill(x[i], y[i], 2 * deltaNLL[i])

# Loop over bins: if content = 0 then set 999
# for ibin in range(1, h2D.GetNbinsX() + 1):
#     for jbin in range(1, h2D.GetNbinsY() + 1):
#         if h2D.GetBinContent(ibin, jbin) == 0:
#             xc = h2D.GetXaxis().GetBinCenter(ibin)
#             yc = h2D.GetYaxis().GetBinCenter(jbin)
#             h2D.Fill(xc, yc, 999)

# Calc Pearson correlation:
projX = h2D.ProjectionX("tauID SF")
projY = h2D.ProjectionY("TES shift")

meanX = projX.GetMean()
meanY = projY.GetMean()

# Calculate covariance
covariance = 0
nBinsX = projX.GetNbinsX()
nBinsY = projY.GetNbinsX()

for binX in range(1, nBinsX + 1):
    for binY in range(1, nBinsY + 1):
        valueX = projX.GetBinCenter(binX)
        valueY = projY.GetBinCenter(binY)
        covariance += (valueX - meanX) * (valueY - meanY)

covariance /= (nBinsX * nBinsY)  # Normalize by the total number of bins

# Calculate standard deviations
stdDevX = projX.GetRMS()
stdDevY = projY.GetRMS()

# => Correlation coefficient:
corr_xy = covariance / (stdDevX * stdDevY)
corr_xy_str = f"Corr.:{corr_xy:.2f}"

# Set up canvas
canv = ROOT.TCanvas("canv", "canv", 680, 600)
canv.SetTickx()
canv.SetTicky()
canv.SetLeftMargin(0.115)
canv.SetRightMargin(0.170)
canv.SetBottomMargin(0.115)
# Extract binwidth
xw = (x_range[1] - x_range[0]) / n_bins
yw = (y_range[1] - y_range[0]) / n_bins

# Set histogram properties
h2D.SetContour(999)
h2D.SetTitle(title_name)
h2D.GetXaxis().SetTitle("#tau ID SF ")
h2D.GetXaxis().SetTitleSize(0.05)
h2D.GetXaxis().SetTitleOffset(0.9)
h2D.GetXaxis().SetRangeUser(x_range[0], x_range[1] - xw)

h2D.GetYaxis().SetTitle("#tau ES shift %")
h2D.GetYaxis().SetTitleSize(0.05)
h2D.GetYaxis().SetTitleOffset(0.9)
h2D.GetYaxis().SetRangeUser(y_range[0], y_range[1] - yw)

h2D.GetZaxis().SetTitle("-2 #Delta ln L")
h2D.GetZaxis().SetTitleSize(0.05)
h2D.GetZaxis().SetTitleOffset(0.8)

# h2D.SetMaximum(400)
ROOT.gStyle.SetPalette(ROOT.kCool)
# Make confidence interval contours
c68, c95 = h2D.Clone(), h2D.Clone()
c68.SetContour(2)
c68.SetContourLevel(1, 2.3)
c68.SetLineWidth(3)
c68.SetLineColor(ROOT.kBlack)
# c68.SetLineColor(ROOT.kRed)
c95.SetContour(2)
c95.SetContourLevel(1, 5.99)
c95.SetLineWidth(3)
c95.SetLineStyle(2)
c95.SetLineColor(ROOT.kBlack)

# Draw histogram and contours
h2D.Draw("COLZ")
# h2D.Draw("SURF2")

# Draw lines for SM point
vline = ROOT.TLine(1, y_range[0], 1, y_range[1] - yw)
vline.SetLineColorAlpha(ROOT.kRed, 0.7)
vline.Draw("Same")
hline = ROOT.TLine(x_range[0], 0, x_range[1] - xw, 0)
hline.SetLineColorAlpha(ROOT.kRed, 0.7)
hline.Draw("Same")

# Draw contours
c68.Draw("cont3same")
# c68.Draw()
c95.Draw("cont3same")

# Make best fit and sm points
gBF = ROOT.TGraph()
gBF.SetPoint(0, grid_x[np.argmin(grid_vals)], grid_y[np.argmin(grid_vals)])
gBF.SetMarkerStyle(34)
gBF.SetMarkerSize(2)
gBF.SetMarkerColor(ROOT.kBlack)
gBF.Draw("P")

# gSM = ROOT.TGraph()
# gSM.SetPoint(0, 1, 1)
# gSM.SetMarkerStyle(33)
# gSM.SetMarkerSize(2)
# gSM.SetMarkerColor(ROOT.kRed)
# gSM.Draw("P")


# Add legend
leg = ROOT.TLegend(0.6, 0.67, 0.8, 0.87)
leg.SetTextSize(0.04)
leg.SetBorderSize(0)
leg.SetFillColor(0)
leg.AddEntry(gBF, "Best fit", "P")
leg.AddEntry(c68, "1#sigma CL", "L")
leg.AddEntry(c95, "2#sigma CL", "L")
leg.AddEntry(h2D, corr_xy_str, "")

# leg.AddEntry(gSM, "SM", "P")
leg.Draw()

# canv.SetLogz()
canv.Update()
canv.SaveAs("scan_2D_"+args.outname+"_id_es_tests.png")
# canv.SaveAs("scan_2D_"+args.outname+"_id_es.pdf")


# Plot the 1D projections:
proj_X = h2D.ProjectionX("tauID SF")
proj_Y = h2D.ProjectionY("TES shift")

# Create a single canvas
c1 = ROOT.TCanvas("c1", "Projections", 800, 600)
c1.SetTitle(title_name)
# Divide the canvas into 1 row and 2 columns (2 pads)
c1.Divide(2, 1)

# Draw the X projection on the first pad
c1.cd(1)  # Go to the first pad
proj_X.Draw()

# Draw the Y projection on the second pad
c1.cd(2)  # Go to the second pad
proj_Y.Draw()

# Update and display the canvas
c1.Update()
c1.SaveAs("1D_projections_2Dscan_"+args.outname+"_id_es_tests.png")

