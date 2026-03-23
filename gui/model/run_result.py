from gui.model.parameter_group_list import ParameterGroupList

from PySide6.QtCore import QDir

import json
from datetime import datetime 
from gui.model.settings import app_settings

class RunResult():
    def __init__(
            self, 
            name: str = "",
            commands: list[str] | None = None,
            parameter_group_list: ParameterGroupList = None,
            time_completed: datetime | None = None
        ):
        self._name = name
        self._commands = commands
        self._parameter_group_list = parameter_group_list or ParameterGroupList.from_yaml(app_settings.yaml_path)
        self._time_completed = time_completed

    @classmethod
    def from_history_file(cls) -> list["RunResult"] | None:
        run_results = []
        try: 
            with open(app_settings.workspace_path.absoluteFilePath("history.json"), "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise json.JSONDecodeError
                for key in data.keys():
                    if not isinstance(data[key], dict):
                        raise json.JSONDecodeError
                    run_results.append(cls.from_dict(data[key]))
                return run_results
        except FileNotFoundError:
            print("No history file found in this workspace")
            return None
        except json.JSONDecodeError:
            print("History file not parseable. Might be empty or formatted incorrectly")
            return []
            

    @classmethod
    def from_dict(cls, dictionary: dict) -> "RunResult":
        name = dictionary.get("name")
        if not isinstance(name, str):
            raise ValueError(
                f"Invalid run name: {name}. "
                + "Expected string name."
            )

        commands = dictionary.get("commands")
        if not isinstance(commands, list):
            raise ValueError(
                f"Invalid commands object: {commands}. "
                + "Expected list."
            )
        
        for command in commands:
            if not isinstance(command, str):
                raise ValueError(
                    f"Invalid command type: {command}"
                    + "Expected string."
                )
        
        parameters = dictionary.get("parameters")
        if not isinstance(parameters, dict):
            raise ValueError(
                f"Invalid parameter object: {parameters}."
                + "Expected dictionary."
            )
        
        parameter_group_list = ParameterGroupList.from_yaml(app_settings.yaml_path)
        # TODO populate with parameter values

        time_completed = dictionary.get("time_completed")
        if not isinstance(time_completed, str):
            raise ValueError(
                f"Invalid time_completed type: {time_completed}"
                + "Expected string."
            )
        time_completed = datetime.strptime(time_completed, "%Y-%m-%d %H:%M:%S.%f")

        return cls(name, commands, parameter_group_list, time_completed)

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
            "name": self.name,
            "commands": self._commands,
            "parameters": parameters_dict,
            "time_completed": self._time_completed
        }
        return dict

    def save_to_history(self) -> None:
        # try: 
        if not app_settings.workspace_path.exists("history.json"):
            # If no history file exists
            with open(app_settings.workspace_path.absoluteFilePath("history.json"), "w") as f:
                history = {}
                history[self._name] = self.to_dict()
                json.dump(history, f, indent=4, default=str)
        else:    
            # If a file exists
            with open(app_settings.workspace_path.absoluteFilePath("history.json"), "r+") as f:
                history = {}
                try:
                    history = json.load(f)
                except:
                    # File could not be parsed
                    print("Problem reading file: might be empty or incorrect format")
                history[self._name] = self.to_dict()
                f.seek(0)
                json.dump(history, f, indent=4, default=str)


    @property
    def name(self) -> str:
        return self._name
    
    @property
    def commands(self) -> list[str] | None:
        return self._commands
    
    @property
    def parameter_group_list(self) -> ParameterGroupList:
        return self._parameter_group_list
    
    @property
    def time_completed(self) -> datetime | None:
        return self._time_completed
    
    def set_name(self) -> None:
        self._name = "Hi" # TODO: fix once merged with PR of run_id

    def set_commands(self) -> None:
        """
        Sets the commands of a run based on the cli representation
        of the ParameterGroupList
        """
        self._commands = self._parameter_group_list.to_cli()

    def set_completed(self) -> None:
        self._time_completed = datetime.now()