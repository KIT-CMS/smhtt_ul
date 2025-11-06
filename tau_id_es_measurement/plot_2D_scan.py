import ROOT
from scipy.interpolate import griddata
import multiprocessing
from contextlib import contextmanager
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.colors as colors
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
parser.add_argument('--closeup_scan', action='store_true', help='Scan with closeup range from whole range scan')
args = parser.parse_args()
title = args.outname
scan_tag = "full_scan" if not args.closeup_scan else "closeup_scan"

use_root = False
interpolate= True

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

initial_fit_index = None
bad_norm = None
if 0.0 in deltaNLL:
    print("[INFO] Initial fit found in the scan!")
    initial_fit_index = deltaNLL.index(0.0)
    initial_fit = [x[initial_fit_index], y[initial_fit_index], deltaNLL[initial_fit_index]]
    del x[initial_fit_index]
    del y[initial_fit_index]
    del deltaNLL[initial_fit_index]

x = np.array(x)
y = np.array(y)
z = 2*np.array(deltaNLL)
grid_best = [x[np.argmin(z)], y[np.argmin(z)], np.min(z)]
if initial_fit_index is None:
    print("[INFO] No initial fit normalization found in the scan! Normalization done via grid minimum.")
    z_min = np.min(z)
    z = z - z_min
    bad_norm = z_min
else:
    if np.min(z) < 0.0:
        print("[Warning] Bad normalization, even though initial fit found! Normalization done via grid minimum.")
        z_min = np.min(z)
        z = z - z_min
        bad_norm = z_min
