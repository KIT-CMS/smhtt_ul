#!/bin/bash

ERA=$1

if [[ "$ERA" =~ "2016" ]]
then
    export GGH_POWHEG_SPLIT1="gghpowheg60,gghpowheg80,gghpowheg100,gghpowheg120,gghpowheg125,gghpowheg130,gghpowheg140,gghpowheg160,gghpowheg180,gghpowheg200,gghpowheg250"
    export GGH_POWHEG_SPLIT2="gghpowheg300,gghpowheg350,gghpowheg400,gghpowheg450,gghpowheg500,gghpowheg600,gghpowheg700,gghpowheg800,gghpowheg900,gghpowheg1000"
    export GGH_POWHEG_SPLIT3="gghpowheg1200,gghpowheg1400,gghpowheg1600,gghpowheg1800,gghpowheg2000,gghpowheg2300,gghpowheg2600,gghpowheg2900,gghpowheg3200,gghpowheg3500"
    export GGH_SAMPLES_SPLIT1="ggh80,ggh90,ggh100,ggh110,ggh120,ggh130,ggh140,ggh160,ggh180,ggh200"
    export GGH_SAMPLES_SPLIT2="ggh250,ggh300,ggh350,ggh400,ggh450,ggh500,ggh600,ggh700,ggh800,ggh900,ggh1000"
    export GGH_SAMPLES_SPLIT3="ggh1200,ggh1400,ggh1500,ggh1600,ggh1800,ggh2000,ggh2300,ggh2600,ggh2900,ggh3200"
    # Define split of amcatnlo bbh samples.
    export BBH_SAMPLES_SPLIT1="bbh80,bbh90,bbh110,bbh120,bbh130,bbh140,bbh160,bbh180,bbh200,bbh250,bbh350,bbh400,bbh450,bbh500"
    export BBH_SAMPLES_SPLIT2="bbh600,bbh700,bbh800,bbh900,bbh1000,bbh1200,bbh1400,bbh1600,bbh1800,bbh2000,bbh2300,bbh2600,bbh2900,bbh3200"
    # export BBH_POWHEG_SPLIT1="bbhpowheg60,bbhpowheg80,bbhpowheg100,bbhpowheg120,bbhpowheg125,bbhpowheg130,bbhpowheg140,bbhpowheg160,bbhpowheg180,bbhpowheg200,bbhpowheg250,bbhpowheg300,bbhpowheg350,bbhpowheg400,bbhpowheg450"
    # export BBH_POWHEG_SPLIT2="bbhpowheg500,bbhpowheg600,bbhpowheg700,bbhpowheg800,bbhpowheg900,bbhpowheg1000,bbhpowheg1200,bbhpowheg1400,bbhpowheg1600,bbhpowheg1800,bbhpowheg2000,bbhpowheg2300,bbhpowheg2600,bbhpowheg2900,bbhpowheg3200,bbhpowheg3500"
    export BBH_POWHEG_SPLIT1="bbhpowheg60,bbhpowheg80,bbhpowheg100,bbhpowheg120,bbhpowheg125,bbhpowheg130,bbhpowheg140,bbhpowheg160,bbhpowheg180,bbhpowheg200,bbhpowheg250,bbhpowheg350,bbhpowheg400,bbhpowheg450"  # 300 removed
    export BBH_POWHEG_SPLIT2="bbhpowheg500,bbhpowheg600,bbhpowheg800,bbhpowheg900,bbhpowheg1200,bbhpowheg1400,bbhpowheg1600,bbhpowheg1800,bbhpowheg2000,bbhpowheg2300,bbhpowheg2600,bbhpowheg2900,bbhpowheg3200,bbhpowheg3500"  # 700 and 1000 removed
