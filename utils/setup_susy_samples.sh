#!/bin/bash

ERA=$1

if [[ "$ERA" =~ "2016" ]]
then
    export GGH_SAMPLES_SPLIT1="ggh80,ggh90,ggh100,ggh110,ggh120,ggh130,ggh140,ggh160,ggh180,ggh200"
    export GGH_SAMPLES_SPLIT2="ggh250,ggh300,ggh350,ggh400,ggh450,ggh500,ggh600,ggh700,ggh800,ggh900,ggh1000"
    export GGH_SAMPLES_SPLIT3="ggh1200,ggh1400,ggh1500,ggh1600,ggh1800,ggh2000,ggh2300,ggh2600,ggh2900,ggh3200"
    # Define split of amcatnlo bbh samples.
    export BBH_SAMPLES_SPLIT1="bbh80,bbh90,bbh110,bbh120,bbh130,bbh140,bbh160,bbh180,bbh200,bbh250,bbh350,bbh400,bbh450,bbh500"
    export BBH_SAMPLES_SPLIT2="bbh600,bbh700,bbh800,bbh900,bbh1000,bbh1200,bbh1400,bbh1600,bbh1800,bbh2000,bbh2300,bbh2600,bbh2900,bbh3200"
elif [[ "$ERA" =~ "2017" ]]
then
    export GGH_SAMPLES_SPLIT1="ggh80,ggh90,ggh100,ggh110,ggh120,ggh130,ggh140,ggh180,ggh200,ggh250"
    export GGH_SAMPLES_SPLIT2="ggh300,ggh350,ggh400,ggh450,ggh600,ggh700,ggh800,ggh900,ggh1200"
    export GGH_SAMPLES_SPLIT3="ggh1400,ggh1500,ggh1600,ggh1800,ggh2000,ggh2300,ggh2600,ggh2900,ggh3200"
    # Define split of amcatnlo bbh samples.
    export BBH_SAMPLES_SPLIT1="bbh600,bbh700,bbh800,bbh900,bbh1000,bbh1200,bbh1400,bbh1600,bbh1800,bbh2000,bbh2300,bbh2600,bbh2900,bbh3200"
    export BBH_SAMPLES_SPLIT2="bbh80,bbh90,bbh110,bbh120,bbh125,bbh130,bbh140,bbh160,bbh180,bbh200,bbh250,bbh300,bbh350,bbh400,bbh450,bbh500"
elif [[ "$ERA" =~ "2018" ]]
then
    export GGH_SAMPLES_SPLIT1="ggh80,ggh90,ggh100,ggh110,ggh120,ggh130,ggh140,ggh160,ggh180,ggh200"
    export GGH_SAMPLES_SPLIT2="ggh250,ggh300,ggh350,ggh400,ggh450,ggh600,ggh700,ggh800,ggh900,ggh1200"
    export GGH_SAMPLES_SPLIT3="ggh1400,ggh1500,ggh1600,ggh1800,ggh2000,ggh2300,ggh2600,ggh2900,ggh3200"
    # Define split of amcatnlo bbh samples.
    export BBH_SAMPLES_SPLIT1="bbh80,bbh90,bbh100,bbh110,bbh120,bbh125,bbh130,bbh140,bbh160,bbh180,bbh200,bbh250,bbh300,bbh350,bbh400,bbh450,bbh500"
    export BBH_SAMPLES_SPLIT2="bbh600,bbh700,bbh800,bbh900,bbh1000,bbh1200,bbh1400,bbh1600,bbh1800,bbh2000,bbh2300,bbh2600,bbh2900,bbh3200,bbh3500"
fi
