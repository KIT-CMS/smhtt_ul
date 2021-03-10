#!/bin/bash

source utils/setup_cmssw.sh

[[ ! -z $1  && ! -z $2 && ! -z $3 ]] || ( echo Invalid number of arguments; exit 1  )
ERA=$1
CHANNEL=$2
VARIABLE=$3
TAG=$4

USE_MC=$5
if [[ -z $5 ]]
then
    USE_MC=0
fi

MorphingCatVariables --base-path=output/shapes/${ERA}-${CHANNEL}-${TAG}-gof-synced_shapes/ \
		     --category=${CHANNEL}_${VARIABLE} \
		     --variable=${VARIABLE} \
	    	     --verbose=1 \
	    	     --output_folder=output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-control/ \
                     --use_mc=${USE_MC} \
	    	     --era=${ERA}
