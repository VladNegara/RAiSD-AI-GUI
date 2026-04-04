from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
)

from ..page import Page
from gui.model.settings import app_settings
from gui.widgets import (
    HBoxLayout,
    VBoxLayout,
)
from gui.style import constants


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
        layout = VBoxLayout(
            self,
            left=constants.GAP_DEFAULT,
            top=constants.GAP_DEFAULT,
            right=constants.GAP_DEFAULT,
            bottom=constants.GAP_DEFAULT,
            spacing=constants.GAP_DEFAULT,
        )

        title_label = QLabel("Settings")
        title_label.setProperty("title", "true")
        layout.addWidget(title_label)

        container_widget = QWidget()
        container_widget.setObjectName("container_widget")
        container_layout = VBoxLayout(
            container_widget,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_DEFAULT,
            spacing=constants.GAP_SMALL,
        )

        # Widget to hold the workspace label and workspace choice button
        workspace_widget = QWidget()
        workspace_widget.setObjectName("workspace_widget")
        workspace_layout = HBoxLayout(workspace_widget)

        # Label to show the workspace folderpath
        self.workspace_label = QLabel()
        self._set_workspace_label()
        app_settings.workspace_path_changed.connect(self._set_workspace_label)
        workspace_layout.addWidget(self.workspace_label, 1)

        # Button to select a new workspace
        self.workspace_chooser = QPushButton("Set Workspace")
        self.workspace_chooser.clicked.connect(app_settings.set_workspace_folder)
        workspace_layout.addWidget(self.workspace_chooser)

        container_layout.addWidget(workspace_widget)

        # Label to show the executable file path
        self.executable_label = QLabel()
        self._set_executable_label()
        app_settings.executable_file_path_changed.connect(self._set_executable_label)
        container_layout.addWidget(self.executable_label)

        # Label to show the environment manager
        self.environment_manager_label = QLabel()
        self._set_environment_manager_label()
        app_settings.environment_manager_changed.connect(self._set_environment_manager_label)
        container_layout.addWidget(self.environment_manager_label)

        # Label to show the environment name
        self.environment_name_label = QLabel()
        self._set_environment_name_label()
        app_settings.environment_name_changed.connect(self._set_environment_name_label)
        container_layout.addWidget(self.environment_name_label)

        layout.addWidget(container_widget)
        layout.addStretch()

    def _set_workspace_label(self) -> None:
        """Set the workspace label with the workspace folder path."""
        self.workspace_label.setText(f"Current Workspace: '{app_settings.workspace_path.absolutePath()}'")

    def _set_executable_label(self) -> None:
        """Set the executable label with the executable file path."""
        self.executable_label.setText(f"Current Executable: '{app_settings.executable_file_path.absoluteFilePath()}'")

    def _set_environment_manager_label(self) -> None:
        """Set the environment manager label with the environment manager value."""
        self.environment_manager_label.setText(f"Current Environment Manager: '{app_settings.environment_manager.value}'")

    def _set_environment_name_label(self) -> None:
        """Set the environment name label with the environment name."""
        self.environment_name_label.setText(f"Current Environment Name: '{app_settings.environment_name}'")
