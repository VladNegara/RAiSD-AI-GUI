#!/bin/bash
# Installs all necessary tools, including micromamba, creates the environments and builds RAiSD-AI.

# INSTALL Tools
sudo apt install curl
sudo apt install make
sudo apt install build-essential
sudo apt install libpng-dev
sudo apt install r-base

# INSTALL Micromamba and create environments
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
eval "$($HOME/RAiSD-AI-GUI/y/micromamba shell hook --shell bash)"
micromamba env create -f environment-raisd-ai.yml --channel-priority flexible
micromamba env create -f environment-raisd-ai-gui.yml --channel-priority flexible

# BUILD RAiSD-AI
micromamba activate raisd-ai
./compile-RAiSD-AI.sh