elif [[ "$ERA" =~ "2017" ]]
then
    export GGH_POWHEG_SPLIT1="gghpowheg60,gghpowheg80,gghpowheg100,gghpowheg120,gghpowheg125,gghpowheg130,gghpowheg140,gghpowheg160,gghpowheg180,gghpowheg200,gghpowheg250"
    export GGH_POWHEG_SPLIT2="gghpowheg300,gghpowheg350,gghpowheg400,gghpowheg450,gghpowheg500,gghpowheg600,gghpowheg700,gghpowheg800,gghpowheg900,gghpowheg1000"
    export GGH_POWHEG_SPLIT3="gghpowheg1200,gghpowheg1400,gghpowheg1600,gghpowheg1800,gghpowheg2000,gghpowheg2300,gghpowheg2600,gghpowheg2900,gghpowheg3200,gghpowheg3500"
    export GGH_SAMPLES_SPLIT1="ggh80,ggh90,ggh100,ggh110,ggh120,ggh130,ggh140,ggh180,ggh200,ggh250"
    export GGH_SAMPLES_SPLIT2="ggh300,ggh350,ggh400,ggh450,ggh600,ggh700,ggh800,ggh900,ggh1200"
    export GGH_SAMPLES_SPLIT3="ggh1400,ggh1500,ggh1600,ggh1800,ggh2000,ggh2300,ggh2600,ggh2900,ggh3200"
    # Define split of amcatnlo bbh samples.
    export BBH_SAMPLES_SPLIT1="bbh600,bbh700,bbh800,bbh900,bbh1000,bbh1200,bbh1400,bbh1600,bbh1800,bbh2000,bbh2300,bbh2600,bbh2900,bbh3200"
    export BBH_SAMPLES_SPLIT2="bbh80,bbh90,bbh110,bbh120,bbh125,bbh130,bbh140,bbh160,bbh180,bbh200,bbh250,bbh300,bbh350,bbh400,bbh450,bbh500"
    export BBH_POWHEG_SPLIT1="bbhpowheg60,bbhpowheg80,bbhpowheg100,bbhpowheg120,bbhpowheg125,bbhpowheg130,bbhpowheg140,bbhpowheg160,bbhpowheg180,bbhpowheg200,bbhpowheg250,bbhpowheg300,bbhpowheg350,bbhpowheg400,bbhpowheg450"
    export BBH_POWHEG_SPLIT2="bbhpowheg500,bbhpowheg600,bbhpowheg700,bbhpowheg800,bbhpowheg900,bbhpowheg1000,bbhpowheg1200,bbhpowheg1400,bbhpowheg1600,bbhpowheg1800,bbhpowheg2000,bbhpowheg2300,bbhpowheg2600,bbhpowheg2900,bbhpowheg3200,bbhpowheg3500"
elif [[ "$ERA" =~ "2018" ]]
then
    export GGH_POWHEG_SPLIT1="gghpowheg60,gghpowheg80,gghpowheg100,gghpowheg120,gghpowheg125,gghpowheg130,gghpowheg140,gghpowheg160,gghpowheg180,gghpowheg200,gghpowheg250"
    export GGH_POWHEG_SPLIT2="gghpowheg300,gghpowheg350,gghpowheg400,gghpowheg450,gghpowheg500,gghpowheg600,gghpowheg700,gghpowheg800,gghpowheg900,gghpowheg1000"
    export GGH_POWHEG_SPLIT3="gghpowheg1200,gghpowheg1400,gghpowheg1600,gghpowheg1800,gghpowheg2000,gghpowheg2300,gghpowheg2600,gghpowheg2900,gghpowheg3200,gghpowheg3500"
    export GGH_SAMPLES_SPLIT1="ggh80,ggh90,ggh100,ggh110,ggh120,ggh130,ggh140,ggh160,ggh180,ggh200"
    export GGH_SAMPLES_SPLIT2="ggh250,ggh300,ggh350,ggh400,ggh450,ggh600,ggh700,ggh800,ggh900,ggh1200"
    export GGH_SAMPLES_SPLIT3="ggh1400,ggh1500,ggh1600,ggh1800,ggh2000,ggh2300,ggh2600,ggh2900,ggh3200"
    # Define split of amcatnlo bbh samples.
    export BBH_SAMPLES_SPLIT1="bbh80,bbh90,bbh100,bbh110,bbh120,bbh125,bbh130,bbh140,bbh160,bbh180,bbh200,bbh250,bbh300,bbh350,bbh400,bbh450,bbh500"
    export BBH_SAMPLES_SPLIT2="bbh600,bbh700,bbh800,bbh900,bbh1000,bbh1200,bbh1400,bbh1600,bbh1800,bbh2000,bbh2300,bbh2600,bbh2900,bbh3200,bbh3500"
    export BBH_POWHEG_SPLIT1="bbhpowheg60,bbhpowheg80,bbhpowheg100,bbhpowheg120,bbhpowheg125,bbhpowheg130,bbhpowheg140,bbhpowheg160,bbhpowheg180,bbhpowheg200,bbhpowheg250,bbhpowheg300,bbhpowheg350,bbhpowheg400,bbhpowheg450"
    export BBH_POWHEG_SPLIT2="bbhpowheg500,bbhpowheg600,bbhpowheg700,bbhpowheg800,bbhpowheg900,bbhpowheg1000,bbhpowheg1200,bbhpowheg1400,bbhpowheg1600,bbhpowheg1800,bbhpowheg2000,bbhpowheg2300,bbhpowheg2600,bbhpowheg2900,bbhpowheg3200,bbhpowheg3500"
fi
