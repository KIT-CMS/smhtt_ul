import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import mplhep as hep
import os
import ROOT
import argparse
from scipy.stats import chi2

# Create the parser and add the directory argument
parser = argparse.ArgumentParser(description='Load JSON data from a directory.')
parser.add_argument('-d', '--directory', required=True, help='The directory to load JSON files from.')
parser.add_argument('-x', '--massX', required=True, help='Which mass for X should be plotted.')
parser.add_argument('-y', '--massY', required=True, help='Which mass for Y should be plotted.')

# Parse the command line arguments
args = parser.parse_args()

filepath = os.path.join(f"{args.directory}/{args.massX}_{args.massY}", f"higgsCombine2018.MultiDimFit.mH{args.massY}.root")

# Load the .root file
file = ROOT.TFile.Open(filepath)

# Get the TTree from the file
tree = file.Get("limit")
      
r_NMSSM = list()
alpha_Ybb = list()
deltaNLL = list()

# Iterate over the entries in the TTree
for entry in tree:
    # Append the x, y, and deltaNLL values to the respective lists
    # if entry.deltaNLL > 0:
    r_NMSSM.append(entry.r_NMSSM)
    alpha_Ybb.append(entry.alpha_Ybb)
    deltaNLL.append(entry.deltaNLL)

print(f"Best fit: r_NMSSM {r_NMSSM[0]}, alpha_Ybb {alpha_Ybb[0]}, deltaNLL {deltaNLL[0]}")
r_NMSSM = np.array(r_NMSSM[1:]) 
alpha_Ybb = np.array(alpha_Ybb[1:]) 
deltaNLL = np.array(deltaNLL[1:])

# Define the bin edges to be halfway between the unique values
x_unique = np.sort(np.unique(alpha_Ybb))
y_unique = np.sort(np.unique(r_NMSSM))

# Compute the differences between consecutive unique values
x_diff = np.diff(x_unique) / 2
y_diff = np.diff(y_unique) / 2

# Add an extra bin edge at the end to ensure all values are included
x_edges = np.concatenate([[x_unique[0] - x_diff[0]], x_unique[:-1] + x_diff, [x_unique[-1] + x_diff[-1]]])
y_edges = np.concatenate([[y_unique[0] - y_diff[0]], y_unique[:-1] + y_diff, [y_unique[-1] + y_diff[-1]]])

# Create a new figure with CMS style
plt.style.use(hep.style.CMS)

fig, ax = plt.subplots()
# h = ax.scatter(alpha_Ybb, r_NMSSM, c=2*deltaNLL, cmap='viridis', norm=LogNorm())
h = ax.hist2d(alpha_Ybb, r_NMSSM, weights=2*deltaNLL, bins=(x_edges, y_edges), cmap='viridis', norm=LogNorm())

# Calculate the 1,2 and 3 sigma levels for a 2 dof 2*nll
sigma_levels = [1,4,9]

# Draw contours at the 1 and 2 sigma levels
contour = ax.contour(x_unique, y_unique, h[0].T, levels=sigma_levels, colors='#FFFFFF')
fmt = {}
strs = [r'$1\sigma$', r'$2\sigma$', r'$3\sigma$']
for l, s in zip(contour.levels, strs):
    fmt[l] = s
ax.clabel(contour, contour.levels, inline=True, fmt=fmt, fontsize=16)

plt.colorbar(h[3], ax=ax, label=r'-2$\Delta$LL')
# Add CMS label
lumi = 59.83
hep.cms.label(ax=ax, data=True, label='Private Work', lumi=lumi, lumi_format='{:.1f}')
plt.ylabel(r'$r_{NMSSM}$')
plt.xlabel(r'$\alpha_{Y(bb)}$')

plt.savefig(f"{args.directory}/{args.massX}_{args.massY}" + "/2D_scan_plot.pdf")
plt.savefig(f"{args.directory}/{args.massX}_{args.massY}" + "/2D_scan_plot.png")
plt.close()