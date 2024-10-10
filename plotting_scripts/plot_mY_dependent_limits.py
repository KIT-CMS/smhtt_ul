import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep
import os
import json
import argparse

# Create the parser and add the directory argument
parser = argparse.ArgumentParser(description='Load JSON data from a directory.')
parser.add_argument('-d', '--directory', required=True, help='The directory to load JSON files from.')
parser.add_argument('-c', '--channel', required=True, help='Which channel should be plotted.')
parser.add_argument('-p', '--process', required=True, help='Which process should be plotted.')
parser.add_argument('-x', '--massX', required=True, help='Which mass for X should be plotted.')

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

previous_analysis = {
    "240": [0.151], 
    "450": [0.014, 0.019, 0.079],
    "800": [0.0043, 0.0044, 0.0053, 0.0113],
    "1200": [0.0058, 0.0055, 0.005, 0.0041, 0.0268],
    "2000": [0.0233, 0.023, 0.02, 0.0166, 0.0086, 0.0044],
    "4000": [0.112, 0.112, 0.097, 0.0738, 0.0512, 0.0234, 0.0231],
}

# Iterate over every file in the directory
for filename in os.listdir(args.directory):
    # Check if the file is a JSON file
    if filename.endswith('.json') and args.massX in filename:
        # Construct the full file path
        filepath = os.path.join(args.directory, filename)
        # Open the file and load the JSON data
        with open(filepath, 'r') as f:
            file_data = json.load(f)
            # Append the data to your list
            data = file_data
      
mass_Y = list()
limit_obs = list()
limit_exp = list()
limit_1sigma_up = list()
limit_2sigma_up = list()
limit_1sigma_down = list()
limit_2sigma_down = list()

scaling = 0.1

for mY in data:
    mass_Y.append(float(mY))
    limit_exp.append(scaling * data[mY]['exp0']) # 0.1 is scaling to 1 pb
    limit_1sigma_up.append(scaling * data[mY]['exp+1']) # 0.1 is scaling to 1 pb
    limit_2sigma_up.append(scaling * data[mY]['exp+2']) # 0.1 is scaling to 1 pb
    limit_1sigma_down.append(scaling * data[mY]['exp-1']) # 0.1 is scaling to 1 pb
    limit_2sigma_down.append(scaling * data[mY]['exp-2']) # 0.1 is scaling to 1 pb
    if 'obs' in data[mY]:
        limit_obs.append(scaling * data[mY]['obs']) # 0.1 is scaling to 1 pb
    else:
        limit_obs.append(scaling * data[mY]['exp0']) # 0.1 is scaling to 1 pb
        
# Assuming mass_X, mass_Y, and limit_values are numpy arrays
mass_Y = np.array(mass_Y)
limit_exp = np.array(limit_exp)  
limit_1sigma_up = np.array(limit_1sigma_up) 
limit_2sigma_up = np.array(limit_2sigma_up) 
limit_1sigma_down = np.array(limit_1sigma_down) 
limit_2sigma_down = np.array(limit_2sigma_down) 
limit_obs = np.array(limit_obs)  

# sorting for mass of Y
sort_indices = np.argsort(mass_Y)
mass_Y = mass_Y[sort_indices]
limit_exp = limit_exp[sort_indices]
limit_1sigma_up = limit_1sigma_up[sort_indices]
limit_2sigma_up = limit_2sigma_up[sort_indices]
limit_1sigma_down = limit_1sigma_down[sort_indices]
limit_2sigma_down = limit_2sigma_down[sort_indices]
limit_obs = limit_obs[sort_indices]

# Create a new figure with CMS style
plt.style.use(hep.style.CMS)

# Create the plot
fig, ax = plt.subplots()

cms_blue = '#85D1FBff' 
cms_yellow = '#FFDF7Fff'

# Draw 2-sigma band
ax.fill_between(mass_Y, limit_2sigma_down, limit_2sigma_up, facecolor=cms_blue, alpha=1.0, label=r'Expected limit $\pm$ 2$\sigma$')

# Draw 1-sigma band
ax.fill_between(mass_Y, limit_1sigma_down, limit_1sigma_up, facecolor=cms_yellow, alpha=1.0, label=r'Expected limit $\pm$ 1$\sigma$')

# Draw expected limit line
ax.plot(mass_Y, limit_exp, 'k--', label='Expected 95% upper limit')

if args.process == 'Ybb':
    # Draw previous analysis expected limit line
    ax.plot(mass_Y, previous_analysis[args.massX], 'r--', label='Expected 95% UL (prev. result)')

# Draw observed limit line
# ax.plot(mass_Y, limit_obs, 'k-', label='Observed 95% CL')

# Add CMS label
lumi = 59.83
hep.cms.label(ax=ax, data=True, label='Private Work', lumi=lumi, lumi_format='{:.1f}', loc=2)
plt.text(0, 1.005, r'$' + ch_str + r'$, $m_X =' + args.massX + r'$ GeV', transform=plt.gca().transAxes, va='bottom', ha='left', fontsize='small')

# Set labels and legend
ax.set_yscale('log')
ax.set_xlim(60., 2800.)
ax.set_ylim(0.0001, 100.)
ax.set_xlabel(r'$m_Y$ (GeV)')
ax.set_ylabel(r'95% CL limit on $' + process_str + r'$ (pb)')
ax.legend(loc='best')

plt.savefig(args.directory + f"/limit_plot_mX{args.massX}.pdf")
plt.savefig(args.directory + f"/limit_plot_mX{args.massX}.png")
plt.close()

# plt.show()
