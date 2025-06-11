
import os
import yaml
eras= [("2016preVFP","pre"),("2016postVFP","post"), ("2017","17"), ("2018","18")]
wps = [("Medium","M"),("Tight","T")]
dms = ["DM0","DM0_PT20_40","DM0_PT40_200","DM1","DM1_PT20_40","DM1_PT40_200","DM10","DM10_PT20_40","DM10_PT40_200", "DM11","DM11_PT20_40","DM11_PT40_200"]
table_labels = [("DM0","DM1","DM10","DM11"),("Incl.", "PT20-40", "PT40-200")]
latex_code = ""
table_code = ""
impact_dict = {}
total_path = "/work/jvoss/ntuples/smhtt_ul_SFs/"
poi_path="/work/jvoss/ntuples/smhtt_ul_SFs/poi_corr_all.yaml"
for era, era_short in eras:
    for wp, wp_short in wps:
        for dm in dms:
            # Get fit results from impact jsons.
            impact_str_ES = total_path+f"impacts_{wp_short}_{era_short}_8to8/{era}/mt/{wp}/tauid_{wp}_impacts_r_{dm}_{wp_short}_{era_short}_8to8_ES.json"
            impact_str = total_path+f"impacts_{wp_short}_{era_short}_8to8/{era}/mt/{wp}/tauid_{wp}_impacts_r_{dm}_{wp_short}_{era_short}_8to8.json"
            
            if era not in impact_dict:
                impact_dict[era] = {}
            if wp not in impact_dict[era]:
                impact_dict[era][wp] = {}
            if dm not in impact_dict[era][wp]:
                impact_dict[era][wp][dm] = {}
            
            if os.path.exists(impact_str_ES):
                with open(impact_str_ES, "r") as file_ES:
                    data_ES = yaml.safe_load(file_ES) or {}
                    if data_ES["POIs"][0]["name"] == "ES_"+dm:
                        es_list = data_ES["POIs"][0]["fit"]
                        es = round(es_list[1], 2)
                        es_down = round(es_list[0] - es, 2)
                        es_up = round(es_list[2] - es, 2)
                        impact_dict[era][wp][dm]["ES_"+dm] = (es, es_down, es_up)
                    else:
                        breakpoint()
                    
            if os.path.exists(impact_str):
                with open(impact_str, "r") as file:
                    data = yaml.safe_load(file) or {}
                    if data["POIs"][0]["name"] == "r_EMB_"+dm:
                        id_list = data["POIs"][0]["fit"]
                        id = round(id_list[1], 3)
                        id_down = round(id_list[0] - id, 3)
                        id_up = round(id_list[2] - id, 3)
                        impact_dict[era][wp][dm]["r_EMB_"+dm] = (id, id_down, id_up)
                    else:
                        breakpoint()
            
            # Do LATeX plots:
            latex_code+=rf"""
\begin{{frame}}{{Scan {era} {wp} WP}}
    \begin{{columns}}
        \column{{\kitthreecolumns}}
        \vspace{{-1.1cm}}
            \begin{{figure}}
                \centering
                \includegraphics[width=\linewidth]{{images/scan_{era_short}_{wp_short}/scan_2D_{dm}_{wp_short}_{era_short}_8to8_id_es_tests.pdf}}
                \caption{{2D likelihood scan}}
            \end{{figure}}
        \column{{\kitthreecolumns}}
        \vspace{{-2cm}}
            \begin{{figure}}
                \centering
                \includegraphics[width=\linewidth]{{images/scan_{era_short}_{wp_short}/1D_profiles_2Dscan_{dm}_{wp_short}_{era_short}_8to8_id_es_tests.pdf}}
                \caption{{1D profiles of 2D scan}}
            \end{{figure}}           
    \end{{columns}}
\end{{frame}}

\begin{{frame}}{{Impact {era} {wp} WP}}
    \begin{{columns}}
        % \vspace{{-1.1cm}}
        \column{{\kitthreecolumns}}
            \begin{{figure}}
                \centering
                \includegraphics[width=\linewidth]{{images/impacts_{era_short}_{wp_short}/tauid_{wp}_impacts_r_{dm}_{wp_short}_{era_short}_8to8.pdf}}
                \caption{{Impact on ID}}
            \end{{figure}}
        \column{{\kitthreecolumns}}
            \begin{{figure}}
                \centering
                \includegraphics[width=\linewidth]{{images/impacts_{era_short}_{wp_short}/tauid_{wp}_impacts_r_{dm}_{wp_short}_{era_short}_8to8_ES.pdf}}
                \caption{{Impact on ES}}
            \end{{figure}}
    \end{{columns}}
\end{{frame}}
"""

