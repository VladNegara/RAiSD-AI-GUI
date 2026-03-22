import sys

from PySide6.QtCore import (
    QDir,
    QFileInfo,
)
from PySide6.QtWidgets import (
    QApplication, 
    QStyleFactory,
)

from gui.model.settings import app_settings, EnvironmentManager
from gui.model.parameter_group_list import ParameterGroupList
from gui.windows.main import MainWindow
from gui.model.run_result import RunResult


def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("windowsvista"))

    app_settings.workspace_path = QDir()
    app_settings.executable_file_path = QFileInfo(QDir().absoluteFilePath("RAiSD-AI"))
    app_settings.environment_manager = EnvironmentManager.MICROMAMBA
    app_settings.environment_name = "raisd-ai"

    # parameter_group_list = ParameterGroupList.from_yaml("gui/config.yaml")

    run_result = RunResult("gui/config.yaml")
    app_settings.workspace_path_changed.connect(lambda path: setattr(run_result, 'path', path))

    window = MainWindow(run_result)  
    window.show()
    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
