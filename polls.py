import ROOT
import argparse
# import matplotlib.pyplot as plt
import os


parser = argparse.ArgumentParser(description="Plot the tau ID SF")
parser.add_argument("--wp", type=str, default="tight", help="TauID WP: tight, medium, loose etc")
parser.add_argument("--era", type=str, default="2018", help="2016, 2017 or 2018")
parser.add_argument("--ntupletag", type=str, default="2022_07_v6", help="ntupletag like 2022_07_v6")
parser.add_argument("--tag", type=str, default="medium_mt_2018UL", help="tag like medium_mt_2018UL")
parser.add_argument("--channel", type=str, default="mt", help="mt, et, em , tt")
parser.add_argument("--mode", type=str, default="postfit", help="pefit or postfit")



args = parser.parse_args()

output_folder = "/work/olavoryk/tauID_SF_ES/smhtt_ul/polls/{NTUPLETAG}-{TAG}/{ERA}_tauid_{WP}".format(NTUPLETAG = args.ntupletag, TAG=args.tag, ERA=args.era, WP=args.wp)

# if args.wp == "medium":
#     output_folder = "/work/olavoryk/tauID_SF_ES/smhtt_ul/output/datacards/2022_07_v6-medium_mt_2018UL_29Sep/2018_tauid_medium"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)


datacard_output="/work/olavoryk/tauID_SF_ES/smhtt_ul/output/datacards/{NTUPLETAG}-{TAG}/{ERA}_tauid_{WP}".format(NTUPLETAG = args.ntupletag, TAG=args.tag, ERA=args.era, WP=args.wp)



pt_bins_folder = ["DM0", "DM1", "DM10_11", "Inclusive", "Pt20to25", "Pt30to35", "Pt35to40", "PtGt40"]


root_file = "fitDiagnostics.2018.root"


if args.mode == "postfit":
    if not os.path.exists(output_folder+"/postfit/"):
        os.makedirs(output_folder+"/postfit/")

    for pt_b in pt_bins_folder:
        os.system("python HiggsAnalysis/CombinedLimit/test/diffNuisances.py --pullDef unconstPullAsym /work/olavoryk/tauID_SF_ES/smhtt_ul/output/datacards/{NTUPLETAG}-{TAG}/{ERA}_tauid_{WP}/".format(NTUPLETAG = args.ntupletag, TAG=args.tag, ERA=args.era, WP=args.wp)+"htt_mt_"+pt_b+"/"+root_file+" -f html > "+ output_folder+"/postfit/pulls_postfit_"+pt_b+".html")
    

if args.mode == "prefit":

    if not os.path.exists(output_folder+"/prefit/"):
        os.makedirs(output_folder+"/prefit/")

    for pt_b in pt_bins_folder:
        os.system("python HiggsAnalysis/CombinedLimit/test/diffNuisances.py   /work/olavoryk/tauID_SF_ES/smhtt_ul/output/datacards/{NTUPLETAG}-{TAG}/{ERA}_tauid_{WP}/".format(NTUPLETAG = args.ntupletag, TAG=args.tag, ERA=args.era, WP=args.wp)+"htt_mt_"+pt_b+"/"+root_file+" -f html > "+ output_folder+"/prefit/pulls_prefit_"+pt_b+".html")

