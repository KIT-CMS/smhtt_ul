import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import mplhep as hep
import ROOT
import argparse

# Create the parser and add the directory argument
parser = argparse.ArgumentParser(description='Load JSON data from a directory.')
parser.add_argument('--name',type=str, help='Name of the file')
parser.add_argument('--in-path',type=str, help='Input path to the 2D scan file') 
parser.add_argument('--tau-id-poi',type=str, help='Name of the tau ID POI')
parser.add_argument('--tau-es-poi',type=str, help='Name of the tau ES POI')
parser.add_argument('--outname',type=str, help='Name of the outputfile')

# Parse the command line arguments
args = parser.parse_args()

filepath = f"{args.in_path}higgsCombine.{args.name}.MultiDimFit.mH125.root"

# Load the .root file
file = ROOT.TFile.Open(filepath)

# Get the TTree from the file
tree = file.Get("limit")
 
tauid = list()
tes = list()
deltaNLL = list()

# Iterate over the entries in the TTree
for entry in tree:
    # Append the x, y, and deltaNLL values to the respective lists
    # if entry.deltaNLL > 0:
    tauid.append(getattr(entry, args.tau_id_poi))
    tes.append(getattr(entry, args.tau_es_poi))
    deltaNLL.append(entry.deltaNLL)

print(f"Best fit: {args.tau_id_poi} {tauid[0]}, {args.tau_es_poi} {tes[0]}, deltaNLL {deltaNLL[0]}")
tauid = np.array(tauid[1:]) 
tes = np.array(tes[1:]) 
deltaNLL = np.array(deltaNLL[1:])
deltaNLL[deltaNLL<0] = 0.1

print(tauid)
print(tes)
print(deltaNLL)

# Define the bin edges to be halfway between the unique values
x_unique = np.sort(np.unique(tauid))
y_unique = np.sort(np.unique(tes))

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
h = ax.hist2d(tauid, tes, weights=2*deltaNLL, bins=(x_edges, y_edges), cmap='viridis', norm=LogNorm())

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
hep.cms.label(ax=ax, data=True, label='Private Work')
plt.ylabel('Tau ES in %')
plt.xlabel('Tau ID SF')

plt.savefig(f"{args.in_path}/2D_scan_plot.pdf")
plt.savefig(f"{args.in_path}/2D_scan_plot.png")
plt.close()

