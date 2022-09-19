from ntuple_processor.utils import Cut
from ntuple_processor.utils import Weight

from ntuple_processor.variations import ReplaceVariable
from ntuple_processor.variations import ReplaceCut
from ntuple_processor.variations import ReplaceWeight
from ntuple_processor.variations import RemoveCut
from ntuple_processor.variations import RemoveWeight
from ntuple_processor.variations import AddCut
from ntuple_processor.variations import AddWeight
from ntuple_processor.variations import SquareWeight
from ntuple_processor.variations import ReplaceCutAndAddWeight
from ntuple_processor.variations import ReplaceMultipleCuts
from ntuple_processor.variations import ReplaceMultipleCutsAndAddWeight
from ntuple_processor.variations import ReplaceVariableReplaceCutAndAddWeight
from ntuple_processor.variations import ChangeDatasetReplaceMultipleCutsAndAddWeight

##############################
# Signal uncertainties   #####
##############################


ggH_htxs = {
    "ggH125": "(HTXS_stage1_2_cat_pTjet30GeV>=100)&&(HTXS_stage1_2_cat_pTjet30GeV<=113)",
    "ggH_GG2H_FWDH125": "HTXS_stage1_2_cat_pTjet30GeV == 100",
    "ggH_GG2H_PTH_200_300125": "(HTXS_stage1_2_cat_pTjet30GeV == 101)&&(genbosonpt<300)",
    "ggH_GG2H_PTH_300_450125": "(HTXS_stage1_2_cat_pTjet30GeV == 101)&&(genbosonpt>=300)&&(genbosonpt<450)",
    "ggH_GG2H_PTH_450_650125": "(HTXS_stage1_2_cat_pTjet30GeV == 101)&&(genbosonpt>=450)&&(genbosonpt<650)",
    "ggH_GG2H_PTH_GT650125": "(HTXS_stage1_2_cat_pTjet30GeV == 101)&&(genbosonpt>=650)",
    "ggH_GG2H_0J_PTH_0_10125": "HTXS_stage1_2_cat_pTjet30GeV == 102",
    "ggH_GG2H_0J_PTH_GT10125": "HTXS_stage1_2_cat_pTjet30GeV == 103",
    "ggH_GG2H_1J_PTH_0_60125": "HTXS_stage1_2_cat_pTjet30GeV == 104",
    "ggH_GG2H_1J_PTH_60_120125": "HTXS_stage1_2_cat_pTjet30GeV == 105",
    "ggH_GG2H_1J_PTH_120_200125": "HTXS_stage1_2_cat_pTjet30GeV == 106",
    "ggH_GG2H_GE2J_MJJ_0_350_PTH_0_60125": "HTXS_stage1_2_cat_pTjet30GeV == 107",
    "ggH_GG2H_GE2J_MJJ_0_350_PTH_60_120125": "HTXS_stage1_2_cat_pTjet30GeV == 108",
    "ggH_GG2H_GE2J_MJJ_0_350_PTH_120_200125": "HTXS_stage1_2_cat_pTjet30GeV == 109",
    "ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125": "HTXS_stage1_2_cat_pTjet30GeV == 110",
    "ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125": "HTXS_stage1_2_cat_pTjet30GeV == 111",
    "ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125": "HTXS_stage1_2_cat_pTjet30GeV == 112",
    "ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125": "HTXS_stage1_2_cat_pTjet30GeV == 113",
}

qqH_htxs = {
    "qqH125": "(HTXS_stage1_2_cat_pTjet30GeV>=200)&&(HTXS_stage1_2_cat_pTjet30GeV<=210)",
    "qqH_QQ2HQQ_FWDH125": "HTXS_stage1_2_cat_pTjet30GeV == 200",
    "qqH_QQ2HQQ_0J125": "HTXS_stage1_2_cat_pTjet30GeV == 201",
    "qqH_QQ2HQQ_1J125": "HTXS_stage1_2_cat_pTjet30GeV == 202",
    "qqH_QQ2HQQ_GE2J_MJJ_0_60125": "HTXS_stage1_2_cat_pTjet30GeV == 203",
    "qqH_QQ2HQQ_GE2J_MJJ_60_120125": "HTXS_stage1_2_cat_pTjet30GeV == 204",
    "qqH_QQ2HQQ_GE2J_MJJ_120_350125": "HTXS_stage1_2_cat_pTjet30GeV == 205",
    "qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200125": "HTXS_stage1_2_cat_pTjet30GeV == 206",
    "qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125": "HTXS_stage1_2_cat_pTjet30GeV == 207",
    "qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125": "HTXS_stage1_2_cat_pTjet30GeV == 208",
    "qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125": "HTXS_stage1_2_cat_pTjet30GeV == 209",
    "qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125": "HTXS_stage1_2_cat_pTjet30GeV == 210",
}

WH_htxs = {
    "WH_lep125": "(HTXS_stage1_2_cat_pTjet30GeV>=300)&&(HTXS_stage1_2_cat_pTjet30GeV<=305)",
    "WH_lep_QQ2HLNU_FWDH125": "HTXS_stage1_2_cat_pTjet30GeV == 300",
    "WH_lep_QQ2HLNU_PTV_0_75125": "HTXS_stage1_2_cat_pTjet30GeV == 301",
    "WH_lep_QQ2HLNU_PTV_75_150125": "HTXS_stage1_2_cat_pTjet30GeV == 302",
    "WH_lep_QQ2HLNU_PTV_150_250_0J125": "HTXS_stage1_2_cat_pTjet30GeV == 303",
    "WH_lep_QQ2HLNU_PTV_150_250_GE1J125": "HTXS_stage1_2_cat_pTjet30GeV == 304",
    "WH_lep_QQ2HLNU_PTV_GT250125": "HTXS_stage1_2_cat_pTjet30GeV == 305",
}

