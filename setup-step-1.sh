#!/bin/bash
# Installs all necessary tools, including micromamba.

# INSTALL Tools
echo "Installing tools"
sudo apt-get update
sudo apt install curl
sudo apt install make
sudo apt install build-essential
sudo apt install libpng-dev
sudo apt install r-base

# INSTALL Micromamba
echo "Installing Micromamba"
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
echo "Restarting shell"
exec bash
