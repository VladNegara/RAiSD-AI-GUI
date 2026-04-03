from enum import Enum

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

    def __init__(self):
        """
        Initialize the `Settings` class.
        """
        super().__init__()

        workspace_directory = "workspace"
        QDir().mkdir(workspace_directory)

        self._workspace_path = QDir(workspace_directory)
        self._executable_file_path = QFileInfo("RAiSD-AI-ZLIB")
        self._environment_manager = EnvironmentManager.CONDA
        self._config_path = "gui/config.yaml"

    @property
    def workspace_path(self) -> QDir:
        """
        Get the current workspace path.

        :return: The current workspace path.
        :rtype: QDir
        """
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
        return self._executable_file_path

    @executable_file_path.setter
    def executable_file_path(self, value: QFileInfo) -> None:
        """
        Set the executable file path.

        :param value: The new executable file path.
        :type value: QFileInfo
        """
        if self._executable_file_path != value:
            self._executable_file_path = value
            self.executable_file_path_changed.emit(value)
            self.settings_changed.emit()

    @property
    def environment_manager(self) -> EnvironmentManager:
        """
        Get the current environment manager.

        :return: The current environment manager.
        :rtype: EnvironmentManager
        """
        return self._environment_manager

    @environment_manager.setter
    def environment_manager(self, value: EnvironmentManager) -> None:
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
    def config_path(self) -> str:
        """
        Get the current config path.

        :return: The current config path.
        :rtype: str
        """
        return self._config_path

    @config_path.setter
    def config_path(self, value: str) -> None:
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
            self._workspace_path.absolutePath(),
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