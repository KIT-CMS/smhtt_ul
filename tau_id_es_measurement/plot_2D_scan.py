import ROOT
# from scipy.interpolate import griddata
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import argparse
import yaml
from array import array
# os.system("pip3 install mplhep")
import mplhep as hep
hep.style.use("CMS")


parser = argparse.ArgumentParser()
parser.add_argument('--name-2D',type=str, help='Name of the file')
parser.add_argument('--name-1D-ID',type=str, help='Name of the 1D ID file')
parser.add_argument('--name-1D-ES',type=str, help='Name of the 1D ES file')
parser.add_argument('--in-path',type=str, help='Input path to the 2D scan file')
parser.add_argument('--tau-id-poi',type=str, help='Name of the tau ID POI')
parser.add_argument('--tau-es-poi',type=str, help='Name of the tau ES POI')
parser.add_argument('--outname',type=str, help='Name of the outputfile')
parser.add_argument('--tag',type=str, help='Tag of the processed files')
parser.add_argument('--nbins',type=int, help='Number of bins per axis')
parser.add_argument('--x-range',type=float, nargs=2, help='X range for the plot')
parser.add_argument('--y-range',type=float, nargs=2, help='Y range for the plot')
parser.add_argument('--scale_range',type=float, help='Scale the range of parameters extraced from scan')
args = parser.parse_args()
title = args.outname
if "DM" in title:
    title_map = {"DM0":"DM 0", "DM1":"DM 1", "DM1011":"DM 10+11", "DM10":"DM 10", "DM11":"DM 11",
                 "DM0_PT20_40":"DM 0 pt20-40", "DM1_PT20_40":"DM 1 pt20-40", "DM1011_PT20_40":"DM 10+11 pt20-40",
                 "DM10_PT20_40":"DM 10 pt20-40", "DM11_PT20_40":"DM 11 pt20-40", "DM0_PT40_200":"DM 0 pt40-200",
                 "DM1_PT40_200":"DM 1 pt40-200", "DM1011_PT40_200":"DM 10+11 pt40-200", "DM10_PT40_200":"DM 10 pt40-200",
                 "DM11_PT40_200":"DM 11 pt40-200"}
    # title_map_plot = {"DM0":"DM 0", "DM1":"#tau_{h}#rightarrow#pi^{#pm} #pi^{0} #nu_{#tau}", "DM10_11":"DM 10+11"}
    title_name = title_map[title]
else:
    title_name = title

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

file_name = args.in_path+"higgsCombine."+args.name_2D+".MultiDimFit.mH125.root"
f = ROOT.TFile(file_name)
t = f.Get("limit")

# Number of points in interpolation
# n_points = 
x_range = [args.x_range[0], args.x_range[1]]
y_range = [args.y_range[0], args.y_range[1]]
print(f"X range: {x_range}, Y range: {y_range}")
# Number of bins in plot
n_bins = args.nbins

x, y, deltaNLL = [], [], []
try:
    for ev in t:
        x.append(getattr(ev, f"r_EMB_{title}"))
        y.append(getattr(ev, args.tau_es_poi))
        deltaNLL.append(getattr(ev, "deltaNLL"))
except:
    breakpoint()
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
# x_np = np.delete(x_np_0, 0)
# y_np = np.delete(y_np_0, 0)
# deltaNLL_np = np.delete(deltaNLL_np_0, 0)

# # Check if there are missing values:
# loss_flag = False
# points_lost = n_bins **2 - len(x_np)
# if len(x_np) != len(y_np) or len(x_np) != len(deltaNLL_np):
#     print("Lengths of x, y, and deltaNLL arrays are not equal!")
#     exit(1)
# elif len(x_np) != n_bins **2:
#     loss_flag = True

# # If values are missing, find index and fill the gaps, deltaNLL gaps get -1.0 values:
# if loss_flag:
#     set_x = set(x_np)
#     set_y = set(y_np)
#     sequence_x = [i for i in set_x]
#     sequence_y = [i for i in set_y]
#     if len(sequence_x) != n_bins or len(sequence_y) != n_bins:
#         print("Could not find a sequence! there are a lot of missing values! If you still want to multifit, use max parameter ranges.")
#         print(f"This many points have failed: {points_lost}")
#         print(f"Check if number of bins was set correctly. It should be the sqrt of number of grid points used! n_bins is set to {n_bins}")
#         exit(1)
    
    
#     missing_indices = []
#     seq_x = np.array(sequence_x)
#     seq_x.sort()
#     x_np_full = np.tile(seq_x, n_bins)
#     debug_list = []
#     debug_flag = False
#     if len(x_np_full) != n_bins**2:
#         print(f"Length of full x_np array: {len(x_np_full)} should be {n_bins**2}")
#         exit(1)
#     x_np_cp = x_np.copy()
#     acc=0
#     while len(missing_indices) != points_lost:            
#         for i,val in enumerate(x_np_full):
#             try:
#                 if val != x_np_cp[i] or (not np.isclose(val, x_np_cp[i])):
                    
