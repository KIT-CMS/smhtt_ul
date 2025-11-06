import pathlib
from copy import deepcopy
import os
from tqdm import tqdm

rules = [
    ("Run2018_", ""),
    ("2018_", ""),
    ("Run2017_", ""),
    ("2017_", ""),
    ("Run2016preVFP_", ""),
    ("2016preVFP_", ""),
    ("Run2016postVFP_", ""),
    ("2016postVFP_", ""),
    ("_m_vis_", "_"),
    ("_extended", ""),
    ("_POIS_correlations_ID_ES", ""),
    ("_8to8_20_06", ""),
    ("_scan_", "_"),
    
]

for x in tqdm(pathlib.Path("/web/jvoss/public_html/20_06_2025_SFs_LO/").glob("**/*.pdf")):
    # if "m_vis" not in x.name:
        # continue
    _x = deepcopy(x)
    trigger = False
    for rule in rules:
        if rule[0] in x.name:
            new_name = x.name.replace(rule[0], rule[1])
            x = x.parent / new_name
            trigger = True
    if not trigger:
        continue
    _x = str(_x.resolve())
    x = str(x.resolve())
    # print(f"Renaming")
    # print(f"\t{_x}")
    # print(f"\t{x}")
    os.system(f"mv {_x} {x}")
    # break

    
    