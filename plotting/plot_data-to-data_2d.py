#code adapted from FCCAnalyses/do_plots.py

import sys
import os
import os.path
import ntpath
import importlib
import copy
import re
import logging
import numpy as np
import uproot
import matplotlib.pyplot as plt

def sorted_dict_values(dic: dict) -> list:
    ''''
    Sort values in the dictionary.
    '''
    keys = sorted(dic)
    return [dic[key] for key in keys]

def make_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.system("cp /web/sgiappic/public_html/index.php {}".format(directory)) #copy index to show plots in web page automatically
        print(f"Directory created successfully.")
    else:
        print(f"Directory already exists.")

# directory with final stage files
DIRECTORY = "/work/sgiappic/smhtt_ul/output/"

#directory where you want your plots to go
DIR_PLOTS = '/web/sgiappic/public_html/CMS_HTT/Run2024/data-to-data/' 

#now you can list all the histograms that you want to plot
VARIABLES_LIST = [
    "pt_1", "eta_1", "phi_1", "tau_decaymode_1", "mt_1", "iso_1", "mass_1",
    "pt_2", "eta_2", "phi_2", "tau_decaymode_2", "mt_2", "iso_2", "mass_2",
    "jpt_1", "jeta_1", "jphi_1",
    "jpt_2", "jeta_2", "jphi_2",
    "bpt_1", "beta_1", "bphi_1", "btag_value_1",
    "bpt_2", "beta_2", "bphi_2", "btag_value_2",
    "pt_tt", "pt_tt", "pt_vis", "pt_dijet", "pt_ttjj",
    "mjj", "mt_tot", "m_vis",
    "met", "metphi", "mTdileptonMET", "metSumEt",
    "nbtag", "njets",
    "q_1", "pzetamissvis", "jet_hemisphere",
    "deltaR_ditaupair",
]

era = [
    "2024",
    "2025"
]

channel = [
    "et",
    "mt",
    "tt",
]

# Modify the script to plot the 2D distribution in the eta-phi plane of the ratio of the two plots
for ch in channel:
    for i in [1, 2]:
        histos = []

        # Read histograms from ROOT files
        for s in era:
            file_path = f"{DIRECTORY}/{s}-{ch}-htt_251211_2024-25_v2-251211/control_shapes-{s}-{ch}-htt_251211_2024-25_v2-251211.root"
            with uproot.open(file_path) as root_file:
                eta_hist = root_file[f"data#{ch}#Nominal#eta_{i}"].to_numpy()
                phi_hist = root_file[f"data#{ch}#Nominal#phi_{i}"].to_numpy()

                # Normalize histograms
                eta_values, eta_edges = eta_hist
                phi_values, phi_edges = phi_hist

                if eta_values.sum() > 0:
                    eta_values = eta_values / eta_values.sum()
                if phi_values.sum() > 0:
                    phi_values = phi_values / phi_values.sum()

                histos.append((eta_values, eta_edges, phi_values, phi_edges))

        # Avoid division by zero by replacing zeros with NaN
        eta_values_0 = np.where(histos[0][0] == 0, np.nan, histos[0][0])
        phi_values_0 = np.where(histos[0][2] == 0, np.nan, histos[0][2])

        # Calculate the ratio of histograms
        eta_ratio = histos[1][0] / eta_values_0
        phi_ratio = histos[1][2] / phi_values_0

        # Create 2D grid for eta and phi
        eta_centers = 0.5 * (histos[0][1][:-1] + histos[0][1][1:])
        phi_centers = 0.5 * (histos[0][3][:-1] + histos[0][3][1:])
        eta_grid, phi_grid = np.meshgrid(eta_centers, phi_centers)

        # Create 2D ratio array
        ratio_2d = np.outer(eta_ratio, phi_ratio)

        # Adjust the ratio_2d dimensions to match the grid size
        ratio_2d = ratio_2d[: eta_grid.shape[0] - 1, : phi_grid.shape[1] - 1]

        # Plot the 2D ratio
        plt.figure(figsize=(8, 8))
        plt.pcolormesh(eta_grid, phi_grid, ratio_2d, cmap="BuPu", shading="auto")
        plt.colorbar(label="Ratio")
        plt.xlabel("eta")
        plt.ylabel("phi")
        plt.title(f"Eta-Phi {i}, 2025/2024 normalised")

        # Increase the number of ticks on the axes
        plt.locator_params(axis='x', nbins=15)
        plt.locator_params(axis='y', nbins=15)

        # Save the plot
        dir = f"{DIR_PLOTS}/{ch}/"
        make_dir_if_not_exists(dir)
        plt.savefig(f"{dir}/ratio_2d_{ch}_{i}.png")
        plt.close()