#                     missing_indices.append(i)
#                     x_np_cp = np.insert(x_np_cp, i, x_np_full[i])
#                     break
#             except:
#                 # Standard catch: Index out of range because last indices are missing! But everything else will also end up here!
#                 if i == len(x_np_cp):
#                     missing_indices.append(i)
#                     x_np_cp = np.insert(x_np_cp, i, x_np_full[i])
#                     break
#                 else:
#                     print(f'Something went wrong with the indices! i:{i}, len(x_np_cp):{len(x_np_cp)}, len(x_np_full):{len(x_np_full)}')
#                     print('\n If above print does not show index problems, other Errors will also end up here!\n')
#                     exit(1)
            
#         acc += 1
#         # Finished findind all indices?
#         if len(missing_indices) == points_lost:
#             print(f"Found all missing indices (#{points_lost}), now fixing the arrays")
#             break
#         elif acc > (n_bins**2 + n_bins):
#             print(f"acc:{acc} Missing indices/points lost: {len(missing_indices)}/{points_lost} and could not recover for some reason! Please inspect!")
#             debug_flag = True
#             for i,val in enumerate(x_np_full):
#                 try:
#                     if val != x_np_cp[i] or (not np.isclose(val, x_np_cp[i])):
#                         debug_list += ((i,val,x_np_cp[i]),)
#                 except:
#                     debug_list += ((i,val,None),)
#             print(f"Debug list: {debug_list}")
#             break
    
    
#     y_np_fu = np.array(sequence_y)
#     y_np_full = np.tile(y_np_fu, n_bins)
#     y_np_full.sort()
#     deltaNLL_full = list(deltaNLL_np.copy())
#     for i in missing_indices:
#         deltaNLL_full.insert(i, np.nan)
#     deltaNLL_np_full = np.array(deltaNLL_full)
    
#     #CHECK:
#     if len(x_np_cp) != len(y_np_full) != len(deltaNLL_full) != n_bins **2:
#         print("Lengths of x, y, and deltaNLL arrays are not equal or unequal n_bins^2!")
#         print(f"Lengths: x:{len(x_np_cp)}, x_full:{len(x_np_full)}, y_full:{len(y_np_full)}, deltaNLL:{len(deltaNLL_full)}")
#         print(f'nbins: {n_bins}')
#         # exit(1)

# else:
#     x_np_full = x_np.copy()
#     y_np_full = y_np.copy()
#     deltaNLL_np_full = deltaNLL_np.copy()


# Get the smallest value per axis for profiling curves:
# x_profile = []
# y_profile = []
# profile_y_np = [np.array_split(x_np_full, n_bins), np.array_split(y_np, n_bins), np.array_split(deltaNLL_np_full, n_bins)]
# profile_x_np = [[[] for _ in range(n_bins)],[[] for _ in range(n_bins)],[[] for _ in range(n_bins)]]

# for i,val in enumerate(x_np_full):
#     profile_x_np[0][i % n_bins].append(val)
# for i,val in enumerate(y_np_full):
#     profile_x_np[1][i % n_bins].append(val)
# for i,val in enumerate(deltaNLL_np_full):
#     profile_x_np[2][i % n_bins].append(val)

# nan_falgs_x = []
# nan_falgs_y = []
# for i in range(n_bins):
#     nan_mask_x = np.isnan(profile_x_np[2][i])
#     nan_mask_y = np.isnan(profile_y_np[2][i])
#     dNLL_min_x = np.nanmin(profile_x_np[2][i])
#     dNLL_min_y = np.nanmin(profile_y_np[2][i])
#     if nan_mask_x.any():
#         nan_falgs_x += (i,)
#     else:
#         nan_falgs_x += (-1,)
#     if nan_mask_y.any():
#         nan_falgs_y += (i,)
#     else:
#         nan_falgs_y += (-1,)
#     index_dNLL_min_y = np.where(profile_y_np[2][i] == dNLL_min_y)[0][0]
#     index_dNLL_min_x = np.where(profile_x_np[2][i] == dNLL_min_x)[0][0]
#     y_profile += ([profile_y_np[0][i][index_dNLL_min_y], profile_y_np[1][i][0], dNLL_min_y * 2], )
#     x_profile += ([profile_x_np[0][i][0], profile_x_np[1][i][index_dNLL_min_x], dNLL_min_x * 2], )

