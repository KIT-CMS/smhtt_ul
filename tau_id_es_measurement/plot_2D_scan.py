import ROOT
# from scipy.interpolate import griddata
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import argparse
# os.system("pip3 install mplhep")
import mplhep as hep
hep.style.use("CMS")

parser = argparse.ArgumentParser()
parser.add_argument('--name',type=str, help='Name of the file')
parser.add_argument('--in-path',type=str, help='Input path to the 2D scan file') 
parser.add_argument('--tau-id-poi',type=str, help='Name of the tau ID POI')
parser.add_argument('--tau-es-poi',type=str, help='Name of the tau ES POI')
parser.add_argument('--outname',type=str, help='Name of the outputfile')
parser.add_argument('--nbins',type=int, help='Number of bins per axis')
args = parser.parse_args()
title = args.outname
if "DM" in title:
    title_map = {"DM0":"DM 0", "DM1":"DM 1", "DM10_11":"DM 10+11", "DM10":"DM 10", "DM11":"DM 11",
                 "DM0_PT20_40":"DM 0 pt20-40", "DM1_PT20_40":"DM 1 pt20-40", "DM10_PT20_40":"DM 10 pt20-40", "DM11_PT20_40":"DM 11 pt20-40",
                 "DM0_PT40_200":"DM 0 pt40-200", "DM1_PT40_200":"DM 1 pt40-200", "DM10_PT40_200":"DM 10 4pt0-200", "DM11_PT40_200":"DM 11 pt40-200"}
    # title_map_plot = {"DM0":"DM 0", "DM1":"#tau_{h}#rightarrow#pi^{#pm} #pi^{0} #nu_{#tau}", "DM10_11":"DM 10+11"}
    title_name = title_map[title]
else:
    title_name = title

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

file_name = args.in_path+"higgsCombine."+args.name+".MultiDimFit.mH125.root"
f = ROOT.TFile(file_name)
t = f.Get("limit")

# Number of points in interpolation
# n_points = 
x_range = [0.5, 1.5]
y_range = [-8.0, 4]

# Number of bins in plot
n_bins = args.nbins

x, y, deltaNLL = [], [], []
for ev in t:
    x.append(getattr(ev, f"r_EMB_{title}"))
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
x_np_0 = np.array(x)
y_np_0 = np.array(y)
deltaNLL_np_0 = np.array(deltaNLL)
bestfit_np = np.array([x_np_0[0], y_np_0[0], deltaNLL_np_0[0]])
print(f"Best fit value for {title}: {bestfit_np}")
x_np = np.delete(x_np_0, 0)
y_np = np.delete(y_np_0, 0)
deltaNLL_np = np.delete(deltaNLL_np_0, 0)

# Check if there are missing values:
loss_flag = False
points_lost = n_bins **2 - len(x_np)
if len(x_np) != len(y_np) or len(x_np) != len(deltaNLL_np):
    print("Lengths of x, y, and deltaNLL arrays are not equal!")
    exit(1)
elif len(x_np) != n_bins **2:
    loss_flag = True

