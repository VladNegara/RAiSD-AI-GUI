import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from PySide6.QtCore import QDir

from gui.model.parameter_group_list import ParameterGroupList
from gui.windows.main import MainWindow
from gui.model.run_result import RunResult


def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("windowsvista"))

    parameter_group_list = ParameterGroupList.from_yaml("gui/config.yaml")

    run_result = RunResult(parameter_group_list, QDir.currentPath())

    window = MainWindow(run_result)  
    window.show()
    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
