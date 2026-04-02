from PySide6.QtCore import (
    QFileInfo,
    QDir,
    Signal
)
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton, QStyleOption, QStyle,
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
        self.setObjectName("settings_widget")
        layout = QVBoxLayout(self)
        settings_label = QLabel("Settings")
        settings_label.setObjectName("settings_label")
        layout.addWidget(settings_label)

        container_widget = QWidget()
        container_widget.setObjectName("container_widget")
        container_layout = QVBoxLayout(container_widget)

        # Workspace
        workspace_widget = SettingsItemWidget("Workspace", app_settings.workspace_path.absolutePath())
        app_settings.workspace_path_changed.connect(
            lambda p = app_settings.workspace_path.absolutePath: workspace_widget._update_label(p))
        workspace_widget.button_clicked.connect(app_settings.set_workspace_folder)
        container_layout.addWidget(workspace_widget)

        # Executable
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

    def _update_workspace_label(self, path: QDir) -> None:
        """Update the workspace label with the new workspace folder path."""
        self.workspace_label.setText(f"Current Workspace: '{path.absolutePath()}'")

    def _update_executable_label(self, path: QFileInfo) -> None:
        """Update the executable label with the new executable file path."""
        self.executable_label.setText(f"Current Executable: '{path.absoluteFilePath()}'")

    def _update_environment_manager_label(self, manager: str) -> None:
        """Update the environment manager label with the new environment manager value."""
        self.environment_manager_label.setText(f"Current Environment Manager: '{manager}'")

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

class SettingsItemWidget(QWidget):

    button_clicked = Signal()

    def __init__(self, name: str, value: str):
        super().__init__()
        self._name = name
        self._value = value
        self.setObjectName("workspace_widget")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Label to show the workspace folderpath
        self.label = QLabel()
        self._update_label(self._value)
        layout.addWidget(self.label, 1)

        # Button to select a new workspace
        self.chooser = QPushButton(f"Set {self._name}")
        self.chooser.clicked.connect(self.button_clicked)
        layout.addWidget(self.chooser)

        layout.addSpacing(10)   
        
    def _update_label(self, value: str) -> None:
        self._value = value
        self.label.setText(f"Current {self._name}: '{self._value}'")