# If values are missing, find index and fill the gaps, deltaNLL gaps get -1.0 values:
if loss_flag:
    set_x = set(x_np)
    set_y = set(y_np)
    sequence_x = [i for i in set_x]
    sequence_y = [i for i in set_y]
    if len(sequence_x) != n_bins or len(sequence_y) != n_bins:
        print("Could not find a sequence! there are a lot of missing values! If you still want to multifit, use max parameter ranges.")
        print(f"This many points have failed: {points_lost}")
        print(f"Check if number of bins was set correctly. It should be the sqrt of number of grid points used! n_bins is set to {n_bins}")
        exit(1)
    
    
    missing_indices = []
    seq_x = np.array(sequence_x)
    seq_x.sort()
    x_np_full = np.tile(seq_x, n_bins)
    debug_list = []
    debug_flag = False
    if len(x_np_full) != n_bins**2:
        print(f"Length of full x_np array: {len(x_np_full)} should be {n_bins**2}")
        exit(1)
    x_np_cp = x_np.copy()
    acc=0
    while len(missing_indices) != points_lost:            
        for i,val in enumerate(x_np_full):
            try:
                if val != x_np_cp[i] or (not np.isclose(val, x_np_cp[i])):
                    
                    missing_indices.append(i)
                    x_np_cp = np.insert(x_np_cp, i, x_np_full[i])
                    break
            except:
                # Standard catch: Index out of range because last indices are missing! But everything else will also end up here!
                if i == len(x_np_cp):
                    missing_indices.append(i)
                    x_np_cp = np.insert(x_np_cp, i, x_np_full[i])
                    break
                else:
                    print(f'Something went wrong with the indices! i:{i}, len(x_np_cp):{len(x_np_cp)}, len(x_np_full):{len(x_np_full)}')
                    print('\n If above print does not show index problems, other Errors will also end up here!\n')
                    exit(1)
            
        acc += 1
        # Finished findind all indices?
        if len(missing_indices) == points_lost:
            print(f"Found all missing indices (#{points_lost}), now fixing the arrays")
            break
        elif acc > (n_bins**2 + n_bins):
            print(f"acc:{acc} Missing indices/points lost: {len(missing_indices)}/{points_lost} and could not recover for some reason! Please inspect!")
            debug_flag = True
            for i,val in enumerate(x_np_full):
                try:
                    if val != x_np_cp[i] or (not np.isclose(val, x_np_cp[i])):
                        debug_list += ((i,val,x_np_cp[i]),)
                except:
                    debug_list += ((i,val,None),)
            print(f"Debug list: {debug_list}")
            break
    
    
    y_np_fu = np.array(sequence_y)
    y_np_full = np.tile(y_np_fu, n_bins)
    y_np_full.sort()
    deltaNLL_full = list(deltaNLL_np.copy())
    for i in missing_indices:
        deltaNLL_full.insert(i, np.nan)
    deltaNLL_np_full = np.array(deltaNLL_full)
    
    #CHECK:
    if len(x_np_cp) != len(y_np_full) != len(deltaNLL_full) != n_bins **2:
        print("Lengths of x, y, and deltaNLL arrays are not equal or unequal n_bins^2!")
        print(f"Lengths: x:{len(x_np_cp)}, x_full:{len(x_np_full)}, y_full:{len(y_np_full)}, deltaNLL:{len(deltaNLL_full)}")
        print(f'nbins: {n_bins}')
        # exit(1)

else:
    x_np_full = x_np.copy()
    y_np_full = y_np.copy()
    deltaNLL_np_full = deltaNLL_np.copy()


# Get the smallest value per axis for profiling curves:
x_profile = []
y_profile = []
profile_y_np = [np.array_split(x_np_full, n_bins), np.array_split(y_np, n_bins), np.array_split(deltaNLL_np_full, n_bins)]
profile_x_np = [[[] for _ in range(n_bins)],[[] for _ in range(n_bins)],[[] for _ in range(n_bins)]]

for i,val in enumerate(x_np_full):
    profile_x_np[0][i % n_bins].append(val)
for i,val in enumerate(y_np_full):
    profile_x_np[1][i % n_bins].append(val)
for i,val in enumerate(deltaNLL_np_full):
    profile_x_np[2][i % n_bins].append(val)

nan_falgs_x = []
nan_falgs_y = []
for i in range(n_bins):
    nan_mask_x = np.isnan(profile_x_np[2][i])
    nan_mask_y = np.isnan(profile_y_np[2][i])
    dNLL_min_x = np.nanmin(profile_x_np[2][i])
    dNLL_min_y = np.nanmin(profile_y_np[2][i])
    if nan_mask_x.any():
        nan_falgs_x += (i,)
    else:
        nan_falgs_x += (-1,)
    if nan_mask_y.any():
        nan_falgs_y += (i,)
    else:
        nan_falgs_y += (-1,)
    index_dNLL_min_y = np.where(profile_y_np[2][i] == dNLL_min_y)[0][0]
    index_dNLL_min_x = np.where(profile_x_np[2][i] == dNLL_min_x)[0][0]
    y_profile += ([profile_y_np[0][i][index_dNLL_min_y], profile_y_np[1][i][0], dNLL_min_y * 2], )
    x_profile += ([profile_x_np[0][i][0], profile_x_np[1][i][index_dNLL_min_x], dNLL_min_x * 2], )

# Plot the 1D profiles:
fig = plt.figure()

ax_x , ax_y = fig.subplots(1,2)
for nan_flag,i in zip(nan_falgs_x,range(n_bins)):
    if nan_flag == -1:
        ax_x.scatter(x_profile[i][0], x_profile[i][2], marker='_', color='k',lw=2)
    else:
        ax_x.scatter(x_profile[i][0], x_profile[i][2], marker='_', color='r', lw=3)