with open("latex_figures.tex", "w") as f:
    f.write(latex_code)

###################
# Do LATeX tables:#
with open(poi_path, "r") as f:
    corr_yaml = yaml.safe_load(f) or {}

for era, era_short in eras:
    for wp, wp_short in wps:
        # Build table for r_EMB impacts ("ID" impacts)
        table_r_emb = r"""\begin{tabular}{lccc}
\hline
 & %s & %s & %s \\
\hline
""" % (table_labels[1][0], table_labels[1][1], table_labels[1][2])
        # Build table for ES impacts
        table_es = r"""\begin{tabular}{lccc}
\hline
 & %s & %s & %s \\
\hline
""" % (table_labels[1][0], table_labels[1][1], table_labels[1][2])
        
        for row_label in table_labels[0]:
            # Define keys corresponding to the row: first column is row_label,
            # second: row_label+"_PT20_40", third: row_label+"_PT40_200"
            keys = [row_label, f"{row_label}_PT20_40", f"{row_label}_PT40_200"]
            row_r_emb = row_label
            row_es = row_label
            for key in keys:
                # Build the expected keys for the impact dictionary entries.
                r_key  = f"r_EMB_{key}"
                es_key = f"ES_{key}"
                # Extract the tuple (value, down, up) if available; otherwise substitute "N/A".
                try:
                    tup = impact_dict[era][wp][key][r_key]
                    val_r = f"{tup[0]}$^{{{tup[2]}}}_{{{tup[1]}}}$"
                except KeyError:
                    val_r = "N/A"
                    # breakpoint()
                try:
                    tup = impact_dict[era][wp][key][es_key]
                    val_es = f"{tup[0]}$^{{{tup[2]}}}_{{{tup[1]}}}$"
                except KeyError:
                    val_es = "N/A"
                row_r_emb += " & " + val_r
                row_es    += " & " + val_es
            table_r_emb += row_r_emb + r" \\[0.5ex]" + "\n"
            table_es    += row_es    + r" \\[0.5ex]" + "\n"
        table_r_emb += r"\hline" + "\n" + r"\end{tabular}"
        table_es    += r"\hline" + "\n" + r"\end{tabular}"
        
        # Corelation table:
        corr_data = corr_yaml.get(era, {}).get(wp_short, {})
        table_corr = r"""\begin{tabular}{lc}
\hline
DM & Correlation \\
\hline
"""
        for dm_label in table_labels[0]:
            # Convert e.g. "DM0" to "DM_0"
            dm_trans = dm_label.replace("DM", "DM_")
            corr_key = f"ES_{dm_label}-EMB_{dm_trans}"
            dm_corr = corr_data.get(dm_label, {})
            corr_val_raw = dm_corr.get(corr_key, "N/A")
            if corr_val_raw != "N/A":
                corr_val = f"{round(corr_val_raw, 2)}"
            else:
                corr_val = "N/A"
            table_corr += f"{dm_label} & {corr_val} \\\\ \n"
        table_corr += r"\hline" + "\n" + r"\end{tabular}"
        
        
        
        latex_table = rf"""
\begin{{frame}}{{Fits {era} {wp} WP}}
    \begin{{columns}}
        \column{{0.5\textwidth}}
            \centering
            \textbf{{ID fits}}\\[5mm]
            {table_r_emb}
        \column{{0.5\textwidth}}
            \centering
            \textbf{{ES fits}}\\[5mm]
            {table_es}
    \end{{columns}}
    \vspace{{7mm}}
    \centering
    \textbf{{Correlations (ID-ES)}}\\[5mm]
    {table_corr}
\end{{frame}}
"""
        table_code += latex_table

with open("latex_tables.tex", "w") as f:
    f.write(table_code)