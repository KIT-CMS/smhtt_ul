#!/bin/bash

STATUS='\033[0;33m' # Use brown color for status messages
ERROR='\033[0;31m'
NC='\033[0m' # No color

function logandrun () {
    COMMAND=${@:1}
    echo -e "${STATUS}[START]${NC} - $(date +%F\ %k:%M:%S) - ${COMMAND}"
    eval $COMMAND
    if [[ $? != 0 ]]
    then
        echo -e "${ERROR}[FAILED]${NC} - $(date +%F\ %k:%M:%S) - ${COMMAND}"
    else
        echo -e "${STATUS}[END]${NC} - $(date +%F\ %k:%M:%S) - ${COMMAND}"
    fi
}

function sort_string () {
    IFS="," read -a TEMP_ARR <<< $1
    # Sort command taken from https://stackoverflow.com/questions/7442417/how-to-sort-an-array-in-bash
    IFS=$'\n' SORT_ARR=($(sort <<< "${TEMP_ARR[*]}"))
    local SORT_STRING=$SORT_ARR
    for SUBSTRING in "${SORT_ARR[@]:1}"
    do
        SORT_STRING="$SORT_STRING,$SUBSTRING"
    done
    echo $SORT_STRING
}

