min_id_dm0=0.75
max_id_dm0=1.2
min_es_dm0=-4.0
max_es_dm0=4.0
id_dm0=0.97
es_dm0=-0.6

min_id_dm1=0.85
max_id_dm1=1.25
min_es_dm1=-4.0
max_es_dm1=4.0
id_dm1=1.12
es_dm1=-1.4

min_id_dm10_11=0.9
max_id_dm10_11=1.2
min_es_dm10_11=-4.0
max_es_dm10_11=4.0
id_dm10_11=1.02
es_dm10_11=-0.5

min_id_pt20to25=0.75
max_id_pt20to25=1.2
min_es_pt20to25=-4.0
max_es_pt20to25=4.0
id_pt20to25=0.97
es_pt20to25=-0.6

min_id_pt25to30=0.75
max_id_pt25to30=1.2
min_es_pt25to30=-4.0
max_es_pt25to30=4.0
id_pt25to30=0.97
es_pt25to30=-0.6

min_id_pt30to35=0.75
max_id_pt30to35=1.2
min_es_pt30to35=-4.0
max_es_pt30to35=4.0
id_pt30to35=0.97
es_pt30to35=-0.6

min_id_pt35to40=0.75
max_id_pt35to40=1.2
min_es_pt35to40=-4.0
max_es_pt35to40=4.0
id_pt35to40=0.97
es_pt35to40=-0.6

min_id_ptgt40=0.75
max_id_ptgt40=1.2
min_es_ptgt40=-4.0
max_es_ptgt40=4.0
id_ptgt40=0.97
es_ptgt40=-0.6

if [[ $cat == "DM0" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    id_fit_stri='DM_0'
    map_str='"map=^.*/EMB_${cat}:r_EMB_DM_0[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "DM1" ]]; then
    min_id_sep=$min_id_dm1
    max_id_sep=$max_id_dm1
    min_es_sep=$min_es_dm1
    max_es_sep=$max_es_dm1
    cent_id_sep=$id_dm1
    cent_es_sep=$es_dm1
    id_fit_stri=DM_1
    map_str='"map=^.*/EMB_${cat}:r_EMB_DM_1[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "DM10_11" ]]; then
    min_id_sep=$min_id_dm10_11
    max_id_sep=$max_id_dm10_11
    min_es_sep=$min_es_dm10_11
    max_es_sep=$max_es_dm10_11
    cent_id_sep=$id_dm10_11
    cent_es_sep=$es_dm10_11
    id_fit_stri=DM_10_11
    map_str='"map=^.*/EMB_${cat}:r_EMB_DM_10_11[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "Pt20to25" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    id_fit_stri='Pt_20to25'
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_20to25[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "Pt25to30" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    id_fit_stri='Pt_25to30'
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_25to30[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "Pt30to35" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    id_fit_stri='Pt_30to35'
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_30to35[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "Pt35to40" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    id_fit_stri='Pt_35to40'
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_35to40[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "PtGt40" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    id_fit_stri='Pt_Gt40'
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_Gt40[1,${min_id_sep},${max_id_sep}]"'
fi