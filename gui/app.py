import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from gui.model.ParameterGroupList import ParameterGroupList
from gui.windows.main import MainWindow


def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("windowsvista"))

    parameter_group_list = ParameterGroupList.from_configuration_file(
        "gui/..."
    ) # TODO: implement config file and write path

    window = MainWindow(parameter_group_list=parameter_group_list)  
    window.show()
    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
