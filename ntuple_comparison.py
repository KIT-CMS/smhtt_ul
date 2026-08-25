import uproot
import numpy as np
import matplotlib.pyplot as plt
import concurrent.futures
from collections import defaultdict
from XRootD import client
from XRootD.client.flags import DirListFlags

def get_file_list(server, path):
    """Get list of .root files from a directory."""
    fs = client.FileSystem(server)
    status, listing = fs.dirlist(path, DirListFlags.STAT)
    if not status.ok:
        raise RuntimeError(f"Error listing {path}: {status.message}")
    return [f"{server}/{path}/{item.name}" for item in listing if item.name.endswith(".root")]

def read_ntuple_branches(file_path, branches):  # Single file, not list
    """Read specified branches from ntuple tree in a ROOT file."""
    print(f"Reading branches {branches} from {file_path}")
    try:
        with uproot.open(file_path) as f:
            if "ntuple" not in f:
                breakpoint()
            tree = f["ntuple"]
            data = {}
            for branch in branches:
                try:
                    data[branch] = tree[branch].array()
                except KeyError:
                    print(f"Warning: Branch {branch} not found in {file_path}")
                    breakpoint()
            return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        breakpoint()

def apply_cut(data_dict, cut_expression, cut_name):
    """Apply a cut expression to the data dictionary and return mask."""
    # Create a copy of the data to work with
    local_vars = {}
    
    # Copy arrays into local variables for evaluation
    for key, value in data_dict.items():
        local_vars[key] = value
    
    try:
        # Evaluate the cut expression using numpy arrays
        mask = eval(cut_expression, {"np": np, "__builtins__": {}}, local_vars)
        return mask
    except Exception as e:
        print(f"Error evaluating cut '{cut_name}': {e}")
        return None

def process_file_for_cutflow(file_paths, cut_stages, branches):
    """Process a single file and return event counts after each cut stage."""
    data = read_ntuple_branches(file_paths, branches)
    if not data:
        return {}
    
    results = {}
    cumulative_mask = np.ones(len(data[branches[0]]), dtype=bool)
    
    # Stage 0: No cuts (initial sample)
    results["no_cuts"] = len(data[branches[0]])
    
    # Apply cuts sequentially
    for stage_name, cut_expr in cut_stages:
        mask = apply_cut(data, cut_expr, stage_name)
        if mask is None:
            results[stage_name] = 0
            continue
        
        # Cumulative: AND with previous mask
        cumulative_mask = cumulative_mask & mask
        results[stage_name] = int(np.sum(cumulative_mask))
    
    return results

