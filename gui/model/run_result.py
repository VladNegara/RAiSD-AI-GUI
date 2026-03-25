from gui.model.parameter_group_list import ParameterGroupList

import json
from datetime import datetime 
from gui.model.settings import app_settings
from gui.model.history_record import HistoryRecord
from gui.model.parameter import Parameter, OptionalParameter, MultiParameter

class RunResult():
    def __init__(
            self, 
            commands: list[str] | None = None,
            parameter_group_list: ParameterGroupList = None,
            time_completed: datetime | None = None
        ):
        self._commands = commands
        self._parameter_group_list = parameter_group_list or ParameterGroupList.from_yaml(app_settings.yaml_path)
        self._time_completed = time_completed

    def to_history_record(self) -> HistoryRecord:
        """
        Makes a history record with the information of the current RunResult.
        """
        parameters_dict = {}
        for parameter_group in self.parameter_group_list:
            for parameter in parameter_group:
                parameters_dict[parameter.name] = self.parameter_to_value(parameter)
        
        return HistoryRecord(
            self._parameter_group_list.run_id,
            self.commands,
            self._parameter_group_list.operations,
            parameters_dict,
            self._time_completed
        )

    def to_dict(self) -> str:
        """
        Makes a dictionary with the information of the current RunResult. This
        is used to store in the history file.
        """
        parameters_dict = {}
        for parameter_group in self.parameter_group_list:
            for parameter in parameter_group:
                parameters_dict[parameter.name] = self.parameter_to_value(parameter)

        dict = {
            "name": self._parameter_group_list.run_id,
            "commands": self._commands,
            "operations": self._parameter_group_list.operations,
            "parameters": parameters_dict,
            "time_completed": self._time_completed
        }
        return dict

    def parameter_to_value(self, parameter: Parameter) -> str | dict:
        """
        Makes the dictionary or string that is stored as the value of each 
        parameter. Uses recursion for MultiParameter and OptionalParameter
        """
        if type(parameter) is MultiParameter: 
            parameters = {}
            for param in parameter.parameters:
                parameters[param.name] = self.parameter_to_value(param)
            return parameters
        if type(parameter) is OptionalParameter:
            value = {}
            value["enabled"] = parameter.value
            value[parameter.parameter.name] = self.parameter_to_value(parameter.parameter)
            return value
        else:
            return parameter.value

    def save_to_history(self) -> None:
        """
        Saves current run result to the history file of the workspace.
        """
        if not app_settings.workspace_path.exists("history.json"):
            # If no history file exists
            with open(app_settings.workspace_path.absoluteFilePath("history.json"), "w") as f:
                history = {}
                history[f"{self._time_completed}-{self._parameter_group_list.run_id}"] = self.to_dict()
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
                history[f"{self._time_completed}-{self._parameter_group_list.run_id}"] = self.to_dict()
                f.seek(0)
                json.dump(history, f, indent=4, default=str)
    
    @property
    def commands(self) -> list[str] | None:
        return self._commands
    
    @property
    def parameter_group_list(self) -> ParameterGroupList:
        return self._parameter_group_list
    
    @property
    def time_completed(self) -> datetime | None:
        return self._time_completed
    

    def set_commands(self) -> None:
        """
        Sets the commands of a run based on the cli representation
        of the ParameterGroupList
        """
        self._commands = self._parameter_group_list.to_cli()

    def set_completed(self) -> None:
        self._commands = self._parameter_group_list.to_cli()
        self._time_completed = datetime.now()

    def populate(self, history_record: HistoryRecord) -> None:
        """
        Populates the current run result with the contents of a history record.
        This is used to fill the ResultsWidget in history with the contents
        of records when a user clicks on them.
        """
        self.parameter_group_list.run_id_parameter.value = history_record.name
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
        """
        Populates a parameter with the values from a dict or string. Uses
        recursion for optional parameters and multi parameters.
        """
        if type(parameter) is MultiParameter:
            for param in parameter.parameters:
                if value[param.name]:
                    self.populate_parameter(param, value[param.name])
        elif type(parameter) is OptionalParameter:
            if not value['enabled']:
                raise ValueError(
                    "Optional parameter must have 'enabled' value."
                )
            parameter.value = value["enabled"]
            if value[parameter.parameter]:
                self.populate_parameter(
                    parameter.parameter, 
                    value[parameter.parameter.name]
                )
        else:
            if not isinstance(value, str):
                raise ValueError(
                    f"Incorrect value for {parameter.name}: {value}"
                    + "Expected str."
                )
            parameter.value = value