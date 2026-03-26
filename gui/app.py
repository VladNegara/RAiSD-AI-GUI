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
from gui.model.run_record import RunRecord
from gui.windows.main import MainWindow


def main():
    app = QApplication(sys.argv)

    with open("gui/style/variables.scss", "r") as f:
        variables = f.read()

    with open("gui/style/style.qss", "r") as f:
        stylesheet = f.read()

    final_stylesheet = variables + stylesheet
    final_stylesheet = sass.compile(string=final_stylesheet)

    app.setStyleSheet(final_stylesheet)


    run_record = RunRecord.from_yaml(app_settings.yaml_path)

    window = MainWindow(run_record)
    window.resize(1200,800)
    window.show()
    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
