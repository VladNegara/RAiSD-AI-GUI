

# Installation Instructions

Installing pyside6 and the designer into a conda environment

## Linux

```bash
conda env create -f environment-raisd-ai-gui.yml
conda activate raisd-ai-gui
```

# Usage Instructions

## Linux

To run the GUI:

`python -m gui.app`

To run the designer:

`designer6`

To convert saved `.ui` files to `.py` python files:

`uic -g python gui/ui/filename.ui -o gui/ui/filename.py`