# Plot the 1D profiles:
# fig = plt.figure()

# ax_x , ax_y = fig.subplots(1,2)
# for nan_flag,i in zip(nan_falgs_x,range(n_bins)):
#     if nan_flag == -1:
#         ax_x.scatter(x_profile[i][0], x_profile[i][2], marker='_', color='k',lw=2)
#     else:
#         ax_x.scatter(x_profile[i][0], x_profile[i][2], marker='_', color='r', lw=3)


# ax_x.vlines(bestfit_np[0],0,1, colors='b', linestyles='dashed', transform=ax_x.get_xaxis_transform(), label='Best fit')
# ax_x.set(xlabel='tau ID SF', ylabel='-2 $\Delta\\ln\\mathcal{L}$')
# ax_x.legend()
# for nan_flag,i in zip(nan_falgs_y,range(n_bins)):
#     if nan_flag == -1:
#         ax_y.scatter(y_profile[i][1], y_profile[i][2], marker='_', color='k',lw=2)
#     else:
#         ax_y.scatter(y_profile[i][1], y_profile[i][2], marker='_', color='r', lw=3)


# ax_y.set(xlabel='tau ES shift %', ylabel='-2 $\Delta\\ln\\mathcal{L}$')
# ax_y.xaxis.set_ticks(np.arange(y_range[0], y_range[-1]+1, 2))
# ax_y.vlines(bestfit_np[1],0,1, colors='b', linestyles='dashed', transform=ax_y.get_xaxis_transform(), label='Best fit')
# ax_x.hlines(0, 0, 1, colors='k', linestyles='solid', transform=ax_x.get_yaxis_transform())
# ax_y.hlines(0, 0, 1, colors='k', linestyles='solid', transform=ax_y.get_yaxis_transform())
# ax_y.legend()
# fig.suptitle(title_map[title])
# fig.text(0.95, 0.95, f"# points lost:{points_lost}", ha='right', va='top', fontsize=12,
#         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
# fig.tight_layout(pad=1.0)
# # fig.subplots_adjust(top=0.85)
# plt.savefig("1D_profiles_2Dscan_"+args.outname+"_"+args.tag+"_id_es_tests.pdf")

# # tauID
# plt.rcParams["axes.labelsize"] = 13
# plt.rcParams["xtick.labelsize"] = 12
# plt.rcParams["ytick.labelsize"] = 12
# fig1 = plt.figure(figsize=(5, 5))
# ax1 = fig1.add_subplot(111)
# for nan_flag,i in zip(nan_falgs_x,range(n_bins)):
#     if nan_flag == -1:
#         ax1.scatter(x_profile[i][0], x_profile[i][2], marker='_', color='k',lw=2)
#     else:
#         ax1.scatter(x_profile[i][0], x_profile[i][2], marker='_', color='r', lw=3)

# ax1.vlines(bestfit_np[0],0,1, colors='b', linestyles='dashed', transform=ax1.get_xaxis_transform(), label='Best fit')
# ax1.set(xlabel='tau ID correction', ylabel='-2 $\Delta\\ln$L')
# hep.cms.text('Private Work (Data/Simulation)',loc=0,fontsize=10)
# ax1.legend(fontsize=11)
# ax1.hlines(0, 0, 1, colors='k', linestyles='solid', transform=ax1.get_yaxis_transform())
# fig1.tight_layout(pad=0.2)
# fig1.savefig("1D_profiles_2Dscan_"+args.outname+"_"+args.tag+"_id_es_tests_onlyID.png")
# plt.close(fig1)

# # tau ES
# fig2 = plt.figure(figsize=(5, 5))
# ax2 = fig2.add_subplot(111)
# for nan_flag,i in zip(nan_falgs_y,range(n_bins)):
#     if nan_flag == -1:
#         ax2.scatter(y_profile[i][1], y_profile[i][2], marker='_', color='k',lw=2)
#     else:
#         ax2.scatter(y_profile[i][1], y_profile[i][2], marker='_', color='r', lw=3)

