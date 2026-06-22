#!/usr/bin/env python3
"""
Calculate ttbar em-channel weights from ROOT files.

Calculates ratio = (data - background) / TT MC for m_vis > 100 region
by integrating over all bins with m_vis > 100. This integrated ratio
is used as a uniform correction weight applied to all ttbar events.

Formula: weight = integral(data - backgrounds) / integral(TT) for m_vis > 100
"""

import numpy as np
import uproot
from pathlib import Path
import sys

def get_integral_above_cut(hist, m_vis_cut=100):
    """
    Get integral of histogram above m_vis cut value.
    
    Args:
        hist: uproot histogram
        m_vis_cut: minimum m_vis value
    
    Returns:
        tuple: (integral, error)
    """
    if hist is None:
        return 0.0, 0.0
    
    try:
        values = hist.values()
        variances = hist.variances()
        errors = np.sqrt(variances)
        
        # Get bin centers (edges is a method, need to call it)
        axis = hist.axes[0]
        centers = axis.centers()
        
        integral = 0.0
        error_sq = 0.0
        
        # Find bins above cut
        for i, center in enumerate(centers):
            if center > m_vis_cut:
                integral += values[i]
                error_sq += errors[i] ** 2
        
        return float(integral), float(np.sqrt(error_sq))
    except Exception as e:
        print(f"    Error getting integral: {e}")
        import traceback
        traceback.print_exc()
        return 0.0, 0.0

def find_em_file(era):
    """Find em channel ROOT file for given era with tag 260417."""
    output_dir = Path("/work/sgiappic/smhtt_ul/output")
    
    # Look for directories matching
    em_dirs = sorted(output_dir.glob(f"{era}-em-htt*260602_btag*"))
    
    if not em_dirs:
        return None
    
    # Filter for exact pattern (em-htt_260417_...-260417, not the ff variants)
    for em_dir in em_dirs:
        dir_name = em_dir.name
        # Skip directories ending with _ff or other variants
        if dir_name.endswith("_ff") or dir_name.endswith("_rawff"):
            continue
        
        # Look for control_shapes*.root file
        root_files = sorted(em_dir.glob("control_shapes*.root"))
        if root_files:
            return root_files[0]
    
    return None

def get_histograms_by_process(f, m_vis_variable="met"):
    """
    Extract m_vis histograms by process from ROOT file.
    
    Histograms are named like: PROCESS#em-PROCESS-VARIANT#Nominal#m_vis;1
    Groups all variants of each process.
    
    Returns:
        dict: {process_name: [list_of_histograms]}
    """
    histograms = {}
    
    for key in f.keys():
        key_str = key.decode() if isinstance(key, bytes) else key
        
        if m_vis_variable.lower() not in key_str.lower():
            continue
        
        # Only use Nominal, not variations
        if "#Nominal#" not in key_str:
            continue
        
        try:
            hist = f[key_str]
            if not hasattr(hist, 'values'):
                continue
            
            # Parse process name from key
            # Format: PROCESS#em-PROCESS-VARIANT#Nominal#m_vis;1
            parts = key_str.split("#")
            if len(parts) < 2:
                continue
            
            process_full = parts[0]  # e.g., "DY", "TT", "data", "VV"
            
            # Normalize process name
            process_lower = process_full.lower()
            
            # Skip Higgs processes (ggH, qqH, VH, WH, ZH, ttH, HWW)
            if any(x in process_lower for x in ["ggh", "qqh", "vh", "wh", "zh", "tth", "hww"]):
                continue
            
            if "data" in process_lower:
                process = "data"
            elif "tt" in process_lower:
                process = "tt"
            elif "vv" in process_lower:
                process = "vv"
            elif "dy" in process_lower:
                process = "dy"
            elif "w" in process_lower:
                process = "w"
            elif "qcdmc" in process_lower:
                process = "qcd"
            else:
                # Skip unknown processes
                continue
            
            # Store histogram in list (collect all variants)
            if process not in histograms:
                histograms[process] = []
            histograms[process].append((key_str, hist))
        
        except Exception as e:
            pass
    
    return histograms

