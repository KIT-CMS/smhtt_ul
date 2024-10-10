#!/usr/bin/env python

import argparse
import os
import json
import yaml
import numpy as np
# import seaborn as sns

import matplotlib as mpl
import mplhep as hep

# mpl.use('Agg')
# mpl.rcParams['font.size'] = 16
import matplotlib.pyplot as plt
# fromcno matplotlib import cm
# sns.set_style("ticks")
# hep.style.use("CMS")
hep.style.use({"font.size": 16})

import logging
logger = logging.getLogger("plot_gof")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# TODO: Update label dict
labeldict = {
    'pt_1' : '$p_{T}(\\tau_1)$',
    'pt_2' : '$p_{T}(\\tau_2)$',
    'eta_1': '$\\eta(\\tau_1$)',
    'eta_2': '$\\eta(\\tau_2$)',
    'phi_1': '$\\phi(\\tau_1$)',
    'phi_2': '$\\phi(\\tau_2$)',
    'iso_1' : 'iso($\\tau_1$)',
    'iso_2' : 'iso($\\tau_2$)',
    'mass_1' : 'mass($\\tau_1$)',
    'mass_2' : 'mass($\\tau_2$)',
    'tau_decaymode_1': 'decay mode 1',
    'tau_decaymode_2': 'decay mode 2',
    'mt_1' : '$m_{T}(\\tau_1,MET)$',
    'mt_2' : '$m_{T}(\\tau_2,MET)$',
    'deltaR_ditaupair': '$\Delta$R $(\\tau_1, \\tau_2)$',
    'm_vis' : 'visible di-$\\tau$ mass',
    'm_fastmtt': 'fastMTT di-$\\tau$ mass',
    'pt_fastmtt': 'fastMTT $p_{T}(\\tau\\tau)$',
    'eta_fastmtt': 'fastMTT $\\eta(\\tau\\tau)$',
    'phi_fastmtt': 'fastMTT $\phi(\\tau\\tau)$',
    'boosted_pt_1': '$p_{T}(\\tau_1)$',
    'boosted_pt_2': '$p_{T}(\\tau_2)$',
    'boosted_eta_1': '$\\eta(\\tau_1$)',
    'boosted_eta_2': '$\\eta(\\tau_2$)',
    'boosted_phi_1': '$\\phi(\\tau_1$)',
    'boosted_phi_2': '$\\phi(\\tau_2$)',
    'boosted_iso_1' : 'iso($\\tau_1$)',
    'boosted_iso_2' : 'iso($\\tau_2$)',
    'boosted_mass_1' : 'mass($\\tau_1$)',
    'boosted_mass_2' : 'mass($\\tau_2$)',
    'boosted_tau_decaymode_1': 'decay mode 1',
    'boosted_tau_decaymode_2': 'decay mode 2',
    'boosted_mt_1' : '$m_{T}(\\tau_1,MET)$',
    'boosted_mt_2' : '$m_{T}(\\tau_2,MET)$',
    'boosted_deltaR_ditaupair': '$\Delta$R $(\\tau_1, \\tau_2)$',
    'boosted_m_vis' : 'visible di-$\\tau$ mass',
    'boosted_m_fastmtt': 'fastMTT di-$\\tau$ mass',
    'boosted_pt_fastmtt': 'fastMTT $p_{T}(\\tau\\tau)$',
    'boosted_eta_fastmtt': 'fastMTT $\\eta(\\tau\\tau)$',
    'boosted_phi_fastmtt': 'fastMTT $\phi(\\tau\\tau)$',
    'bpair_pt_1' : 'Leading b-jet $p_T$',
    'bpair_pt_2' : 'Sub-leading b-jet $p_T$',
    'bpair_eta_1' : 'Leading b-jet $\\eta$',
    'bpair_eta_2' : 'Sub-leading b-jet $\\eta$',
    'bpair_phi_1' : 'Leading b-jet $\\phi$',
    'bpair_phi_2' : 'Sub-leading b-jet $\\phi$',
    'bpair_btag_value_1' : 'Leading b-jet b-tag score',
    'bpair_btag_value_2' : 'Sub-leading b-jet b-tag score',
    'bpair_m_inv': 'di-b mass',
    'bpair_pt_dijet': 'di-b $p_T$',
    'bpair_deltaR': '$\Delta$R $(b_1, b_2)$',
    'bpair_pt_1_boosted' : 'Leading b-jet $p_T$',
    'bpair_pt_2_boosted' : 'Sub-leading b-jet $p_T$',
    'bpair_eta_1_boosted' : 'Leading b-jet $\\eta$',
    'bpair_eta_2_boosted' : 'Sub-leading b-jet $\\eta$',
    'bpair_phi_1_boosted' : 'Leading b-jet $\\phi$',
    'bpair_phi_2_boosted' : 'Sub-leading b-jet $\\phi$',
    'bpair_btag_value_1_boosted' : 'Leading b-jet b-tag score',
    'bpair_btag_value_2_boosted' : 'Sub-leading b-jet b-tag score',
    'bpair_m_inv_boosted': 'di-b mass',
    'bpair_pt_dijet_boosted': 'di-b $p_T$',
    'bpair_deltaR_boosted': '$\Delta$R $(b_1, b_2)$',
    'fj_Xbb_pt': 'X(bb)-tagged fatjet $p_T$',
    'fj_Xbb_eta': 'X(bb)-tagged fatjet $\\eta$',
    'fj_Xbb_phi': 'X(bb)-tagged fatjet $\\phi$',
    'fj_Xbb_msoftdrop': 'X(bb)-tagged fatjet softdrop mass',
    'fj_Xbb_nsubjettiness_2over1': 'X(bb)-tagged fatjet nsubjettiness 2/1',
    'fj_Xbb_nsubjettiness_3over2': 'X(bb)-tagged fatjet nsubjettiness 3/2',
    'fj_Xbb_pt_boosted': 'X(bb)-tagged fatjet $p_T$',
    'fj_Xbb_eta_boosted': 'X(bb)-tagged fatjet $\\eta$',
    'fj_Xbb_phi_boosted': 'X(bb)-tagged fatjet $\\phi$',
    'fj_Xbb_msoftdrop_boosted': 'X(bb)-tagged fatjet softdrop mass',
    'fj_Xbb_nsubjettiness_2over1_boosted': 'X(bb)-tagged fatjet nsubjettiness 2/1',
    'fj_Xbb_nsubjettiness_3over2_boosted': 'X(bb)-tagged fatjet nsubjettiness 3/2',
    'mass_tautaubb': 'bb+$\\tau\\tau$ mass',
    'pt_tautaubb': 'bb+$\\tau\\tau$ $p_T$',
    'kinfit_mX': 'kinfit X mass',
    'kinfit_mY': 'kinfit Y mass',
    'kinfit_chi2': 'kinfit $\\chi^2$',
    'njets' : 'number of jets',
    'nfatjets' : 'number of fatjets',
    'nbtag' : 'number of b-jets',
    'boosted_mass_tautaubb': 'bb+$\\tau\\tau$ mass',
    'boosted_pt_tautaubb': 'bb+$\\tau\\tau$ $p_T$',
    'kinfit_mX_boosted': 'kinfit X mass',
    'kinfit_mY_boosted': 'kinfit Y mass',
    'kinfit_chi2_boosted': 'kinfit $\\chi^2$',
    'njets_boosted' : 'number of jets',
    'nfatjets_boosted' : 'number of fatjets',
    'nbtag_boosted' : 'number of b-jets',
    'met' : 'MET',
    'metphi' : '$\phi_{MET}$',
    'met_boosted' : 'MET',
    'metphi_boosted' : '$\phi_{MET}$',
    
    'm_sv' : 'di-$\\tau$ mass',
    'mt_1_pf': '$m_{T}(\\tau_1,PFMET)$',
    'mt_2_pf': '$m_{T}(\\tau_2,PFMET)$',
    'ptvis' : 'visible $p_T(\\tau\\tau)$',
    'pt_tt' : '$p_T(\\tau\\tau)$',
    'pt_tt_pf': '$p_T(\\tau\\tau)$ (PF)',
    'mjj' : 'di-jet mass',
    'jdeta' : '$\Delta\eta_{jj}$',
    'dijetpt' : '$p_T(jj)$',
    'pfmet': 'MET (PF)',
    'pfmetphi': '$\phi_{PFMET}$',
    'm_sv_puppi': 'di-$\\tau$ mass (Puppi)',
    'pt_tt_puppi': '$p_{T}(\\tau\\tau)$ (Puppi)',
    'ME_q2v1': 'MELA $Q^{2}(^{}V_{1}$)',
    'ME_q2v2': 'MELA $Q^{2}(^{}V_{2}$)',
    'mTdileptonMET_puppi': '$m_{T}(\\tau_1+\\tau_2, MET)$ (Puppi)',
    'pzetamissvis': '$p_{Z}^{miss} - p_{Z}^{vis}$',
    'pzetamissvis_pf': '$p_{Z}^{miss} - p_{Z}^{vis}$ (PF)',
    'pt_dijet': '$p_{T}(jj)$',
    'mt_tot': '$m_{T}(\\tau_1+\\tau_2, MET)$',
    "jet_hemisphere": 'jet hemisphere',
    "pt_vis": 'visible $p_T(\\tau\\tau)$',
    'jeta_1': 'Leading jet $\\eta$',
    'jeta_2': 'Subleading jet $\\eta$',
    'jpt_1' : 'Leading jet $p_T$',
    'jpt_2' : 'Sub-leading jet $p_T$',
}

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Plot goodness of fit results")
    parser.add_argument(
        "--variables", help="Considered variables in goodness of fit test")
    parser.add_argument(
        "--path", help="Path to directory with goodness of fit results")
    parser.add_argument("--channel", type=str, help="Select channel to be plotted")
    parser.add_argument("--era", type=str, help="Select era to be plotted")
    parser.add_argument("-c", "--classification", type=str, default=None)
    return parser.parse_args()


