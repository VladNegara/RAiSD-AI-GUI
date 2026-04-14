from PySide6.QtWidgets import (
    QWidget,
    QLabel,
)

from ..page import Page
from gui.model.settings import app_settings
from gui.components.settings.settings_item_widget import SettingsItemWidget
from gui.components import (
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
            left=constants.GAP_MEDIUM,
            top=constants.GAP_MEDIUM,
            right=constants.GAP_MEDIUM,
            bottom=constants.GAP_MEDIUM,
            spacing=constants.GAP_MEDIUM,
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
            bottom=constants.GAP_MEDIUM,
            spacing=constants.GAP_SMALL,
        )

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
        config_widget = SettingsItemWidget("Config file", app_settings.config_path.absoluteFilePath(), button=False)
        container_layout.addWidget(config_widget)

        layout.addWidget(container_widget)

        info_label = QLabel("Developers")
        info_label.setProperty("title", "true")
        layout.addWidget(info_label)

        info_container_widget = QWidget()
        info_container_widget.setObjectName("container_widget")
        info_container_layout = VBoxLayout(
            info_container_widget,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_MEDIUM,
            spacing=constants.GAP_SMALL,
        )

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

        layout.addWidget(info_container_widget)

        layout.addStretch()
