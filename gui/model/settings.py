from enum import Enum
from yaml import load, Loader, dump
from typing import Literal

from PySide6.QtCore import (
    QObject, 
    QDir,
    QFileInfo,
    Signal,
    Slot
)
from PySide6.QtWidgets import (
    QFileDialog,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QDialogButtonBox
)


class EnvironmentManager(Enum):
    """
    Class to hold the allowed environment manager values.
    """
    CONDA = "conda"
    MINICONDA = "miniconda"
    MAMBA = "mamba"
    MICROMAMBA = "micromamba"


class Settings(QObject):
    """
    Class to manage the application settings.

    Do not instantiate this class directly. 
    Use the `app_settings` singleton instance instead.
    """

    class SetupDialog(QDialog):
        """
        A dialog for displaying and setting the application settings.
        """

        def __init__(
                self, 
                parent=None, 
                ):
            super().__init__(parent)
            self.setWindowTitle("Complete setup")
            self.setModal(True)
            self.resize(400, 300)
            
            layout = QVBoxLayout(self)

            # workspace
            workspace_header = QLabel("Select workspace")
            layout.addWidget(workspace_header)

            self._file_browse = QPushButton('Browse')
            self._file_browse.clicked.connect(lambda _, i=self._file_browse: self._open_file_dialog_folder(i))
            layout.addWidget(self._file_browse)

            self.buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            self.buttonbox.setCenterButtons(True)
            layout.addWidget(self.buttonbox)

            
    
        @Slot(QPushButton)
        def _open_file_dialog_folder(self, button : QPushButton) -> None:
            """
            Helper function that opens the OS file picker. If `multiple`
            is `True`, it uses `getOpenFileNames` to allow for multiple
            file selection. Otherwise, it uses `getOpenFileName` to allow
            only a single file.
            """
            new_path = QFileDialog.getExistingDirectory(
                None,
                "Select Directory",
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            if not new_path:  # Check for empty string (canceled)
                return  
            try:
                app_settings.workspace_path = QDir(new_path)
                button.setText(new_path)
            except Exception as e:
                print(f"Error setting workspace: {e}")

    workspace_path_changed = Signal(QDir)
    executable_file_path_changed = Signal(QFileInfo)
    environment_manager_changed = Signal(EnvironmentManager)
    environment_name_changed = Signal(str)
    config_path_changed = Signal(str)
    settings_changed = Signal()

    settings_file_path = "gui/settings.yaml"
    environment_managers = Literal["micromamba", "conda"]

    def __init__(
            self,
            workspace_path: QDir | None = None,
            executable_file_path: QFileInfo | None = None,
            environment_manager: str | None = None,
            environment_name: str | None = None,
            config_path: QFileInfo | None = None,
            ):
        """
        Initialize the `Settings` class.
        """
        super().__init__()
        
        self._workspace_path = workspace_path
        self._executable_file_path = executable_file_path
        self._environment_manager = environment_manager
        self._environment_name = environment_name
        self._config_path = config_path
    
    def initialize(self) -> None:
        self.from_yaml(self.settings_file_path)
        if not self._workspace_path:
            dialog = self.SetupDialog()
            dialog.exec()

    def from_yaml(self, file_path: str) -> None:
        try: 
            with open(file_path) as f:
                settings_text = f.read() or ""
            settings_obj = load(settings_text, Loader=Loader) or {}
        except FileNotFoundError:
            settings_obj = {}

        # Workspace
        if "workspace" in settings_obj:
            workspace_path = settings_obj["workspace"]
            if not isinstance(workspace_path, str):
                raise ValueError(
                    f"Incorrect type for workspace: {workspace_path} "
                    + "Expected string."
                )
            workspace = QDir(workspace_path)
            if not workspace.exists():
                raise ValueError(
                    f"Incorrect folder path for workspace: {workspace} "
                    + "This workspace does not exist."
                )
            # Do not use setters because do not write to file
            self._workspace_path = workspace

        # Executable
        if "executable" in settings_obj:
            executable_file_path = settings_obj["executable"]
            if not isinstance(executable_file_path, str):
                raise ValueError(
                    f"Incorrect type for executable path: {executable_file_path} "
                    + "Expected string."
                )
            executable_file = QFileInfo(executable_file_path)
            if not executable_file.exists():
                raise ValueError(
                    f"Incorrect filepath for executable: {executable_file_path} "
                    + "This file does not exist."
                )
            self._executable_file_path = executable_file
        if not self._executable_file_path:
            self._executable_file_path = QFileInfo("RAiSD-AI")

        # Environment manager
        if "environment_manager" in settings_obj:
            environment_manager = settings_obj["environment_manager"]
            if not isinstance(environment_manager, str):
                raise ValueError(
                    f"Incorrect type for environment manager: {environment_manager} "
                    + "Expected string."
                )
            
            if environment_manager not in self.environment_managers.__args__:
                raise ValueError(
                    f"Incorrect environment manager: {environment_manager}."
                    + f"Must be one of: {", ".join([str(x) for x in self.environment_managers])}"
                )
            self._environment_manager = environment_manager
        if not self._environment_manager:
            self._environment_manager = "micromamba"

        # Environment name
        if "environment_name" in settings_obj:
            environment_name = settings_obj["environment_name"]
            if not isinstance(environment_name, str):
                raise ValueError(
                    f"Incorrect environment name: {environment_name}"
                    + "Expected string."
                )
            self._environment_name = environment_name
        if not self._environment_name:
            self._environment_name = "raisd-ai"

        # Config file
        if "config_file" in settings_obj:
            config = settings_obj["config_file"]
            if not isinstance(config, str):
                raise ValueError(
                    f"Incorrect type for executable path: {config} "
                    + "Expected string."
                )
            config_file = QFileInfo(config)
            if not config_file.exists():
                raise ValueError(
                    f"Incorrect filepath for executable: {config} "
                    + "This file does not exist."
                )
            self._config_path = config_file
        if not self._config_path:
            self._config_path = QFileInfo("gui/config.yaml")

        
    @property
    def workspace_path(self) -> QDir:
        """
        Get the current workspace path.

        :return: The current workspace path.
        :rtype: QDir
        """
        if not self._workspace_path:
            raise RuntimeError("Workspace path used before it is set.")
        return self._workspace_path

    @workspace_path.setter
    def workspace_path(self, value: QDir) -> None:
        """
        Set the workspace path.

        :param value: The new workspace path.
        :type value: QDir
        """
        if self._workspace_path != value:
            self._workspace_path = value
            self.workspace_path_changed.emit(value)
            self.settings_changed.emit()

    @property
    def executable_file_path(self) -> QFileInfo:
        """
        Get the current executable file path.

        :return: The current executable file path.
        :rtype: QFileInfo
        """
        if not self._executable_file_path:
            raise RuntimeError("Executable used before it is set.")
        return self._executable_file_path

    @executable_file_path.setter
    def executable_file_path(self, value: QFileInfo) -> None:
        """
        Set the executable file path.

        :param value: The new executable file path.
        :type value: QFileInfo
        """
        if self.executable_file_path != value:
            self.executable_file_path = value
            self.executable_file_path_changed.emit(value)
            self.settings_changed.emit()

    @property
    def environment_manager(self) -> str:
        """
        Get the current environment manager.

        :return: The current environment manager.
        :rtype: EnvironmentManager
        """
        if not self._environment_manager:
            raise RuntimeError("Environment manager used before it is set.")
        return self._environment_manager

    @environment_manager.setter
    def environment_manager(self, value: str) -> None:
        """
        Set the environment manager.

        :param value: The new environment manager.
        :type value: EnvironmentManager
        """
        if self._environment_manager != value:
            self._environment_manager = value
            self.environment_manager_changed.emit(value)
            self.settings_changed.emit()

    @property
    def environment_name(self) -> str:
        """
        Get the current environment name.

        :return: The current environment name.
        :rtype: str
        """
        if not self._environment_name:
            raise RuntimeError("Environment name used before it is set.")
        return self._environment_name

    @environment_name.setter
    def environment_name(self, value: str) -> None:
        """
        Set the environment name.

        :param value: The new environment name.
        :type value: str
        """
        if self._environment_name != value:
            self._environment_name = value
            self.environment_name_changed.emit(value)
            self.settings_changed.emit()

    @property
    def config_path(self) -> QFileInfo:
        """
        Get the current config path.

        :return: The current config path.
        :rtype: str
        """
        if not self._config_path:
            raise RuntimeError("Config path used before it is set.")
        return self._config_path

    @config_path.setter
    def config_path(self, value: QFileInfo) -> None:
        """
        Set the config path.

        :param value: The new config path.
        :type value: str
        """
        if self._config_path != value:
            self._config_path = value
            self.config_path_changed.emit(value)
            self.settings_changed.emit()

    def set_workspace_folder(self) -> None:
        """
        Open a file dialog to select a new workspace folder and update the workspace path.

        If the user selects a new workspace folder, 
        the workspace path is updated and the `workspace_path_changed` signal is emitted.

        If the user cancels the dialog, the workspace path remains unchanged.
        If the the selected path is invalid, the workspace path remains unchanged.
        """
        new_workspace_folder_str = QFileDialog.getExistingDirectory(
            None,
            "Select Workspace Folder",
            self.workspace_path.absolutePath(),
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        if not new_workspace_folder_str:  # Check for empty string (canceled)
            return  
        try:
            app_settings.workspace_path = QDir(new_workspace_folder_str)
        except Exception as e:
            print(f"Error setting workspace: {e}")


# create a global singleton instance
app_settings = Settings()