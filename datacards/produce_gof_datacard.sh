#!/bin/bash

source utils/setup_cmssw.sh

[[ ! -z $1  && ! -z $2 && ! -z $3 ]] || ( echo Invalid number of arguments; exit 1  )
ERA=$1
CHANNEL=$2
VARIABLE=$3
TAG=$4

MorphingCatVariables --base-path=output/shapes/${ERA}-${CHANNEL}-${TAG}-gof-synced_shapes/ \
		     --category=${CHANNEL}_${VARIABLE} \
		     --variable=${VARIABLE} \
	    	     --verbose=1 \
	    	     --output_folder=output/datacards/${ERA}-${CHANNEL}-${VARIABLE}-control/ \
	    	     --era=${ERA}
