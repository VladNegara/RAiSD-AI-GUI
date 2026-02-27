

# Installation Instructions

Installing pyside6 and the designer into a virtual environment. Make sure to have python3.13 or python3.14

## Windows

`python3.13 -m venv venv`

`.\venv\Scripts\activate`

`pip install -r gui/requirements.txt`

## Linux

`python3.13 -m venv venv`

`source venv/bin/activate`

`pip install -r gui/requirements.txt`

# Usage Instructions

## Windows

To run the GUI:

`python -m gui.app`

To run the designer:

`pyside6-designer`

To convert saved `.ui` files:

`pyside6-uic "ui/filename.ui" -o "ui/filename.py"`

## Linux

To run the GUI:

`python -m gui.app`

To run the designer:

`venv/lib64/python3.14/site-packages/PySide6/designer`

To convert saved `.ui` files:

`pyside6-uic "ui/filename.ui" -o "ui/filename.py"`

