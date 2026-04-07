#!/bin/bash

PACKAGE_MANAGER="conda" # Default package manager

while getopts "hm" opt; do
    case $opt in
        h)
        echo "Usage: $0 [-h] [-m]"
        echo "  -h  Show this help message and exit"
        echo "  -m  Use micromamba instead of conda as the package manager"
        exit 0
        ;;
        m)
        # Package manager set
        PACKAGE_MANAGER="micromamba"
        ;;
    esac
done

if [ "$PACKAGE_MANAGER" == "conda" ]; then
    source $(conda info --base)/bin/activate "raisd-ai-gui"
    conda activate raisd-ai-gui
else
    eval "$(micromamba shell hook --shell bash)"
    micromamba activate raisd-ai-gui
fi

python -m gui.app