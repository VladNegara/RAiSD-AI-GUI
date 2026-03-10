from re import compile
from typing import Any
from yaml import load, Loader

from gui.model.parameter_group import ParameterGroup
from gui.model.parameter import (
    Parameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
)


class ParameterGroupList():
    """
    A list of parameters for a terminal command.

    The parameters are organized in `ParameterGroup` objects, based on
    the operation mode they correspond to and how they relate.
    """

    def __init__(
            self,
            command: str,
            parameter_groups: list[ParameterGroup] | None = None,
    ) -> None:
        """
        Initialize a `ParameterGroupList` object.

        :param command: the terminal command to use
        :type command: str

        :param parameter_groups: the groups of parameters
        :type parameter_groups: list[ParameterGroup] | None
        """
        self.command = command
        self._parameter_groups = parameter_groups or []

    @classmethod
    def from_yaml(cls, file_path: str) -> "ParameterGroupList":
        """
        Create a list of parameters from a YAML file.

        :param file_path: the path to the configuration file
        :type file_path: str

        :return: the parameter list
        :rtype: Self
        """
        def parse_parameter(obj: dict) -> Parameter[Any]:
            name = obj.get("name", "") or ""

            description = obj.get("description", "") or ""

            parameter_type: str
            if "type" in obj:
                parameter_type = obj["type"]
            else:
                raise ValueError("Parameter type missing.")

            flag = obj.get("cli", "") or ""

            match parameter_type:
                case "int":
                    if "default" in obj:
                        default_value = obj["default"]
                    else:
                        raise ValueError(f"No default value provided for int parameter {name}")

                    lower_bound = obj.get("min", None)
                    upper_bound = obj.get("max", None)

                    return IntParameter(
                        name,
                        description,
                        flag,
                        default_value,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound
                    )
                case "float":
                    if "default" in obj:
                        default_value = obj["default"]
                    else:
                        raise ValueError(f"No default value provided for int parameter {name}")

                    lower_bound = obj.get("min", None)
                    upper_bound = obj.get("max", None)

                    return FloatParameter(
                        name,
                        description,
                        flag,
                        default_value,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound
                    )
                case "enum":
                    options_list = obj.get("options")
                    options: list[tuple[str, str]]
                    options = []
                    for option in options_list:
                        if "name" in option:
                            option_name = option.get("name")
                        else:
                            raise ValueError(f"An enum option does not have a name for enum parameter {name}")
                        cli = option.get("cli", "") or ""
                        options.append([option_name, cli])

                    if "default" in obj:
                        default_value = obj["default"]
                    else:
                        raise ValueError(f"No default value provided for enum parameter {name}")
                    
                    return EnumParameter(
                        name,
                        description,
                        flag,
                        options,
                        default_value
                    )
                case _:
                    raise ValueError(
                        "Invalid parameter definition in configuration file."
                    )

        def parse_parameter_group(all_parameters: dict, obj: dict) -> ParameterGroup:
            parameters = []
            name = obj["name"] or ""
            for parameter in obj["parameters"]:
                try:
                    parameters.append(parse_parameter(all_parameters[parameter]))
                except ValueError:
                    pass # This should not be ignored in the final code
            return ParameterGroup(name, parameters)

        with open(file_path) as f:
            config_text = f.read()

        config = load(config_text, Loader=Loader)
        groups = []
        modes = config["modes"]
        for mode in modes:
            parameter_groups = mode["parameter_groups"]
            for parameter_group in parameter_groups:
                groups.append(parse_parameter_group(config["parameters"], parameter_group))
            operations = mode["operations"]
            for operation in operations:
                parameter_groups = operation["parameter_groups"]
                for parameter_group in parameter_groups:
                    groups.append(parse_parameter_group(config["parameters"], parameter_group))

        return cls("./RAiSD-AI", groups)

    @property
    def parameter_groups(self) -> list[ParameterGroup]:
        """
        The list of groups in the parameter list.
        """
        return self._parameter_groups

    def add_parameter_group(self, parameter_group: ParameterGroup) -> None:
        """
        Add a group of parameters to the list.

        :param parameter_group: the group to be added
        :type parameter_group: ParameterGroup
        """
        self._parameter_groups.append(parameter_group)

    @property
    def valid(self) -> bool:
        """
        Whether the current parameter values are valid.

        The list is valid if and only if every group is valid.
        """
        return all([group.valid for group in self.parameter_groups])

    def to_cli(self) -> list[str]:
        """
        Produce command-line instructions for the current parameter
        values.

        A separate instruction is produced for each parameter group. The
        command is obtained by prepending the list's command to the
        group's CLI representation.

        :return: the list of instructions
        :rtype: list[str]
        """
        return [
            f"{self.command} {param_group.to_cli()}"
            for param_group in self.parameter_groups
        ]
