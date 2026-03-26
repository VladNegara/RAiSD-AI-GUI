import sys
import sass

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

    with open("gui/style/variables.scss", "r") as f:
        variables = f.read()

    with open("gui/style/style.qss", "r") as f:
        stylesheet = f.read()

    final_stylesheet = variables + stylesheet
    final_stylesheet = sass.compile(string=final_stylesheet)

    app.setStyleSheet(final_stylesheet)


    parameter_group_list = ParameterGroupList.from_yaml("gui/config.yaml")

    run_result = RunResult(parameter_group_list, app_settings.workspace_path)
    app_settings.workspace_path_changed.connect(lambda path: setattr(run_result, 'path', path))

    window = MainWindow(run_result)
    window.resize(1200,800)
    window.show()
    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