def aggregate_cutflow(paths, cut_stages, branches, label, max_workers=12):
    """Aggregate cutflow results across all files for a version."""
    total_counts = defaultdict(int)
    print(f"--> Processing {len(paths)} paths for {label}...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_file_for_cutflow, f, cut_stages, branches) for f in paths]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            for k, v in res.items():
                total_counts[k] += v
    
    return dict(total_counts)

def create_cutflow_histograms(v9_results, v15_results, cut_stages, output_name):
    """Create histograms with ratio plots for cutflow comparison."""
    
    # Define the stages including "no_cuts" as baseline
    stage_names = ["no_cuts"] + [name for name, _ in cut_stages]
    
    # Extract counts
    v9_counts = np.array([v9_results.get(s, 0) for s in stage_names])
    v15_counts = np.array([v15_results.get(s, 0) for s in stage_names])
    
    # Calculate ratios
    ratios = np.divide(v15_counts, v9_counts, out=np.zeros_like(v15_counts, dtype=float), where=v9_counts!=0)
    
    # Create figure with two subplots (main + ratio)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True, 
                                   gridspec_kw={'height_ratios': [3, 1]})
    plt.subplots_adjust(hspace=0.05)
    
    x = np.arange(len(stage_names))
    width = 0.35
    
    # Main histogram: Bar chart showing event counts
    bars_v9 = ax1.bar(x - width/2, v9_counts, width, label='V9 (nanoAOD v9)', color='steelblue', alpha=0.8)
    bars_v15 = ax1.bar(x + width/2, v15_counts, width, label='V15 (nanoAOD v15)', color='coral', alpha=0.8)
    
    ax1.set_ylabel("Event Count", fontsize=12)
    ax1.set_title("Cutflow Comparison: V9 vs V15 (mm channel)", fontsize=14)
    ax1.legend(loc='upper right')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_yscale('log')
    
    # Add value labels on bars
    for bar in bars_v9:
        height = bar.get_height()
        if height > 0:
            ax1.annotate(f'{height:.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=7, rotation=45)
    
    for bar in bars_v15:
        height = bar.get_height()
        if height > 0:
            ax1.annotate(f'{height:.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=7, rotation=45)
    
    # Ratio plot
    ax2.errorbar(x, ratios, yerr=0, fmt='ko', markersize=6, capsize=3)
    ax2.axhline(1.0, color='red', linestyle='--', linewidth=1.5, label='V15/V9 = 1')
    ax2.set_ylabel("V15 / V9 Ratio", fontsize=12)
    ax2.set_xlabel("Cut Stage", fontsize=12)
    ax2.set_ylim(0.8, 1.2)
    ax2.set_xticks(x)
    ax2.set_xticklabels(stage_names, rotation=45, ha='right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.legend(loc='best')
    
    plt.tight_layout()
    
    # Save outputs
    plt.savefig(f"{output_name}.pdf")
    plt.savefig(f"{output_name}.png")
    print(f"\nOutput saved to: {output_name}.pdf and {output_name}.png")
    plt.close()

def main():
    # --- CONFIG ---
    REDIRECTOR = "root://cmsdcache-kit-disk.gridka.de"
    
    V9_data_dirs = [
        # "SingleMuon_Run2016B-ver1",
        #"SingleMuon_Run2016B-ver2",
        #"SingleMuon_Run2016C-HIPM",
        #"SingleMuon_Run2016D-HIPM",
        #"SingleMuon_Run2016E-HIPM",
        #"SingleMuon_Run2016F-HIPM",
        "SingleMuon_Run2017B-UL2017",
        "SingleMuon_Run2017C-UL2017",
        "SingleMuon_Run2017D-UL2017",
        "SingleMuon_Run2017E-UL2017"
    ]
    V15_data_dirs = [
        # "SingleMuon_Run2016B_v1-HIPM",
        #"SingleMuon_Run2016B_v2-HIPM",
        #"SingleMuon_Run2016C-HIPM",
        #"SingleMuon_Run2016D-HIPM",
        #"SingleMuon_Run2016E-HIPM",
        #"SingleMuon_Run2016F-HIPM",
        "SingleMuon_Run2017B-UL2017",
        "SingleMuon_Run2017C-UL2017",
        "SingleMuon_Run2017D-UL2017",
        "SingleMuon_Run2017E-UL2017"
    ]
    # tauID_nTuples_MT_vvL_20_06_2025_SFs_ES_m8p8-17_18 tauID_nTuples_MT_vvL_20_06_2025_SFs_ES_m8p8-16
    V9_PATH = "/store/user/jvoss/CROWN/ntuples/tauID_nTuples_MT_vvL_20_06_2025_SFs_ES_m8p8-17_18/CROWNRun/2017/*/mm"
    #V15_PATH = "/store/user/jvoss/CROWN/ntuples/SFs_EMB_Run2_v15nanoAOD_29_06_26__16PreVFP/CROWNRun/2016preVFP/*/mm"
    V15_PATH_bit = "/store/user/jvoss/CROWN/ntuples/SFs_TEST_bit/CROWNRun/2017/*/mm"
    
    # Required branches for mm channel cuts
    BRANCHES = [
        "q_1", "q_2",           # charge
        "pt_1", "pt_2",         # transverse momentum
        "iso_1", "iso_2",       # isolation
        "m_vis",                # visible mass
        "trg_single_mu24",
        "trg_single_mu27",
        #"trg_single_mu22_eta2p1",
        #"trg_single_mu22_tk_eta2p1",
    ]
    
    # Sequential cut stages for mm channel (cumulative)
    # Each stage builds on the previous one
    CUT_STAGES = [
        ("os", "((q_1 * q_2) < 0)"),
        ("m_vis", "(m_vis>70) & (m_vis<110)"),
        ("muon_iso", "((iso_1 < 0.15) & (iso_2 < 0.15))"),
        ("pt_2", "(pt_2 > 15)"),
        ("pt_1", "(pt_1 > 25)"),
        ("trg_selection", "((trg_single_mu24 > 0.5) | (trg_single_mu27 > 0.5))"),
    ]
    #((trg_single_mu22 > 0.5) | (trg_single_mu22_tk > 0.5) | (trg_single_mu22_eta2p1 > 0.5) | (trg_single_mu22_tk_eta2p1 > 0.5))"
    
    # 1. Get file lists
    paths_v9 = []
    paths_v15 = []
    for i in range(len(V9_data_dirs)):
        paths_v9.extend(get_file_list(REDIRECTOR, V9_PATH.replace("*", V9_data_dirs[i])))
    
    for i in range(len(V15_data_dirs)):
        # paths_v15.extend(get_file_list(REDIRECTOR, V15_PATH.replace("*", V15_data_dirs[i])))
        paths_v15.extend(get_file_list(REDIRECTOR, V15_PATH_bit.replace("*", V15_data_dirs[i])))
    
    print(f"Found {len(paths_v9)} V9 paths and {len(paths_v15)} V15 paths")
    
    # 2. Aggregate cutflow results
    v9_results = aggregate_cutflow(paths_v9, CUT_STAGES, BRANCHES, "V9", max_workers=10)
    v15_results = aggregate_cutflow(paths_v15, CUT_STAGES, BRANCHES, "V15", max_workers=10)
    
    # 3. Print summary table
    print("\n" + "="*95)
    print(f"{'Cut Stage'} | {'V9 Events'} | {'V15 Events'} | {'Ratio'}")
    print("-" * 95)
    stage_names = ["no_cuts"] + [name for name, _ in CUT_STAGES]
    for stage in stage_names:
        v9 = v9_results.get(stage, 0)
        v15 = v15_results.get(stage, 0)
        ratio = v15 / v9 if v9 > 0 else 0
        print(f"{stage} | {v9:.1f} | {v15:.1f} | {ratio:.8f}")
    print("="*95)
    
    # 4. Create histograms with ratio plots
    create_cutflow_histograms(v9_results, v15_results, CUT_STAGES, "data_mm_channel_2017_bit")

if __name__ == "__main__":
    main()