# ax2.set(xlabel='tau energy scale shift %', ylabel='-2 $\Delta\\ln$L')
# hep.cms.text('Private Work (Data/Simulation)',loc=0, fontsize=10)
# ax2.xaxis.set_ticks(np.arange(y_range[0], y_range[-1]+1, 2))
# ax2.vlines(bestfit_np[1],0,1, colors='b', linestyles='dashed', transform=ax2.get_xaxis_transform(), label='Best fit')
# ax2.hlines(0, 0, 1, colors='k', linestyles='solid', transform=ax2.get_yaxis_transform())
# ax2.legend(fontsize=11)
# fig2.tight_layout(pad=0.2)
# # fig2.set_size_inches(4, 6)
# fig2.savefig("1D_profiles_2Dscan_"+args.outname+"_"+args.tag+"_id_es_tests_onlyES.png")
# plt.close(fig2)

# plt.close(fig)


# Fill the 2D histogram
for i in range(len(deltaNLL)):
    h2D.Fill(x[i], y[i], 2 * deltaNLL[i])

# Calc Pearson correlation coeffs from profiles:
# prof_x = [x_profile[i][2] for i in range(n_bins)]
# prof_y = [y_profile[i][2] for i in range(n_bins)]
# cov_np = np.corrcoef(prof_x, prof_y)
# corr_det = np.linalg.det(cov_np)

# Calc Pearson correlation:
# projX = h2D.ProjectionX("tauID SF")
# projY = h2D.ProjectionY("TES shift")

# meanX = projX.GetMean()
# meanY = projY.GetMean()
# # Calculate covariance
# covariance = 0
# nBinsX = projX.GetNbinsX()
# nBinsY = projY.GetNbinsX()

# for binX in range(1, nBinsX + 1):
#     for binY in range(1, nBinsY + 1):
#         valueX = projX.GetBinCenter(binX)
#         valueY = projY.GetBinCenter(binY)
#         covariance += (valueX - meanX) * (valueY - meanY)

# covariance /= (nBinsX * nBinsY)  # Normalize by the total number of bins

# # Calculate standard deviations
# stdDevX = projX.GetRMS()
# stdDevY = projY.GetRMS()

# # => Correlation coefficient:
# corr_xy = covariance / ((stdDevX * stdDevY) + 0.0000001)
# corr_xy_str = f"Corr.:{corr_xy:.3f}"

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
# leg.AddEntry(h2D, f"correl.:{corr_det:.3f}", "")

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
label.DrawLatex(x_range[0], y_range[1]-0.1, "CMS #it{#bf{Private Work (Data/Simulation)}}")

# canv.Update()

# canv.SetLogz()
# canv.cd()
canv.Update()
canv.SaveAs("scan_2D_"+args.outname+"_"+args.tag+"_id_es_tests.pdf")
# canv.SaveAs("scan_2D_"+args.outname+"_id_es.pdf")

# ================================================================================= #
# # Collect contours and save them in a YAML file
# # Make sure the pad is updated so that the contour list is created
# temp_canv = ROOT.TCanvas("temp_canv", "temp_canv", 680, 600)
# temp_c68 = c68.Clone("temp_c68")
# temp_canv.cd()
# temp_c68.Draw("CONT Z LIST")
# temp_canv.Update()

# contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
# if not contours or contours.GetSize() == 0:
#     print("[ERROR] No c68 contours found!")
# else:
#     # Extract x (ID) and y (ES) minima and maxima from the contours.
#     global_x_min = float('inf')
#     global_x_max = float('-inf')
#     global_y_min = float('inf')
#     global_y_max = float('-inf')
    
#     # Loop over each contour object:
#     for i in range(contours.GetSize()):
#         cont = contours.At(i)
#         # If the object is a TGraph:
#         if cont.InheritsFrom("TGraph"):
#             graph_list = [cont]
#         # If the object is a TList, extract its TGraph entries:
#         elif cont.InheritsFrom("TList"):
#             graph_list = []
#             for j in range(cont.GetSize()):
#                 obj = cont.At(j)
#                 if obj.InheritsFrom("TGraph"):
#                     graph_list.append(obj)
#         else:
#             continue
        
#         for gr in graph_list:
#             n_points = gr.GetN()
#             for j in range(n_points):
#                 a_x = array('d', [0.0])
#                 a_y = array('d', [0.0])
#                 gr.GetPoint(j, a_x, a_y)
#                 x_val = a_x[0]
#                 y_val = a_y[0]
#                 if x_val < global_x_min: global_x_min = x_val
#                 if x_val > global_x_max: global_x_max = x_val
#                 if y_val < global_y_min: global_y_min = y_val
#                 if y_val > global_y_max: global_y_max = y_val
            
