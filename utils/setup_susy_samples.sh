#!/bin/bash

ERA=$1

if [[ "$ERA" =~ "2016" ]]
then
    export GGH_SAMPLES_SPLIT1="ggh80,ggh90,ggh100,ggh110,ggh120,ggh130"
    export GGH_SAMPLES_SPLIT2="ggh140,ggh160,ggh180,ggh200,ggh250,ggh300,ggh350"
    export GGH_SAMPLES_SPLIT3="ggh400,ggh450,ggh500,ggh600,ggh700,ggh800"
    export GGH_SAMPLES_SPLIT4="ggh900,ggh1000,ggh1200,ggh1400,ggh1500,ggh1600"
    export GGH_SAMPLES_SPLIT5="ggh1800,ggh2000,ggh2300,ggh2600,ggh2900,ggh3200"
    export BBH_SAMPLES="bbh80,bbh90,bbh100,bbh110,bbh120,bbh130,bbh140,bbh160,bbh180,bbh200,bbh250,bbh300,bbh350,bbh400,bbh450,bbh500,bbh600,bbh700,bbh800,bbh900,bbh1000,bbh1200,bbh1400,bbh1500,bbh1600,bbh1800,bbh2000,bbh2300,bbh2600,bbh2900,bbh3200"
    export BBH_NLO_SAMPLES_SPLIT1="bbh80_nlo,bbh90_nlo,bbh110_nlo,bbh120_nlo,bbh130_nlo,bbh140_nlo,bbh160_nlo,bbh180_nlo,bbh200_nlo,bbh250_nlo,bbh350_nlo,bbh400_nlo,bbh450_nlo,bbh500_nlo"
    export BBH_NLO_SAMPLES_SPLIT2="bbh600_nlo,bbh700_nlo,bbh800_nlo,bbh900_nlo,bbh1000_nlo,bbh1200_nlo,bbh1400_nlo,bbh1600_nlo,bbh1800_nlo,bbh2000_nlo,bbh2300_nlo,bbh2600_nlo,bbh2900_nlo,bbh3200_nlo"
elif [[ "$ERA" =~ "2017" ]]
then
    export GGH_SAMPLES_SPLIT1="ggh80,ggh90,ggh100,ggh110,ggh120,ggh130"
    export GGH_SAMPLES_SPLIT2="ggh140,ggh180,ggh200,ggh250,ggh300,ggh350"
    export GGH_SAMPLES_SPLIT3="ggh400,ggh450,ggh600,ggh700,ggh800"
    export GGH_SAMPLES_SPLIT4="ggh900,ggh1200,ggh1400,ggh1500,ggh1600"
    export GGH_SAMPLES_SPLIT5="ggh1800,ggh2000,ggh2300,ggh2600,ggh2900,ggh3200"
    export BBH_SAMPLES="bbh80,bbh90,bbh100,bbh110,bbh120,bbh130,bbh140,bbh160,bbh180,bbh200,bbh250,bbh300,bbh350,bbh400,bbh600,bbh700,bbh800,bbh900,bbh1200,bbh1400,bbh1500,bbh1600,bbh1800,bbh2000,bbh2300,bbh2600,bbh2900,bbh3200"
    export BBH_NLO_SAMPLES_SPLIT1="bbh600_nlo,bbh700_nlo,bbh800_nlo,bbh900_nlo,bbh1000_nlo,bbh1200_nlo,bbh1400_nlo,bbh1600_nlo,bbh1800_nlo,bbh2000_nlo,bbh2300_nlo,bbh2600_nlo,bbh2900_nlo,bbh3200_nlo"
    export BBH_NLO_SAMPLES_SPLIT2="bbh80_nlo,bbh90_nlo,bbh110_nlo,bbh120_nlo,bbh125_nlo,bbh130_nlo,bbh140_nlo,bbh160_nlo,bbh180_nlo,bbh200_nlo,bbh250_nlo,bbh300_nlo,bbh350_nlo,bbh400_nlo,bbh450_nlo,bbh500_nlo"
elif [[ "$ERA" =~ "2018" ]]
then
    export GGH_SAMPLES_SPLIT1="ggh80,ggh90,ggh100,ggh110,ggh120,ggh130"
    export GGH_SAMPLES_SPLIT2="ggh140,ggh160,ggh180,ggh200,ggh250,ggh300,ggh350"
    export GGH_SAMPLES_SPLIT3="ggh400,ggh450,ggh600,ggh700,ggh800"
    export GGH_SAMPLES_SPLIT4="ggh900,ggh1200,ggh1400,ggh1500,ggh1600"
    export GGH_SAMPLES_SPLIT5="ggh1800,ggh2000,ggh2300,ggh2600,ggh2900,ggh3200"
    export BBH_SAMPLES="bbh80,bbh90,bbh100,bbh110,bbh120,bbh130,bbh140,bbh160,bbh180,bbh200,bbh250,bbh300,bbh350,bbh400,bbh450,bbh600,bbh700,bbh800,bbh900,bbh1200,bbh1400,bbh1500,bbh1600,bbh1800,bbh2000,bbh2300,bbh2600,bbh2900,bbh3200"
    export BBH_NLO_SAMPLES_SPLIT1="bbh80_nlo,bbh90_nlo,bbh100_nlo,bbh110_nlo,bbh120_nlo,bbh125_nlo,bbh130_nlo,bbh140_nlo,bbh160_nlo,bbh180_nlo,bbh200_nlo,bbh250_nlo,bbh300_nlo,bbh350_nlo,bbh400_nlo,bbh450_nlo,bbh500_nlo"
    export BBH_NLO_SAMPLES_SPLIT2="bbh600_nlo,bbh700_nlo,bbh800_nlo,bbh900_nlo,bbh1000_nlo,bbh1200_nlo,bbh1400_nlo,bbh1600_nlo,bbh1800_nlo,bbh2000_nlo,bbh2300_nlo,bbh2600_nlo,bbh2900_nlo,bbh3200_nlo,bbh3500_nlo"
fi
