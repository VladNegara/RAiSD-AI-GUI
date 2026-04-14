from yaml import load, Loader, dump

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
    QDialogButtonBox,
    QComboBox,
    QLineEdit
)

from gui.style import constants
from gui.components import VBoxLayout


class Settings(QObject):
    """
    Class to manage the application settings.

    Do not instantiate this class directly. 
    Use the `app_settings` singleton instance instead.
    """

    workspace_path_changed = Signal(QDir)
    executable_file_path_changed = Signal(QFileInfo)
    environment_manager_changed = Signal(int)
    environment_name_changed = Signal(str)
    config_path_changed = Signal(str)
    settings_changed = Signal()

    settings_file_path = "gui/settings.yaml"
    environment_managers = ["conda", "micromamba"]

    default_executable_file_path = QFileInfo("RAiSD-AI-ZLIB")
    default_environment_manager = 0
    default_environment_name = "raisd-ai"
    default_config_path = QFileInfo("gui/config.yaml")

    def __init__(
            self,
            workspace_path: QDir | None = None,
            executable_file_path: QFileInfo | None = None,
            environment_manager: int | None = None,
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

    def from_yaml(self, file_path: str) -> None:
        """
        Fill a settings object with values parsed from a yaml file.
        """
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
                    f"Incorrect type for workspace: '{workspace_path}', "
                    f"type: {type(workspace_path)}, "
                    "Expected string."
                )
            workspace = QDir(workspace_path)
            if workspace.exists():
            # Do not use setters because do not write to file
                self._workspace_path = workspace

        # Executable
        if "executable" in settings_obj:
            executable_file_path = settings_obj["executable"]
            if not isinstance(executable_file_path, str):
                raise ValueError(
                    f"Incorrect type for executable path: '{executable_file_path}', "
                    f"type: {type(executable_file_path)}, "
                    "Expected string."
                )
            executable_file = QFileInfo(executable_file_path)
            if not executable_file.exists():
                raise ValueError(
                    f"Incorrect filepath for executable: '{executable_file_path}', "
                    "This file does not exist."
                )
            self._executable_file_path = executable_file
        if not self._executable_file_path:
            self.executable_file_path = self.default_executable_file_path

        # Environment manager
        if "environment_manager" in settings_obj:
            environment_manager = settings_obj["environment_manager"]
            if not isinstance(environment_manager, str):
                raise ValueError(
                    f"Incorrect type for environment manager: '{environment_manager}', "
                    f"type: {type(environment_manager)}, "
                    "Expected string."
                )
            
            if environment_manager not in self.environment_managers:
                raise ValueError(
                    f"Incorrect environment manager: '{environment_manager}'."
                    "Must be one of: {", ".join([str(x) for x in self.environment_managers])}"
                )
            self._environment_manager = self.environment_managers.index(environment_manager)
        if self._environment_manager is None:
            self.environment_manager = self.default_environment_manager

        # Environment name
        if "environment_name" in settings_obj:
            environment_name = settings_obj["environment_name"]
            if not isinstance(environment_name, str):
                raise ValueError(
                    f"Incorrect type for environment name: '{environment_name}', "
                    f"type: {type(environment_name)}, "
                    "Expected string."
                )
            self._environment_name = environment_name
        if not self._environment_name:
            self.environment_name = self.default_environment_name

        # Config file
        if "config_file" in settings_obj:
            config = settings_obj["config_file"]
            if not isinstance(config, str):
                raise ValueError(
                    f"Incorrect type for config file: '{config}', "
                    f"type: {type(config)}, "
                    "Expected string."
                )
            config_file = QFileInfo(config)
            if not config_file.exists():
                raise ValueError(
                    f"Incorrect filepath for config file: '{config}', "
                    "This file does not exist."
                )
            self._config_path = config_file
        if not self._config_path:
            self.config_path = self.default_config_path

        
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
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._workspace_path = value
            settings_obj["workspace"] = value.absolutePath()
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
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
        if self._executable_file_path != value:
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._executable_file_path = value
            settings_obj["executable"] = value.absoluteFilePath()
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
            self.executable_file_path_changed.emit(value)
            self.settings_changed.emit()

    @property
    def environment_manager(self) -> int:
        """
        Get index of the current environment manager.

        :return: The current environment manager.
        :rtype: int
        """
        if self._environment_manager is None:
            raise RuntimeError("Environment manager used before it is set.")
        return self._environment_manager

    @environment_manager.setter
    def environment_manager(self, value: int) -> None:
        """
        Set index of the environment manager.

        :param value: The new environment manager.
        :type value: int
        """
        if self._environment_manager != value:
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._environment_manager = value
            settings_obj["environment_manager"] = self.environment_manager_name
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
            self.environment_manager_changed.emit(value)
            self.settings_changed.emit()

    @property
    def environment_manager_name(self) -> str:
        """
        Get the name of the current environment manager.

        :return: The current environment manager.
        :rtype: str
        """
        if self._environment_manager is None:
            raise RuntimeError("Environment manager used before it is set.")
        return self.environment_managers[self._environment_manager]

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
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._environment_name = value
            settings_obj["environment_name"] = value
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
            self.environment_name_changed.emit(value)
            self.settings_changed.emit()

    @property
    def config_path(self) -> QFileInfo:
        """
        Get the current config path.

        :return: The current config path.
        :rtype: QFileInfo
        """
        if not self._config_path:
            raise RuntimeError("Config path used before it is set.")
        return self._config_path

    @config_path.setter
    def config_path(self, value: QFileInfo) -> None:
        """
        Set the config path.

        :param value: The new config path.
        :type value: QFileInfo
        """
        if self._config_path != value:
            try:
                with open(self.settings_file_path) as f:
                    settings_text = f.read() or ""
                    settings_obj = load(settings_text, Loader=Loader) or {}            
            except:
                settings_obj = {}
            self._config_path = value
            settings_obj["config_file"] = value.absoluteFilePath()
            with open(self.settings_file_path, "w") as f:
                dump(settings_obj, f)
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

    def set_executable_path(self) -> None:
        """
        Open a file dialog to select a new executable file.
        # TODO: check that the file is a (RAiSD) executable?
        """
        new_executable_path, _ = QFileDialog.getOpenFileName(
                None,
                "Select File",
                app_settings.executable_file_path.absolutePath(),
            )
        if not new_executable_path:  # Check for empty string (canceled)
            return  
        try:
            app_settings.executable_file_path = QFileInfo(new_executable_path)
        except Exception as e:
            print(f"Error setting workspace: {e}")

    def set_environment_manager(self) -> None:
        """
        Open a dialog to select a new environment manager.
        """
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Choose environment manager")
        self.dialog.setModal(True)
        self.dialog.resize(300, 200)

        layout = VBoxLayout(self.dialog, spacing=constants.GAP_TINY)

        combo_box = QComboBox()
        combo_box.addItems(self.environment_managers)
        combo_box.setCurrentIndex(self.environment_manager)
        layout.addWidget(combo_box)

        self.buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonbox.setCenterButtons(True)
        self.buttonbox.accepted.connect(
            lambda : self._on_environment_manager_select(combo_box.currentIndex()))
        layout.addWidget(self.buttonbox)

        self.dialog.exec()
    
    @Slot(int)
    def _on_environment_manager_select(self, index: int) -> None:
        """
        Set the environment manager to the new value and close the dialog.
        # TODO: check that the environment manager is installed?

        :param index: the index of the new environment manager
        :type index: int
        """
        if index != self._environment_manager:
            self.environment_manager = index
        self.dialog.close()

    def set_environment_name(self) -> None:
        """
        Open a dialog to choose a new environment name.
        """
        self.dialog = QDialog()
        self.dialog.setWindowTitle("Choose environment name")
        self.dialog.setModal(True)
        self.dialog.resize(300, 200)

        layout = VBoxLayout(self.dialog, spacing=constants.GAP_TINY)

        line_edit = QLineEdit()
        line_edit.setText(self.environment_name)
        layout.addWidget(line_edit)

        self.buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonbox.setCenterButtons(True)
        self.buttonbox.accepted.connect(
            lambda : self._on_environment_name_select(line_edit.text()))
        layout.addWidget(self.buttonbox)

        self.dialog.exec()

    @Slot(str)
    def _on_environment_name_select(self, name: str) -> None:
        """
        Set the environment name to the new value and close the dialog.
        # TODO: check that the environment exists?

        :param name: the name of the environment
        :type name: str
        """
        if name != self.environment_name:
            self.environment_name = name
        self.dialog.close()

    def set_config_path(self) -> None:
        """
        Open a file dialog to select a new config file.
        # TODO: check the contents of the file?
        """
        new_config_path, _ = QFileDialog.getOpenFileName(
                None,
                "Select File",
                app_settings.config_path.absolutePath(),
            )
        if not new_config_path:  # Check for empty string (canceled)
            return  
        try:
            app_settings.config_path = QFileInfo(new_config_path)
        except Exception as e:
            print(f"Error setting workspace: {e}")

# create a global singleton instance
app_settings = Settings()