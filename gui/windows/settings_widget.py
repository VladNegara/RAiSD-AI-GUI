from PySide6.QtCore import (
    QFileInfo,
    QDir,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from gui.model.settings import EnvironmentManager, app_settings


class SettingsWidget(QWidget):
    """
    The settings widget of the RAiSD-AI GUI application.
    """
    def __init__(self):
        """
        Initialize the `SettingsWidget`.
        """
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: lightyellow;")
        layout = QVBoxLayout(self)
        settings_label = QLabel("Settings")
        layout.addWidget(settings_label)

        # Widget to hold the workspace label and workspace choice button
        workspace_widget = QWidget()
        workspace_layout = QHBoxLayout(workspace_widget)

        # Label to show the workspace folderpath
        self.workspace_label = QLabel()
        self._update_workspace_label(app_settings.workspace_path)
        app_settings.workspace_path_changed.connect(self._update_workspace_label)
        workspace_layout.addWidget(self.workspace_label, 1)

        # Button to select a new workspace
        self.workspace_chooser = QPushButton("Set Workspace")
        self.workspace_chooser.clicked.connect(app_settings.set_workspace_folder)
        workspace_layout.addWidget(self.workspace_chooser)

        layout.addWidget(workspace_widget)

        # Label to show the executable file path
        self.executable_label = QLabel()
        self._update_executable_label(app_settings.executable_file_path)
        app_settings.executable_file_path_changed.connect(self._update_executable_label)
        layout.addWidget(self.executable_label)

        # Label to show the environment manager
        self.environment_manager_label = QLabel()
        self._update_environment_manager_label(app_settings.environment_manager)
        app_settings.environment_manager_changed.connect(self._update_environment_manager_label)
        layout.addWidget(self.environment_manager_label)

        # Label to show the environment name
        self.environment_name_label = QLabel()
        self._update_environment_name_label(app_settings.environment_name)
        app_settings.environment_name_changed.connect(self._update_environment_name_label)
        layout.addWidget(self.environment_name_label)

    def _update_workspace_label(self, path: QDir) -> None:
        """Update the workspace label with the new workspace folder path."""
        self.workspace_label.setText(f"Current Workspace: '{path.absolutePath()}'")

    def _update_executable_label(self, path: QFileInfo) -> None:
        """Update the executable label with the new executable file path."""
        self.executable_label.setText(f"Current Executable: '{path.absoluteFilePath()}'")

    def _update_environment_manager_label(self, manager: EnvironmentManager) -> None:
        """Update the environment manager label with the new environment manager value."""
        self.environment_manager_label.setText(f"Current Environment Manager: '{manager.value}'")

    def _update_environment_name_label(self, name: str) -> None:
        """Update the enviroment name label with the new environment name."""
        self.environment_name_label.setText(f"Current Environment Name: '{name}'")