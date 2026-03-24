from gui.model.parameter_group_list import ParameterGroupList

from PySide6.QtCore import QDir

import json
from datetime import datetime 
from gui.model.settings import app_settings
from gui.model.history_record import HistoryRecord
from gui.model.parameter import Parameter, OptionalParameter, MultiParameter

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
                parameters_dict[parameter.name] = self.parameter_to_value(parameter)

        dict = {
            "name": self.name,
            "commands": self._commands,
            "operations": self._parameter_group_list.operations,
            "parameters": parameters_dict,
            "time_completed": self._time_completed
        }
        return dict

    def parameter_to_value(self, parameter: Parameter) -> str | dict:
        print(f"value of {parameter.name}: ")
        if type(parameter) is MultiParameter: 
            parameters = {}
            print(f"multiparameter with {parameter.parameters}")
            for param in parameter.parameters:
                parameters[param.name] = self.parameter_to_value(param)
            return parameters
        if type(parameter) is OptionalParameter:
            print(f"optional parameter with {parameter.parameter}")
            value = {}
            value["enabled"] = parameter.value
            value[parameter.parameter.name] = self.parameter_to_value(parameter.parameter)
            return value
        else:
            print(f"value: {parameter.value}")
            return parameter.value

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

    def populate(self, history_record: HistoryRecord) -> None:
        self._name = history_record.name
        self._commands = history_record.commands
        dictionary = history_record.parameters
        for parameter_group in self._parameter_group_list:
            for parameter in parameter_group:
                if parameter.name in dictionary:
                    self.populate_parameter(parameter, dictionary[parameter.name])
                    #TODO: validiity checking?
        self._time_completed = history_record.time_completed
        for operation in history_record.operations:
            self._parameter_group_list.set_operation(operation, history_record.operations[operation])

    def populate_parameter(self, parameter: Parameter, value: dict | str) -> None:
        if type(parameter) is MultiParameter:
            for param in parameter.parameters:
                self.populate_parameter(param, value[param.name])
        elif type(parameter) is OptionalParameter:
            parameter.value = value["enabled"]
            self.populate_parameter(parameter.parameter, value[parameter.parameter.name])
        else:
            parameter.value = value