# def make_cmap(colors, position):
#     if len(position) != len(colors):
#         raise Exception("position length must be the same as colors")
#     elif position[0] != 0 or position[-1] != 1:
#         raise Exception("position must start with 0 and end with 1")

#     cdict = {'red': [], 'green': [], 'blue': []}
#     for pos, color in zip(position, colors):
#         cdict['red'].append((pos, color[0], color[0]))
#         cdict['green'].append((pos, color[1], color[1]))
#         cdict['blue'].append((pos, color[2], color[2]))

#     cmap = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 256)
#     return cmap


# def plot_2d(variables, results, filename, t_coeff=None):
#     plt.figure(figsize=(1.5 * len(variables), 1.0 * len(variables)))
#     a = plt.gca()
#     if t_coeff is None:
#         pass
#     else:
#         max_coeff = max(map(float, t_coeff.values()))
#         marks_x, marks_y = [], []
#     for i1 in range(len(variables)):
#         for i2 in range(len(variables)):
#             if results[i1, i2] == -1.0:
#                 results[i1, i2] = np.nan
#                 continue
#             if i1 >= i2:
#                 results[i1, i2] = np.nan
#                 continue
#             a.text(
#                 i1 + 0.5,
#                 i2 + 0.5,
#                 '{0:.2f}'.format(results[i1, i2]),
#                 ha='center',
#                 va='center')
#             if t_coeff is None:
#                 pass
#             else:
#                 if "{}, {}".format(variables[i1], variables[i2]) in t_coeff.keys():
#                     if float(t_coeff["{}, {}".format(variables[i1], variables[i2])]) > (0.1 * max_coeff):
#                         marks_x.append(i1 + 0.85)
#                         marks_y.append(i2 + 0.85)
#                 elif "{}, {}".format(variables[i2], variables[i1]) in t_coeff.keys():
#                     if float(t_coeff["{}, {}".format(variables[i2], variables[i1])]) > (0.1 * max_coeff):
#                         marks_x.append(i1 + 0.85)
#                         marks_y.append(i2 + 0.85)
#                 else:
#                     raise Exception("Variable combination {} {} not present in variables.".format(variables[i1], variables[i2]))
#     cmap = make_cmap([(1, 0, 0), (1, 1, 0), (0, 1, 0)],
#                      np.array([0.0, 0.05, 1.0]))
#     cmap.set_bad(color='w')
#     results = np.ma.masked_invalid(results)
#     p = plt.pcolormesh(results.T, vmin=0.0, vmax=1.0, cmap=cmap)
#     cbar = plt.colorbar(p)
#     cbar.set_label(
#         'Saturated goodness of fit p-value', rotation=270, labelpad=50)
#     plt.xticks(
#         np.array(range(len(variables))) + 0.5, [labeldict[x] for x in variables], rotation='vertical')
#     plt.yticks(
#         np.array(range(len(variables))) + 0.5,
#         [labeldict[x] for x in variables],
#         rotation='horizontal')
#     plt.xlim(0, len(variables))
#     plt.ylim(0, len(variables))
#     if t_coeff is None:
#         pass
#     else:
#         plt.plot(marks_x, marks_y, "b*", ms=12)
#     plt.savefig(filename+".png", bbox_inches="tight")
#     plt.savefig(filename+".pdf", bbox_inches="tight")


