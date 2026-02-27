# RAiSD-AI Graphical User Interface

## Installation instructions

This section contains instructions for creating a Conda environment with PySide6 and the Qt Widgets Designer installed.

### Linux

```bash
conda env create -f environment-raisd-ai-gui.yml
conda activate raisd-ai-gui
```


## Usage instructions

This section contains instructions for running the GUI, as well as development tools.

### Linux

To run the GUI:

```bash
python -m gui.app
```

To run the Qt Widgets Designer:

```bash
designer6
```

To convert saved `.ui` files to `.py` files:

```bash
uic -g python gui/ui/filename.ui -o gui/ui/filename.py
```
