#!/usr/bin/env python3
"""
Scan all .log files in a directory and extract the graph identifiers from lines like:
    Event loop for graph embminus12p8 started
Prints each extracted identifier to stdout.
"""
import re
import glob
import os
import argparse
import numpy as np

def main():
    parser = argparse.ArgumentParser(
        description="Extract graph IDs from log files in a directory"
    )
    parser.add_argument(
        'logdir', nargs='?', default='.',
        help='Path to folder containing .log files (default: current directory)'
    )
    args = parser.parse_args()

    values = []  # list to store numeric graph values

    # Regex to find lines and capture the graph identifier
    pattern = re.compile(r'Event loop for graph ([^\s]+) started')

    # Iterate over all .log files
    for logfile in glob.glob(os.path.join(args.logdir, '*.log')):
        try:
            with open(logfile, 'r') as f:
                for line in f:
                    match = pattern.search(line)
                    if match:
                        name = match.group(1)
                        # Remove optional 'emb' prefix
                        core = name[3:] if name.startswith('emb') else name
                        # Handle 'minus' prefix
                        if core.startswith('minus'):
                            core = '-' + core[5:]
                        # Replace 'p' with '.' to form a float string
                        num_str = core.replace('p', '.')
                        try:
                            value = float(num_str)
                            values.append(value)
                        except ValueError:
                            # Skip entries that don't parse
                            continue
        except (OSError, UnicodeDecodeError):
            # Skip files we can't read
            continue

    # Sort and print the numeric graph values
    print(sorted(values), len(values))
    aranged_down = np.arange(-8.1, -20 - 0.1, -0.1).round(2).tolist()[:-1]
    aranged_up = np.arange(20, 8.1 - 0.1, -0.1).round(2).tolist()
    aranged_nom = np.arange(8, -8 - 0.1, -0.1).round(2).tolist()
    tauESvariations_down = sorted([x for x in aranged_down if x != 0.0])
    tauESvariations_up = sorted([x for x in aranged_up if x != 0.0])
    tauESvariations_nom = sorted([x for x in aranged_nom if x != 0.0])
    compare_down = [x for x in tauESvariations_down if x not in values]
    compare_up = [x for x in tauESvariations_up if x not in values]
    compare_nom = [x for x in tauESvariations_nom if x not in values]
    print("Missing down variations:", compare_down)
    print("Missing up variations:", compare_up)
    print("Missing nominal variations:", compare_nom)
if __name__ == '__main__':
    main()