# breakpoint()
if interpolate:
    def _gridwrapper(method, points, values, grid, queue):
        result = griddata(points, values, grid, method=method)
        queue.put(result)
    
    @contextmanager
    def process_context(target, args):
        proc = multiprocessing.Process(target=target, args=args)
        proc.start()
        try:
            yield proc
        finally:
            if proc.is_alive():
                proc.terminate()
            proc.join()
    
    # Create a regular grid
    xi = np.linspace(x_range[0], x_range[1], n_bins)
    yi = np.linspace(y_range[0], y_range[1], n_bins)
    grid_x, grid_y = np.meshgrid(xi, yi)
    # Interpolate the z values onto the grid
    grid_z = griddata(np.column_stack((x, y)), z, (grid_x, grid_y), method='cubic')
    # Replace nans with nearest neighbor
    nan_mask = np.isnan(grid_z)
    if np.any(nan_mask):
        # Use nearest-neighbor interpolation to fill missing values only. Switch to cubic if it does not converge in time!
        points = np.column_stack((x, y))
        grid = (grid_x, grid_y)
        queue = multiprocessing.Queue()
        
        with process_context(_gridwrapper, ('nearest', points, z, grid, queue)) as proc:
            proc.join(timeout=20)
            if proc.is_alive():
                print("[INFO] 'nearest' method took longer than 20 seconds; switching to cubic and terminating process.")
                # The process_context context manager will terminate the process.
                grid_z_nearest = griddata(points, z, grid, method='cubic', fill_value=np.nanmax(grid_z))
            else:
                grid_z_nearest = queue.get()
        
        grid_z[nan_mask] = grid_z_nearest[nan_mask]
    
    # breakpoint()
    plt.style.use(hep.style.CMS)
    fig, ax = plt.subplots(figsize=(10, 8))
    linear_levels = np.linspace(0, 1, 10)
    log_levels = np.logspace(np.log10(1), np.log10(np.max(grid_z)), 90)
    levels = np.unique(np.sort(np.concatenate((linear_levels, log_levels))))
    cf = ax.contourf(grid_x, grid_y, grid_z, levels=levels,
                   norm=colors.SymLogNorm(1))
    plt.colorbar(cf, ax=ax, label='-2Δln L')

    # Define thresholds for contours (e.g. 1σ and 2σ levels)
    contour_levels = [2.2957, 6.1800]
    cs = ax.contour(grid_x, grid_y, grid_z, levels=contour_levels, colors='white', linewidths=2)
    ax.clabel(cs, fmt={contour_levels[0]:"1σ", contour_levels[1]:"2σ"}, inline=True, fontsize=10)

    # Draw best-fit point
    if initial_fit_index is not None:
        norm_str = ""
        if bad_norm:
            norm_str = f" (bad norm {bad_norm:.2f})"
        ax.plot(initial_fit[0], initial_fit[1], marker='o', markersize=8, color='blue', label=f'Initial fit: {initial_fit[2]:.2f}{norm_str}')
    else:
        ax.plot([], [], ' ', label=f"Initial fit: None (bad norm {bad_norm:.2f})")
    ax.plot(grid_best[0], grid_best[1], marker='+', markersize=12, color='white', label=f'Best grid value: {grid_best[2]:.2f}')
    ax.set_xlim(*ax.get_xlim())
    ax.set_ylim(*ax.get_ylim())
    ax.axhline(0,0,1, color='r', linestyle='-', markersize=8)
    ax.axvline(1,0,1, color='r', linestyle='-', markersize=8)
    ax.set_xlabel("Tau ID correction")
    ax.set_ylabel("Tau energy scale shift [%]")
    ax.set_title(f"2D Scan (Interpolated) {title_name}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"2D_{scan_tag}_{args.outname}_{args.tag}_interpolated.pdf")
    plt.savefig(f"2D_{scan_tag}_{args.outname}_{args.tag}_interpolated.png")
    plt.close()

# Binned data without interpolation
H, xedges, yedges = np.histogram2d(x, y, bins=args.nbins, range=[args.x_range, args.y_range], weights=z)
counts, _, _ = np.histogram2d(x, y, bins=args.nbins, range=[args.x_range, args.y_range])
mask_empty = (counts == 0)

# Avoid division by zero: bins with no entries will become NaN.
with np.errstate(divide='ignore', invalid='ignore'):
    H_avg = H / counts

H_avg_masked = np.ma.masked_where(counts == 0, H_avg)

xcenters = (xedges[:-1] + xedges[1:]) / 2
ycenters = (yedges[:-1] + yedges[1:]) / 2
grid_x, grid_y = np.meshgrid(xcenters, ycenters)

plt.style.use(hep.style.CMS)
fig, ax = plt.subplots(figsize=(10, 8))

cmap = plt.get_cmap('viridis')
cmap.set_bad('lightgrey')

cmesh = ax.pcolormesh(xedges, yedges, H_avg_masked.T, norm=colors.SymLogNorm(1), cmap=cmap)
plt.colorbar(cmesh, ax=ax, label='-2Δln L')

# Draw contour lines at the desired thresholds directly on the binned data:
contour_levels = [2.2957, 6.1800]
cs = ax.contour(grid_x, grid_y, H_avg_masked.T, levels=contour_levels, colors='white', linewidths=2)
ax.clabel(cs, fmt={contour_levels[0]:"1σ", contour_levels[1]:"2σ"}, inline=True, fontsize=10)

# Draw best-fit point
if initial_fit_index is not None:
    norm_str = ""
    if bad_norm:
        norm_str = f" (bad norm {bad_norm:.2f})"
    ax.plot(initial_fit[0], initial_fit[1], marker='o', markersize=8, color='blue', label=f'Initial fit: {initial_fit[2]:.2f}{norm_str}')
else:
    ax.plot([], [], ' ', label=f"Initial fit: None (bad norm {bad_norm:.2f})")
ax.plot(grid_best[0], grid_best[1], marker='+', markersize=12, color='white', label=f'Best grid value: {grid_best[2]:.2f}')

ax.set_xlim(*ax.get_xlim())
ax.set_ylim(*ax.get_ylim())
ax.axhline(0,0,1, color='r', linestyle='-', markersize=8)
ax.axvline(1,0,1, color='r', linestyle='-', markersize=8)
ax.set_xlabel("Tau ID correction")
ax.set_ylabel("Tau energy scale shift [%]")
ax.set_title(f"2D Scan (Binned) {title_name}")
ax.legend()
plt.tight_layout()
plt.savefig(f"2D_{scan_tag}_{args.outname}_{args.tag}_binned.pdf")
plt.savefig(f"2D_{scan_tag}_{args.outname}_{args.tag}_binned.png")
plt.close()


if use_root:
    # Define Profile2D histogram
    h2D = ROOT.TProfile2D("h", title_name, n_bins, x_range[0], x_range[1], n_bins, y_range[0], y_range[1])
    
    # Fill the 2D histogram
    for i in range(len(z)):
        h2D.Fill(x[i], y[i], z[i])

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
    c68.SetContourLevel(1, 2.2957)
    c68.SetLineWidth(3)
    c68.SetLineColor(ROOT.kWhite)
    # c68.SetLineColor(ROOT.kRed)
    c95.SetContour(2)
    c95.SetContourLevel(1, 6.1800)
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


    # Add legend
    leg = ROOT.TLegend(0.15, 0.7, 0.4, 0.89)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.SetFillColor(ROOT.kGray)
    leg.AddEntry(gBF, "Best grid", "P")
    leg.AddEntry(c68, "1#sigma CL", "L")
    leg.AddEntry(c95, "2#sigma CL", "L")
    leg.Draw()

    # Add CMS labeling
    # label = ROOT.TText(0.5, 3.74, "CMS Private Work (Data/Simulation)")
    # label.SetTextAlign(13) 
    # label.SetTextSize(0.025) 
    # label.Draw()
    label = ROOT.TLatex()
    label.SetTextSize(0.025)
    label.SetTextAlign(13)
    label.DrawLatex(x_range[0], y_range[1], "CMS #it{#bf{Private Work (Data/Simulation)}}")
    # canv.SetLogz()
    canv.Update()
    # canv.SaveAs(f"2D_{scan_tag}_{args.outname}_{args.tag}.pdf")
    canv.SaveAs(f"2D_{scan_tag}_{args.outname}_{args.tag}.png")
    # canv.SaveAs("scan_2D_"+args.outname+"_id_es.pdf")


#########################
#### 1D Scan Section ####
#########################

# Get data from 1D grid scan files:
file_name_1D_ID = args.in_path+"higgsCombine."+args.name_1D_ID+".MultiDimFit.mH125.root"
f_1D_ID = ROOT.TFile(file_name_1D_ID)
file_name_1D_ES = args.in_path+"higgsCombine."+args.name_1D_ES+".MultiDimFit.mH125.root"
f_1D_ES = ROOT.TFile(file_name_1D_ES)


def extract_1d_scan(file, poi_name:str) -> tuple[list, list, list]:
    t = file.Get("limit")
    poi_vals = []
    dnll_vals = []
    fit = None
    bad_nrm = None
    for ev in t:
        poi_vals.append(getattr(ev, poi_name))
        dnll_vals.append(2 * getattr(ev, "deltaNLL"))
    
    fit_index = None
    if 0.0 in dnll_vals:
        print("[INFO] Initial fit found in the scan! Normalization should be valid.")
        fit_index = dnll_vals.index(0.0)
        fit = [poi_vals[fit_index], dnll_vals[fit_index]]
        del poi_vals[fit_index]
        del dnll_vals[fit_index]
        if np.min(dnll_vals) < 0.0:
            print("[Warning] Bad normalization, even though initial fit found! Normalization done via grid minimum.")
            dnll_vals_min = np.min(dnll_vals)
            dnll_vals = np.array(dnll_vals) - dnll_vals_min
            bad_nrm = dnll_vals_min
    else:
        dnll_vals_min = np.min(dnll_vals)
        dnll_vals = np.array(dnll_vals) - dnll_vals_min
    norm_str = ""
    if bad_nrm:
        norm_str = f" (bad norm {bad_nrm:.2f})"
    return np.array(poi_vals), np.array(dnll_vals), fit, norm_str

def extract_confidence_interval(poi:list, dnll:list, threshold=1.0) -> tuple[float, float]:
    # Sort the arrays by poi value.
    sorted_idx = np.argsort(poi)
    poi_sorted = poi[sorted_idx]
    dnll_sorted = dnll[sorted_idx]

    # Locate the best grid point (the minimum dnll)
    best_fit_index = np.argmin(dnll_sorted)

    # Find the lower edge: scan from best fit to left until last crossing threshold.
    lower_edge = None
    for i in range(best_fit_index, 0, -1):
        if dnll_sorted[i] < threshold and dnll_sorted[i-1] > threshold:
            # Perform linear interpolation between these points:
            x1, x2 = poi_sorted[i-1], poi_sorted[i]
            y1, y2 = dnll_sorted[i-1], dnll_sorted[i]
            lower_edge = x1 + (threshold - y1) * (x2 - x1) / (y2 - y1)

    # Find the upper edge: scan from best fit to right until last crossing threshold.
    upper_edge = None
    for i in range(best_fit_index, len(poi_sorted)-1):
        if dnll_sorted[i] < threshold and dnll_sorted[i+1] > threshold:
            x1, x2 = poi_sorted[i], poi_sorted[i+1]
            y1, y2 = dnll_sorted[i], dnll_sorted[i+1]
            upper_edge = x1 + (threshold - y1) * (x2 - x1) / (y2 - y1)
            
    return lower_edge, upper_edge

# Scale range to have the contours completely inside the later fit:
def scale_contour_range(lower_edge_id: float, upper_edge_id: float, lower_edge_es: float, upper_edge_es: float, scale_range: float, x_borders: list, y_borders: list, scan=scan_tag) -> tuple[float, float, float, float]:
    def _scaler(edge, low_up, scale):
        if low_up == "lower":
            newbound = float(round(edge-scale, 4))
            
        elif low_up == "upper":
            newbound = float(round(edge+scale, 4))
        else:
            raise ValueError("low_up must be 'lower' or 'upper'")
        return newbound
        
    if scan == "closeup_scan":
        yaml_file = f"tau_id_es_measurement/confidence_yaml/1D_full_scan_{args.tag}_{title}_contours.yaml"
        try:
            with open(yaml_file, "r") as f1:
                yml = yaml.safe_load(f1) or {}
        except FileNotFoundError:
            yml = {}
        if yml:
            id_range = yml[args.tag][title]["id_range"]
            es_range = yml[args.tag][title]["es_range"]

    elif scan == "full_scan":
        id_range = x_borders
        es_range = y_borders
    else:
        raise ValueError("scan must be 'closeup_scan' or 'full_scan'")
        
    if lower_edge_id is not None:
        low_id = _scaler(lower_edge_id, "lower", scale_range)
        if low_id < id_range[0]:
            low_id = float(id_range[0])
    else:
        low_id = float(id_range[0])
        print("[WARNING] No lower edge found for ID scan. Set to border value!")
        
    if upper_edge_id is not None:
        up_id = _scaler(upper_edge_id, "upper", scale_range)
        if up_id > id_range[1]:
            up_id = float(id_range[1])
    else:
        up_id = float(id_range[1])
        print("[WARNING] No upper edge found for ID scan. Set to border value!")
    
    if lower_edge_es is not None:
        low_es = _scaler(lower_edge_es, "lower", scale_range*10) # Times 10 for ES larger range.
        if low_es < es_range[0]:
            low_es = float(es_range[0])
    else:
        low_es = float(es_range[0])
        print("[WARNING] No lower edge found for ES scan. Set to border value!")
    
    if upper_edge_es is not None:
        up_es = _scaler(upper_edge_es, "upper", scale_range*10)
        if up_es > es_range[1]:
            up_es = float(es_range[1])
    else:
        up_es = float(es_range[1])
        print("[WARNING] No upper edge found for ES scan. Set to border value!")
    return low_id, up_id, low_es, up_es

# 1D scan for tau ID SF (profiling ES)
poi_id, dnll_id, fit_id, nrm_str_id = extract_1d_scan(f_1D_ID, f"r_EMB_{title}")
lower_edge_id, upper_edge_id = extract_confidence_interval(poi_id, dnll_id, threshold=2.2957)
lower_edge_id_2, upper_edge_id_2 = extract_confidence_interval(poi_id, dnll_id, threshold=6.1800)
plt.figure()
if initial_fit_index is not None:
    plt.axvline(initial_fit[0], color='b', linestyle='--', label='2D Initial fit', lw=4)
else:
    plt.plot([], [], ' ', label="2D Initial fit: None")
plt.axvline(grid_best[0], color='k', linestyle='-.', label='2D Best grid', lw=2)

if fit_id is not None:
    plt.axvline(fit_id[0], color='g', linestyle='--', label=f'1D Initial fit{nrm_str_id}', lw=2)
else:
    plt.plot([], [], ' ', label=f"1D Initial fit: None{nrm_str_id}")
plt.axvline(poi_id[np.argmin(dnll_id)], color='k', linestyle=':', label='1D Best grid',lw=5)
if lower_edge_id is not None:
    plt.axvline(lower_edge_id, color='r', linestyle='--', label=r'$+/-1\sigma$', lw=1)
else:
    print("[WARNING] No lower edge found for ID scan.")
if upper_edge_id is not None:
    plt.axvline(upper_edge_id, color='r', linestyle='--', lw=1)
else:
    print("[WARNING] No upper edge found for ID scan.")
if lower_edge_id_2 is not None:
    plt.axvline(lower_edge_id_2, color='b', linestyle='--', label=r'$+/-2\sigma$', lw=1)
if upper_edge_id_2 is not None:
    plt.axvline(upper_edge_id_2, color='b', linestyle='--', lw=1)
plt.plot(poi_id, dnll_id, marker='o', color='b', label='1D scan (profiled ES)')
plt.axhline(2.2957, color='r', linestyle='-', label=r'$-2\Delta\ln\mathcal{L}\approx$2.3', lw=1)
plt.axhline(6.1800, color='b', linestyle='-', label=r'$-2\Delta\ln\mathcal{L}\approx$6.2', lw=1)
plt.axhline(0, color='k', linestyle='-')
plt.xlabel('tau ID SF')
plt.ylabel(r'$-2\Delta\ln\mathcal{L}$')
plt.title(f'1D Scan tau ID SF ({title_name})')
plt.legend()
# if np.max(dnll_id) > 3*1e2 or np.min(dnll_id) < -1:
#     plt.yscale('symlog', linthresh=1e-3)
plt.tight_layout()
plt.savefig(f"1D_{scan_tag}_tauID_{args.outname}_{args.tag}.pdf")
plt.savefig(f"1D_{scan_tag}_tauID_{args.outname}_{args.tag}.png")
plt.close()

# 1D scan for tau ES shift (profiling ID)
poi_es, dnll_es, fit_es, norm_str_es = extract_1d_scan(f_1D_ES, f"ES_{title}")
lower_edge_es, upper_edge_es = extract_confidence_interval(poi_es, dnll_es, threshold=2.2957)
lower_edge_es_2, upper_edge_es_2 = extract_confidence_interval(poi_es, dnll_es, threshold=6.1800)
plt.figure()
if initial_fit_index is not None:
    plt.axvline(initial_fit[1], color='b', linestyle='--', label='2D Initial fit',lw=4)
else:
    plt.plot([], [], ' ', label="2D Initial fit: None")
plt.axvline(grid_best[1], color='k', linestyle='-.', label='2D Best grid', lw=2)
if fit_es is not None:
    plt.axvline(fit_es[0], color='g', linestyle='--', label=f'1D Initial fit{norm_str_es}', lw=2)
else:
    plt.plot([], [], ' ', label=f"1D Initial fit: None {norm_str_es}")
plt.axvline(poi_es[np.argmin(dnll_es)], color='k', linestyle=':', label='1D Best grid',lw=5)
if lower_edge_es is not None:
    plt.axvline(lower_edge_es, color='r', linestyle='--', label=r'$+/-1\sigma$', lw=1)
else:
    print("[WARNING] No lower edge found for ES scan.")
if upper_edge_es is not None:
    plt.axvline(upper_edge_es, color='r', linestyle='--', lw=1)
else:
    print("[WARNING] No upper edge found for ES scan.")
if lower_edge_es_2 is not None:
    plt.axvline(lower_edge_es_2, color='b', linestyle='--', label=r'$+/-2\sigma$', lw=1)
if upper_edge_es_2 is not None:
    plt.axvline(upper_edge_es_2, color='b', linestyle='--', lw=1)
plt.plot(poi_es, dnll_es, marker='o', color='b',label='1D scan (profiled ID)')
plt.axhline(2.2957, color='r', linestyle='-', label=r'$-2\Delta\ln\mathcal{L}\approx$2.3', lw=1)
plt.axhline(6.1800, color='b', linestyle='-', label=r'$-2\Delta\ln\mathcal{L}\approx$6.2', lw=1)
plt.axhline(0, color='k', linestyle='-')
plt.xlabel('tau ES shift [%]')
plt.ylabel(r'$-2\Delta\ln\mathcal{L}$')
plt.title(f'1D Scan tau ES shift ({title_name})')
plt.legend()
# if np.max(dnll_es) > 3*1e2 or np.min(dnll_es) < -1:
#     plt.yscale('symlog', linthresh=1e-3)
plt.tight_layout()
plt.savefig(f"1D_{scan_tag}_tauES_{args.outname}_{args.tag}.pdf")
plt.savefig(f"1D_{scan_tag}_tauES_{args.outname}_{args.tag}.png")
plt.close()


low_id, up_id, low_es, up_es = scale_contour_range(lower_edge_id, upper_edge_id, lower_edge_es, upper_edge_es, args.scale_range, x_range, y_range, scan=scan_tag)
low_id_2, up_id_2, low_es_2, up_es_2 = scale_contour_range(lower_edge_id_2, upper_edge_id_2, lower_edge_es_2, upper_edge_es_2, args.scale_range, x_range, y_range, scan=scan_tag)
# Problems with best fit workaround: Use grid minimum instead:
fit_id = round(poi_id[np.argmin(dnll_id)].item(),4)
fit_es = round(poi_es[np.argmin(dnll_es)].item(),4)
# Check if values for yaml are python floats, not numpy floats


yaml_file_1D = f"tau_id_es_measurement/confidence_yaml/1D_{scan_tag}_{args.tag}_{title}_contours.yaml"
try:
    with open(yaml_file_1D, "r") as f1:
        yaml_data1 = yaml.safe_load(f1) or {}
except FileNotFoundError:
    yaml_data1 = {}

if args.tag not in yaml_data1:
    yaml_data1[args.tag] = {}
yaml_data1[args.tag][title] = {
    "ID": [low_id, up_id],
    "ID_2": [low_id_2, up_id_2],
    "ES": [low_es, up_es],
    "ES_2": [low_es_2, up_es_2],
    "fit": {"ID": fit_id, "ES": fit_es},
    "scale_range": args.scale_range
}

if scan_tag == "full_scan":
    yaml_data1[args.tag][title]["id_range"] = [x_range[0], x_range[1]]
    yaml_data1[args.tag][title]["es_range"] = [y_range[0], y_range[1]]

def np_float_representer(dumper, data):
    return dumper.represent_float(float(data))

yaml.add_representer(np.float32, np_float_representer)
yaml.add_representer(np.float64, np_float_representer)

# Double check data types saved to yaml file
def _python_float_check(value):
    if isinstance(value, float) and not isinstance(value, np.floating):
        return True
    else:
        return False

def check_types(obj, path="root"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            check_types(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_types(v, f"{path}[{i}]")
    elif isinstance(obj, tuple):
        for i, v in enumerate(obj):
            check_types(v, f"{path}({i})")
    elif isinstance(obj, np.generic):
        print(f"Found NumPy type at {path}: {type(obj)}")

check_float_list = [low_id, up_id, low_es, up_es, low_id_2, up_id_2, low_es_2, up_es_2, fit_id, fit_es, args.scale_range, *x_range, *y_range]
check_types(yaml_data1)
if any([not _python_float_check(val) for val in check_float_list]):
    breakpoint()


with open(yaml_file_1D, "w") as f2:
    yaml.safe_dump(yaml_data1, f2, default_flow_style=False)
print(f"[INFO] Contour extrema and best fit coordinates saved in {yaml_file_1D}")