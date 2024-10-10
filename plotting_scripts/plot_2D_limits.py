import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import mplhep as hep
import os
import json
import argparse

# Create the parser and add the directory argument
parser = argparse.ArgumentParser(description='Load JSON data from a directory.')
parser.add_argument('-d', '--directory', required=True, help='The directory to load JSON files from.')
parser.add_argument('-c', '--channel', required=True, help='Which channel should be plotted.')
parser.add_argument('-p', '--process', required=True, help='Which process is plotted.')

# Parse the command line arguments
args = parser.parse_args()

if args.channel == 'et':
    ch_str = r'e\tau_h'
elif args.channel == 'mt':
    ch_str = r'\mu\tau_h'
elif args.channel == 'tt':
    ch_str = r'\tau_h\tau_h'
elif args.channel == 'all':
    ch_str = r'e\tau_h +\mu\tau_h +\tau_h\tau_h'
else:
    print(f'Wrong channel: {args.channel}')    

if args.process == 'Ytt':
    process_str = r'\sigma\times BR(X\rightarrow Y(\tau\tau)H(bb))'
elif args.process == 'Ybb':
    process_str = r'\sigma\times BR(X\rightarrow Y(bb)H(\tau\tau))'
elif args.process == 'combined':
    process_str = r'\sigma(X\rightarrow YH)\times BR(Y\rightarrow bb/\tau\tau)'
else:
    print(f'Wrong process: {args.process}')

data = dict()

# Iterate over every file in the directory
for filename in os.listdir(args.directory):
    # Check if the file is a JSON file
    if filename.endswith('.json'):
        # Construct the full file path
        filepath = os.path.join(args.directory, filename)
        # Split the filename by "_"
        mX_str = filename.split("_")[3]
        # Open the file and load the JSON data
        with open(filepath, 'r') as f:
            file_data = json.load(f)
            # Append the data to your list
            data[mX_str] = file_data
      
mass_X = list()
mass_Y = list()
limit_values = list()

scaling = 0.1

for mX in data:
    for mY in data[mX]:
        mass_X.append(float(mX))
        mass_Y.append(float(mY))
        limit_values.append(scaling * data[mX][mY]["exp0"]) # 0.1 is scaling to 1 pb
        
# Assuming mass_X, mass_Y, and limit_values are numpy arrays
mass_X = np.array(mass_X)  # replace with your data
mass_Y = np.array(mass_Y)  # replace with your data
limit_values = np.array(limit_values)  # replace with your data

# Define the bin edges to be halfway between the unique values
x_unique = np.sort(np.unique(mass_X))
y_unique = np.sort(np.unique(mass_Y))

# Compute the differences between consecutive unique values
x_diff = np.diff(x_unique) / 2
y_diff = np.diff(y_unique) / 2

# Add an extra bin edge at the end to ensure all values are included
x_edges = np.concatenate([[x_unique[0] - x_diff[0]], x_unique[:-1] + x_diff, [x_unique[-1] + x_diff[-1]]])
y_edges = np.concatenate([[y_unique[0] - y_diff[0]], y_unique[:-1] + y_diff, [y_unique[-1] + y_diff[-1]]])

# Create a new figure with CMS style
plt.style.use(hep.style.CMS)

fig, ax = plt.subplots()
# h = ax.hist2d(mass_X, mass_Y, weights=limit_values, bins=(x_edges, y_edges), cmap='viridis', norm=LogNorm())
h = ax.hist2d(mass_X, mass_Y, weights=limit_values, bins=(x_edges, y_edges), cmap='viridis', norm=LogNorm(vmin=0.001, vmax=1.0))
# plt.xticks(x_unique)
# plt.yticks(y_unique)
plt.colorbar(h[3], ax=ax, label=r'95% CL limit on $' + process_str + r'$ (pb)')
# Add CMS label
lumi = 59.83
hep.cms.label(ax=ax, data=True, label='Private Work', lumi=lumi, lumi_format='{:.1f}', loc=2)
plt.text(0, 1.005, r'$' + ch_str + r'$', transform=plt.gca().transAxes, va='bottom', ha='left', fontsize='small')
plt.xlabel(r'$m_X$ (GeV)')
plt.ylabel(r'$m_Y$ (GeV)')
# plt.grid(True)
plt.savefig(args.directory + "/2D_limit_plot.pdf")
plt.savefig(args.directory + "/2D_limit_plot.png")
plt.close()
# plt.show()