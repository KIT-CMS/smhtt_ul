import uproot
import numpy as np
import matplotlib.pyplot as plt
import concurrent.futures
from collections import defaultdict
from XRootD import client
from XRootD.client.flags import DirListFlags

def get_file_list(server, path):
    fs = client.FileSystem(server)
    status, listing = fs.dirlist(path, DirListFlags.STAT)
    if not status.ok:
        raise RuntimeError(f"Error listing {path}: {status.message}")
    return [f"{server}/{path}/{item.name}" for item in listing if item.name.endswith(".root")]

def get_cutflow_data(file_path, hist_name):
    """Accesses the histogram and pulls labels directly from the fXaxis member."""
    try:
        with uproot.open(file_path) as f:
            # Get the histogram object
            if hist_name not in f:
                return {}
            hist = f[hist_name]
            
            # 1. Get values (excluding underflow/overflow)
            vals = hist.values(flow=False)
            
            # 2. Get labels directly from the fXaxis member
            # This is the most robust way to get labels in uproot
            try:
                # Try high-level first
                labels = hist.axis().labels()
                # If high-level fails, try low-level member access
                if labels is None or len(labels) == 0:
                    labels = hist.member("fXaxis").member("fLabels")
            except:
                labels = None

            # 3. Last resort fallback: manually iterate through bins
            if labels is None or len(labels) == 0:
                try:
                    # ROOT bins are 1-based, we want n bins
                    labels = [hist.axis().label(i) for i in range(1, len(vals) + 1)]
                except:
                    return {}

            # Create the dictionary {label: value}
            # Only keep bins that have a non-empty string label
            data = {}
            for lbl, v in zip(labels, vals):
                if lbl: # filter out None or empty
                    data[str(lbl)] = v
            return data
            
    except Exception:
        return {}

def find_master_labels(files, hist_name):
    """Finds the first file that gives us the 9 labels we need."""
    print("Searching files for bin labels...")
    for f_path in files[:20]: # Check up to 20 files
        data = get_cutflow_data(f_path, hist_name)
        if data:
            labels = list(data.keys())
            if len(labels) > 0:
                print(f"--> Found {len(labels)} labels.")
                return labels
    return []

def aggregate(files, hist_name, label):
    """Sums up all files for a version."""
    counts = defaultdict(float)
    print(f"--> Summing {len(files)} files for {label}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(get_cutflow_data, f, hist_name) for f in files]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            for k, v in res.items():
                counts[k] += v
    return counts

def main():
    # --- CONFIG ---
    REDIRECTOR = "root://cmsdcache-kit-disk.gridka.de"
    V9_PATH = "/store/user/jvoss/CROWN/ntuples/tauID_nTuples_MT_vvL_20_06_2025_SFs_ES_m8p8-16/CROWNRun/2016preVFP/SingleMuon_Run2016C-HIPM/mm"
    """
    V9 all data dirs:
    SingleMuon_Run2016B-ver1                                               
    SingleMuon_Run2016B-ver2                                               
    SingleMuon_Run2016C-HIPM                                               
    SingleMuon_Run2016D-HIPM
    SingleMuon_Run2016E-HIPM
    SingleMuon_Run2016F-HIPM
    """
    
    V15_PATH = "/store/user/jvoss/CROWN/ntuples/SFs_EMB_Run2_v15nanoAOD_29_06_26__16PreVFP/CROWNRun/2016preVFP/SingleMuon_Run2016C-HIPM/mm"
    """
    V15 all data dirs:
    SingleMuon_Run2016B_v1-HIPM
    SingleMuon_Run2016B_v2-HIPM
    SingleMuon_Run2016C-HIPM
    SingleMuon_Run2016D-HIPM
    SingleMuon_Run2016E-HIPM
    SingleMuon_Run2016F-HIPM
    """
    HIST_NAME = "cutflow"
    # --------------

    # 1. Get file lists
    files_v9 = get_file_list(REDIRECTOR, V9_PATH)
    files_v15 = get_file_list(REDIRECTOR, V15_PATH)

    # 2. Get the labels
    master_labels = find_master_labels(files_v9, HIST_NAME)
    if not master_labels:
        master_labels = find_master_labels(files_v15, HIST_NAME)
    
    if not master_labels:
        print("Fatal: Could not find any labels in 'cutflow' histogram.")
        return

    # 3. Fix the order: alphabetical, then GoodMuMuPairs at the end
    if "GoodMuMuPairs" in master_labels:
        master_labels.remove("GoodMuMuPairs")
        master_labels.sort()
        master_labels.append("GoodMuMuPairs")
    if "GoldenJSONFilter" and "Flag_goodVertices" and "Flag_globalSuperTightHalo2016Filter" in master_labels:
        master_labels.remove("Flag_goodVertices")
        master_labels.remove("Flag_globalSuperTightHalo2016Filter")
        master_labels.remove("GoldenJSONFilter")
        master_labels.insert(0,"Flag_globalSuperTightHalo2016Filter")
        master_labels.insert(0,"Flag_goodVertices")
        master_labels.insert(0,"GoldenJSONFilter")

    # 4. Sum everything
    sum_v9 = aggregate(files_v9, HIST_NAME, "V9")
    sum_v15 = aggregate(files_v15, HIST_NAME, "V15")

    # 5. Extract aligned arrays
    final_v9 = np.array([sum_v9.get(l, 0) for l in master_labels])
    final_v15 = np.array([sum_v15.get(l, 0) for l in master_labels])

    # 6. Print Table
    print("\n" + "="*95)
    print(f"{'Cut Selection Step':<45} | {'Sum V9':>15} | {'Sum V15':>15} | {'Ratio V15/V9':>8}")
    print("-" * 95)
    for i, lbl in enumerate(master_labels):
        v9, v15 = final_v9[i], final_v15[i]
        ratio = v15 / v9 if v9 > 0 else 0
        print(f"{lbl:<45} | {v9:>15.1f} | {v15:>15.1f} | {ratio:>8.8f}")
    print("="*95)

    # 7. Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, 
                                   gridspec_kw={'height_ratios': [3, 1]})
    plt.subplots_adjust(hspace=0.05)
    x = np.arange(len(master_labels))

    ax1.step(x, final_v9, where='mid', label='Version 9', color='blue', lw=2)
    ax1.step(x, final_v15, where='mid', label='Version 15', color='red', ls='--', lw=2)
    # ax1.set_yscale('log')
    ax1.set_ylabel("Summed Events")
    ax1.legend()
    ax1.grid(alpha=0.2)

    ratio_vals = np.divide(final_v15, final_v9, out=np.zeros_like(final_v15), where=final_v9!=0)
    ax2.errorbar(x, ratio_vals, yerr=0, fmt='ko')
    ax2.axhline(1, color='black')
    ax2.set_ylabel("V15 / V9")
    ax2.set_ylim(0.9, 1.1)
    ax2.set_xticks(x)
    ax2.set_xticklabels(master_labels, rotation=40, ha='right')
    ax2.grid(axis='y', ls='--', alpha=0.5)

    plt.tight_layout()
    out_filename = "cutflow_comparison_V9_V15_data"
    plt.savefig(f"{out_filename}.pdf")
    plt.savefig(f"{out_filename}.png")
    print(f"\nOutput saved to: {out_filename}.p*")

if __name__ == "__main__":
    main()