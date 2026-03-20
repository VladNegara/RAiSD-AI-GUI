from gui.model.parameter_group_list import ParameterGroupList

from PySide6.QtCore import QDir

import json


class RunResult():
    def __init__(
            self, 
            parameter_group_list: ParameterGroupList,
            path: QDir,
            run_completed: bool = False
        ):
        self._run_completed = run_completed
        self._results_path = path
        self._info_files = None
        self._commands = None
        self._parameter_group_list = parameter_group_list

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
            "path": self._results_path.path(),
            "info-files": self._info_files,
            "commands": self._commands
        }
        return dir

    @property
    def run_completed(self) -> bool:
        return self._run_completed

    @run_completed.setter
    def run_completed(self, run_completed: bool) -> None:
        self._run_completed = run_completed

    @property
    def path(self) -> QDir:
        return self._results_path
    
    @path.setter 
    def path(self, path: QDir) -> None:
        self._results_path = path
    
    @property
    def info_files(self) -> list[str] | None:
        return self._info_files
    
    @info_files.setter
    def info_files(self, files: list[str]) -> None:
        self._info_files = files

    @property
    def commands(self) -> list[str] | None:
        return self._commands
    
    def set_commands(self) -> None:
        """
        Sets the commands of a run based on the cli representation
        of the ParameterGroupList
        """
        self._commands = self._parameter_group_list.to_cli()

    @property
    def parameter_group_list(self) -> ParameterGroupList:
        return self._parameter_group_list