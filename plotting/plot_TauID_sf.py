import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import mplhep as hep
import argparse
import glob
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
sns.set_style("ticks")
plt.style.use(hep.style.CMS)


def load_fitresults_from_file(filename):
    # print("[INFO] Print fit results from file {}.".format(filename))
    f = ROOT.TFile(filename)
    if f == None:
        raise Exception("[ERROR] File {} not found.".format(filename))

    tree = f.Get("limit")
    if tree == None:
        raise Exception("[ERROR] Tree {} not found in file {}.".format("limit", filename))
    num_entries = tree.GetEntries()

    indices = {}
    count = 1
    results = {}
    for key in tree.GetListOfBranches():
        name = key.GetName()
        if name.startswith("r"):
            indices[name] = count
            count += 2
            results[name] = [-999, -999, -999]

    for i, row in enumerate(tree):
        for name in indices:
            if i == 0:
                results[name][0] = getattr(row, name)
            elif i == indices[name]:
                results[name][1] = getattr(row, name)
            elif i == indices[name]+1:
                results[name][2] = getattr(row, name)
    data = {}
    for name in results:
        data["r"] = results[name][0]
        data["d"] = results[name][1]
        data["u"] = results[name][2]
        # print("[INFO] {0:<30}: {1:.4f} {2:.4f} +{3:.4f}".format(name, data["r"], data["d"]-data["r"], data["u"]-data["r"]))
    return data




# first a simple argparser to the the datacard directory
parser = argparse.ArgumentParser(description='Plot the tau ID SF')
parser.add_argument('--wp', type=str, default='tight', help='TauID WP')
parser.add_argument('--input', type=str, default='', help='input')
parser.add_argument('--output', type=str, default='', help='output')

args = parser.parse_args()

data = {}
# glob for the .root files in the input folder
files = glob.glob(args.input + 'htt_mt_*/*MultiDimFit.mH125.root')
print("[INFO] Found {} files.".format(len(files)))
for fitfile in files:
    data[fitfile] = load_fitresults_from_file(fitfile)

pt_binning = ["20to25","25to30","30to35","35to40","Gt40"]
dm_binning = ["DM0", "DM1", "DM10_11"]
pt_labels = ["20-25", "25-30", "30-35", "35-40", ">40"]
dm_labels = ["0", "1", "10 & 11"]

# first the pt_binned plot
print("[INFO] Plotting pt binned SF.")
pt_binned_data = {}
for bin in pt_binning:
    for dataentry in data.keys():
        if bin in dataentry:
            pt_binned_data[bin] = data[dataentry]
# now plot the values
plt.rcParams.update({'font.size': 17})
fig, ax = plt.subplots(figsize=(7,7))
y = []
x = []
errors = [[],[]]
for i,bin in enumerate(pt_binning):
    r = pt_binned_data[bin]["r"]
    d = pt_binned_data[bin]["d"]
    u = pt_binned_data[bin]["u"]
    y.append(r)
    x.append(i)
    errors[0].append(abs(d-r))
    errors[1].append(abs(u-r))
    # print(i, r, [d-r, u-r], bin)
ax.errorbar(x=x, y=y, xerr=0, yerr=errors ,fmt = 'o', ecolor = 'black',color='black', capsize=1.5)
hep.cms.label(ax=ax, label=f"TauID {args.wp} WP", data=True, lumi="59.83", fontsize=17)
ax.set_xlabel(r"$p_{T}(\tau_h)$ [GeV]")
ax.set_ylabel("Correction Factor")
ax.set_xticks(x, minor=False)
ax.set_xticklabels(pt_labels, rotation = 45, ha="center")
ax.set_ylim(0.0, 1.5)
ax.set_xlim(-0.5, len(pt_binning)-0.5)
# set the default fontsize
plt.minorticks_off()
plt.tight_layout()
plt.savefig(f"{args.output}/tauID_sf_{args.wp}_pt_binned.pdf")
plt.savefig(f"{args.output}/tauID_sf_{args.wp}_pt_binned.png")

# now the dm_binned plot
print("[INFO] Plotting dm binned SF.")
dm_binned_data = {}
for bin in dm_binning:
    for dataentry in data.keys():
        if bin in dataentry:
            dm_binned_data[bin] = data[dataentry]
# now plot the values
plt.rcParams.update({'font.size': 17})
fig, ax = plt.subplots(figsize=(7,7))
y = []
x = []
errors = [[],[]]
for i,bin in enumerate(dm_binning):
    r = dm_binned_data[bin]["r"]
    d = dm_binned_data[bin]["d"]
    u = dm_binned_data[bin]["u"]
    y.append(r)
    x.append(i)
    errors[0].append(abs(d-r))
    errors[1].append(abs(u-r))
ax.errorbar(x=x, y=y, xerr=0, yerr=errors ,fmt = 'o', ecolor = 'black',color='black', capsize=1.5)
hep.cms.label(ax=ax, label=f"TauID {args.wp} WP", data=True, lumi="59.83", fontsize=17)
ax.set_xlabel(r"$\tau_h$ decay mode")
ax.set_ylabel("Correction Factor")
ax.set_xticks(x, minor=False)
ax.set_xticklabels(dm_labels, rotation = 45, ha="center")
ax.set_ylim(0.0, 1.5)
ax.set_xlim(-0.5, len(dm_binning)-0.5)
# set the default fontsize
plt.minorticks_off()
plt.tight_layout()
plt.savefig(f"{args.output}/tauID_sf_{args.wp}_dm_binned.pdf")
plt.savefig(f"{args.output}/tauID_sf_{args.wp}_dm_binned.png")