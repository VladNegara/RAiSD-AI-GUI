from PySide6.QtCore import (
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

from gui.model.settings import app_settings


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
            lambda p : workspace_widget._update_label(p.absolutePath()))
        workspace_widget.button_clicked.connect(app_settings.set_workspace_folder)
        container_layout.addWidget(workspace_widget)

        # Executable
        executable_widget = SettingsItemWidget("Executable", app_settings.executable_file_path.absoluteFilePath())
        app_settings.executable_file_path_changed.connect(
            lambda p : executable_widget._update_label(p.absoluteFilePath()))
        executable_widget.button_clicked.connect(app_settings.set_executable_path)
        container_layout.addWidget(executable_widget)

        # Environment manager
        environment_manager_widget = SettingsItemWidget("Environment manager", app_settings.environment_manager_name)
        app_settings.environment_manager_changed.connect(
            lambda _ : environment_manager_widget._update_label(app_settings.environment_manager_name))
        environment_manager_widget.button_clicked.connect(app_settings.set_environment_manager)
        container_layout.addWidget(environment_manager_widget)

        # Environment name
        environment_name_widget = SettingsItemWidget("Environment name", app_settings.environment_name)
        app_settings.environment_name_changed.connect(
            lambda _ : environment_name_widget._update_label(app_settings.environment_name)
        )
        environment_name_widget.button_clicked.connect(app_settings.set_environment_name)
        container_layout.addWidget(environment_name_widget)

        # Config file
        config_widget = SettingsItemWidget("Config file", app_settings.config_path.absoluteFilePath())
        config_widget.button_clicked.connect(app_settings.set_config_path)
        container_layout.addWidget(config_widget)

        layout.addSpacing(40)
        layout.addWidget(container_widget)
        layout.addStretch()

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
    """
    A widget for a single setting. 
    Includes a name, current value and button to set it.
    """

    button_clicked = Signal()

    def __init__(self, name: str, value: str):
        """
        Initialize the widget for a single setting.
        """
        super().__init__()
        self._name = name
        self._value = value
        self.setObjectName("workspace_widget")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Label to show the workspace folderpath
        self.label = QLabel(self)
        self._update_label(self._value)
        layout.addWidget(self.label, 1)

        # Button to select a new workspace
        self.chooser = QPushButton(f"Set {self._name}")
        self.chooser.clicked.connect(self.button_clicked)
        layout.addWidget(self.chooser)

        layout.addSpacing(10)   
        
    def _update_label(self, value: str) -> None:
        """
        Update the label of a setting when the current value changes. 
        """
        self._value = value
        self.label.setText(f"Current {self._name}: '{self._value}'")