ax_x.vlines(bestfit_np[0],0,1, colors='b', linestyles='dashed', transform=ax_x.get_xaxis_transform(), label='Best fit')
ax_x.set(xlabel='tau ID SF', ylabel='-2 $\Delta\\ln\\mathcal{L}$')
ax_x.legend()
for nan_flag,i in zip(nan_falgs_y,range(n_bins)):
    if nan_flag == -1:
        ax_y.scatter(y_profile[i][1], y_profile[i][2], marker='_', color='k',lw=2)
    else:
        ax_y.scatter(y_profile[i][1], y_profile[i][2], marker='_', color='r', lw=3)


ax_y.set(xlabel='tau ES shift %', ylabel='-2 $\Delta\\ln\\mathcal{L}$')
ax_y.xaxis.set_ticks(np.arange(y_range[0], y_range[-1]+1, 2))
ax_y.vlines(bestfit_np[1],0,1, colors='b', linestyles='dashed', transform=ax_y.get_xaxis_transform(), label='Best fit')
ax_x.hlines(0, 0, 1, colors='k', linestyles='solid', transform=ax_x.get_yaxis_transform())
ax_y.hlines(0, 0, 1, colors='k', linestyles='solid', transform=ax_y.get_yaxis_transform())
ax_y.legend()
fig.suptitle(title_map[title])
fig.text(0.95, 0.95, f"# points lost:{points_lost}", ha='right', va='top', fontsize=12,
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
fig.tight_layout(pad=3.0)
plt.savefig("1D_profiles_2Dscan_"+args.outname+"_id_es_tests.png")

# tauID
plt.rcParams["axes.labelsize"] = 13
plt.rcParams["xtick.labelsize"] = 12
plt.rcParams["ytick.labelsize"] = 12
fig1 = plt.figure(figsize=(5, 5))
ax1 = fig1.add_subplot(111)
for nan_flag,i in zip(nan_falgs_x,range(n_bins)):
    if nan_flag == -1:
        ax1.scatter(x_profile[i][0], x_profile[i][2], marker='_', color='k',lw=2)
    else:
        ax1.scatter(x_profile[i][0], x_profile[i][2], marker='_', color='r', lw=3)

ax1.vlines(bestfit_np[0],0,1, colors='b', linestyles='dashed', transform=ax1.get_xaxis_transform(), label='Best fit')
ax1.set(xlabel='tau ID correction', ylabel='-2 $\Delta\\ln$L')
hep.cms.text('Private Work (Data/Simulation)',loc=0,fontsize=10)
ax1.legend(fontsize=11)
ax1.hlines(0, 0, 1, colors='k', linestyles='solid', transform=ax1.get_yaxis_transform())
fig1.tight_layout(pad=0.2)
fig1.savefig("1D_profiles_2Dscan_"+args.outname+"_id_es_tests_onlyID.png")
plt.close(fig1)

# tau ES
fig2 = plt.figure(figsize=(5, 5))
ax2 = fig2.add_subplot(111)
for nan_flag,i in zip(nan_falgs_y,range(n_bins)):
    if nan_flag == -1:
        ax2.scatter(y_profile[i][1], y_profile[i][2], marker='_', color='k',lw=2)
    else:
        ax2.scatter(y_profile[i][1], y_profile[i][2], marker='_', color='r', lw=3)

ax2.set(xlabel='tau energy scale shift %', ylabel='-2 $\Delta\\ln$L')
hep.cms.text('Private Work (Data/Simulation)',loc=0, fontsize=10)
ax2.xaxis.set_ticks(np.arange(y_range[0], y_range[-1]+1, 2))
ax2.vlines(bestfit_np[1],0,1, colors='b', linestyles='dashed', transform=ax2.get_xaxis_transform(), label='Best fit')
ax2.hlines(0, 0, 1, colors='k', linestyles='solid', transform=ax2.get_yaxis_transform())
ax2.legend(fontsize=11)
fig2.tight_layout(pad=0.2)
# fig2.set_size_inches(4, 6)
fig2.savefig("1D_profiles_2Dscan_"+args.outname+"_id_es_tests_onlyES.png")
plt.close(fig2)

plt.close(fig)


# Fill the 2D histogram
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

# Calc Pearson correlation coeffs from profiles:
prof_x = [x_profile[i][2] for i in range(n_bins)]
prof_y = [y_profile[i][2] for i in range(n_bins)]
cov_np = np.corrcoef(prof_x, prof_y)
corr_det = np.linalg.det(cov_np)

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
corr_xy = covariance / ((stdDevX * stdDevY) + 0.0000001)
corr_xy_str = f"Corr.:{corr_xy:.3f}"

# Set up canvas
canv = ROOT.TCanvas("canv", "canv", 680, 600)
# canv.SetFillColor(0)
# canv.SetFrameFillColor(0)
canv.SetTickx()
canv.SetTicky()
canv.SetLeftMargin(0.115)
canv.SetRightMargin(0.170)
canv.SetBottomMargin(0.115)
# canv.SetLogz()

# Extract binwidth
xw = (x_range[1] - x_range[0]) / n_bins
yw = (y_range[1] - y_range[0]) / n_bins

# Set histogram properties
h2D.SetContour(999)
h2D.SetTitle(title_name)
h2D.GetXaxis().SetTitle("#tau ID correction")
h2D.GetXaxis().SetTitleSize(0.05)
h2D.GetXaxis().SetTitleOffset(0.9)
h2D.GetXaxis().SetRangeUser(x_range[0], x_range[1] - xw)

h2D.GetYaxis().SetTitle("#tau energy scale shift %")
h2D.GetYaxis().SetTitleSize(0.05)
h2D.GetYaxis().SetTitleOffset(0.9)
h2D.GetYaxis().SetRangeUser(y_range[0], y_range[1] - yw)

h2D.GetZaxis().SetTitle("-2 #Delta ln L")
h2D.GetZaxis().SetTitleSize(0.05)
h2D.GetZaxis().SetTitleOffset(0.8)

# h2D.SetMaximum(400)
# ROOT.gStyle.SetPalette(ROOT.kCool)
ROOT.gStyle.SetPalette(ROOT.kBird)
# ROOT.gStyle.SetPalette(ROOT.kLivid)
# Make confidence interval contours
c68, c95 = h2D.Clone(), h2D.Clone()
c68.SetContour(2)
c68.SetContourLevel(1, 2.3)
c68.SetLineWidth(3)
c68.SetLineColor(ROOT.kWhite)
# c68.SetLineColor(ROOT.kRed)
c95.SetContour(2)
c95.SetContourLevel(1, 5.99)
c95.SetLineWidth(3)
c95.SetLineStyle(2)
c95.SetLineColor(ROOT.kWhite)

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
# gBF.SetPoint(0, grid_x[np.argmin(grid_vals)], grid_y[np.argmin(grid_vals)])
gBF.SetPoint(0, x[np.argmin(deltaNLL)], y[np.argmin(deltaNLL)])
gBF.SetMarkerStyle(34)
gBF.SetMarkerSize(2)
gBF.SetMarkerColor(ROOT.kWhite)
gBF.Draw("P")

# gSM = ROOT.TGraph()
# gSM.SetPoint(0, 1, 1)
# gSM.SetMarkerStyle(33)
# gSM.SetMarkerSize(2)
# gSM.SetMarkerColor(ROOT.kRed)
# gSM.Draw("P")


# Add legend
leg = ROOT.TLegend(0.15, 0.7, 0.4, 0.89)
leg.SetTextSize(0.04)
leg.SetBorderSize(0)
leg.SetFillColor(ROOT.kGray)
leg.AddEntry(gBF, "Best fit", "P")
leg.AddEntry(c68, "1#sigma CL", "L")
leg.AddEntry(c95, "2#sigma CL", "L")
# leg.AddEntry(h2D, corr_xy_str, "")
leg.AddEntry(h2D, f"correl.:{corr_det:.3f}", "")

# leg.AddEntry(gSM, "SM", "P")
leg.Draw()

# Add CMS labeling
# label = ROOT.TText(0.5, 3.74, "CMS Private Work (Data/Simulation)")
# label.SetTextAlign(13) 
# label.SetTextSize(0.025) 
# label.Draw()
label = ROOT.TLatex()
label.SetTextSize(0.025)
label.SetTextAlign(13)
label.DrawLatex(0.5, 3.74, "CMS #it{#bf{Private Work (Data/Simulation)}}")


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

# Plot the 1D profiles: does not work if any bin failed and thus the # of bins is not the same!
# prof_X = h2D.ProfileX("tauID SF profile")
# prof_Y = h2D.ProfileY("TES shift profile")

# # Create a single canvas
# c2 = ROOT.TCanvas("c2", "Profiles", 800, 600)
# c2.SetTitle(title_name)
# c2.Divide(2, 1)
# c2.cd(1)
# prof_X.Draw()
# c2.cd(2)
# prof_Y.Draw()
# c2.Update()
# c2.SaveAs("1D_profiles_2Dscan_"+args.outname+"_id_es_tests.png")