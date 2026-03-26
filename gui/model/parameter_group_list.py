from re import compile
from typing import Any, Iterator
from yaml import load, Loader

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from gui.model.file_structure import (
    FileStructure,
    SingleFile,
    Directory,
)
from gui.model.operation import Operation
from gui.model.operation_tree import OperationTree
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
    AndCondition,
    OrCondition,
)


class ParameterGroupList(QObject):
    """
    A list of parameters for a terminal command.

    The parameters are organized in `ParameterGroup` objects, based on
    the operation mode they correspond to and how they relate.
    """

    run_id_valid_changed = Signal(bool)
    operations_valid_changed = Signal(bool)

    def __init__(
            self,
            run_id_parameter: StringParameter,
            operation_trees: list[OperationTree],
            parameter_groups: list[ParameterGroup] | None = None,
            dependencies: list[Dependency] | None = None,
    ) -> None:
        """
        Initialize a `ParameterGroupList` object.

        :param parameter_groups: the groups of parameters
        :type parameter_groups: list[ParameterGroup] | None
        """
        super().__init__()
        self._run_id_parameter = run_id_parameter
        self._run_id = run_id_parameter.value
        self._run_id_parameter.value_changed.connect(
            self._run_id_parameter_value_changed
        )
        self._operation_trees = operation_trees
        for tree in self._operation_trees:
            tree.valid_changed.connect(self._operation_tree_valid_changed)
        self._selected_operation_tree_index = 0
        self._parameter_groups = parameter_groups or []
        self._dependencies = dependencies or []
        # Set using setter
        self.selected_operation_tree_index = 0

    @classmethod
    def from_yaml(cls, file_path: str) -> "ParameterGroupList":
        """
        Create a list of parameters from a YAML file.

        :param file_path: the path to the configuration file
        :type file_path: str

        :return: the parameter list
        :rtype: Self
        """

        id_to_parameter: dict[str, Parameter[Any]] = {}
        parameter_to_condition_objs: dict[Parameter[Any], list[dict]] = {}

        def parse_file_structure(
                obj: dict,
        ) -> FileStructure:
            if "type" not in obj:
                raise ValueError("File structure type missing.")
            file_type = obj["type"]
            match file_type:
                case "file" | "single" | "single file":
                    formats = obj.get("formats", [])
                    if not isinstance(formats, list):
                        raise ValueError("Invalid format list for single file.")
                    for format in formats:
                        if not isinstance(format, str):
                            raise ValueError(
                                f"Invalid format for single file: {format}. "
                                + "Expected string."
                            )

                    return SingleFile(formats)
                case "folder" | "directory" | "dir":
                    contents_list = obj.get("contents", [])
                    if not isinstance(contents_list, list):
                        raise ValueError("Invalid contents list for directory.")
                    contents = []
                    for contents_obj in contents_list:
                        if not isinstance (contents_obj, dict):
                            raise ValueError(
                                f"Invalid item in contents for directory: {contents_obj}."
                                + "Expected object."
                            )
                        contents.append(parse_file_structure(contents_obj))

                    return Directory(contents)
                case _:
                    raise ValueError(
                        f"Invalid file structure. Unknown file type {file_type}"
                    )
                
        def parse_operation(
                obj: dict,
                id: str
        ) -> Operation:
            name = obj.get("name", "") or ""
            if not isinstance(name, str):
                raise ValueError(
                    f"Invalid operation name: {name}. Expected string or null."
                )

            description = obj.get("description", "") or ""
            if not isinstance(description, str):
                raise ValueError(
                    f"Invalid description for operation {name}: {description}."
                    + " Expected string or null."
                )
            
            cli = obj.get("cli", "") or ""
            if not isinstance(cli, str):
                raise ValueError(
                    f"Invalid CLI representation for operation {name}: {cli}."
                    + " Expected string or null."
                )

            requires = []
            requires_list = obj.get("input", []) or []
            if not isinstance(requires_list, list):
                raise ValueError(
                    f"Invalid input for operation {name}: {requires_list}."
                    + "Expected list."
                )
            for requires_obj in requires_list:
                if not isinstance (requires_obj, dict):
                    raise ValueError(
                        f"Invalid item in input list: {requires_obj}. "
                        + "Expected object."
                    )
                file_name = requires_obj.get("name", "")
                if not isinstance(file_name, str):
                    raise ValueError(
                    f"Invalid file name: {file_name}. Expected string or null."
                    )
                file_cli = requires_obj.get("cli", "") or ""
                if not isinstance(file_cli, str):
                    raise ValueError(
                        f"Invalid CLI representation for file {file_name}: "
                        + f"{file_cli}. Expected string or null."
                    )

                if "file" not in requires_obj:
                    raise ValueError("File missing.")
                file_obj = requires_obj["file"]
                file = parse_file_structure(file_obj)
                requires.append((file_name, file_cli, file))

            produces_obj = obj.get("output", "") or ""
            if not isinstance(produces_obj, dict):
                raise ValueError(
                    f"Invalid output for operation: {produces_obj}."
                    + "Expected object."
                )
            produces = parse_file_structure(produces_obj)

            prefix = obj.get("prefix", "") or ""
            if not isinstance(prefix, str):
                raise ValueError(
                    f"Invalid prefix for output path {prefix}."
                    + " Expected string or null."
                )
            
            return Operation(id, name, description, cli, requires, produces, prefix)

        def parse_parameter(
                obj: dict,
                operations: set[str]
        ) -> Parameter[Any]:
            name = obj.get("name", "") or ""
            if not isinstance(name, str):
                raise ValueError(
                    f"Invalid parameter name: {name}. Expected string or null."
                )

            description = obj.get("description", "") or ""
            if not isinstance(description, str):
                raise ValueError(
                    f"Invalid description for parameter {name}: {description}."
                    + " Expected string or null."
                )

            if "type" not in obj:
                raise ValueError("Parameter type missing.")
            parameter_type = obj["type"]

            flag = obj.get("cli", "") or ""
            if not isinstance(flag, str):
                raise ValueError(
                    f"Invalid CLI representation for parameter {name}: {flag}."
                    + " Expected string or null."
                )

            parameter_operations = set(operations)

            if "operations" in obj:
                operation_diffs_obj = obj["operations"]
                if not isinstance(operation_diffs_obj, dict):
                    raise ValueError(
                        f"Invalid value of 'operations' for parameter {name}: "
                        + f"{operation_diffs_obj}. Expected an object."
                    )
                if "add" in operation_diffs_obj:
                    operations_add_list = operation_diffs_obj["add"]
                    if not isinstance(operations_add_list, list):
                        raise ValueError(
                            "Invalid value of 'operations.add' for parameter "
                            + f"{name}: {operations_add_list} Expected a list."
                        )
                    for operation_id in operations_add_list:
                        if not isinstance(operation_id, str):
                            raise ValueError(
                                "Invalid operation ID added for parameter "
                                + f"{name}: {operation_id}. Expected a string."
                            )
                        parameter_operations.add(operation_id)
                if "remove" in operation_diffs_obj:
                    operations_remove_list = operation_diffs_obj["remove"]
                    if not isinstance(operations_remove_list, list):
                        raise ValueError(
                            "Invalid value of 'operations.remove' for "
                            + f" parameter {name}: {operations_remove_list}. "
                            + "Expected a list."
                        )
                    for operation_id in operations_remove_list:
                        if not isinstance(operation_id, str):
                            raise ValueError(
                                "Invalid operation ID removed for parameter "
                                + f"{name}: {operation_id}. Expected a string."
                            )
                        parameter_operations.remove(operation_id)

            parameter: Parameter

            match parameter_type:
                case "int":
                    if "default" not in obj:
                        raise ValueError(
                            "No default value provided "
                            + f"for int parameter {name}."
                        )
                    default_value = obj["default"]
                    if not isinstance(default_value, int):
                        raise ValueError(
                            f"Invalid default value for int parameter {name}: "
                            + f"{default_value}. Expected int."
                        )

                    lower_bound = obj.get("min", None)
                    if (lower_bound is not None
                        and not isinstance(lower_bound, int)):
                        raise ValueError(
                            f"Invalid minimum for int parameter {name}: "
                            + f"{lower_bound}. Expected int or null."
                        )
                    upper_bound = obj.get("max", None)
                    if (upper_bound is not None
                        and not isinstance(upper_bound, int)):
                        raise ValueError(
                            f"Invalid maximum for int parameter {name}: "
                            + f"{upper_bound}. Expected int or null."
                        )

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
                    if "default" not in obj:
                        raise ValueError(
                            "No default value provided "
                            + f"for float parameter {name}."
                        )
                    default_value = obj["default"]
                    if (not isinstance(default_value, int)
                        and not isinstance(default_value, float)):
                        raise ValueError(
                            f"Invalid default value for float parameter {name}"
                            + f": {default_value}. Expected float."
                        )

                    lower_bound = obj.get("min", None)
                    if (lower_bound is not None
                        and not isinstance(lower_bound, int)
                        and not isinstance(lower_bound, float)):
                        raise ValueError(
                            f"Invalid minimum for float parameter {name}: "
                            + f"{lower_bound}. Expected float or null."
                        )
                    upper_bound = obj.get("max", None)
                    if (upper_bound is not None
                        and not isinstance(upper_bound, int)
                        and not isinstance(upper_bound, float)):
                        raise ValueError(
                            f"Invalid maximum for float parameter {name}: "
                            + f"{upper_bound}. Expected float or null."
                        )

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
                    if "default" not in obj:
                        raise ValueError(
                            "No default value provided "
                            + f"for bool parameter {name}."
                        )
                    default_value = obj["default"]
                    if not isinstance(default_value, bool):
                        raise ValueError(
                            f"Invalid default value for bool parameter {name}"
                            + f": {default_value}. Expected bool."
                        )
                    
                    parameter = BoolParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        default_value,
                    )
                case "enum":
                    options: list[tuple[str, str]] = []
                    options_list = obj.get("options", [])
                    for option_obj in options_list:
                        if "name" not in option_obj:
                            raise ValueError(
                                "An enum option does not have a name "
                                + f"for enum parameter {name}."
                            )
                        option_name = option_obj["name"]
                        if not isinstance(option_name, str):
                            raise ValueError(
                                f"Invalid option name for parameter {name}: "
                                + f"{option_name}. Expected string."
                            )

                        option_cli = option_obj.get("cli", "") or ""
                        if not isinstance(option_cli, str):
                            raise ValueError(
                                "Invalid CLI representation for parameter "
                                + f"{name}: {option_cli}. Expected string or "
                                + "null."
                            )

                        options.append((option_name, option_cli))

                    default_value = obj.get("default", 0)
                    if not isinstance(default_value, int):
                        raise ValueError(
                            f"Invalid default value for enum parameter {name}:"
                            + f" {default_value}. Expected int or null."
                        )
                    
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
                    if not isinstance(default_value, str):
                        raise ValueError(
                            "Invalid default value for string parameter "
                            + f"{name}: {default_value}. Expected string or "
                            + "null."
                        )

                    max_length = obj.get("max_length", None)
                    if (max_length is not None
                        and not isinstance(max_length, int)):
                        raise ValueError(
                            f"Invalid max length for string parameter {name}: "
                            + f"{max_length}. Expected int or null."
                        )

                    pattern = obj.get("pattern", None)
                    if pattern is None:
                        compiled_pattern = None
                    elif isinstance(pattern, str):
                        compiled_pattern = compile(pattern)
                    else:
                        raise ValueError(
                            f"Invalid pattern for string parameter {name}: "
                            + f"{pattern}. Expected string or null."
                        )

                    parameter = StringParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        default_value,
                        max_length,
                        compiled_pattern,
                    )
                case "file":
                    accepted_formats = obj.get("formats", None)
                    if accepted_formats is not None and not isinstance(accepted_formats, list):
                        raise ValueError(
                            "Invalid list of file formats for file parameter "
                            + f"{name}: {accepted_formats}. Expected list or "
                            + "None."
                        )
                    if accepted_formats is not None:
                        for format in accepted_formats:
                            if not isinstance(format, str):
                                raise ValueError(
                                    "Invalid accepted format for file parameter "
                                    + f"{name}: {format}. Expected string."
                                )

                    strict = obj.get("strict", False)
                    if not isinstance(strict, bool):
                        raise ValueError(
                            "Invalid strict property for file parameter "
                            + f"{name}: {strict}. Expected bool or null."
                        )
                    if strict and not accepted_formats:
                        raise ValueError(
                            f"Strict file parameter {name} has no accepted "
                            + "file formats."
                        )

                    multiple = obj.get("multiple", False)
                    if not isinstance(multiple, bool):
                        raise ValueError(
                            "Invalid multiple property for file parameter "
                            + f"{name}: {multiple}. Expected bool or null."
                        )

                    parameter = FileParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        accepted_formats,
                        strict,
                        multiple,
                    )
                case "optional":
                    default_value = obj.get("default", False) or False
                    if not isinstance(default_value, bool):
                        raise ValueError(
                            "Invalid default value for optional parameter "
                            + f"{name}: {default_value}. Expected bool or "
                            + "null."
                        )

                    if "parameter" not in obj:
                        raise ValueError(
                            "Inner parameter not provided "
                            + f"for optional parameter {name}."
                        )
                    inner_parameter = parse_parameter(
                        obj["parameter"],
                        operations,
                    )

                    parameter = OptionalParameter(
                        name,
                        description,
                        parameter_operations,
                        default_value,
                        inner_parameter,
                    )
                case "multi":
                    if "parameters" not in obj:
                        raise ValueError(
                            f"Inner parameters not provided "
                            + f"for multi-value parameter {name}."
                        )
                    parameters_list = obj["parameters"]
                    if not isinstance(parameters_list, list):
                        raise ValueError(
                            "Invalid inner parameter list for multi-value "
                            + f"parameter {name}: {parameters_list}. Expected "
                            + "a list."
                        )
                    inner_parameters: list[Parameter[Any]] = []
                    for inner_parameter_obj in parameters_list:
                        inner_parameters.append(
                            parse_parameter(
                                inner_parameter_obj,
                                operations,
                            ),
                        )

                    parameter = MultiParameter(
                        name,
                        description,
                        flag,
                        parameter_operations,
                        inner_parameters,
                    )
                case _:
                    raise ValueError(
                        f"Invalid or missing type for parameter {name}: "
                        + f"{parameter_type}."
                    )

            condition_objs = obj.get("conditions", [])
            if not isinstance(condition_objs, list):
                raise ValueError(
                    f"Invalid condition list for parameter {name}: "
                    + f"{condition_objs}. Expected list or null."
                )
            parameter_to_condition_objs[parameter] = condition_objs

            return parameter

        def parse_parameter_group(obj: dict) -> ParameterGroup:
            name = obj.get("name", "") or ""
            if not isinstance(name, str):
                raise ValueError(
                    f"Invalid name for parameter group: {name}. Expected "
                    + "string or null."
                )

            operations = obj.get("operations", [])
            if not isinstance(operations, list):
                raise ValueError(
                    f"Invalid operations list for parameter group {name}: "
                    + f"{operations}. Expected list or null."
                )
            for operation in operations:
                if not isinstance(operation, str):
                    raise ValueError(
                        f"Invalid operation for parameter group {name}: "
                        + f"{operation}. Expected string."
                    )

            if "parameters" not in obj:
                raise ValueError(
                    f"Parameter group {name} does has no parameters object."
                )
            parameters_obj = obj["parameters"]
            if not isinstance(parameters_obj, dict):
                raise ValueError(
                    f"Invalid parameters field of parameter group {name}: "
                    + f" {parameters_obj}. Expected an object."
                )
            parameters: list[Parameter[Any]] = []
            for parameter_id, parameter_obj in obj["parameters"].items():
                if not isinstance(parameter_id, str):
                    raise ValueError(
                        f"Invalid parameter id: {parameter_id}. Expected "
                        + "string."
                    )
                parameter = parse_parameter(parameter_obj, set(operations))
                parameters.append(parameter)
                id_to_parameter[parameter_id] = parameter
            return ParameterGroup(name, parameters)

        def parse_condition(obj: dict) -> Dependency.Condition:
            if "type" not in obj:
                raise ValueError("Parameter condition has no type.")
            
            condition_type = obj["type"]

            match condition_type:
                case "or":
                    if "conditions" not in obj:
                        raise ValueError(
                            "Missing list of child conditions for 'or' "
                            + "condition."
                        )
                    conditions_list = obj["conditions"]
                    if not isinstance(conditions_list, list):
                        raise ValueError(
                            "Invalid child condition list for 'or' condition: "
                            + f"{conditions_list}. Expected a list."
                        )

                    conditions: list[Dependency.Condition] = []
                    for condition_obj in conditions_list:
                        conditions.append(
                            parse_condition(condition_obj)
                        )

                    return OrCondition(
                        conditions,
                    )
                case "enabled":
                    if "parameter" not in obj:
                        raise ValueError(
                            "Enabled condition has no target parameter."
                        )
                    parameter_id = obj["parameter"]
                    if not isinstance(parameter_id, str):
                        raise ValueError(
                            "Invalid target parameter ID for enabled condition"
                            + f": {parameter_id}. Expected string."
                        )

                    parameter = id_to_parameter[parameter_id]

                    target_value = obj.get("value", True)
                    if target_value is None:
                        target_value = True
                    if not isinstance(target_value, bool):
                        raise ValueError(
                            "Invalid target value for enabled condition: "
                            + f"{target_value}. Expected bool or null."
                        )
                    
                    return Parameter.EnabledCondition(
                        parameter,
                        target_value,
                    )
                case "opt" | "optional":
                    if "parameter" not in obj:
                        raise ValueError(
                            "Optional condition has no target parameter."
                        )
                    parameter_id = obj["parameter"]
                    if not isinstance(parameter_id, str):
                        raise ValueError(
                            "Invalid target parameter ID for optional "
                            + f"condition: {parameter_id}. Expected string."
                        )

                    parameter = id_to_parameter[parameter_id]
                    if not isinstance(parameter, OptionalParameter):
                        raise ValueError(
                            "Bool condition references non-optional parameter "
                            + f"{parameter_id}."
                        )

                    target_value = obj.get("value", True)
                    if target_value is None:
                        target_value = True
                    if not isinstance(target_value, bool):
                        raise ValueError(
                            "Invalid target value for optional condition: "
                            + f"{target_value}. Expected bool or null."
                        )

                    return OptionalParameter.Condition(
                        parameter,
                        target_value,
                    )
                case "bool":
                    if "parameter" not in obj:
                        raise ValueError(
                            "Bool condition has no target parameter."
                        )
                    parameter_id = obj["parameter"]
                    if not isinstance(parameter_id, str):
                        raise ValueError(
                            "Invalid target parameter ID for bool condition: "
                            + f"{parameter_id}. Expected string."
                        )

                    parameter = id_to_parameter[parameter_id]
                    if not isinstance(parameter, BoolParameter):
                        raise ValueError(
                            "Bool condition references non-bool parameter "
                            + f"{parameter_id}."
                        )

                    target_value = obj.get("value", True)
                    if target_value is None:
                        target_value = True
                    if not isinstance(target_value, bool):
                        raise ValueError(
                            "Invalid target value for bool condition: "
                            + f"{target_value}. Expected bool or null."
                        )

                    return BoolParameter.Condition(
                        parameter,
                        target_value,
                    )
                case "enum":
                    if "parameter" not in obj:
                        raise ValueError("Enum condition has no target parameter.")
                    parameter_id = obj["parameter"]
                    parameter = id_to_parameter[parameter_id]
                    if not isinstance(parameter, EnumParameter):
                        raise ValueError("Enum condition is referencing a non-enum parameter.")

                    if "values" not in obj:
                        raise ValueError("Enum condition has no list of target values.")
                    target_values = obj["values"]
                    if not isinstance(target_values, list):
                        raise ValueError(
                            "Invalid target value list for enum condition: "
                            + f"{target_values}. Expected a list of ints."
                        )
                    for target_value in target_values:
                        if not isinstance(target_value, int):
                            raise ValueError(
                                f"Invalid target value for enum condition: "
                                + f"{target_value}. Expected int."
                            )

                    return EnumParameter.Condition(
                        parameter,
                        target_values,
                    )
                case _:
                    raise ValueError(f"Invalid condition type '{condition_type}'.")

        with open(file_path) as f:
            config_text = f.read()

        config_obj = load(config_text, Loader=Loader)

        operations = {}
        if "modes" not in config_obj:
            raise ValueError("Configuration file contains no list of modes.")
        mode_list = config_obj["modes"]
        if not isinstance(mode_list, list):
            raise ValueError(
                f"Invalid mode list: {mode_list}. Expected a list."
            )
        for mode_obj in mode_list:
            if not isinstance(mode_obj, dict):
                raise ValueError(f"Invalid mode: {mode_obj}. Expected object.")
            if "operations" not in mode_obj:
                raise ValueError(f"Mode has no operation list.")
            operations_obj = mode_obj["operations"]
            if not isinstance(operations_obj, dict):
                raise ValueError(
                    f"Invalid operations dictionary: {operations_obj}. "
                    + "Expected an object."
                )
            for operation_id in operations_obj:
                operation_obj = operations_obj[operation_id]
                if not isinstance(operation_obj, dict):
                    raise ValueError(
                        f"Invalid operation: {operation_obj}"
                        + "Expected an object."
                    )
                operations[operation_id] = parse_operation(operation_obj, operation_id)

        if "run_id_parameter" not in config_obj:
            raise ValueError(
                "Run ID parameter missing from configuration file!"
            )
        run_id_parameter_obj = config_obj["run_id_parameter"]
        if not isinstance(run_id_parameter_obj, dict):
            raise ValueError(
                "Invalid value for run ID parameter: "
                + f"{run_id_parameter_obj}. Expected object."
            )
        run_id_parameter = parse_parameter(
            run_id_parameter_obj,
            # Assign the run ID parameter to all operations so it is
            # always present.
            set(operations.keys()),
        )
        if not isinstance(run_id_parameter, StringParameter):
            raise ValueError(
                f"Invalid run ID parameter: {run_id_parameter}. "
                + "Expected string parameter."
            )

        parameter_groups = []
        for parameter_group_obj in config_obj["parameter_groups"]:
            parameter_groups.append(parse_parameter_group(parameter_group_obj))

        operation_trees, operation_conditions = OperationTree.build_trees(operations)

        result = cls(run_id_parameter, operation_trees, parameter_groups)

        parameter_conditions: dict[Parameter[Any], list[Dependency.Condition]] = {}

        for param in id_to_parameter.values():
            parameter_conditions[param] = []
            for condition_obj in parameter_to_condition_objs[param]:
                parameter_conditions[param].append(
                    parse_condition(condition_obj)
                )

            single_operation_conditions = []
            for operation_id in param.operations:
                single_operation_conditions.append(
                    operation_conditions[operation_id]
                )
            parameter_conditions[param].append(
                OrCondition(single_operation_conditions)
            )

            Dependency(
                AndCondition(parameter_conditions[param]),
                Parameter.EnabledEffect(param),
                result,
            )

        return result

    @property
    def run_id_parameter(self) -> StringParameter:
        return self._run_id_parameter

    @property
    def run_id(self) -> str:
        return self.run_id_parameter.value

    @run_id.setter
    def run_id(self, new_run_id: str) -> None:
        self.run_id_valid_changed.emit(self.run_id_valid)
        if self.run_id_parameter.value == new_run_id:
            return # Nothing actually changed
        self.run_id_parameter.value = new_run_id
        for operation_tree in self.operation_trees:
            operation_tree.run_id = new_run_id

    @property
    def run_id_valid(self) -> bool:
        return self.run_id_parameter.valid

    @property
    def operation_trees(self) -> list[OperationTree]:
        return self._operation_trees

    @property
    def selected_operation_tree(self) -> OperationTree:
        return self.operation_trees[self.selected_operation_tree_index]

    @property
    def selected_operation_tree_index(self) -> int:
        return self._selected_operation_tree_index

    @selected_operation_tree_index.setter
    def selected_operation_tree_index(self, new_index: int) -> None:
        self.selected_operation_tree.enabled = False
        self._selected_operation_tree_index = new_index
        self.selected_operation_tree.enabled = True
        self.operations_valid_changed.emit(self.operations_valid)

    @property
    def operations_valid(self) -> bool:
        return self.selected_operation_tree.valid

    @property
    def parameter_groups(self) -> list[ParameterGroup]:
        """
        The list of groups in the parameter list.
        """
        return self._parameter_groups

    @property
    def parameters(self) -> list[Parameter]:
        result = [self.run_id_parameter]
        for parameter_group in self:
            result.extend(parameter_group)
        return result

    @property
    def valid(self) -> bool:
        """
        Whether the current parameter values are valid.

        The list is valid if and only if every group is valid.
        """
        return all(
            [self._run_id_parameter.valid]
            + [group.valid for group in self]
        )

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

        return self.selected_operation_tree.to_cli(self.parameters)

    def __iter__(self) -> Iterator[ParameterGroup]:
        return iter(self.parameter_groups)

    def __getitem__(self, i) -> ParameterGroup:
        return self.parameter_groups[i]

    @Slot(str, bool)
    def _run_id_parameter_value_changed(
        self,
        new_run_id: str,
        new_valid: bool,
    ) -> None:
        self.run_id = new_run_id

    @Slot(bool)
    def _operation_tree_valid_changed(self, new_valid: bool) -> None:
        self.operations_valid_changed.emit(self.operations_valid)
