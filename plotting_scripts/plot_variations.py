import uproot
import matplotlib.pyplot as plt
import mplhep as hep
import argparse
import os
import numpy as np

# Create a new figure with CMS style
plt.style.use(hep.style.CMS)

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Plot root histogram variations")

     # Add arguments
    parser.add_argument("-r", "--root-file", required=True, help="Path to the ROOT file")
    parser.add_argument("-v", "--variable", required=True, help="Name of the variable")
    parser.add_argument("-c", "--channel", required=True, help="Name of the channel")
    parser.add_argument("-p", "--process", required=True, help="Name of the process")

    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Dict of processes with relevant variations
    general = ["CMS_PileUp"]
    signal = ["LHE_scale_norm"]
    btagging = [
        "CMS_btag_b_HF", 
        "CMS_btag_b_HFstats1_2018", 
        "CMS_btag_b_HFstats2_2018", 
        "CMS_btag_c_CFerr1", 
        "CMS_btag_c_CFerr2",
        "CMS_btag_j_LF", 
        "CMS_btag_j_LFstats1_2018", 
        "CMS_btag_j_LFstats2_2018",
    ]
    pNet = ["CMS_XbbTag_fj_2018"]
    jec = [
        "CMS_res_j_2018", 
        "CMS_scale_j_Absolute", 
        "CMS_scale_j_Absolute_2018", 
        "CMS_scale_j_BBEC1", 
        "CMS_scale_j_BBEC1_2018", 
        "CMS_scale_j_EC2", 
        "CMS_scale_j_EC2_2018", 
        "CMS_scale_j_FlavorQCD", 
        "CMS_scale_j_HEMIssue_2018", 
        "CMS_scale_j_HF",
        "CMS_scale_j_HF_2018", 
        "CMS_scale_j_RelativeBal", 
        "CMS_scale_j_RelativeSample_2018",
    ]
    tauID = {
        "et": [
            "CMS_eff_t_30-35_2018",
            "CMS_eff_t_35-40_2018", 
            "CMS_eff_t_40-500_2018", 
            "CMS_eff_t_500-1000_2018", 
            "CMS_eff_t_1000-Inf_2018",
        ],
        "mt": [
            "CMS_eff_t_30-35_2018",
            "CMS_eff_t_35-40_2018", 
            "CMS_eff_t_40-500_2018", 
            "CMS_eff_t_500-1000_2018", 
            "CMS_eff_t_1000-Inf_2018",
        ],
        "tt": ["CMS_eff_t_dm0_2018", "CMS_eff_t_dm1_2018", "CMS_eff_t_dm10_2018", "CMS_eff_t_dm11_2018"],
    }
    tauID_emb = {
        "et": [
            # "CMS_eff_t_emb_20-25_2018", 
            # "CMS_eff_t_emb_25-30_2018",
            "CMS_eff_t_emb_30-35_2018",
            "CMS_eff_t_emb_35-40_2018", 
            "CMS_eff_t_emb_40-Inf_2018", 
            
        ],
        "mt": [
            # "CMS_eff_t_emb_20-25_2018", 
            # "CMS_eff_t_emb_25-30_2018",
            "CMS_eff_t_emb_30-35_2018",
            "CMS_eff_t_emb_35-40_2018", 
            "CMS_eff_t_emb_40-Inf_2018", 
        ],
        "tt": ["CMS_eff_t_emb_dm0_2018", "CMS_eff_t_emb_dm1_2018", "CMS_eff_t_emb_dm10_2018", "CMS_eff_t_emb_dm11_2018"],
    }
    tauID_boosted = {
        "et": [
            # "CMS_eff_boosted_t_30-35_2018",
            # "CMS_eff_boosted_t_35-40_2018", 
            "CMS_eff_boosted_t_40-500_2018", 
            "CMS_eff_boosted_t_500-1000_2018", 
            "CMS_eff_boosted_t_1000-Inf_2018",
        ],
        "mt": [
            # "CMS_eff_boosted_t_30-35_2018",
            # "CMS_eff_boosted_t_35-40_2018", 
            "CMS_eff_boosted_t_40-500_2018", 
            "CMS_eff_boosted_t_500-1000_2018", 
            "CMS_eff_boosted_t_1000-Inf_2018",
        ],
        "tt": ["CMS_eff_boosted_t_dm0_2018", "CMS_eff_boosted_t_dm1_2018", "CMS_eff_boosted_t_dm10_2018"],
    }
    DYshapes = {
        "et": ["CMS_fake_e_Barrel_2018", "CMS_fake_e_Endcap_2018"],
        "mt": [
            "CMS_fake_m_Wheel1_2018", 
            "CMS_fake_m_Wheel2_2018", 
            "CMS_fake_m_Wheel3_2018",
            "CMS_fake_m_Wheel4_2018", 
            "CMS_fake_m_Wheel5_2018",
        ],
        "tt": [],
    }
    DYshapes_boosted = {
        "et": ["CMS_fake_boosted_e_Barrel_2018", "CMS_fake_boosted_e_Endcap_2018"],
        "mt": [
            "CMS_fake_boosted_m_Wheel1_2018", 
            "CMS_fake_boosted_m_Wheel2_2018", 
            "CMS_fake_boosted_m_Wheel3_2018",
            "CMS_fake_boosted_m_Wheel4_2018", 
            "CMS_fake_boosted_m_Wheel5_2018",
        ],
        "tt": [],
    }
    tauES = [
        "CMS_scale_t_1prong1pizero_2018", 
        "CMS_scale_t_1prong_2018", 
        "CMS_scale_t_3prong_2018",
        "CMS_scale_t_3prong1pizero_2018",
    ]
    tauES_emb = [
        "CMS_scale_t_emb_1prong1pizero_2018", 
        "CMS_scale_t_emb_1prong_2018", 
        "CMS_scale_t_emb_3prong_2018",
        "CMS_scale_t_emb_3prong1pizero_2018",
    ]
    tauES_boosted = [
        "CMS_scale_boosted_t_1prong1pizero_2018", 
        "CMS_scale_boosted_t_1prong_2018", 
        "CMS_scale_boosted_t_3prong_2018",
    ]
    tauLepFakeES = {
        "et": [
            "CMS_ZLShape_et_1prong_barrel_2018", 
            "CMS_ZLShape_et_1prong_endcap_2018", 
            "CMS_ZLShape_et_1prong1pizero_barrel_2018",
            "CMS_ZLShape_et_1prong1pizero_endcap_2018",
        ],
        "mt": ["CMS_ZLShape_mt_2018"],
        "tt": [],
    }
    
    eleES = {
        "et": ["CMS_res_e", "CMS_scale_e"],
        "mt": [],
        "tt": [],
    }
    eleES_emb = {
        "et": ["CMS_scale_e_barrel_emb", "CMS_scale_e_endcap_emb"],
        "mt": [],
        "tt": [],
    }
    trg = [f"CMS_eff_trigger_{args.channel}_2018"]
    trg_emb = [f"CMS_eff_trigger_emb_{args.channel}_2018"]
    trg_boosted = [f"CMS_eff_trigger_boosted_{args.channel}_2018"]
    met_resonant = ["CMS_htt_boson_res_met_2018", "CMS_htt_boson_scale_met_2018"]
    met = ["CMS_scale_met_unclustered_2018"]
    toppt = ["CMS_topPt_Shape"]
    
    jetfakes = {
        "et": [
            "CMS_QCDFFnormUnc_et_2018", 
            "CMS_QCDFFslopeUnc_et_2018", 
            "CMS_QCDFFmcSubUnc_et_2018",
            "CMS_WjetsFFnormUnc_et_2018", 
            "CMS_WjetsFFslopeUnc_et_2018", 
            "CMS_WjetsFFmcSubUnc_et_2018", 
            "CMS_ttbarFFnormUnc_et_2018", 
            "CMS_ttbarFFslopeUnc_et_2018", 
            "CMS_fracQCDUnc_et_2018", 
            "CMS_fracWjetsUnc_et_2018", 
            "CMS_fracTTbarUnc_et_2018", 
            "CMS_QCDClosureLeadingLepPtCorr_et_2018",
            "CMS_QCDClosureSubleadingTauMassCorr_et_2018",
            "CMS_QCDDRtoSRCorr_et_2018",
            "CMS_WjetsClosureLeadingLepPtCorr_et_2018",
            "CMS_WjetsClosureSubleadingTauMassCorr_et_2018",
            "CMS_WjetsDRtoSRCorr_et_2018",
            "CMS_ttbarClosureLeadingLepPtCorr_et_2018",
            "CMS_ttbarClosureSubleadingTauMassCorr_et_2018",
        ],
        "mt": [
            "CMS_QCDFFnormUnc_mt_2018", 
            "CMS_QCDFFslopeUnc_mt_2018", 
            "CMS_QCDFFmcSubUnc_mt_2018",
            "CMS_WjetsFFnormUnc_mt_2018", 
            "CMS_WjetsFFslopeUnc_mt_2018", 
            "CMS_WjetsFFmcSubUnc_mt_2018", 
            "CMS_ttbarFFnormUnc_mt_2018", 
            "CMS_ttbarFFslopeUnc_mt_2018", 
            "CMS_fracQCDUnc_mt_2018", 
            "CMS_fracWjetsUnc_mt_2018", 
            "CMS_fracTTbarUnc_mt_2018", 
            "CMS_QCDClosureLeadingLepPtCorr_mt_2018",
            "CMS_QCDClosureSubleadingTauMassCorr_mt_2018",
            "CMS_QCDDRtoSRCorr_mt_2018",
            "CMS_WjetsClosureLeadingLepPtCorr_mt_2018",
            "CMS_WjetsClosureSubleadingTauMassCorr_mt_2018",
            "CMS_WjetsDRtoSRCorr_mt_2018",
            "CMS_ttbarClosureLeadingLepPtCorr_mt_2018",
            "CMS_ttbarClosureSubleadingTauMassCorr_mt_2018",
        ],
        "tt": [
            "CMS_QCDFFnormUnc_tt_2018", 
            "CMS_QCDFFslopeUnc_tt_2018", 
            "CMS_QCDFFmcSubUnc_tt_2018",
            "CMS_ttbarFFnormUnc_tt_2018", 
            "CMS_ttbarFFslopeUnc_tt_2018",
            "CMS_QCDSubleadingFFnormUnc_tt_2018", 
            "CMS_QCDSubleadingFFslopeUnc_tt_2018", 
            "CMS_QCDSubleadingFFmcSubUnc_tt_2018",
            "CMS_ttbarSubleadingFFnormUnc_tt_2018", 
            "CMS_ttbarSubleadingFFslopeUnc_tt_2018", 
            "CMS_fracQCDUnc_tt_2018", 
            "CMS_fracWjetsUnc_tt_2018", 
            "CMS_fracTTbarUnc_tt_2018", 
            "CMS_fracQCDSubleadingUnc_tt_2018", 
            "CMS_fracWjetsSubleadingUnc_tt_2018", 
            "CMS_fracTTbarSubleadingUnc_tt_2018", 
            "CMS_QCDClosureSubleadingLepPtCorr_tt_2018",
            "CMS_QCDClosureLeadingTauMassCorr_tt_2018",
            "CMS_QCDDRtoSRCorr_tt_2018",
            "CMS_ttbarClosureSubleadingLepPtCorr_tt_2018",
            "CMS_ttbarClosureLeadingTauMassCorr_tt_2018",
            "CMS_QCDSubleadingClosureLeadingLepPtCorr_tt_2018",
            "CMS_QCDSubleadingClosureSubleadingTauMassCorr_tt_2018",
            "CMS_QCDSubleadingDRtoSRCorr_tt_2018",
            "CMS_ttbarSubleadingClosureLeadingLepPtCorr_tt_2018",
            "CMS_ttbarSubleadingClosureSubleadingTauMassCorr_tt_2018",
        ],
    }
    jetfakes_boosted = {
        "et": [
            "CMS_boostedtau_QCDFFnormUnc_et_2018", 
            "CMS_boostedtau_QCDFFslopeUnc_et_2018", 
            "CMS_boostedtau_QCDFFmcSubUnc_et_2018",
            "CMS_boostedtau_WjetsFFnormUnc_et_2018", 
            "CMS_boostedtau_WjetsFFslopeUnc_et_2018", 
            "CMS_boostedtau_WjetsFFmcSubUnc_et_2018", 
            "CMS_boostedtau_ttbarFFnormUnc_et_2018", 
            "CMS_boostedtau_ttbarFFslopeUnc_et_2018", 
            "CMS_boostedtau_fracQCDUnc_et_2018", 
            "CMS_boostedtau_fracWjetsUnc_et_2018", 
            "CMS_boostedtau_fracTTbarUnc_et_2018", 
            "CMS_boostedtau_QCDClosureLeadingLepPtCorr_et_2018",
            "CMS_boostedtau_QCDClosureSubleadingTauMassCorr_et_2018",
            "CMS_boostedtau_QCDDRtoSRCorr_et_2018",
            "CMS_boostedtau_WjetsClosureLeadingLepPtCorr_et_2018",
            "CMS_boostedtau_WjetsClosureSubleadingTauMassCorr_et_2018",
            "CMS_boostedtau_WjetsDRtoSRCorr_et_2018",
            "CMS_boostedtau_ttbarClosureLeadingLepPtCorr_et_2018",
            "CMS_boostedtau_ttbarClosureSubleadingTauMassCorr_et_2018",
        ],
        "mt": [
            "CMS_boostedtau_QCDFFnormUnc_mt_2018", 
            "CMS_boostedtau_QCDFFslopeUnc_mt_2018", 
            "CMS_boostedtau_QCDFFmcSubUnc_mt_2018",
            "CMS_boostedtau_WjetsFFnormUnc_mt_2018", 
            "CMS_boostedtau_WjetsFFslopeUnc_mt_2018", 
            "CMS_boostedtau_WjetsFFmcSubUnc_mt_2018", 
            "CMS_boostedtau_ttbarFFnormUnc_mt_2018", 
            "CMS_boostedtau_ttbarFFslopeUnc_mt_2018", 
            "CMS_boostedtau_fracQCDUnc_mt_2018", 
            "CMS_boostedtau_fracWjetsUnc_mt_2018", 
            "CMS_boostedtau_fracTTbarUnc_mt_2018", 
            "CMS_boostedtau_QCDClosureLeadingLepPtCorr_mt_2018",
            "CMS_boostedtau_QCDClosureSubleadingTauMassCorr_mt_2018",
            "CMS_boostedtau_QCDDRtoSRCorr_mt_2018",
            "CMS_boostedtau_WjetsClosureLeadingLepPtCorr_mt_2018",
            "CMS_boostedtau_WjetsClosureSubleadingTauMassCorr_mt_2018",
            "CMS_boostedtau_WjetsDRtoSRCorr_mt_2018",
            "CMS_boostedtau_ttbarClosureLeadingLepPtCorr_mt_2018",
            "CMS_boostedtau_ttbarClosureSubleadingTauMassCorr_mt_2018",
        ],
        "tt": [
            "CMS_boostedtau_QCDFFnormUnc_tt_2018", 
            "CMS_boostedtau_QCDFFslopeUnc_tt_2018", 
            "CMS_boostedtau_QCDFFmcSubUnc_tt_2018",
            "CMS_boostedtau_ttbarFFnormUnc_tt_2018", 
            "CMS_boostedtau_ttbarFFslopeUnc_tt_2018",
            "CMS_boostedtau_QCDSubleadingFFnormUnc_tt_2018", 
            "CMS_boostedtau_QCDSubleadingFFslopeUnc_tt_2018", 
            "CMS_boostedtau_QCDSubleadingFFmcSubUnc_tt_2018",
            "CMS_boostedtau_ttbarSubleadingFFnormUnc_tt_2018", 
            "CMS_boostedtau_ttbarSubleadingFFslopeUnc_tt_2018", 
            "CMS_boostedtau_fracQCDUnc_tt_2018", 
            "CMS_boostedtau_fracWjetsUnc_tt_2018", 
            "CMS_boostedtau_fracTTbarUnc_tt_2018", 
            "CMS_boostedtau_fracQCDSubleadingUnc_tt_2018", 
            "CMS_boostedtau_fracWjetsSubleadingUnc_tt_2018", 
            "CMS_boostedtau_fracTTbarSubleadingUnc_tt_2018", 
            "CMS_boostedtau_QCDClosureSubleadingLepPtCorr_tt_2018",
            "CMS_boostedtau_QCDClosureLeadingTauMassCorr_tt_2018",
            "CMS_boostedtau_QCDDRtoSRCorr_tt_2018",
            "CMS_boostedtau_ttbarClosureSubleadingLepPtCorr_tt_2018",
            "CMS_boostedtau_ttbarClosureLeadingTauMassCorr_tt_2018",
            "CMS_boostedtau_QCDSubleadingClosureLeadingLepPtCorr_tt_2018",
            "CMS_boostedtau_QCDSubleadingClosureSubleadingTauMassCorr_tt_2018",
            "CMS_boostedtau_QCDSubleadingDRtoSRCorr_tt_2018",
            "CMS_boostedtau_ttbarSubleadingClosureLeadingLepPtCorr_tt_2018",
            "CMS_boostedtau_ttbarSubleadingClosureSubleadingTauMassCorr_tt_2018",
        ],
    }
    
    variations = {
        "NMSSM_Ybb": general+signal+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met_resonant+eleES[args.channel],
        "NMSSM_Ytt": general+signal+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met_resonant+eleES[args.channel],
        "TTL": general+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met+toppt+eleES[args.channel], 
        "STL": general+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met+eleES[args.channel],
        "VVL": general+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met+eleES[args.channel],
        "ZL_NLO": general+btagging+pNet+jec+trg+met_resonant+DYshapes[args.channel]+tauLepFakeES[args.channel]+eleES[args.channel],
        "jetFakes": jetfakes[args.channel], 
        "EMB": tauID_emb[args.channel]+tauES_emb+eleES_emb[args.channel]+trg_emb+["CMS_emb_ttbar_2018"],
        "ggH_bb": general+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met_resonant+eleES[args.channel], 
        "ggH_tt": general+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met_resonant+eleES[args.channel], 
        "qqH_bb": general+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met_resonant+eleES[args.channel], 
        "qqH_tt": general+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met_resonant+eleES[args.channel], 
        "VH_bb": general+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met_resonant+eleES[args.channel], 
        "VH_tt": general+btagging+pNet+jec+tauID[args.channel]+tauES+trg+met_resonant+eleES[args.channel],
    }
    boosted_variations = {
        "NMSSM_Ybb": general+signal+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met_resonant+eleES[args.channel],
        "NMSSM_Ytt": general+signal+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met_resonant+eleES[args.channel],
        "TTL": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met+toppt+eleES[args.channel], 
        "STL": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met+eleES[args.channel],
        "VVL": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met+eleES[args.channel],
        "ZL_NLO": general+btagging+pNet+jec+trg_boosted+met_resonant+DYshapes_boosted[args.channel]+eleES[args.channel],
        "TTT": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met+toppt+eleES[args.channel], 
        "STT": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met+eleES[args.channel],
        "VVT": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met+eleES[args.channel],
        "ZTT_NLO": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met_resonant+eleES[args.channel],   
        "jetFakes": jetfakes_boosted[args.channel], 
        "ggH_bb": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met_resonant+eleES[args.channel], 
        "ggH_tt": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met_resonant+eleES[args.channel], 
        "qqH_bb": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met_resonant+eleES[args.channel], 
        "qqH_tt": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met_resonant+eleES[args.channel], 
        "VH_bb": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met_resonant+eleES[args.channel], 
        "VH_tt": general+btagging+pNet+jec+tauID_boosted[args.channel]+tauES_boosted+trg_boosted+met_resonant+eleES[args.channel],
    }
    
    use_variations = variations
    if "boosted" in args.root_file:
        use_variations = boosted_variations
    
    # Load the root file
    root_file = uproot.open(args.root_file)
    save_path = os.path.dirname(args.root_file)
    print("Saved to path: "+save_path+"/"+args.variable)

    if not os.path.exists(save_path+"/"+args.variable):
        os.makedirs(save_path+"/"+args.variable)
    
    for var in use_variations[args.process]:
        # Get the nominal histogram
        nominal_hist = root_file[args.channel+"_"+args.variable+"/"+args.process].to_numpy()

        # Get the up variation histogram
        up_hist = root_file[args.channel+"_"+args.variable+"/"+args.process+"_"+var+"Up"].to_numpy()

        # Get the down variation histogram
        down_hist = root_file[args.channel+"_"+args.variable+"/"+args.process+"_"+var+"Down"].to_numpy()

        # Calculate the difference histograms
        ratio_up = up_hist[0] / (nominal_hist[0]+0.0000001)
        ratio_up = (ratio_up, nominal_hist[1])
        ratio_down = down_hist[0] / (nominal_hist[0]+0.0000001)
        ratio_down = (ratio_down, nominal_hist[1])

        # Create a figure with two subplots (histogram and ratio)
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, gridspec_kw={"height_ratios": [3, 1]})


        # Plot the nominal histogram
        hep.histplot(nominal_hist, label="Nominal", color="black", histtype="step", ax=ax1)

        # Plot the up variation histogram
        hep.histplot(up_hist, label=var+"Up", color="red", histtype="step", ax=ax1)

        # Plot the down variation histogram
        hep.histplot(down_hist, label=var+"Down", color="blue", histtype="step", ax=ax1)

        # Add labels and legend
        ax1.set_ylabel("Events")
        # ax.set_title("Histogram with Nominal and Variations")
        ax1.legend(fontsize="x-small")
        
        # Plot the up variation histogram
        hep.histplot(ratio_up, label=var+"Up", color="red", histtype="step", ax=ax2)

        # Plot the down variation histogram
        hep.histplot(ratio_down, label=var+"Down", color="blue", histtype="step", ax=ax2)
        
        ax2.set_xlabel(args.variable)
        ax2.set_ylabel("Ratio")
        ax2.axhline(y=1, color="gray", linestyle="--", linewidth=0.8)
        
        # Set y-axis limits for both plots
        ax1.set_ylim(bottom=0) 
        ax2.set_ylim(0.95, 1.05)
        
        lumi = 59.83
        hep.cms.label(ax=ax1, data=True, label=args.process, lumi=lumi, lumi_format='{:.1f}')

        # Save the plot
        plt.savefig(save_path+"/"+args.variable+"/"+args.process+"_"+var+".png")
        plt.savefig(save_path+"/"+args.variable+"/"+args.process+"_"+var+".pdf")

        # Show the plot
        plt.close()

        # Print a success message
        print(f"Variations plot for {var} saved for variable {args.variable} from file {args.root_file}")

if __name__ == "__main__":
    main()