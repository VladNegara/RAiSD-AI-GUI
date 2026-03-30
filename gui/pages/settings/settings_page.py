from PySide6.QtCore import (
    QFileInfo,
    QDir,
)
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton, QStyleOption, QStyle,
)

from ..page import Page
from gui.model.settings import EnvironmentManager, app_settings


class SettingsPage(Page):
    """
    The settings page of the RAiSD-AI GUI application.
    """
    def __init__(self):
        """
        Initialize the `SettingsPage`.
        """
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("settings_widget")
        layout = QVBoxLayout(self)
        settings_label = QLabel("Settings")
        settings_label.setObjectName("settings_label")
        layout.addWidget(settings_label)

        container_widget = QWidget()
        container_widget.setObjectName("container_widget")
        container_layout = QVBoxLayout(container_widget)

        # Widget to hold the workspace label and workspace choice button
        workspace_widget = QWidget()
        workspace_widget.setObjectName("workspace_widget")
        workspace_layout = QHBoxLayout(workspace_widget)
        workspace_layout.setContentsMargins(0,0,0,0)
        workspace_layout.setSpacing(0)

        # Label to show the workspace folderpath
        self.workspace_label = QLabel()
        self._update_workspace_label(app_settings.workspace_path)
        app_settings.workspace_path_changed.connect(self._update_workspace_label)
        workspace_layout.addWidget(self.workspace_label, 1)

        # Button to select a new workspace
        self.workspace_chooser = QPushButton("Set Workspace")
        self.workspace_chooser.clicked.connect(app_settings.set_workspace_folder)
        workspace_layout.addWidget(self.workspace_chooser)

        container_layout.addWidget(workspace_widget)
        container_layout.addSpacing(10)

        # Label to show the executable file path
        self.executable_label = QLabel()
        self._update_executable_label(app_settings.executable_file_path)
        app_settings.executable_file_path_changed.connect(self._update_executable_label)
        container_layout.addWidget(self.executable_label)
        container_layout.addSpacing(15)

        # Label to show the environment manager
        self.environment_manager_label = QLabel()
        self._update_environment_manager_label(app_settings.environment_manager)
        app_settings.environment_manager_changed.connect(self._update_environment_manager_label)
        container_layout.addWidget(self.environment_manager_label)
        container_layout.addSpacing(15)

        # Label to show the environment name
        self.environment_name_label = QLabel()
        self._update_environment_name_label(app_settings.environment_name)
        app_settings.environment_name_changed.connect(self._update_environment_name_label)
        container_layout.addWidget(self.environment_name_label)
        container_layout.addSpacing(15)

        layout.addSpacing(20)
        layout.addWidget(container_widget)
        layout.addStretch()

    def update_ui(self) -> None:
        """
        Update the UI elements of the page when it is shown.
        """
        pass

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

    def paintEvent(self, event) -> None:
        """
        Override paintEvent so that QSS styling (background, border,
        etc.) is applied to this plain QWidget subclass.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)