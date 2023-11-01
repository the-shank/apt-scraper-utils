#!/bin/bash

set -eu
set -o pipefail

# [!] update this when running on another machine
HANDLERR_DIR=/home/shank/code/research/HandlERR
DETECTERR_BENCHMARKS_DIR=/home/shank/code/research/the100/data/detecterr_benchmarks
SOURCE_BASE_DIR=/home/shank/code/research/the100/data/apt_scraper_sources

COMPILATION_RESULTS_FILE=$(realpath "./results_compilation.txt")

TOOL_RESULTS_FILE="./results_runtool.txt"
truncate -s 0 $TOOL_RESULTS_FILE
TOOL_RESULTS_FILE=$(realpath $TOOL_RESULTS_FILE)

nprocessed=0
(
  cd $HANDLERR_DIR

  for pkg in $(cat $COMPILATION_RESULTS_FILE | rg ",success" | sd -s ",success" "" | sort -u); do
    echo "============================================================"
    echo ">> processing: $pkg"
    nprocessed=$((nprocessed+1)) 
    echo ">> nprocessed: $nprocessed"

    # disable errors
    set +o pipefail
    set +eu

    # check if pkg dir has a compile_commands.json file available
    ls ${SOURCE_BASE_DIR}/${pkg} | rg --quiet "compile_commands.json"
    exit_code=$?
    if [ $exit_code != 0 ]; then
      echo ">> compile_commands.json not found... skipping..."
      continue
    fi

    # clang/tools/detecterr/utils/runtool.py \
    #   -p /path/to/detecterr \
    #   -m /path/to/detecterr_benchmarks \
    #   -b /path/to/bear \
    #   -s /path/to/extracted/libsqlite

    cmd="clang/tools/detecterr/utils/runtool.py \
      -p $(pwd)/build/bin/detecterr \
      -m ${DETECTERR_BENCHMARKS_DIR} \
      -b /usr/bin/bear \
      -s ${SOURCE_BASE_DIR}/${pkg}"

    echo ">> executing: ${cmd}"
    ${cmd}

    exit_code=$?
    if [ $exit_code == 0 ]; then
      echo ">> success"
      echo "${pkg},success" >> $TOOL_RESULTS_FILE
    else
      echo ">> failed"
      echo "${pkg},failed" >> $TOOL_RESULTS_FILE
    fi

    # re-enable errors
    set -eu
    set -o pipefail

    # exit 1
  done
)
