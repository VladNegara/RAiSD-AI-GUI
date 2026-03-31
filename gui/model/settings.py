from enum import Enum
from yaml import load, Loader, dump
from typing import Literal

from PySide6.QtCore import (
    QObject, 
    QDir,
    QFileInfo,
    Signal,
)
from PySide6.QtWidgets import (
    QFileDialog,
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
    workspace_path_changed = Signal(QDir)
    executable_file_path_changed = Signal(QFileInfo)
    environment_manager_changed = Signal(EnvironmentManager)
    environment_name_changed = Signal(str)
    config_path_changed = Signal(str)
    settings_changed = Signal()

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

    @classmethod
    def from_yaml(cls, file_path: str) -> "Settings":
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
                    f"Incorrect folder path for workspace: {workspace_path} "
                    + "This workspace does not exist."
                )
        else:
            QDir().mkdir("workspace")
            workspace = QDir("workspace")
            settings_obj["workspace"] = workspace.absolutePath()

        # Executable
        if "executable" in settings_obj:
            executable_file_path = settings_obj["executable"]
            if not isinstance(executable_file_path, str):
                raise ValueError(
                    f"Incorrect type for executable path: {executable_file_path} "
                    + "Expected string."
                )
            file = QFileInfo(executable_file_path)
            if not file.exists():
                raise ValueError(
                    f"Incorrect filepath for executable: {executable_file_path} "
                    + "This file does not exist."
                )
        else:
            file = QFileInfo("RAiSD-AI")
            settings_obj["executable"] = file.absoluteFilePath()

        # Environment manager
        if "environment_manager" in settings_obj:
            environment_manager = settings_obj["environment_manager"]
            if not isinstance(environment_manager, str):
                raise ValueError(
                    f"Incorrect type for environment manager: {environment_manager} "
                    + "Expected string."
                )
            
            if environment_manager not in cls.environment_managers.__args__:
                raise ValueError(
                    f"Incorrect environment manager: {environment_manager}."
                    + f"Must be one of: {", ".join([str(x) for x in cls.environment_managers])}"
                )
        else:
            environment_manager = "micromamba"

        # Environment name
        if "environment_name" in settings_obj:
            environment_name = settings_obj["environment_name"]
            if not isinstance(environment_name, str):
                raise ValueError(
                    f"Incorrect environment name: {environment_name}"
                    + "Expected string."
                )
        else:
            environment_name = ""

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
        else:
            config_file = QFileInfo("gui/config.yaml")
            settings_obj["executable"] = config_file.absoluteFilePath()


        return cls(
            workspace, 
            file,
            environment_manager,
            environment_name,
            config_file,
            )

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
        if not self.executable_file_path:
            raise RuntimeError("Executable used before it is set.")
        return self.executable_file_path

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