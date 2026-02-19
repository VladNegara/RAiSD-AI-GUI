

# Installation Instructions

Installing pyside6 and the designer into a virtual environment.

`cd gui`

`python -m venv venv`

`.\venv\Scripts\activate`

`pip install -r requirements.txt`

# Usage Instructions

To run the designer:

`pyside6-designer`

To convert saved `.ui` files:

`pyside6-uic "ui/filename.ui" -o "ui/filename.py"`
