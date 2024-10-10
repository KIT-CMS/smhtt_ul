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
parser.add_argument('-y', '--massY', required=True, help='Which mass for Y should be plotted.')

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
    "70": [0.151, 0.014, 0.0043, 0.0058, 0.0233, 0.112], 
    "125": [0.019, 0.0044, 0.0055, 0.023, 0.112],
    "250": [0.079, 0.0053, 0.005, 0.02, 0.097],
    "500": [0.0113, 0.0041, 0.0166, 0.0738],
    "1000": [0.0268, 0.0086, 0.0512],
    "1600": [0.0044, 0.0234],
    "2800": [0.0231],
}

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
limit_obs = list()
limit_exp = list()
limit_1sigma_up = list()
limit_2sigma_up = list()
limit_1sigma_down = list()
limit_2sigma_down = list()

scaling = 0.1

for mX in data:
    for mY in data[mX]:
        if float(args.massY) == float(mY):
            mass_X.append(float(mX))
            limit_exp.append(scaling * data[mX][mY]['exp0']) # 0.1 is scaling to 1 pb
            limit_1sigma_up.append(scaling * data[mX][mY]['exp+1']) # 0.1 is scaling to 1 pb
            limit_2sigma_up.append(scaling * data[mX][mY]['exp+2']) # 0.1 is scaling to 1 pb
            limit_1sigma_down.append(scaling * data[mX][mY]['exp-1']) # 0.1 is scaling to 1 pb
            limit_2sigma_down.append(scaling * data[mX][mY]['exp-2']) # 0.1 is scaling to 1 pb
            if 'obs' in data[mX]:
                limit_obs.append(scaling * data[mX][mY]['obs']) # 0.1 is scaling to 1 pb
            else:
                limit_obs.append(scaling * data[mX][mY]['exp0']) # 0.1 is scaling to 1 pb    
        
# Assuming mass_X, mass_Y, and limit_values are numpy arrays
mass_X = np.array(mass_X)
limit_exp = np.array(limit_exp)  
limit_1sigma_up = np.array(limit_1sigma_up) 
limit_2sigma_up = np.array(limit_2sigma_up) 
limit_1sigma_down = np.array(limit_1sigma_down) 
limit_2sigma_down = np.array(limit_2sigma_down) 
limit_obs = np.array(limit_obs)  

# sorting for mass of Y
sort_indices = np.argsort(mass_X)
mass_X = mass_X[sort_indices]
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
ax.fill_between(mass_X, limit_2sigma_down, limit_2sigma_up, facecolor=cms_blue, alpha=1.0, label=r'Expected limit $\pm$ 2$\sigma$')

# Draw 1-sigma band
ax.fill_between(mass_X, limit_1sigma_down, limit_1sigma_up, facecolor=cms_yellow, alpha=1.0, label=r'Expected limit $\pm$ 1$\sigma$')

# Draw expected limit line
ax.plot(mass_X, limit_exp, 'k--', label='Expected 95% upper limit')

if args.process == 'Ybb':
    # Draw previous analysis expected limit line
    xAxis = mass_X
    xAxis[xAxis == 4000] = 3000
    ax.plot(xAxis, previous_analysis[args.massY], 'r--', label='Expected 95% UL (prev. result)')

# Draw observed limit line
# ax.plot(mass_Y, limit_obs, 'k-', label='Observed 95% CL')

# Add CMS label
lumi = 59.83
hep.cms.label(ax=ax, data=True, label='Private Work', lumi=lumi, lumi_format='{:.1f}', loc=2)
plt.text(0, 1.005, r'$' + ch_str + r'$, $m_Y =' + args.massY + r'$ GeV', transform=plt.gca().transAxes, va='bottom', ha='left', fontsize='small')

# Set labels and legend
ax.set_yscale('log')
ax.set_xlim(240., 4000.)
ax.set_ylim(0.0001, 100.)
ax.set_xlabel(r'$m_X$ (GeV)')
ax.set_ylabel(r'95% CL limit on $' + process_str + r'$ (pb)')
ax.legend(loc='best')

plt.savefig(args.directory + f"/limit_plot_mY{args.massY}.pdf")
plt.savefig(args.directory + f"/limit_plot_mY{args.massY}.png")
plt.close()

# plt.show()
