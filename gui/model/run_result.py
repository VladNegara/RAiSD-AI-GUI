from gui.model.parameter_group_list import ParameterGroupList

from PySide6.QtCore import QDir

import json


class RunResult():
    def __init__(
            self, 
            yaml_path: str,
            name: str,
        ):
        self._folder_name = name
        self._commands = None
        self._parameter_group_list = ParameterGroupList.from_yaml(yaml_path)

    @classmethod
    def from_history_file(cls, path: str) -> list["RunResult"]:
        #TODO: implement parsing
        pass

    @classmethod
    def from_str(cls, string: str) -> "RunResult":
        #TODO: implement parsing
        pass

    def populate_parameter_group_list(
            self, 
            parameter_group_list: ParameterGroupList, 
            command: str
        ) -> ParameterGroupList:
        #TODO: implement
        pass

    def to_dir(self) -> str:
        dir = {
            # "path": self._results_path.path(),
            # "info-files": self._info_files,
            # "commands": self._commands
        }
        return dir

    @property
    def folder_name(self) -> str:
        return self._folder_name
    
    @property
    def commands(self) -> list[str] | None:
        return self._commands
    
    @property
    def parameter_group_list(self) -> ParameterGroupList:
        return self._parameter_group_list
    
    def set_name(self) -> None:
        self._folder_name = "Hi" # TODO: fix once merged with Steefs PR

    def set_commands(self) -> None:
        """
        Sets the commands of a run based on the cli representation
        of the ParameterGroupList
        """
        self._commands = self._parameter_group_list.to_cli()

