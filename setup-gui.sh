#!/bin/bash

INSTALL_ALL=false
PACKAGE_MANAGER="conda" # Default package manager
RAiSD_AI_VERSION="RAiSD-AI-ZLIB" # Default version

create_environment() {
    local env_file=$1

    echo "Creating environment from: $env_file"
    $PACKAGE_MANAGER env create -f "$env_file" --channel-priority flexible
}

install_raisd_ai() {
    # check for existance of RAiSD-AI executable file
    echo "Checking for $RAiSD_AI_VERSION executable..."
    if [ ! -f "$RAiSD_AI_VERSION" ]; then
        echo "$RAiSD_AI_VERSION executable not found."
        echo "Compiling $RAiSD_AI_VERSION..."
        ./compile-$RAiSD_AI_VERSION.sh
    else
        echo "$RAiSD_AI_VERSION executable found."
        # ask for confirmation to recompile
        read -p "Do you want to recompile $RAiSD_AI_VERSION? (y/n) " answer
        if [[ "$answer" == "y" ]]; then
            echo "Recompiling $RAiSD_AI_VERSION..."
            ./compile-$RAiSD_AI_VERSION.sh
        else
            echo "Skipping compilation."
        fi
    fi

}

while getopts "hap:r" opt; do
    case $opt in
        h)
        echo "Usage: $0 [-h] [-a] [-p] [-r]"
        echo "  -h  Show this help message and exit"
        echo "  -a  Install the dependencies for both RAiSD-AI and its GUI"
        echo "  -p  Specify package manager (e.g., conda, micromamba)"
        echo "  -r  Compile RAiSD-AI instead of RAiSD-AI-ZLIB (not recommended)"
        exit 0
        ;;
        a)
        INSTALL_ALL=true
        ;;
        p)
        # Package manager set
        PACKAGE_MANAGER=$OPTARG
        ;;
        r)
        # Compile RAiSD-AI instead of RAiSD-AI-ZLIB
        RAiSD_AI_VERSION="RAiSD-AI"
        ;;
        *)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    esac
    done

if $INSTALL_ALL; then
    echo "Installing $RAiSD_AI_VERSION and its environment..."
    create_environment "environment-raisd-ai.yml"
    install_raisd_ai
fi

echo "Setting up RAiSD-AI-GUI environment..."
create_environment "environment-raisd-ai-gui.yml"


