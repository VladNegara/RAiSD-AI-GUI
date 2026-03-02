#!/bin/bash
# Installs all necessary tools, including micromamba.

# INSTALL Tools
sudo apt install curl
sudo apt install make
sudo apt install build-essential
sudo apt install libpng-dev
sudo apt install r-base

# INSTALL Micromamba
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
exec bash
