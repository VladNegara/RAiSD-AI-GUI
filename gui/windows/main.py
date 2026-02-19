from PySide6.QtWidgets import QMainWindow, QWidget

from ui.uiMainWindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # connect standard signals (buttons)
        self.ui.buttonBox.accepted.connect(self.click)

        # take parameter config files
        # add parameter buttons
        # connect buttons

    def click(arg):
        print("smth clicked")
