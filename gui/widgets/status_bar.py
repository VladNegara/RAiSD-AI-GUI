from PySide6.QtCore import (
    Signal,
    QDir,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QScrollArea,
    QPushButton,
    QLabel,
    QStatusBar,
)

from gui.model.settings import app_settings

class StatusBar(QStatusBar):
    workspace_path_changed = Signal(QDir)

    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet("background-color: lightgray;")

        self.workspace_label = QLabel()
        self.workspace_path_changed.connect(self.update_workspace_label)
        self.update_workspace_label(app_settings.workspace_path)

        self.addWidget(self.workspace_label)

    def update_workspace_label(self, new_workspace: QDir) -> None:
        self.workspace_label.setText(f"Current Workspace: '{new_workspace.absolutePath()}'")