def calculate_weight_for_era(era, m_vis_cut=100):
    """
    Calculate the ttbar weight for a given era.
    
    Ratio = (data - all_backgrounds) / TT
    Where: TT includes TTT + TTL (but NOT TTJ which is in fake factors)
           Backgrounds: DY, W, VV, QCD (NOT Higgs processes)
    
    Args:
        era: era name
        m_vis_cut: m_vis cutoff value
    
    Returns:
        dict: with weight and diagnostic info, or None
    """
    root_file = find_em_file(era)
    
    if not root_file:
        print(f"{era:15s}: ROOT file not found")
        return None
    
    print(f"\n{era:15s}: {root_file.name}")
    
    try:
        with uproot.open(root_file) as f:
            # Get all histograms
            print(f"  Available keys: {len(f.keys())}")
            
            # Get m_vis histograms grouped by process
            hists_by_process = get_histograms_by_process(f)
            
            if not hists_by_process:
                print(f"  No m_vis histograms found")
                return None
            
            print(f"  Found processes: {', '.join(sorted(hists_by_process.keys()))}")
            
            # Calculate integrals for each process (summing all variants)
            integrals = {}
            for process, hist_list in hists_by_process.items():
                integral = 0.0
                error_sq = 0.0
                
                # Exclude TTJ from TT integral (it's counted as fake factors)
                for key_str, hist in hist_list:
                    # For TT, exclude TTJ variant
                    if process == "tt" and "TTJ" in key_str:
                        continue
                    
                    vals = hist.values()
                    variances = hist.variances()
                    errors = np.sqrt(variances)
                    axis = hist.axes[0]
                    centers = axis.centers()
                    
                    for i, center in enumerate(centers):
                        if center > m_vis_cut:
                            integral += vals[i]
                            error_sq += errors[i] ** 2
                
                integrals[process] = {
                    "integral": integral,
                    "error": np.sqrt(error_sq)
                }
                print(f"    {process:10s} (m_vis>{m_vis_cut}): {integral:10.1f} ± {np.sqrt(error_sq):8.1f}")
            
            # Calculate ratio: (data - everything except TT) / TT
            if "data" not in integrals or "tt" not in integrals:
                print(f"  Missing data or TT histogram")
                return None
            
            data_int = integrals["data"]["integral"]
            data_err = integrals["data"]["error"]
            tt_int = integrals["tt"]["integral"]
            tt_err = integrals["tt"]["error"]
            
            # Sum all other backgrounds (not TT, not data, not higgs)
            # Higgs already excluded from hists_by_process
            bg_int = 0.0
            bg_err_sq = 0.0
            for process, vals in integrals.items():
                if process not in ["data", "tt"]:
                    bg_int += vals["integral"]
                    bg_err_sq += vals["error"] ** 2
            
            bg_err = np.sqrt(bg_err_sq)
            
            # Numerator: data - background
            numerator = data_int - bg_int
            numerator_err = np.sqrt(data_err**2 + bg_err**2)
            
            print(f"  Background sum: {bg_int:10.1f} ± {bg_err:8.1f}")
            print(f"  Numerator (data - bg): {numerator:10.1f} ± {numerator_err:8.1f}")
            
            # Calculate weight
            if tt_int > 0:
                weight = numerator / tt_int
                
                # Error propagation
                if numerator > 0:
                    weight_err = weight * np.sqrt(
                        (numerator_err/numerator)**2 + (tt_err/tt_int)**2
                    )
                else:
                    weight_err = 0.0
                
                print(f"  Weight = (data - bg) / TT: {weight:.6f} ± {weight_err:.6f}")
                
                return {
                    "era": era,
                    "weight": weight,
                    "weight_error": weight_err,
                    "data": data_int,
                    "data_err": data_err,
                    "background": bg_int,
                    "background_err": bg_err,
                    "tt": tt_int,
                    "tt_err": tt_err,
                    "numerator": numerator,
                    "numerator_err": numerator_err,
                    "m_vis_cut": m_vis_cut,
                }
            else:
                print(f"  TT integral is zero")
                return None
    
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function."""
    
    # Eras to process
    eras = [
        "2022preEE",
        "2022postEE", 
        "2023preBPix",
        "2023postBPix",
        "2024",
        "2025",
    ]
    
    m_vis_cut = 0
    
    print("="*80)
    print("TTBar EM-Channel Weight Calculation")
    print(f"Region: m_vis > {m_vis_cut}")
    print("Formula: weight = (data - background) / TT")
    print("="*80)
    
    results = {}
    for era in eras:
        result = calculate_weight_for_era(era, m_vis_cut)
        if result:
            results[era] = result
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)
    
    if results:
        print(f"\n{'Era':<15s} {'Weight':<15s} {'Error':<15s} {'Data':<10s} {'BG':<10s} {'TT':<10s}")
        print("-"*80)
        
        for era in eras:
            if era in results:
                r = results[era]
                print(f"{r['era']:<15s} {r['weight']:<15.6f} {r['weight_error']:<15.6f} "
                      f"{r['data']:<10.1f} {r['background']:<10.1f} {r['tt']:<10.1f}")
        
        print(f"\n✓ All weights calculated successfully")
        
        # Print Python code for process_selection.py
        print("\n" + "="*80)
        print("PYTHON CODE FOR process_selection.py")
        print("="*80)
        print("\nUpdate ttbar_em_weight() function:\n")
        
        for era in eras:
            if era in results:
                r = results[era]
                print(f'    elif era == "{era}":')
                print(f'        ratio_em_mvis60 = "{r["weight"]:.6f}"  # ± {r["weight_error"]:.6f}')
            else:
                print(f'    elif era == "{era}":')
                print(f'        ratio_em_mvis60 = "1.0"  # NOT MEASURED')
    
    else:
        print("\nError: Could not calculate any weights")
        sys.exit(1)

if __name__ == "__main__":
    main()
