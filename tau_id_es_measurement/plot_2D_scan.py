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

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

file_name = args.in_path+"higgsCombine."+args.name+".MultiDimFit.mH120.root"
f = ROOT.TFile(file_name)
t = f.Get("limit")

# Number of points in interpolation
n_points = 400
x_range = [0.55, 1.5]
y_range = [-3.8, 4]

# Number of bins in plot
n_bins = 40

x, y, deltaNLL = [], [], []
for ev in t:
    x.append(getattr(ev, "r"))
    y.append(getattr(ev, args.tau_es_poi))
    deltaNLL.append(getattr(ev, "deltaNLL"))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Do interpolation
# Convert to numpy arrays as required for interpolation
dnll = np.asarray(deltaNLL)
points = np.array([x, y]).transpose()
# Set up grid
grid_x, grid_y = np.mgrid[x_range[0] : x_range[1] : n_points * 1j, y_range[0] : y_range[1] : n_points * 1j]
grid_vals = griddata(points, dnll, (grid_x, grid_y), "cubic")

# Remove NANS
grid_x = grid_x[grid_vals == grid_vals]
grid_y = grid_y[grid_vals == grid_vals]
grid_vals = grid_vals[grid_vals == grid_vals]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define Profile2D histogram
# h2D = ROOT.TProfile2D("h", "h", n_bins, x_range[0], x_range[1], n_bins, y_range[0], y_range[1], -10, 400, "h")
h2D = ROOT.TProfile2D("h", "h", n_bins, x_range[0], x_range[1], n_bins, y_range[0], y_range[1])

for i in range(len(grid_vals)):
    # Factor of 2 comes from 2*NLL
    h2D.Fill(grid_x[i], grid_y[i], 2 * grid_vals[i])

# Loop over bins: if content = 0 then set 999
for ibin in range(1, h2D.GetNbinsX() + 1):
    for jbin in range(1, h2D.GetNbinsY() + 1):
        if h2D.GetBinContent(ibin, jbin) == 0:
            xc = h2D.GetXaxis().GetBinCenter(ibin)
            yc = h2D.GetYaxis().GetBinCenter(jbin)
            h2D.Fill(xc, yc, 999)

# Set up canvas
canv = ROOT.TCanvas("canv", "canv", 600, 600)
canv.SetTickx()
canv.SetTicky()
canv.SetLeftMargin(0.115)
canv.SetBottomMargin(0.115)
# Extract binwidth
xw = (x_range[1] - x_range[0]) / n_bins
yw = (y_range[1] - y_range[0]) / n_bins

# Set histogram properties
h2D.SetContour(999)
h2D.SetTitle(args.outname)
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
vline.SetLineColorAlpha(ROOT.kGray, 0.5)
vline.Draw("Same")
hline = ROOT.TLine(x_range[0], 1, x_range[1] - xw, 1)
hline.SetLineColorAlpha(ROOT.kGray, 0.5)
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
leg.SetBorderSize(0)
leg.SetFillColor(0)
leg.AddEntry(gBF, "Best fit", "P")
leg.AddEntry(c68, "1#sigma CL", "L")
leg.AddEntry(c95, "2#sigma CL", "L")
# leg.AddEntry(gSM, "SM", "P")
leg.Draw()

# canv.SetLogz()
canv.Update()
canv.SaveAs("scan_2D_"+args.outname+"_id_es.png")
canv.SaveAs("scan_2D_"+args.outname+"_id_es.pdf")


