from ntuple_processor import Histogram
from ntuple_processor.utils import Selection

m_sv_hist = Histogram("m_sv_puppi", "m_sv_puppi", [i for i in range(0, 255, 5)])
mt_tot_hist = Histogram("mt_tot_puppi", "mt_tot_puppi", [i for i in list(range(0, 50, 50)) + list(range(50, 500, 10)) + list(range(500, 1000, 25)) + list(range(1000, 2000, 50)) + list(range(2000, 5100, 100))])


lt_categorization = [
    (Selection(name="Nbtag0_MTLt40",             cuts = [("nbtag==0&&mt_1_puppi<40", "category_selection")]),
            [mt_tot_hist]),
    (Selection(name="Nbtag0_MT40To70",           cuts = [("nbtag==0&&mt_1_puppi>=40&&mt_1_puppi<70", "category_selection")]),
            [mt_tot_hist]),
    # MSSM and SM analysis categories
    (Selection(name="Nbtag0_MTLt40_MHGt250",     cuts = [("nbtag==0&&mt_1_puppi<40&&m_sv_puppi>=250", "category_selection")]),
            [mt_tot_hist]),
    (Selection(name="Nbtag0_MT40To70_MHGt250",   cuts = [("nbtag==0&&mt_1_puppi>=40&&mt_1_puppi<70&&m_sv_puppi", "category_selection")]),
            [mt_tot_hist]),
    (Selection(name="NbtagGt1_MTLt40",           cuts = [("nbtag>=1&&mt_1_puppi<40", "category_selection")]),
            [mt_tot_hist]),
    (Selection(name="NbtagGt1_MT40To70",         cuts = [("nbtag>=1&&mt_1_puppi>=40&&mt_1_puppi<70", "category_selection")]),
            [mt_tot_hist]),
    # Control region.
    (Selection(name="MTGt70",                    cuts = [("mt_1_puppi>=70", "category_selection")]),
            [mt_tot_hist]),
]

categorization = {
    "et": lt_categorization,
    "mt": lt_categorization,
    "tt": [
            # Pure MSSM analysis categories.
            (Selection(name="Nbtag0",                                    cuts=[("nbtag==0", "category_selection")]),
                    [mt_tot_hist]),
            # MSSM and SM analysis categories.
            (Selection(name="Nbtag0_MHGt250",                            cuts=[("nbtag==0&&m_sv_puppi>=250", "category_selection")]),
                    [mt_tot_hist]),
            (Selection(name="NbtagGt1",                                  cuts=[("nbtag>=1", "category_selection")]),
                    [mt_tot_hist]),
    ],
    "em": [
            # Categorization targetting standard model processes.
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
    ],
}
