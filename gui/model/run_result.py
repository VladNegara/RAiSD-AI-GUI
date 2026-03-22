from gui.model.parameter_group_list import ParameterGroupList

from PySide6.QtCore import QDir

import json
from gui.model.settings import app_settings

class RunResult():
    def __init__(
            self, 
            yaml_path: str,
            name: str = "",
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

    def to_dict(self) -> str:
        parameters_dict = {}
        for parameter_group in self.parameter_group_list:
            for parameter in parameter_group:
                parameters_dict[parameter.name] = parameter.value

        dict = {
            "folder_name": self.folder_name,
            "commands": self._commands,
            "parameters": parameters_dict
        }
        return dict

    def save_to_history(self) -> None:
        try: 
            if not app_settings.workspace_path.exists("history.json"):
                with open(app_settings.workspace_path.absoluteFilePath("history.json"), "w") as f:
                    history = {}
                    history[self._folder_name] = self.to_dict()
                    json.dump(history, f)
            else:    
                with open(app_settings.workspace_path.absoluteFilePath("history.json"), "r+") as f:
                    history = json.load(f)
                    history[self._folder_name] = self.to_dict()
                    f.seek(0)
                    json.dump(history, f)
        except:
            raise Exception("Failed to write to history file")


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

