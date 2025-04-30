min_id_dm0=0.8
max_id_dm0=1.1
min_es_dm0=-8.0
max_es_dm0=-2.0
id_dm0=0.95
es_dm0=-7.0

min_id_dm1=0.9
max_id_dm1=1.1
min_es_dm1=-4.0
max_es_dm1=3.0
id_dm1=1.01
es_dm1=0.1

min_id_dm10=0.9
max_id_dm10=1.18
min_es_dm10=-2.6
max_es_dm10=4.0
id_dm10=0.98
es_dm10=2.0

min_id_dm11=0.78
max_id_dm11=1.2
min_es_dm11=-6.0
max_es_dm11=4.0
id_dm11=1.02
es_dm11=-0.2

min_id_dm10_11=0.5
max_id_dm10_11=1.5
min_es_dm10_11=-8.0
max_es_dm10_11=4.0
id_dm10_11=1.05
es_dm10_11=-1.5

min_id_dm0_pt20_40=0.8
max_id_dm0_pt20_40=1.15
min_es_dm0_pt20_40=-8.0
max_es_dm0_pt20_40=-2.0
id_dm0_pt20_40=0.98
es_dm0_pt20_40=-7.98

min_id_dm1_pt20_40=0.85
max_id_dm1_pt20_40=1.2
min_es_dm1_pt20_40=-6.0
max_es_dm1_pt20_40=4.0
id_dm1_pt20_40=1.02
es_dm1_pt20_40=0.2

min_id_dm10_pt20_40=0.8
max_id_dm10_pt20_40=1.23
min_es_dm10_pt20_40=-5.0
max_es_dm10_pt20_40=4.0
id_dm10_pt20_40=1.0
es_dm10_pt20_40=0.0

min_id_dm11_pt20_40=0.65
max_id_dm11_pt20_40=1.5
min_es_dm11_pt20_40=-8.0
max_es_dm11_pt20_40=4.0
id_dm11_pt20_40=1.0
es_dm11_pt20_40=0.0

min_id_dm0_pt40_200=0.5
max_id_dm0_pt40_200=1.2
min_es_dm0_pt40_200=-7.0
max_es_dm0_pt40_200=4.0
id_dm0_pt40_200=0.8
es_dm0_pt40_200=-0.2

min_id_dm1_pt40_200=1.25
max_id_dm1_pt40_200=0.6
min_es_dm1_pt40_200=-3.0
max_es_dm1_pt40_200=4.0
id_dm1_pt40_200=0.85
es_dm1_pt40_200=2.5

min_id_dm10_pt40_200=1.0
max_id_dm10_pt40_200=1.5
min_es_dm10_pt40_200=-8.0
max_es_dm10_pt40_200=4.0
id_dm10_pt40_200=1.49
es_dm10_pt40_200=-6.0

min_id_dm11_pt40_200=0.65
max_id_dm11_pt40_200=1.2
min_es_dm11_pt40_200=-8.0
max_es_dm11_pt40_200=4.0
id_dm11_pt40_200=0.9
es_dm11_pt40_200=-5.8

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
fi

if [[ $cat == "DM1" ]]; then
    min_id_sep=$min_id_dm1
    max_id_sep=$max_id_dm1
    min_es_sep=$min_es_dm1
    max_es_sep=$max_es_dm1
    cent_id_sep=$id_dm1
    cent_es_sep=$es_dm1
fi

if [[ $cat == "DM10" ]]; then
    min_id_sep=$min_id_dm10
    max_id_sep=$max_id_dm10
    min_es_sep=$min_es_dm10
    max_es_sep=$max_es_dm10
    cent_id_sep=$id_dm10
    cent_es_sep=$es_dm10
fi

if [[ $cat == "DM11" ]]; then
    min_id_sep=$min_id_dm11
    max_id_sep=$max_id_dm11
    min_es_sep=$min_es_dm11
    max_es_sep=$max_es_dm11
    cent_id_sep=$id_dm11
    cent_es_sep=$es_dm11
fi

if [[ $cat == "DM10_11" ]]; then
    min_id_sep=$min_id_dm10_11
    max_id_sep=$max_id_dm10_11
    min_es_sep=$min_es_dm10_11
    max_es_sep=$max_es_dm10_11
    cent_id_sep=$id_dm10_11
    cent_es_sep=$es_dm10_11
fi

if [[ $cat == "DM0_PT20_40" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0    
fi

if [[ $cat == "DM1_PT20_40" ]]; then
    min_id_sep=$min_id_dm1
    max_id_sep=$max_id_dm1
    min_es_sep=$min_es_dm1
    max_es_sep=$max_es_dm1
    cent_id_sep=$id_dm1
    cent_es_sep=$es_dm1
fi

if [[ $cat == "DM10_PT20_40" ]]; then
    min_id_sep=$min_id_dm10
    max_id_sep=$max_id_dm10
    min_es_sep=$min_es_dm10
    max_es_sep=$max_es_dm10
    cent_id_sep=$id_dm10
    cent_es_sep=$es_dm10
fi

if [[ $cat == "DM11_PT20_40" ]]; then
    min_id_sep=$min_id_dm11
    max_id_sep=$max_id_dm11
    min_es_sep=$min_es_dm11
    max_es_sep=$max_es_dm11
    cent_id_sep=$id_dm11
    cent_es_sep=$es_dm11
fi

if [[ $cat == "DM0_PT40_200" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0    
fi

if [[ $cat == "DM1_PT40_200" ]]; then
    min_id_sep=$min_id_dm1
    max_id_sep=$max_id_dm1
    min_es_sep=$min_es_dm1
    max_es_sep=$max_es_dm1
    cent_id_sep=$id_dm1
    cent_es_sep=$es_dm1
fi

if [[ $cat == "DM10_PT40_200" ]]; then
    min_id_sep=$min_id_dm10
    max_id_sep=$max_id_dm10
    min_es_sep=$min_es_dm10
    max_es_sep=$max_es_dm10
    cent_id_sep=$id_dm10
    cent_es_sep=$es_dm10
fi

if [[ $cat == "DM11_PT40_200" ]]; then
    min_id_sep=$min_id_dm11
    max_id_sep=$max_id_dm11
    min_es_sep=$min_es_dm11
    max_es_sep=$max_es_dm11
    cent_id_sep=$id_dm11
    cent_es_sep=$es_dm11
fi

if [[ $cat == "Pt20to25" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_20to25[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "Pt25to30" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_25to30[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "Pt30to35" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_30to35[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "Pt35to40" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_35to40[1,${min_id_sep},${max_id_sep}]"'
fi

if [[ $cat == "PtGt40" ]]; then
    min_id_sep=$min_id_dm0
    max_id_sep=$max_id_dm0
    min_es_sep=$min_es_dm0
    max_es_sep=$max_es_dm0
    cent_id_sep=$id_dm0
    cent_es_sep=$es_dm0
    map_str='"map=^.*/EMB_${cat}:r_EMB_Pt_Gt40[1,${min_id_sep},${max_id_sep}]"'
fi