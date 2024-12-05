import ROOT
import json
import argparse

# Uses handwritten input_output_conf.json to get file and output path:
# def in_out_put():
#     with open('input_output_conf.json') as f:
#         d = json.load(f)
#         input_file = d['input_file']
#         out_folder = d['out_fold']

#         return input_file, out_folder

# inp_file = in_out_put()[0]
# out_fold = in_out_put()[1]

# Parsing input and output path:
parser = argparse.ArgumentParser()

parser.add_argument('--input', '-in', type=str, required=True, help='path to input file fitDiagnostics.$ERA.root')
parser.add_argument('--output', '-out', type=str, required=True, help='path to output folder')
parser.add_argument('--era', type=str, required=True, help='Used ERA')
args = parser.parse_args()

inp_file = args.input
out_fold = args.output
era = args.era

file_inp = ROOT.TFile(inp_file)


prefit_fold = "shapes_prefit"
postfit_folder = "shapes_fit_s"

prefit_in_folders_names = []
postfit_in_folders_names = []

prefit_keys = file_inp.Get(prefit_fold).GetListOfKeys()
postfit_keys = file_inp.Get(postfit_folder).GetListOfKeys()


for i in range(len(prefit_keys)):
    prefit_in_folders_names.append(file_inp.Get(prefit_fold).GetListOfKeys()[i].GetName())

for i in range(len(postfit_keys)):
    postfit_in_folders_names.append(file_inp.Get(postfit_folder).GetListOfKeys()[i].GetName())

postfit_in_folders_names

new_file = ROOT.TFile(out_fold+f"postfitshape.{era}.root", "recreate")

for i in range(len(prefit_in_folders_names)):
    print(prefit_in_folders_names[i])
    hist_list  = file_inp.Get("shapes_prefit/"+prefit_in_folders_names[i]).GetListOfKeys()

    hist_list_pre = []
    for j in range(len(hist_list)):
        hist_list_pre.append( file_inp.Get("shapes_prefit/"+prefit_in_folders_names[i]).GetListOfKeys()[j].GetName() )
    # print(hist_list_pre)

    new_file.mkdir(prefit_in_folders_names[i]+"_prefit")
    new_file.cd(prefit_in_folders_names[i]+"_prefit")

    for shap in hist_list_pre:
        hist_proc = file_inp.Get("shapes_prefit/"+prefit_in_folders_names[i]+"/"+shap)
        hist_proc.SetTitle("data_obs")
        if shap == "data":
            n =0
            x0 = 0
            xn = 0
            if prefit_in_folders_names[i] != "htt_mm_100_Run2016":
                n = hist_proc.GetN()
                x0 = 30
                xn = 125
            else:
                n = 1
                x0 = 60
                xn = 120

            histogram = ROOT.TH1F("data_obs", "data_obs", n, x0, xn )
            for k in range(1, n+1):
                histogram.SetBinContent(k, hist_proc.GetPointY(k-1))
                histogram.SetBinError(k, hist_proc.GetErrorYhigh(k-1))
            histogram.Write("data_obs")
            
        else:
            hist_proc.Write()

new_file.Close()

new_file1 = ROOT.TFile(out_fold+f"postfitshape.{era}.root", "update")

for i in range(len(postfit_in_folders_names)):
    hist_list  = file_inp.Get(postfit_folder+"/"+postfit_in_folders_names[i]).GetListOfKeys()

    hist_list_post = []
    for j in range(len(hist_list)):
        hist_list_post.append( file_inp.Get(postfit_folder+"/"+postfit_in_folders_names[i]).GetListOfKeys()[j].GetName() )
    print(hist_list_post)
    

    new_file1.mkdir(postfit_in_folders_names[i]+"_postfit")
    new_file1.cd(postfit_in_folders_names[i]+"_postfit")

    for shap in hist_list_post:
        hist_proc1 = file_inp.Get(postfit_folder+"/"+postfit_in_folders_names[i]+"/"+shap)
        hist_proc1.SetTitle("data_obs")
        if shap == "data":
            n1 =0
            x01 = 0
            xn1 = 0

            if prefit_in_folders_names[i] != "htt_mm_100_Run2016":

                n1 = hist_proc1.GetN()
                x01 = 30
                xn1 = 125
            else:
                n1 = 1
                x01 = 60
                xn1 = 120

            
            histogram1 = ROOT.TH1F("data_obs", "data_obs", n1, x01, xn1 )
            for k in range(1, n1+1):
                histogram1.SetBinContent(k, hist_proc1.GetPointY(k-1))
                histogram1.SetBinError(k, hist_proc1.GetErrorYhigh(k-1))
            histogram1.Write("data_obs")
            
        else:
            hist_proc1.Write()

new_file1.Close()