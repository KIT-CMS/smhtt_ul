#!/usr/bin/env python3
"""
Scan all .root files in a directory, extract graph identifiers from histogram keys, convert them to floats, sort and print.

Looks inside each ROOT file for TH* keys whose name is of the form:
    <graphID>#...  (e.g. embminus18p1#mt-Embedded-Pt20to25#Nominal#m_vis)
Extracts the <graphID> part, strips optional 'emb', converts 'minusNNpM' to -NN.M and 'NNpM' to NN.M,
collects all values, sorts them, and prints them to stdout.
"""
import os
import glob
import argparse
import ROOT    # Source the cmssw setup to use ROOT!!!
import numpy as np

def main():
    parser = argparse.ArgumentParser(
        description="Extract numeric graph IDs from ROOT histogram keys in a directory"
    )
    parser.add_argument(
        'rootdir', nargs='?', default='.',
        help='Path to folder containing .root files (default: current directory)'
    )
    args = parser.parse_args()

    values = []
    # Regex-like conversion logic reused
    for filepath in glob.glob(os.path.join(args.rootdir, '*.root')):
        f = ROOT.TFile.Open(filepath, 'READ')
        if not f or f.IsZombie():
            continue
        for key in f.GetListOfKeys():
            name = key.GetName()
            # Take part before first '#'
            graph = name.split('#', 1)[0]
            # Strip optional 'emb' prefix
            core = graph[3:] if graph.startswith('emb') else graph
            # Handle 'minus' prefix
            if core.startswith('minus'):
                core = '-' + core[5:]
            # Replace 'p' with '.'
            num_str = core.replace('p', '.')
            try:
                value = float(num_str)
                values.append(value)
                f.Close()
                break  # only need first match
            except ValueError:
                continue

    # sort and print
    print(f"Found values: {sorted(values)}, Count: {len(values)}")
    # aranged_down = np.arange(-8.1, -20 - 0.1, -0.1).round(2).tolist()[:-1]
    # aranged_up = np.arange(20, 8.1 - 0.1, -0.1).round(2).tolist()
    aranged_nom = np.arange(8, -12 - 0.2, -0.2).round(2).tolist()
    # tauESvariations_down = sorted([x for x in aranged_down if x != 0.0])
    # tauESvariations_up = sorted([x for x in aranged_up if x != 0.0])
    tauESvariations_nom = sorted([x for x in aranged_nom if x != 0.0])
    # compare_down = [x for x in tauESvariations_down if x not in values]
    # compare_up = [x for x in tauESvariations_up if x not in values]
    compare_nom = [x for x in tauESvariations_nom if x not in values]
    # print("Missing down variations:", compare_down)
    # print("Missing up variations:", compare_up)
    print("Missing nominal variations:", compare_nom)

if __name__ == '__main__':
    main()