# def plot_1d(variables, results, filename):
#     plt.figure(figsize=(len(variables) * 0.5, 8.0))
#     y = results
#     x = range(len(y))
#     plt.plot(x, y, '+', mew=4, ms=16)
#     plt.ylim((-0.05, 1.05))
#     plt.xlim((-0.5, len(x) - 0.5))
#     plt.xticks(x, [labeldict[x] for x in variables], rotation="vertical")
#     plt.axhline(y=0.05, linewidth=3, color='r')
#     for i, res in enumerate(y):
#         if res < 0.05:
#             plt.text(i, 0.9, "{:.3f}".format(res), rotation='vertical',
#                      horizontalalignment="center", verticalalignment="center")
#     plt.ylabel('Saturated goodness of fit p-value', labelpad=20)
#     ax = plt.gca()
#     ax.xaxis.grid()
#     sns.despine()
#     plt.savefig(filename+".png", bbox_inches="tight")
#     plt.savefig(filename+".pdf", bbox_inches="tight")

def plot_1d(variables, results, filename):
    # now plots the results
    # sns.set_style("ticks")
    # sns.set_context("paper", font_scale=2.0, rc={"lines.linewidth": 2.5})
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    ax.set_xlim(-0.05, 1.05)
    x = np.array(results)
    y = np.array(range(len(x)))
    plt.ylim((-0.5, len(results) - 0.5))
    ax.set_xlabel('Saturated GoF p-value', labelpad=20)
    plt.plot(x, y, '1', mew=4, ms=16)
    plt.yticks(y, [labeldict[x] for x in variables])
    plt.axvspan(-1, 0.05, color='red', alpha=0.5, lw=0)
    plt.axvline(x=0.05, linewidth=1, color='black', linestyle='--')
    for i, res in enumerate(x):
        plt.text(0.92, i, "{:.3f}".format(res),horizontalalignment="center", verticalalignment="center", color='k', alpha=0.5)
        ax.axhline(i-0.5, linestyle='--', color='k', linewidth=0.2)
    hep.cms.label(ax=ax, label="Private work", data=True, fontsize=22, lumi=59.83, year=2018)
    plt.tight_layout()
    plt.show()
    fig.savefig(filename+".png", bbox_inches="tight")
    fig.savefig(filename+".pdf", bbox_inches="tight")



