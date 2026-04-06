#!/bin/bash

INSTALL_ALL=false
PACKAGE_MANAGER="conda" # Default package manager
RAiSD_AI_VERSION="RAiSD-AI-ZLIB" # Default version

export C_INCLUDE_PATH="$CONDA_PREFIX/include:$C_INCLUDE_PATH"
export LIBRARY_PATH="$CONDA_PREFIX/lib:$LIBRARY_PATH"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

create_environment() {
    local env_file=$1

    echo "Creating environment from: $env_file"
    if [ "$PACKAGE_MANAGER" == "conda" ]; then
        echo "Using conda as the package manager."
        conda env create -f "$env_file"
    else
        echo "Using micromamba as the package manager."
        micromamba create -f "$env_file" --channel-priority flexible
    fi
}

check_and_install_raisd_ai() {
    # check for existance of RAiSD-AI executable file
    echo "Checking for $RAiSD_AI_VERSION executable..."
    if [ ! -f "$RAiSD_AI_VERSION" ]; then
        echo "$RAiSD_AI_VERSION executable not found."
        echo "Compiling $RAiSD_AI_VERSION..."
        install_raisd_ai
    else
        echo "$RAiSD_AI_VERSION executable found."
        # ask for confirmation to recompile
        read -p "Do you want to recompile $RAiSD_AI_VERSION? (y/n) " answer
        if [[ "$answer" == "y" ]]; then
            echo "Recompiling $RAiSD_AI_VERSION..."
            install_raisd_ai
        else
            echo "Skipping compilation."
        fi
    fi
}

install_raisd_ai() {
    if [ $PACKAGE_MANAGER == "conda" ]; then
        source $(conda info --base)/bin/activate "raisd-ai"
        ./compile-$RAiSD_AI_VERSION.sh
    else
        eval "$(micromamba shell hook --shell bash)"
        micromamba activate raisd-ai
        ./compile-$RAiSD_AI_VERSION.sh
    fi
}

while getopts "hamr" opt; do
    case $opt in
        h)
        echo "Usage: $0 [-h] [-a] [-m] [-r]"
        echo "  -h  Show this help message and exit"
        echo "  -a  Install the dependencies for both RAiSD-AI and its GUI, then compile RAiSD-AI-ZLIB"
        echo "  -m  Use micromamba instead of conda as the package manager"
        echo "  -r  Compile RAiSD-AI instead of RAiSD-AI-ZLIB (not recommended)"
        exit 0
        ;;
        a)
        INSTALL_ALL=true
        ;;
        m)
        # Package manager set
        PACKAGE_MANAGER="micromamba"
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
    check_and_install_raisd_ai
fi

echo "Setting up RAiSD-AI-GUI environment..."
create_environment "environment-raisd-ai-gui.yml"


