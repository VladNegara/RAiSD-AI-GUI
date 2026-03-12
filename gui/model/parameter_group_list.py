from re import compile
from typing import Any
from yaml import load, Loader

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from gui.model.parameter_group import ParameterGroup
from gui.model.parameter import (
    Parameter,
    OptionalParameter,
    MultiParameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
    FileParameter,
)
from gui.model.dependency import (
    Dependency,
    OrCondition,
)


class ParameterGroupList(QObject):
    """
    A list of parameters for a terminal command.

    The parameters are organized in `ParameterGroup` objects, based on
    the operation mode they correspond to and how they relate.
    """

    operations_changed = Signal()

    def __init__(
            self,
            command: str,
            operations: dict[str, bool],
            parameter_groups: list[ParameterGroup] | None = None,
            dependencies: list[Dependency] | None = None,
    ) -> None:
        """
        Initialize a `ParameterGroupList` object.

        :param command: the terminal command to use
        :type command: str

        :param parameter_groups: the groups of parameters
        :type parameter_groups: list[ParameterGroup] | None
        """
        super().__init__()
        self.command = command
        self._operations = operations
        self._parameter_groups = parameter_groups or []
        self._dependencies = dependencies or []

    class OperationEnabledCondition(Dependency.Condition):
        def __init__(
                self,
                parameter_group_list: "ParameterGroupList",
                operation: str,
                target_value: bool = True,
                parent: QObject | None = None,
        ) -> None:
            super().__init__(
                value=parameter_group_list.operations[operation]==target_value,
                parent=parent,
            )
            self._parameter_group_list = parameter_group_list
            self._operation = operation
            self._target_value = target_value

            self._parameter_group_list.operations_changed.connect(self._operations_changed)

        @Slot()
        def _operations_changed(self) -> None:
            self.value = self._parameter_group_list.operations[self._operation] == self._target_value


    @classmethod
    def from_yaml(cls, file_path: str) -> "ParameterGroupList":
        """
        Create a list of parameters from a YAML file.

        :param file_path: the path to the configuration file
        :type file_path: str

        :return: the parameter list
        :rtype: Self
        """

        id_to_parameter: dict[str, Parameter] = {}

        def parse_parameter(
                obj: dict,
                operations: set[str]
        ) -> Parameter[Any]:
            name = obj.get("name", "") or ""

            description = obj.get("description", "") or ""

            parameter_type: str
            if "type" in obj:
                parameter_type = obj["type"]
            else:
                raise ValueError("Parameter type missing.")

            flag = obj.get("cli", "") or ""

            parameter_operations = set(operations)

            if "operations" in obj:
                if "add" in obj["operations"]:
                    for op in obj["operations"]["add"]:
                        parameter_operations.add(op)
                if "remove" in obj["operations"]:
                    for op in obj["operations"]["remove"]:
                        parameter_operations.remove(op)

            parameter: Parameter

            match parameter_type:
                case "int":
                    if "default" in obj:
                        default_value = obj["default"]
                    else:
                        raise ValueError(f"No default value provided for int parameter {name}")

                    lower_bound = obj.get("min", None)
                    upper_bound = obj.get("max", None)

                    parameter = IntParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
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

                    parameter = FloatParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        default_value,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound
                    )
                case "bool":
                    if "default" in obj:
                        default_value = obj["default"]
                    else:
                        raise ValueError(f"No default value provided for bool parameter {name}")
                    
                    parameter = BoolParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        default_value,
                    )
                case "enum":
                    options_list = obj.get("options", [])
                    options: list[tuple[str, str]]
                    options = []
                    for option in options_list:
                        if "name" in option:
                            option_name = option.get("name", "") or ""
                        else:
                            raise ValueError(f"An enum option does not have a name for enum parameter {name}")
                        cli = option.get("cli", "") or ""
                        options.append((option_name, cli))

                    if "default" in obj:
                        default_value = obj["default"]
                    else:
                        raise ValueError(f"No default value provided for enum parameter {name}")
                    
                    parameter = EnumParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        options,
                        default_value,
                    )
                case "str":
                    default_value = obj.get("default", "") or ""

                    max_length = obj.get("max_length", None)

                    pattern = obj.get("pattern", None)
                    compiled_pattern = None
                    if pattern:
                        compiled_pattern = compile(pattern)

                    parameter = StringParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        default_value,
                        max_length,
                        compiled_pattern,
                    )
                case "optional":
                    if "default" in obj:
                        default_value = obj["default"]
                    else:
                        raise ValueError(f"No default value provided for default parameter {name}")
                    
                    inner_parameter = parse_parameter(obj.get("parameter", {}), operations)
                    parameter = OptionalParameter(
                        name,
                        description,
                        parameter_operations,
                        default_value,
                        inner_parameter,
                    )
                case "multi":
                    parameters_list = obj.get("parameters", []) or []
                    inner_parameters: list[Parameter[Any]] = []
                    for inner_parameter_obj in parameters_list:
                        inner_parameters.append(parse_parameter(inner_parameter_obj, operations))

                    parameter = MultiParameter(
                        name,
                        description,
                        flag,
                        inner_parameters,
                    )
                case _:
                    raise ValueError(
                        f"Invalid parameter definition for parameter {name} in configuration file (type: {parameter_type})."
                    )

            return parameter

        def parse_parameter_group(obj: dict) -> ParameterGroup:
            parameters = []
            name = obj["name"] or ""

            operations = obj.get("operations", [])

            for parameter_id, parameter_obj in obj["parameters"].items():
                try:
                    parameter = parse_parameter(parameter_obj, set(operations))
                    parameters.append(parameter)
                    id_to_parameter[parameter_id] = parameter

                except ValueError:
                    pass # This should not be ignored in the final code
            return ParameterGroup(name, parameters)

        with open(file_path) as f:
            config_text = f.read()

        config_obj = load(config_text, Loader=Loader)

        operations = {}
        mode_list = config_obj.get("modes", []) or []
        for mode_obj in mode_list:
            for operation in mode_obj["operations"]:
                operations[operation] = True

        parameter_groups = []
        for parameter_group_obj in config_obj["parameter_groups"]:
            parameter_groups.append(parse_parameter_group(parameter_group_obj))

        result = cls("./RAiSD-AI", operations, parameter_groups)

        for group in result.parameter_groups:
            for param in group.parameters:
                single_operation_conditions = []
                for operation in param.operations:
                    single_operation_conditions.append(
                            cls.OperationEnabledCondition(
                            result,
                            operation,
                            parent=result,
                        )
                    )
                operation_condition = OrCondition(single_operation_conditions)
                Dependency(
                    operation_condition,
                    Parameter.EnabledEffect(param),
                    result,
                )

        return result

    @property
    def operations(self) -> dict[str, bool]:
        """
        The active operations of the parameter list.

        """
        return self._operations

    def set_operation(self, operation: str, value: bool) -> None:
        """
        Set an operation to active or not.

        :param operation: the operation to set.
        :type operation: str

        :param value: the value to set the operation to.
        :type value: bool
        """

        if not operation in self._operations:
            raise Exception(f"Setting an invalid operation: {operation}.")
        self._operations[operation] = value

        self.operations_changed.emit()

    @property
    def parameter_groups(self) -> list[ParameterGroup]:
        """
        The list of groups in the parameter list.
        """
        return self._parameter_groups

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

        A separate instruction is produced for each active operation. The
        command is obtained by prepending the list command to the operations's 
        command to the combination of applicable groups' CLI representations.

        :return: the list of instructions
        :rtype: list[str]
        """

        instructions = []
        operations = [operation for operation in self._operations if self._operations[operation]]
        for operation in operations:
            # For each operation get the cli representation from all param_groups
            # The paramgroups handle the operation by passing it to the parameters
            instruction = f"{self.command} -op {operation}"
            for param_group in self._parameter_groups:
                instruction = f"{instruction} {param_group.to_cli(operation)}"
            instructions.append(instruction)

        return instructions