#     # Retrieve best fit coordinates from bestfit_np (an np.array)
#     bestfit_id = round(float(bestfit_np[0]), 4)
#     bestfit_es = round(float(bestfit_np[1]), 4)
    
#     # Update YAML file with structure: tag -> title -> {"ID": [min, max], "ES": [min, max], "bestfit": {"ID": bestfit, "ES": bestfit}}
#     yaml_file_2D = "tau_id_es_measurement/2Dscan_contours.yaml"
#     try:
#         with open(yaml_file_2D, "r") as f:
#             yaml_data = yaml.safe_load(f) or {}
#     except FileNotFoundError:
#         yaml_data = {}
    
#     if args.tag not in yaml_data: 
#         yaml_data[args.tag] = {}
#     yaml_data[args.tag][title] = {
#         "ID": [round(global_x_min*(1-args.scale_range) if global_x_min>0 else global_x_min*(1+args.scale_range), 4),
#                round(global_x_max*(1+args.scale_range) if global_x_max>0 else global_x_max*(1-args.scale_range), 4)],
#         "ES": [round(global_y_min*(1-args.scale_range) if global_y_min>0 else global_y_min*(1+args.scale_range), 4),
#                round(global_y_max*(1+args.scale_range) if global_y_max>0 else global_y_max*(1-args.scale_range), 4)],
#         "fit": {"ID": bestfit_id, "ES": bestfit_es}
#     }
    
#     with open(yaml_file_2D, "w") as f:
#         yaml.dump(yaml_data, f, default_flow_style=False)
#     print(f"[INFO] Contour extrema and best fit coordinates saved in {yaml_file_2D}")

# temp_canv.Close()

# ================================================================================= #


file_name_1D_ID = args.in_path+"higgsCombine."+args.name_1D_ID+".MultiDimFit.mH125.root"
f_1D_ID = ROOT.TFile(file_name_1D_ID)
file_name_1D_ES = args.in_path+"higgsCombine."+args.name_1D_ES+".MultiDimFit.mH125.root"
f_1D_ES = ROOT.TFile(file_name_1D_ES)


def extract_1d_scan(file, poi_name:str) -> tuple[list, list]:
    t = file.Get("limit")
    poi_vals = []
    dnll_vals = []
    for ev in t:
        # skip the best fit (deltaNLL==0 and not scanned)
        if getattr(ev, "deltaNLL") == 0 and len(poi_vals) > 0:
            continue
        poi_vals.append(getattr(ev, poi_name))
        dnll_vals.append(2 * getattr(ev, "deltaNLL"))
    return np.array(poi_vals), np.array(dnll_vals)

def extract_confidence_interval(poi:list, dnll:list, threshold=1.0) -> tuple[float, float]:
    # Sort the arrays by poi value.
    sorted_idx = np.argsort(poi)
    poi_sorted = poi[sorted_idx]
    dnll_sorted = dnll[sorted_idx]

    # Locate the best fit (the minimum dnll)
    best_fit_index = np.argmin(dnll_sorted)

    # Find the lower edge: scan from best fit to left until crossing threshold.
    lower_edge = None
    for i in range(best_fit_index, 0, -1):
        if dnll_sorted[i] < threshold and dnll_sorted[i-1] > threshold:
            # Perform linear interpolation between these points:
            x1, x2 = poi_sorted[i-1], poi_sorted[i]
            y1, y2 = dnll_sorted[i-1], dnll_sorted[i]
            lower_edge = x1 + (threshold - y1) * (x2 - x1) / (y2 - y1)
            break

    # Find the upper edge: scan from best fit to right until crossing threshold.
    upper_edge = None
    for i in range(best_fit_index, len(poi_sorted)-1):
        if dnll_sorted[i] < threshold and dnll_sorted[i+1] > threshold:
            x1, x2 = poi_sorted[i], poi_sorted[i+1]
            y1, y2 = dnll_sorted[i], dnll_sorted[i+1]
            upper_edge = x1 + (threshold - y1) * (x2 - x1) / (y2 - y1)
            break

    return lower_edge, upper_edge