def search_results_1d(path, channel, era, variables):
    results = []
    missing = []
    for variable in variables:
        filename = os.path.join(path, "{}_{}_{}".format(era, channel, variable),
                                "gof.json")
        print("Searching for {}".format(filename))
        if not os.path.exists(filename):
            missing.append(variable)
            results.append(-1.0)
            continue
        logger.debug(
            "Found goodness of fit result for variable %s in channel %s.",
            variable, channel)

        p_value = json.load(open(filename))
        results.append(p_value["250.0"]["p"])

    return missing, results


# def search_results_2d(path, channel, era, variables):
#     missing = []
#     results = np.ones((len(variables), len(variables))) * (-1.0)
#     for i1, v1 in enumerate(variables):
#         for i2, v2 in enumerate(variables):
#             if i2 <= i1:
#                 continue
#             filename = os.path.join(path, "{}-{}-{}_{}".format(era, channel, v1, v2),
#                                     "gof.json")
#             if not os.path.exists(filename):
#                 missing.append("{}_{}".format(v1, v2))
#                 continue
#             logger.debug(
#                 "Found goodness of fit result for variable pair (%s, %s) in channel %s.",
#                 v1, v2, channel)

#             p_value = json.load(open(filename))
#             results[i1, i2] = p_value["125.0"]["p"]

