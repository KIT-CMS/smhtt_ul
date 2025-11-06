import pathlib
from copy import deepcopy
import os
from tqdm import tqdm


eras = [
    ("2016preVFP", "pre"),
    ("2017", "17"),
    ("2018", "18"),
    ("2016postVFP", "post"),
]
wps = [
    ("Medium", "M"),
    ("Tight", "T"),
]
base_path = pathlib.Path("/web/jvoss/public_html/20_06_2025_SFs_LO/")
work_path = pathlib.Path("/work/jvoss/ntuples/smhtt_ul_SFs/")

trigger=True

for era, era_short in tqdm(eras):
    for wp in wps:
        web_path = str(base_path / f"{era}/{wp[0]}/")
        scan_path = str(work_path / f"scan_2D_{wp[1]}_{era_short}_8to8_20_06_LO_extended/")
        impact_path = str(work_path / f"impacts_{wp[1]}_{era_short}_8to8_20_06_LO_extended_Test_shape_unc/")
        poi_path = str(work_path / f"poi_corr_{wp[1]}_{era_short}_8to8_20_06_LO_extended/")
        postfit_path = str(work_path / f"output/postfitplots_emb_{wp[1]}_{era_short}_8to8_20_06_LO_extended_multifit_sep/{wp[0]}/")
        ctrl_path = str(work_path / f"output/Run{era}_plots_emb_classic_{wp[1]}_{era_short}_8to8_20_06_LO_extended/")

        print(f"cp -r {scan_path} {web_path}")
        print(f"cp -r {impact_path} {web_path}")
        print(f"cp -r {poi_path} {web_path}")
        print(f"cp -r {postfit_path} {web_path}")
        print(f"cp -r {ctrl_path} {web_path}")
        print(f"mv {web_path}/{wp[0]} {web_path}/postfits")
        if trigger:
            try:
                os.system(f"cp -r {scan_path} {web_path}")
                os.system(f"cp -r {impact_path} {web_path}")
                os.system(f"cp -r {poi_path} {web_path}")
                os.system(f"cp -r {postfit_path} {web_path}")
                os.system(f"cp -r {ctrl_path} {web_path}")
                os.system(f"mv {web_path}/{wp[0]} {web_path}/postfits")
            except:
                print(f"Failed for {era} {wp[0]}, might not exist yet")
                continue
                

    
    