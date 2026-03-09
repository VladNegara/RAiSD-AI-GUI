#!/bin/bash
# Creates the environments and builds RAiSD-AI.

# CREATE environments
echo "CREATE raisd-ai environment"
micromamba env create -f environment-raisd-ai.yml --channel-priority flexible
echo "CREATE raisd-ai environment"
micromamba env create -f environment-raisd-ai-gui.yml --channel-priority flexible

# COMPILE RAiSD-AI
echo "Compiling RAiSD-AI"
./compile-RAiSD-AI.sh