#     return missing, results


# def create_mock_results_2d(result, variables):
#     mock = np.ones((len(variables), len(variables))) * (-1.0)
#     for i1, v1 in enumerate(variables):
#         for i2, v2 in enumerate(variables):
#             if i2 <= i1:
#                 continue
#             if result[i1] < 0 or result[i2] < 0:
#                 continue
#             mock[i1, i2] = result[i1] * result[i2]
#     return mock


def main(args):
    # Plot 1D gof results
    variables = args.variables.split(",")
    missing_1d, results_1d = search_results_1d(args.path, args.channel, args.era,
                                               variables)
    for variable in missing_1d:
        logger.debug("Missing variables for 1D plot in channel %s:", args.channel)
        print("{} {} {}".format(args.era, args.channel, variable))

    plot_1d(variables, results_1d, "{}/{}_{}_gof_1d".format(args.path, args.era, args.channel))

    # # Plot 2D gof results
    # """
    # missing_2d, results_2d = search_results_2d(args.path, args.channel, args.era,
    #                                            variables)
    # logger.debug("Missing variables for 2D plot in channel %s:", args.channel)
    # for variable in missing_2d:
    #     print("{} {} {}".format(args.era, args.channel, variable))

    # plot_2d(variables, results_2d, "{}_{}_gof_2d".format(args.era, args.channel))
    # """

    # # Plot results for selected variables
    # variables_selected = yaml.load(open(args.variables))["selected_variables"][int(args.era)][args.channel]
    # logger.info("Use well described variables for channel %s:", args.channel)
    # for i, v in enumerate(variables):
    #     print("- {}".format(v))

    # # Plot 1D gof results for reduced variable set
    # results_1d_selected = [
    #     results_1d[i] for i, v in enumerate(variables)
    #     if v in variables_selected
    # ]

    # plot_1d(variables_selected, results_1d_selected,
    #         "{}/{}_{}_gof_1d_selected".format(args.path, args.era, args.channel))

    # # Plot 2D gof results for reduced variable set
    # missing_2d_selected, results_2d_selected = search_results_2d(
    #     args.path, args.channel, args.era, variables_selected)
    # # Read in taylor coefficients.
    # if args.classification == "stage0":
    #     taylor = yaml.load(open("all_eras_{}_final_stage0/combined_keras_taylor_ranking_signals_{}.yaml".format(args.channel, args.era), "r"))
    # elif args.classification == "stage1p1":
    #     taylor = yaml.load(open("all_eras_{}_final_stage1p1/combined_keras_taylor_ranking_signals_{}.yaml".format(args.channel, args.era), "r"))
    # else:
    #     taylor = None
    # plot_2d(variables_selected, results_2d_selected,
    #         "{}/{}_{}_gof_2d_selected".format(args.path, args.era, args.channel),
    #         taylor)

    # logger.debug("Missing variables for 2D plot in channel %s:", args.channel)
    # for variable in missing_2d_selected:
    #     print("{} {} {}".format(args.era, args.channel, variable))

    # # Plot mock 2D results for comparison with bad 1d GoFs
    # mock_2d_selected = create_mock_results_2d(results_1d_selected, variables_selected)
    # plot_2d(variables_selected, mock_2d_selected,
    #         "{}/{}_{}_gof_2d_selected_mock".format(args.path, args.era, args.channel))

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
