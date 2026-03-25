import json

from datetime import datetime

from gui.model.settings import app_settings
from gui.model.parameter_group_list import ParameterGroupList

class HistoryRecord():
    """
    A history record holds the information of a completed run necessary to
    show in the history.
    """
    def __init__(
            self,
            name: str,
            commands: list[str],
            operations: dict[str, bool],
            parameters: dict,
            time_completed: datetime
    ):
        self._name = name
        self._commands = commands
        self._operations = operations
        self._parameters = parameters
        self._time_completed = time_completed

    @classmethod
    def from_history_file(cls) -> list["HistoryRecord"] | None:
        """
        Class method that retrieves data from a history file in the workspace
        and parses it into a list of history records.
        """
        history_records = []
        try: 
            with open(app_settings.workspace_path.absoluteFilePath("history.json"), "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise json.JSONDecodeError
                for key in data.keys():
                    if not isinstance(data[key], dict):
                        raise json.JSONDecodeError
                    history_records.append(cls.from_dict(data[key]))
                return history_records
        except FileNotFoundError:
            print("No history file found in this workspace")
            return None
        except json.JSONDecodeError:
            print("History file not parseable. Might be empty or formatted incorrectly")
            return []
        
    @classmethod
    def from_dict(cls, dictionary: dict) -> "HistoryRecord":
        """
        Class method that takes a dictionary and parses it to construct a 
        history record. 

        :param dictionary: the dictionary that contains the record data
        :type dictionary: dict
        """
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
        
        operations = dictionary.get("operations")
        if not isinstance(operations, dict):
            raise ValueError(
                f"Invalid operations type: {operations}"
                + "Expected list."
            )

        parameters = dictionary.get("parameters")
        if not isinstance(parameters, dict):
            raise ValueError(
                f"Invalid parameter object: {parameters}."
                + "Expected dictionary."
            )

        time_completed = dictionary.get("time_completed")
        if not isinstance(time_completed, str):
            raise ValueError(
                f"Invalid time_completed type: {time_completed}"
                + "Expected string."
            )
        time_completed = datetime.strptime(time_completed, "%Y-%m-%d %H:%M:%S.%f")

        return cls(name, commands, operations, parameters, time_completed)
    
    @property
    def name(self) -> str:
        """
        The name of the execution. This is the run_id of the parameter
        group list and run result. This is also the name of the directory
        where the output of the operation is stored.
        """
        return self._name
    
    @property
    def commands(self) -> list[str] | None:
        """
        The commands of an execution.
        """
        return self._commands

    @property
    def operations(self) -> dict[str, bool]:
        """
        The operatons that were run during an execution. Stored as a dictionary
        from operation name to a boolean that signifies whether the operation
        was performed.
        """
        return self._operations

    @property
    def parameters(self) -> dict:
        """
        A dictionary that holds the parameters that were used, with their 
        values.
        """
        return self._parameters
    
    @property
    def time_completed(self) -> datetime | None:
        """
        The time at which the run was completed. This is used to show how long 
        ago a run was completed.
        """
        return self._time_completed
    