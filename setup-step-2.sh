#!/bin/bash
# Creates the environments and builds RAiSD-AI.
micromamba env create -f environment-raisd-ai.yml --channel-priority flexible
micromamba env create -f environment-raisd-ai-gui.yml --channel-priority flexible

micromamba activate raisd-ai
./compile-RAiSD-AI.sh

