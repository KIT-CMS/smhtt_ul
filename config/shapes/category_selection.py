from ntuple_processor import Histogram
from ntuple_processor.utils import Selection

m_sv_hist = Histogram("m_sv_puppi", "m_sv_puppi", [i for i in range(0, 255, 5)])
mt_tot_hist = Histogram("mt_tot_puppi", "mt_tot_puppi", [i for i in list(range(0, 50, 50)) + list(range(50, 500, 10)) + list(range(500, 1000, 25)) + list(range(1000, 2000, 50)) + list(range(2000, 5100, 100))])

lt_categorization_sm = [
    # Categorization targetting standard model processes.
    (Selection(name="NJets0_MTLt40",             cuts = [("njets==0&&mt_1_puppi<40", "category_selection"),
                                                        ("mt_1_puppi<70", "signal_region_cut"),
                                                        ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
            [m_sv_hist]),
    (Selection(name="NJets0_MT40To70",           cuts = [("njets==0&&mt_1_puppi>=40&&mt_1_puppi<70", "category_selection"),
                                                        ("mt_1_puppi<70", "signal_region_cut"),
                                                        ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
            [m_sv_hist]),
    (Selection(name="NJetsGt0_DeltaRGt2p5",      cuts = [("njets>=1&&DiTauDeltaR>=2.5", "category_selection"),
                                                        ("mt_1_puppi<70", "signal_region_cut"),
                                                        ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
            [m_sv_hist]),
    (Selection(name="NJets1_PTHLt120",           cuts = [("njets==1&&DiTauDeltaR<2.5&&pt_tt_puppi<120", "category_selection"),
                                                        ("mt_1_puppi<70", "signal_region_cut"),
                                                        ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
            [m_sv_hist]),
    (Selection(name="NJets1_PTH120To200",        cuts = [("njets==1&&DiTauDeltaR<2.5&&pt_tt_puppi>=120&&pt_tt_puppi<200", "category_selection"),
                                                        ("mt_1_puppi<70", "signal_region_cut"),
                                                        ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
            [m_sv_hist]),
    (Selection(name="NJets1_PTHGt200",           cuts = [("njets==1&&DiTauDeltaR<2.5&&pt_tt_puppi>=200", "category_selection"),
                                                        ("mt_1_puppi<70", "signal_region_cut"),
                                                        ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
            [m_sv_hist]),
    (Selection(name="NJetsGt1_MJJLt350",         cuts = [("njets>=2&&DiTauDeltaR<2.5&&mjj<350", "category_selection"),
                                                        ("mt_1_puppi<70", "signal_region_cut"),
                                                        ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
            [m_sv_hist]),
    (Selection(name="NJetsGt1_MJJ350To1000",     cuts = [("njets>=2&&DiTauDeltaR<2.5&&mjj>=350&&mjj<1000", "category_selection"),
                                                        ("mt_1_puppi<70", "signal_region_cut"),
                                                        ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
            [m_sv_hist]),
    (Selection(name="NJetsGt1_MJJGt1000",        cuts = [("njets>=2&&DiTauDeltaR<2.5&&mjj>=1000", "category_selection"),
                                                        ("mt_1_puppi<70", "signal_region_cut"),
                                                        ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
            [m_sv_hist]),
]

tt_categorization_sm = [
            # Categorization targetting standard model processes.
            (Selection(name="Njets0_DeltaRLt3p2",                        cuts=[("njets==0&&DiTauDeltaR<3.2", "category_selection"),
                                                                              ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="Njets1_DeltaRLt2p5_PTHLt100",               cuts=[("njets==1&&DiTauDeltaR<2.5&&pt_tt_puppi<100", "category_selection"),
                                                                              ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="Njets1_DeltaR2p5To3p2_PTHLt100",            cuts=[("njets==1&&DiTauDeltaR>=2.5&&DiTauDeltaR<3.2&&pt_tt_puppi<100", "category_selection"),
                                                                              ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="Njets1_DeltaRLt3p2_PTHGt100",               cuts=[("njets==1&&DiTauDeltaR<3.2&&pt_tt_puppi>=100", "category_selection"),
                                                                              ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NjetsGt2_DeltaRLt2p5_MJJLt350",             cuts=[("njets>=2&&DiTauDeltaR<2.5&&mjj<350", "category_selection"),
                                                                              ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NjetsGt2_DeltaRLt2p5_MJJGt350_EtaJJLt4",    cuts=[("njets>=2&&DiTauDeltaR<2.5&&mjj>=350&&jdeta<4", "category_selection"),
                                                                              ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NjetsGt2_DeltaRLt2p5_MJJGt350_EtaJJGt4",    cuts=[("njets>=2&&DiTauDeltaR<2.5&&mjj>=350&&jdeta>=4", "category_selection"),
                                                                              ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NjetsLt2_DeltaRGt3p2_NjetsGt2_DeltaGt2p5",  cuts=[("(njets<2&&DiTauDeltaR>=3.2)||(njets>=2&&DiTauDeltaR>=2.5)", "category_selection"),
                                                                              ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
]

em_categorization_sm = [
            # Categorization targetting standard model processes.
            (Selection(name="NJets0_DZetam35Tom10_PTHLt10",  cuts=[("njets==0&&pZetaPuppiMissVis>=-35&&pZetaPuppiMissVis<-10&&pt_tt_puppi<10", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NJets0_DZetam35Tom10_PTHGt10",  cuts=[("njets==0&&pZetaPuppiMissVis>=-35&&pZetaPuppiMissVis<-10&&pt_tt_puppi>=10", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NJets0_DZetamGtm10_PTHLt10",    cuts=[("njets==0&&pZetaPuppiMissVis>=-10&&pt_tt_puppi<10", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NJets0_DZetamGtm10_PTHGt10",    cuts=[("njets==0&&pZetaPuppiMissVis>=-10&&pt_tt_puppi>=10", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NJets1_PTHLt40",                cuts=[("njets==1&&pt_tt_puppi<40", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NJets1_PTH40To120",             cuts=[("njets==1&&pt_tt_puppi>=40&&pt_tt_puppi<120", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NJets1_PTH120To200",            cuts=[("njets==1&&pt_tt_puppi>=120&&pt_tt_puppi<200", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NJets1_PTHGt200",               cuts=[("njets==1&&pt_tt_puppi>=200", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NJetsGt2_MJJLt350",             cuts=[("njets>=2&&mjj<350", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
            (Selection(name="NJetsGt2_MJJGt350",             cuts=[("njets>=2&&mjj>=350", "category_selection"),
                                                                  ("pZetaPuppiMissVis>=-35", "signal_region_cut"),
                                                                  ("nbtag==0&&m_sv_puppi<250", "mssm_veto")]),
                    [m_sv_hist]),
]

lt_categorization = [
    (Selection(name="Nbtag0_MTLt40",             cuts = [("nbtag==0&&mt_1_puppi<40", "category_selection")]),
            [mt_tot_hist]),
    (Selection(name="Nbtag0_MT40To70",           cuts = [("nbtag==0&&mt_1_puppi>=40&&mt_1_puppi<70", "category_selection")]),
            [mt_tot_hist]),
    # MSSM and SM analysis categories
    (Selection(name="Nbtag0_MTLt40_MHGt250",     cuts = [("nbtag==0&&mt_1_puppi<40&&m_sv_puppi>=250", "category_selection")]),
            [mt_tot_hist]),
    (Selection(name="Nbtag0_MT40To70_MHGt250",   cuts = [("nbtag==0&&mt_1_puppi>=40&&mt_1_puppi<70&&m_sv_puppi>=250", "category_selection")]),
            [mt_tot_hist]),
    (Selection(name="NbtagGt1_MTLt40",           cuts = [("nbtag>=1&&mt_1_puppi<40", "category_selection")]),
            [mt_tot_hist]),
    (Selection(name="NbtagGt1_MT40To70",         cuts = [("nbtag>=1&&mt_1_puppi>=40&&mt_1_puppi<70", "category_selection")]),
            [mt_tot_hist]),
    # Control region.
    (Selection(name="MTGt70",                    cuts = [("mt_1_puppi>=70", "category_selection")]),
            [mt_tot_hist]),
]

tt_categorization = [
            # Pure MSSM analysis categories.
            (Selection(name="Nbtag0",                                    cuts=[("nbtag==0", "category_selection")]),
                    [mt_tot_hist]),
            # MSSM and SM analysis categories.
            (Selection(name="Nbtag0_MHGt250",                            cuts=[("nbtag==0&&m_sv_puppi>=250", "category_selection")]),
                    [mt_tot_hist]),
            (Selection(name="NbtagGt1",                                  cuts=[("nbtag>=1", "category_selection")]),
                    [mt_tot_hist]),
]

em_categorization = [
            # Pure MSSM analysis categories.
            (Selection(name="Nbtag0_DZetam35Tom10",          cuts=[("nbtag==0&&pZetaPuppiMissVis>=-35&&pZetaPuppiMissVis<-10", "category_selection")]),
                    [mt_tot_hist]),
            (Selection(name="Nbtag0_DZetam10To30",           cuts=[("nbtag==0&&pZetaPuppiMissVis>=-10&&pZetaPuppiMissVis<30", "category_selection")]),
                    [mt_tot_hist]),
            (Selection(name="Nbtag0_DZetaGt30",              cuts=[("nbtag==0&&pZetaPuppiMissVis>=30", "category_selection")]),
                    [mt_tot_hist]),
            # MSSM and SM analysis categories.
            (Selection(name="Nbtag0_DZetam35Tom10_MHGt250",  cuts=[("nbtag==0&&pZetaPuppiMissVis>=-35&&pZetaPuppiMissVis<-10&&m_sv_puppi>=250", "category_selection")]),
                    [mt_tot_hist]),
            (Selection(name="Nbtag0_DZetam10To30_MHGt250",   cuts=[("nbtag==0&&pZetaPuppiMissVis>=-10&&pZetaPuppiMissVis<30&&m_sv_puppi>=250", "category_selection")]),
                    [mt_tot_hist]),
            (Selection(name="Nbtag0_DZetaGt30_MHGt250",      cuts=[("nbtag==0&&pZetaPuppiMissVis>=30&&m_sv_puppi>=250", "category_selection")]),
                    [mt_tot_hist]),
            (Selection(name="NbtagGt1_DZetam35Tom10",        cuts=[("nbtag>=1&&pZetaPuppiMissVis>=-35&&pZetaPuppiMissVis<-10", "category_selection")]),
                    [mt_tot_hist]),
            (Selection(name="NbtagGt1_DZetam10To30",         cuts=[("nbtag>=1&&pZetaPuppiMissVis>=-10&&pZetaPuppiMissVis<30", "category_selection")]),
                    [mt_tot_hist]),
            (Selection(name="NbtagGt1_DZetaGt30",            cuts=[("nbtag>=1&&pZetaPuppiMissVis>=30", "category_selection")]),
                    [mt_tot_hist]),
            # Control regions.
            (Selection(name="DZetaLtm35",                    cuts=[("pZetaPuppiMissVis<-35", "category_selection")]),
                    [mt_tot_hist]),
]

categorization = {
    "et": lt_categorization,
    "mt": lt_categorization,
    "tt": tt_categorization,
    "em": em_categorization,
}
