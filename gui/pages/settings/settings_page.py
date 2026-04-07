from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton, QStyleOption, QStyle,
)

from ..page import Page
from gui.model.settings import app_settings


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
        self._set_workspace_label()
        app_settings.workspace_path_changed.connect(self._set_workspace_label)
        workspace_layout.addWidget(self.workspace_label, 1)

        # Button to select a new workspace
        self.workspace_chooser = QPushButton("Set Workspace")
        self.workspace_chooser.clicked.connect(app_settings.set_workspace_folder)
        workspace_layout.addWidget(self.workspace_chooser)

        container_layout.addWidget(workspace_widget)
        container_layout.addSpacing(10)

        # Label to show the executable file path
        self.executable_label = QLabel()
        self._set_executable_label()
        app_settings.executable_file_path_changed.connect(self._set_executable_label)
        container_layout.addWidget(self.executable_label)
        container_layout.addSpacing(15)

        # Label to show the environment manager
        self.environment_manager_label = QLabel()
        self._set_environment_manager_label()
        app_settings.environment_manager_changed.connect(self._set_environment_manager_label)
        container_layout.addWidget(self.environment_manager_label)
        container_layout.addSpacing(15)

        # Label to show the environment name
        self.environment_name_label = QLabel()
        self._set_environment_name_label()
        app_settings.environment_name_changed.connect(self._set_environment_name_label)
        container_layout.addWidget(self.environment_name_label)
        container_layout.addSpacing(15)

        layout.addSpacing(20)
        layout.addWidget(container_widget)

        info_label = QLabel("Developers")
        info_label.setObjectName("settings_label")
        layout.addWidget(info_label)

        layout.addSpacing(20)

        info_container_widget = QWidget()
        info_container_widget.setObjectName("container_widget")
        info_container_layout = QVBoxLayout(info_container_widget)

        raisd_ai_label = QLabel(
            """<a href='https://www.nature.com/articles/s42003-018-0085-8'>
            RAiSD-AI</a> (Raised Accuracy in Sweep Detection using AI) is a
            command-line tool for detecting selective sweeps in genomic data
            developed by <b>Nikolaos Alachiotis</b> & <b>Pavlos Pavlidis</b>
            (<a href='https://github.com/alachins/RAiSD-AI'>GitHub</a>).
            """
        )
        raisd_ai_label.setWordWrap(True)
        raisd_ai_label.setOpenExternalLinks(True)
        info_container_layout.addWidget(raisd_ai_label)

        raisd_ai_gui_label = QLabel(
            """<a href='https://github.com/VladNegara/RAiSD-AI-GUI'>RAiSD-AI 
            GUI</a> developed by <b>Loes Baart de la Faille</b>, <b>Steef 
            Broeder</b>, <b>Taylan Kıncır</b>, <b>Alphan Mete</b>, <b>Vlad 
            Negară</b> and <b>Giulia Tălău</b>."""
        )
        raisd_ai_gui_label.setWordWrap(True)
        raisd_ai_gui_label.setOpenExternalLinks(True)
        info_container_layout.addWidget(raisd_ai_gui_label)

        # TODO: add a link to the user manual

        info_container_layout.addSpacing(15)

        layout.addWidget(info_container_widget)

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

    def paintEvent(self, event) -> None:
        """
        Override paintEvent so that QSS styling (background, border,
        etc.) is applied to this plain QWidget subclass.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)