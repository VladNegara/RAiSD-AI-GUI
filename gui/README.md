# RAiSD-AI Graphical User Interface

## Installation instructions

This section contains instructions for installing all necessary packages, installing Micromamba, creating a Mamba environment with PySide6 and the Qt Widgets Designer installed, and compiling RAiSD-AI.

Run the following commands in the root directory:

### Linux

```bash
./setup-step-1.sh
./setup-step-2.sh
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
