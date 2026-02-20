import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from model.ParameterGroupSet import ParameterGroupSet
from windows.main import MainWindow

def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("windowsvista"))

    parameter_group_set = ParameterGroupSet("gui/...") # TODO: implement config file and write path

    window = MainWindow(parameter_group_set=parameter_group_set)  
    window.show()
    app.exec()
    print("App closed")

if __name__ == "__main__":
    main()