# 1D scan for tau ID SF (profiling ES)
poi_id, dnll_id = extract_1d_scan(f_1D_ID, f"r_EMB_{title}")
lower_edge_id, upper_edge_id = extract_confidence_interval(poi_id, dnll_id, threshold=1.0)
plt.figure()
plt.plot(poi_id[1:], dnll_id[1:], marker='o', label='1D scan (profiled ES)')
plt.axvline(bestfit_np[0], color='b', linestyle='--', label='2D best fit', lw=4)
plt.axvline(poi_id[0], color='g', linestyle='--', label='1D best fit',lw=2)
if lower_edge_id is not None:
    plt.axvline(lower_edge_id, color='r', linestyle='--', label=r'$+/-1\sigma$', lw=1)
else:
    print("[WARNING] No lower edge found for ID scan.")
if upper_edge_id is not None:
    plt.axvline(upper_edge_id, color='r', linestyle='--', lw=1)
else:
    print("[WARNING] No upper edge found for ID scan.")
plt.axhline(1, color='r', linestyle='-', label=r'$-2\Delta\ln\mathcal{L}$=1', lw=1)
plt.axhline(0, color='k', linestyle='-')
plt.xlabel('tau ID SF')
plt.ylabel(r'$-2\Delta\ln\mathcal{L}$')
plt.title(f'1D Scan tau ID SF ({title_name})')
plt.legend()
plt.tight_layout()
plt.savefig(f"1D_fit_tauID_{args.outname}_{args.tag}.pdf")
plt.close()

# 1D scan for tau ES shift (profiling ID)
poi_es, dnll_es = extract_1d_scan(f_1D_ES, f"ES_{title}")
lower_edge_es, upper_edge_es = extract_confidence_interval(poi_es, dnll_es, threshold=1.0)
plt.figure()
plt.plot(poi_es[1:], dnll_es[1:], marker='o', label='1D scan (profiled ID)')
plt.axvline(bestfit_np[1], color='b', linestyle='--', label='2D best fit',lw=4)
plt.axvline(poi_es[0], color='g', linestyle='--', label='1D best fit',lw=2)
if lower_edge_es is not None:
    plt.axvline(lower_edge_es, color='r', linestyle='--', label=r'$+/-1\sigma$', lw=1)
else:
    print("[WARNING] No lower edge found for ES scan.")
if upper_edge_es is not None:
    plt.axvline(upper_edge_es, color='r', linestyle='--', lw=1)
else:
    print("[WARNING] No upper edge found for ES scan.")
plt.axhline(1, color='r', linestyle='-', label=r'$-2\Delta\ln\mathcal{L}$=1', lw=1)
plt.axhline(0, color='k', linestyle='-')
plt.xlabel('tau ES shift [%]')
plt.ylabel(r'$-2\Delta\ln\mathcal{L}$')
plt.title(f'1D Scan tau ES shift ({title_name})')
plt.legend()
plt.tight_layout()
plt.savefig(f"1D_fit_tauES_{args.outname}_{args.tag}.pdf")
plt.close()

if lower_edge_id is not None:
    low_id = float(round(lower_edge_id*(1-args.scale_range) if lower_edge_id>0 else lower_edge_id*(1+args.scale_range), 4))
else:
    low_id = None
if upper_edge_id is not None:
    up_id = float(round(upper_edge_id*(1+args.scale_range) if upper_edge_id>0 else upper_edge_id*(1-args.scale_range), 4))
else:
    up_id = None
if lower_edge_es is not None:
    low_es = float(round(lower_edge_es*(1-args.scale_range) if lower_edge_es>0 else lower_edge_es*(1+args.scale_range), 4))
else:
    low_es = None
if upper_edge_es is not None:
    up_es = float(round(upper_edge_es*(1+args.scale_range) if upper_edge_es>0 else upper_edge_es*(1-args.scale_range), 4))
else:
    up_es = None
fit_id = float(poi_id[0])
fit_es = float(poi_es[0])

yaml_file_1D = "tau_id_es_measurement/1Dscan_contours.yaml"
try:
    with open(yaml_file_1D, "r") as f1:
        yaml_data1 = yaml.safe_load(f1) or {}
except FileNotFoundError:
    yaml_data1 = {}


if args.tag not in yaml_data1:
    yaml_data1[args.tag] = {}
yaml_data1[args.tag][title] = {
    "ID": [low_id, up_id],
    "ES": [low_es, up_es],
    "fit": {"ID": fit_id, "ES": fit_es},
    "scale_range": args.scale_range
}

with open(yaml_file_1D, "w") as f2:
    yaml.dump(yaml_data1, f2, default_flow_style=False)
print(f"[INFO] Contour extrema and best fit coordinates saved in {yaml_file_1D}")