ZH_htxs = {
    "ZH_lep125": "(HTXS_stage1_2_cat_pTjet30GeV>=400)&&(HTXS_stage1_2_cat_pTjet30GeV<=405)",
    "ZH_lep_QQ2HLL_FWDH125": "HTXS_stage1_2_cat_pTjet30GeV == 400",
    "ZH_lep_QQ2HLL_PTV_0_75125": "HTXS_stage1_2_cat_pTjet30GeV == 401",
    "ZH_lep_QQ2HLL_PTV_75_150125": "HTXS_stage1_2_cat_pTjet30GeV == 402",
    "ZH_lep_QQ2HLL_PTV_150_250_0J125": "HTXS_stage1_2_cat_pTjet30GeV == 403",
    "ZH_lep_QQ2HLL_PTV_150_250_GE1J125": "HTXS_stage1_2_cat_pTjet30GeV == 404",
    "ZH_lep_QQ2HLL_PTV_GT250125": "HTXS_stage1_2_cat_pTjet30GeV == 405",
}

ggZH_htxs = {
    "ggZH_lep125": "(HTXS_stage1_2_cat_pTjet30GeV>=500)&&(HTXS_stage1_2_cat_pTjet30GeV<=505)",
    "ggZH_lep_GG2HLL_FWDH125": "HTXS_stage1_2_cat_pTjet30GeV == 500",
    "ggZH_lep_GG2HLL_PTV_0_75125": "HTXS_stage1_2_cat_pTjet30GeV == 501",
    "ggZH_lep_GG2HLL_PTV_75_150125": "HTXS_stage1_2_cat_pTjet30GeV == 502",
    "ggZH_lep_GG2HLL_PTV_150_250_0J125": "HTXS_stage1_2_cat_pTjet30GeV == 503",
    "ggZH_lep_GG2HLL_PTV_150_250_GE1J125": "HTXS_stage1_2_cat_pTjet30GeV == 504",
    "ggZH_lep_GG2HLL_PTV_GT250125": "HTXS_stage1_2_cat_pTjet30GeV == 505",
}


ggh_acceptance = []
for unc in [
    "THU_ggH_Mig01",
    "THU_ggH_Mig12",
    "THU_ggH_Mu",
    "THU_ggH_PT120",
    "THU_ggH_PT60",
    "THU_ggH_Res",
    "THU_ggH_VBF2j",
    "THU_ggH_VBF3j",
    "THU_ggH_qmtop",
]:
    ggh_acceptance.append(
        AddWeight(unc + "Up", Weight("({})".format(unc), "{}_weight".format(unc)))
    )
    ggh_acceptance.append(
        AddWeight(unc + "Down", Weight("(2.0-{})".format(unc), "{}_weight".format(unc)))
    )

qqh_acceptance = []
for unc in [
    "THU_qqH_25",
    "THU_qqH_JET01",
    "THU_qqH_Mjj1000",
    "THU_qqH_Mjj120",
    "THU_qqH_Mjj1500",
    "THU_qqH_Mjj350",
    "THU_qqH_Mjj60",
    "THU_qqH_Mjj700",
    "THU_qqH_PTH200",
    "THU_qqH_TOT",
]:
    qqh_acceptance.append(
        AddWeight(unc + "Up", Weight("({})".format(unc), "{}_weight".format(unc)))
    )
    qqh_acceptance.append(
        AddWeight(unc + "Down", Weight("(2.0-{})".format(unc), "{}_weight".format(unc)))
    )

# STXS Acceptance Uncertainties
scheme_ggH = {
    "ggH_scale_0jet": ["ggH_GG2H_0J_PTH_0_10125", "ggH_GG2H_0J_PTH_GT10125"],
    "ggH_scale_1jet_lowpt": [
        "ggH_GG2H_1J_PTH_0_60125",
        "ggH_GG2H_1J_PTH_60_120125",
        "ggH_GG2H_1J_PTH_120_200125",
    ],
    "ggH_scale_2jet_lowpt": [
        "ggH_GG2H_GE2J_MJJ_0_350_PTH_0_60125",
        "ggH_GG2H_GE2J_MJJ_0_350_PTH_60_120125",
        "ggH_GG2H_GE2J_MJJ_0_350_PTH_120_200125",
    ],
    "ggH_scale_highpt": ["ggH_GG2H_PTH_200_300125", "ggH_GG2H_PTH_300_450125"],
    "ggH_scale_very_highpt": ["ggH_GG2H_PTH_450_650125", "ggH_GG2H_PTH_GT650125"],
    "ggH_scale_vbf": [
        "ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125",
        "ggH_GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125",
        "ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125",
        "ggH_GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125",
    ],
}
scheme_qqH = {
    "vbf_scale_0jet": ["qqH_QQ2HQQ_0J125"],
    "vbf_scale_1jet": ["qqH_QQ2HQQ_1J125"],
    "vbf_scale_lowmjj": [
        "qqH_QQ2HQQ_GE2J_MJJ_0_60125",
        "qqH_QQ2HQQ_GE2J_MJJ_60_120125",
        "qqH_QQ2HQQ_GE2J_MJJ_120_350125",
    ],
    "vbf_scale_highmjj_lowpt": [
        "qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25125",
        "qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25125",
        "qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25125",
        "qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25125",
    ],
    "vbf_scale_highmjj_highpt": ["qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200125"],
}
