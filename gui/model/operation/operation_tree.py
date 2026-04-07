"""
A module for representing operation trees.

RAiSD-AI operations, needing one or more input files which can be
obtained from the output of other operations, are hierarchical in
nature. The `OperationTree` class represents such an operation hierarchy
with a specified operation as the root.

The recommended way to construct operation trees is using the
`OperationTree#build_trees` factory method.
"""

from typing import Any, Mapping

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    QFileInfo,
    QDir,
)

from .file_structure import (
    FileStructure,
    SingleFile,
    Directory,
)
from .operation import Operation
from gui.model.parameter import (
    Parameter,
    StringParameter,
)
from gui.model.dependency import (
    Dependency,
    OrCondition,
)


class FileProducerNode(QObject):
    """
    An abstract class for nodes that can produce a file.
    """

    file_changed = Signal(str)
    valid_changed = Signal(bool)

    @property
    def produces(self) -> FileStructure:
        """
        The type of file this node produces.
        """
        raise NotImplementedError()

    @property
    def file(self) -> str | None:
        """
        The path to the file produced by this node, if available.
        """
        raise NotImplementedError()

    @property
    def valid(self) -> bool:
        """
        Whether the node is in a valid state.
        """
        raise NotImplementedError()

    def _set_run_id(self, new_run_id: str) -> None:
        raise NotImplementedError()

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str) -> None:
        raise NotImplementedError()
    
    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether the node is enabled.

        This property is used in generating commands.
        """
        raise NotImplementedError()

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        raise NotImplementedError()

    def reset(self) -> None:
        raise NotImplementedError()

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: list[Parameter],
    ) -> list[str]:
        """
        Get the terminal commands needed to produce the file.

        :param parameters: the parameters to use in the commands
        :type parameters: list[Parameter]

        :return: the (possibly empty) list of commands
        :rtype: list[str]
        """
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()

    def populate_from_dict(self, values: dict) -> None:
        raise NotImplementedError()


class FileConsumerNode(QObject):
    """
    A node representing an input file required by another node.

    A file consumer node has a list of `FileProducerNode` children that
    produce the required file type, allowing the user to choose between 
    them.
    """

    selected_index_changed = Signal(int)
    valid_changed = Signal(bool)

    def __init__(
            self,
            requires: FileStructure,
            label: str,
            cli: str,
            enabled: bool = False
    ) -> None:
        """
        Initialize a `FileConsumerNode` object.

        :param requires: the required file type
        :type requires: FileStructure

        :param label: what the required file represents, for the user
        :type label: str

        :param cli: the command-line option for this input file
        :type cli: str

        :param enabled: whether the node is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._requires = requires
        self._producers = []
        self._selected_index = 0
        self._label = label
        self._cli = cli
        self._enabled = enabled

    @property
    def requires(self) -> FileStructure:
        """
        The file type the node requires.
        """
        return self._requires

    def add_producer(self, producer: FileProducerNode) -> None:
        """
        Add a `FileProducerNode` as a child of this node.

        :param producer: the child node
        :type producer: FileProducerNode
        """
        self._producers.append(producer)
        producer.valid_changed.connect(self._producer_valid_changed)

    @property
    def producers(self) -> list[FileProducerNode]:
        """
        The list of `FileProducerNode` children.
        """
        return self._producers

    @property
    def label(self) -> str:
        """
        The label to display to the user, explaining what the required
        input file represents.
        """
        return self._label

    @property
    def cli_parameter(self) -> str:
        """
        The representation of this file as a command-line argument.
        """
        return f"{self._cli}{self.file}"

    @property
    def selected_index(self) -> int:
        """
        The index of the currently selected child node. Setting this
        enables the corresponding child node and disables the previous
        one, if this node is enabled.
        """
        return self._selected_index

    @selected_index.setter
    def selected_index(self, new_selected_index: int) -> None:
        self.selected_producer.enabled = False
        self._selected_index = new_selected_index
        self.selected_index_changed.emit(new_selected_index)
        self.selected_producer.enabled = self.enabled
        self.valid_changed.emit(self.valid)

    @property
    def selected_producer(self) -> FileProducerNode:
        """
        The currently selected child node.
        """
        return self.producers[self.selected_index]

    def _set_run_id(self, new_run_id: str):
        for producer in self.producers:
            producer.run_id = new_run_id

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str):
        for producer in self.producers:
            producer.base_directory_path = new_base_directory_path

    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether this node is currently enabled. Setting this sets the
        enabled status of the selected child node to the same value.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        self._enabled = new_enabled
        self.selected_producer.enabled = self.enabled

    @property
    def file(self) -> str | None:
        """
        The path to the file produced by the currently selected child 
        node, if available.
        """
        return self.selected_producer.file

    @property
    def valid(self) -> bool:
        """
        Whether this node is in a valid state.
        """
        return self.selected_producer.valid
    
    def reset(self) -> None:
        self.selected_index = 0
        for producer in self.producers:
            producer.reset()

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: list[Parameter],
    ) -> list[str]:
        """
        Get the terminal commands needed to produce the file.

        :param parameters: the parameters to use in the commands
        :type parameters: list[Parameter]

        :return: the (possibly empty) list of commands
        :rtype: list[str]
        """
        return self.selected_producer.to_cli(run_id_parameter, parameters)

    def to_dict(self) -> dict:
        return {
            "selected": self.selected_index,
            "file_producers": [
                producer.to_dict() for producer in self.producers
            ]
        }

    def populate_from_dict(self, values: dict) -> None:
        if "selected" not in values:
            raise ValueError("Missing 'selected' in dict.")
        selected_index = values["selected"]
        if not isinstance(selected_index, int):
            raise ValueError(
                f"Invalid 'selected' in dict: {selected_index}. Expected int."
            )
        self.selected_index = selected_index
        
        if "file_producers" not in values:
            raise ValueError("Missing 'file_producers' in dict.")
        file_producer_values_list = values["file_producers"]
        if not isinstance(file_producer_values_list, list):
            raise ValueError(
                "Invalid 'file_producers' in dict: "
                + f"{file_producer_values_list}. Expected a list."
            )
        if len(file_producer_values_list) != len(self.producers):
            raise ValueError("Mismatch in 'file_producers' length.")
        for i, file_producer_values in enumerate(file_producer_values_list):
            if not isinstance(file_producer_values, dict):
                raise ValueError(
                    f"Invalid item in 'file_producers': {file_producer_values}"
                    + ". Expected an object."
                )
            self.producers[i].populate_from_dict(file_producer_values)
            

    @Slot(bool)
    def _producer_valid_changed(self, new_valid: bool) -> None:
        self.valid_changed.emit(self.valid)


class CommonParentDirectoryNode(FileProducerNode):
    """
    A node which produces a directory of files by producing each file
    individually.

    Implements `FileProducerNode`.
    """

    def __init__(
            self,
            produces: Directory,
            enabled: bool = False,
    ) -> None:
        """
        Initialize a `CommonParentDirectoryNode` object.

        The `produces` argument describes the contents of the directory
        this node must produce. For each item in the directory, a child
        `FileConsumerNode` will be instantiated with no label or
        command-line representation.

        :param produces: the file structure to be produced
        :type produces: Directory

        :param enabled: whether the node is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._produces = produces
        self._file_consumers = []
        for file_structure in self._produces.contents:
            file_consumer = FileConsumerNode(
                file_structure,
                "",
                "",
            )
            self._file_consumers.append(file_consumer)
            file_consumer.valid_changed.connect(self._consumer_valid_changed)
        self._enabled = enabled

    @property
    def produces(self) -> Directory:
        """
        The file structure this node produces.
        """
        return self._produces

    @property
    def file_consumers(self) -> list[FileConsumerNode]:
        """
        The list of child `FileConsumerNode`s.
        """
        return self._file_consumers

    @property
    def file(self) -> str | None:
        """
        The path to the directory produced by this node's children, if
        available.
        """
        parent_directory_paths: set[str] = set()
        for consumer in self.file_consumers:
            if consumer.file is None:
                return None
            parent_directory_paths.add(
                QFileInfo(consumer.file).dir().absolutePath()
            )
        if len(parent_directory_paths) == 1:
            return list(parent_directory_paths)[0]
        return None

    def _set_run_id(self, new_run_id: str) -> None:
        for file_consumer in self.file_consumers:
            file_consumer.run_id = new_run_id
        self.file_changed.emit(self.file)

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str) -> None:
        for file_consumer in self.file_consumers:
            file_consumer.base_directory_path = new_base_directory_path
        self.file_changed.emit(self.file)

    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether this node is enabled. Setting this property sets the
        enabled state of each child node to the same value.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled) -> None:
        self._enabled = new_enabled
        for file_consumer in self.file_consumers:
            file_consumer.enabled = self.enabled

    @property
    def valid(self) -> bool:
        """
        Whether the node is in a valid state.

        A `CommonParentDirectoryNode` is valid if each of its children
        is valid, and they all produce output in the same directory.
        """
        # TODO: hide the node if its children don't have the same output
        # location
        if not all(consumer.valid for consumer in self.file_consumers):
            return False

        return self.file is not None

    def reset(self) -> None:
        for consumer in self.file_consumers:
            consumer.reset()

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: list[Parameter],
    ) -> list[str]:
        """
        Get the terminal commands needed to produce the directory.

        :param parameters: the parameters to use in the commands
        :type parameters: list[Parameter]

        :return: the (possibly empty) list of commands
        :rtype: list[str]
        """
        commands = []
        for consumer in self.file_consumers:
            commands.extend(consumer.to_cli(run_id_parameter, parameters))
        return commands

    def to_dict(self) -> dict:
        return {
            "file_consumers": [
                consumer.to_dict() for consumer in self.file_consumers
            ]
        }

    def populate_from_dict(self, values: dict) -> None:
        if "file_consumers" not in values:
            raise ValueError("Missing 'file_consumers' key in dict.")
        file_consumer_values_list = values["file_consumers"]
        if not isinstance(file_consumer_values_list, list):
            raise ValueError(
                f"Wrong 'file_consumers': {file_consumer_values_list}. "
                + "Expected a list."
            )
        if len(file_consumer_values_list) != len(self.file_consumers):
            raise ValueError(
                "Mismatched length of 'file_consumers'."
            )
        for i, file_consumer_values in enumerate(file_consumer_values_list):
            if not isinstance(file_consumer_values, dict):
                raise ValueError(
                    f"Wrong item in 'file_consumers': {file_consumer_values}. "
                    + "Expected a dict."
                )
            self.file_consumers[i].populate_from_dict(file_consumer_values)

    @Slot(bool)
    def _consumer_valid_changed(self, new_valid: bool) -> None:
        self.valid_changed.emit(self.valid)


class FilePickerNode(FileProducerNode):
    """
    A node which allows the user to select an existing file.

    Implements `FileProducerNode`.
    """

    def __init__(
            self,
            produces: FileStructure,
            enabled: bool = False,
    ) -> None:
        """
        Initialize a `FilePickerNode` object.

        :param produces: the file type the user should choose
        :type produces: FileStructure

        :param enabled: whether the node is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._produces = produces
        self._file: str | None = None
        self._enabled = enabled

    @property
    def produces(self) -> FileStructure:
        """
        The type of file the user is expected to choose.
        """
        return self._produces

    @property
    def file(self) -> str | None:
        """
        The path to the file chosen by the user, if they have done so.
        """
        return self._file

    @file.setter
    def file(self, new_file: str | None) -> None:
        self._file = new_file
        self.file_changed.emit(self._file)
        self.valid_changed.emit(self.valid)

    def _set_run_id(self, new_run_id: str) -> None:
        pass

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str) -> None:
        pass

    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether the node is enabled.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled) -> None:
        self._enabled = new_enabled

    @property
    def valid(self) -> bool:
        """
        Whether the user has chosen a file matching the required type.
        """
        if self.file is None:
            return False
        return self.produces.matches(self.file)

    def reset(self) -> None:
        self.file = None

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: list[Parameter],
    ) -> list[str]:
        """
        Get the terminal commands needed to produce the file.

        Note: this method always returns an empty list.

        :param parameters: the parameters to use in the commands
        :type parameters: list[Parameter]

        :return: the empty list of commands
        :rtype: list[str]
        """
        return []

    def to_dict(self) -> dict:
        return {
            "file_path": self.file
        }

    def populate_from_dict(self, values: dict) -> None:
        if "file_path" not in values:
            raise ValueError("Missing file path in dict.")
        file_path = values["file_path"]
        if file_path is not None and not isinstance(file_path, str):
            raise ValueError(
                f"Invalid file path in dict: {file_path}. Expected a string "
                + "or null."
            )
        self.file = file_path


class OperationNode(FileProducerNode):
    """
    A node which allows the user to run an operation.

    Implements `FileProducerNode` by producing the output file of
    the operation.
    """

    class PathFragmentGenerator:
        @classmethod
        def from_path_fragment(
            cls,
            path_fragment: Operation.PathFragment,
            operation_node: "OperationNode",
        ) -> "OperationNode.PathFragmentGenerator":
            if isinstance(path_fragment, Operation.ConstPathFragment):
                return OperationNode.ConstPathFragmentGenerator(
                    value=path_fragment.value,
                )
            if isinstance(path_fragment, Operation.RunIdPathFragment):
                return OperationNode.RunIdPathFragmentGenerator(
                    operation_node=operation_node,
                )
            if isinstance(path_fragment, Operation.SlashPathFragment):
                return OperationNode.SlashPathFragmentGenerator()
            if isinstance(path_fragment, Operation.ParameterValuePathFragment):
                return OperationNode.ParameterValuePathFragmentGenerator(
                    parameter=operation_node.parameters[
                        path_fragment.parameter_id
                    ]
                )
            raise NotImplementedError("Unknown path fragment type!")

        @property
        def value(self) -> str:
            raise NotImplementedError()

    class ConstPathFragmentGenerator(PathFragmentGenerator):
        def __init__(
                self,
                value: str,
        ) -> None:
            self._value = value

        @property
        def value(self) -> str:
            return self._value

    class RunIdPathFragmentGenerator(PathFragmentGenerator):
        def __init__(
                self,
                operation_node: "OperationNode",
        ) -> None:
            self._operation_node = operation_node

        @property
        def value(self) -> str:
            return self._operation_node.run_id

    class SlashPathFragmentGenerator(PathFragmentGenerator):
        @property
        def value(self) -> str:
            return "/"

    class ParameterValuePathFragmentGenerator(PathFragmentGenerator):
        def __init__(
                self,
                parameter: Parameter[Any],
        ) -> None:
            self._parameter = parameter

        @property
        def value(self) -> str:
            return str(self._parameter.value)

    class EnabledCondition(Dependency.Condition):
        """
        A condition that tracks whether an operation node is enabled.
        """

        def __init__(
                self,
                operation_node: "OperationNode",
                target_value: bool = True,
                parent: QObject | None = None,
        ) -> None:
            """
            Initialize an `OperationNode.EnabledCondition` object.

            :param operation_node: the operation node to track
            :type operation_node: "OperationNode"

            :param target_value: the target value
            :type target_value: bool

            :param parent: the parent of this `QObject`
            :type parent: QObject | None
            """
            super().__init__(
                value=operation_node.enabled==target_value,
                parent=parent,
            )
            self._operation_node = operation_node
            self._target_value = target_value

            self._operation_node.enabled_changed.connect(self._enabled_changed)

        @Slot(bool)
        def _enabled_changed(self, new_enabled: bool):
            self.value = new_enabled==self._target_value

    enabled_changed = Signal(bool)

    def __init__(self,
        operation: Operation,
        run_id: str = "",
        base_directory_path: str = "",
        enabled: bool = False,
    ) -> None:
        """
        Initialize an `OperationNode` object.

        For each required file of `operation`, a child
        `FileConsumerNode` is initialized with its details. A
        `FilePickerNode` is added by default.

        :param operation: the operation this node represents
        :type operation: Operation

        :param enabled: whether the node is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._id = operation.id
        self._name = operation.name
        self._description = operation.description
        self._cli = operation.cli
        self._produces = operation.produces
        self._file_consumers = []
        for file_name, cli, file_structure in operation.requires:
            file_consumer = FileConsumerNode(
                file_structure,
                file_name,
                cli,
            )
            file_picker = FilePickerNode(file_structure)
            file_consumer.add_producer(file_picker)
            self._file_consumers.append(file_consumer)
            file_consumer.valid_changed.connect(self._consumer_valid_changed)
        self._overwrite_parameter = operation.overwrite_parameter_builder()
        self._parameters = {}
        for parameter_id in operation.parameter_builders:
            parameter_builder = operation.parameter_builders[parameter_id]
            parameter = parameter_builder()
            self._parameters[parameter_id] = parameter
            # TODO: consider if there is a way to only connect the
            # used parameters
            parameter.value_changed.connect(self._parameter_value_changed)
        self._output_path = [
            OperationNode.PathFragmentGenerator.from_path_fragment(
                path_fragment=path_fragment,
                operation_node=self,
            )
            for path_fragment in operation.output_path
        ]
        self._run_id = run_id
        self._base_directory_path = base_directory_path
        self._enabled = enabled

    @property
    def id(self) -> str:
        """
        The string identifier of the operation.
        """
        return self._id

    @property
    def name(self) -> str:
        """
        The name of the operation.
        """
        return self._name

    @property
    def description(self) -> str:
        """
        The description of the operation.
        """
        return self._description

    @property
    def produces(self) -> FileStructure:
        """
        The type of file produced by the operation.
        """
        return self._produces

    @property
    def parameters(self) -> dict[str, Parameter[Any]]:
        return self._parameters

    @property
    def file_consumers(self) -> list[FileConsumerNode]:
        """
        The list of `FileConsumerNode` children.
        """
        return self._file_consumers

    @property
    def run_id(self) -> str:
        """
        The run ID stored in this node.
        """
        return self._run_id

    @run_id.setter
    def run_id(self, new_run_id: str) -> None:
        self._run_id = f"{new_run_id}_{self.id}"
        for file_consumer in self.file_consumers:
            file_consumer.run_id = self.run_id
        self.file_changed.emit(self.file)

    @property
    def base_directory_path(self) -> str:
        return self._base_directory_path
    
    @base_directory_path.setter
    def base_directory_path(self, new_base_directory_path: str) -> None:
        self._base_directory_path = new_base_directory_path
        for file_consumer in self.file_consumers:
            file_consumer.base_directory_path = self.base_directory_path
        self.file_changed.emit(self.file)

    @property
    def enabled(self) -> bool:
        """
        Whether the node is enabled. Setting this property sets the
        enabled status of each child node to the same value.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled: bool):
        self._enabled = new_enabled
        for file_consumer in self.file_consumers:
            file_consumer.enabled = self.enabled
        self.enabled_changed.emit(self.enabled)

    @property
    def file(self) -> str:
        """
        The path to the output file of the operation.
        """
        return QDir(self.base_directory_path).absoluteFilePath(
            "".join(generator.value for generator in self._output_path)
        )

    @property
    def valid(self) -> bool:
        """
        Whether the operation's inputs are in a valid state.
        """
        return all(
            [self._overwrite_parameter.valid] # TODO: implement this
            + [parameter.valid for parameter in self.parameters.values()]
            + [consumer.valid for consumer in self._file_consumers]
        )
    
    def reset(self) -> None:
        for consumer in self.file_consumers:
            consumer.reset()
        for parameter in self.parameters.values():
            parameter.reset_value()

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: list[Parameter],
    ) -> list[str]:
        """
        Get the terminal commands needed to produce the operation's
        input files, then run the operation.

        The command lists of each child node are concatenated, then this
        node's own command is appended to the list.

        :param parameters: the parameters to use in the commands
        :type parameters: list[Parameter]

        :return: the list of commands
        :rtype: list[str]
        """
        commands = []
        own_command_pieces = [self._cli]

        for file_consumer in self.file_consumers:
            commands.extend(file_consumer.to_cli(run_id_parameter, parameters))
            own_command_pieces.append(file_consumer.cli_parameter)

        own_command_pieces.append(
            run_id_parameter.to_cli(self.id, self.run_id)
        )

        own_command_pieces.append(self._overwrite_parameter.to_cli(self.id))

        for parameter in self.parameters.values():
            own_command_pieces.append(parameter.to_cli(self.id))

        for parameter in parameters:
            own_command_pieces.append(parameter.to_cli(self.id))

        own_command_pieces = [piece for piece in own_command_pieces if piece]
        own_command = " ".join(own_command_pieces)
        commands.append(own_command)

        return commands

    def to_dict(self) -> dict:
        return {
            "file_consumers": [
                consumer.to_dict() for consumer in self.file_consumers
            ]
        }

    def populate_from_dict(self, values: dict) -> None:
        if "file_consumers" not in values:
            raise ValueError("Missing 'file_consumers' key in dict.")
        file_consumer_values_list = values["file_consumers"]
        if not isinstance(file_consumer_values_list, list):
            raise ValueError(
                f"Wrong 'file_consumers': {file_consumer_values_list}. "
                + "Expected a list."
            )
        if len(file_consumer_values_list) != len(self.file_consumers):
            raise ValueError(
                "Mismatched length of 'file_consumers'."
            )
        for i, file_consumer_values in enumerate(file_consumer_values_list):
            if not isinstance(file_consumer_values, dict):
                raise ValueError(
                    f"Wrong item in 'file_consumers': {file_consumer_values}. "
                    + "Expected a dict."
                )
            self.file_consumers[i].populate_from_dict(file_consumer_values)

    @Slot(bool)
    def _consumer_valid_changed(self, new_valid: bool) -> None:
        self.valid_changed.emit(self.valid)

    @Slot()
    def _parameter_value_changed(self) -> None:
        self.file_changed.emit(self.file)
        self.valid_changed.emit(self.valid)


class OperationTree(QObject):
    """
    An operation tree.

    An `OperationTree` object holds a reference to an `OperationNode` as
    its root.

    The recommended way of creating operation trees is through the
    `build_trees` factory method.
    """

    valid_changed = Signal(bool)

    def __init__(
            self,
            root: OperationNode,
            enabled: bool = False,
    ) -> None:
        """
        Initialize an `OperationTree` object.

        :param root: the operation node at the root of the tree
        :type root: OperationNode

        :param enabled: whether the tree is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._root = root
        self.root.enabled = enabled
        self.root.valid_changed.connect(self._root_valid_changed)

    @property
    def root(self) -> OperationNode:
        """
        The `OperationNode` at the root of the tree.
        """
        return self._root

    def _set_run_id(self, new_run_id: str) -> None:
        self.root.run_id = new_run_id

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str) -> None:
        self.root.base_directory_path = new_base_directory_path

    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether the tree is enabled. Setting this property sets the
        enabled status of the root node to the same value.
        """
        return self.root.enabled

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        self.root.enabled = new_enabled

    @property
    def valid(self) -> bool:
        return self.root.valid

    @classmethod
    def build_trees(
            cls,
            operations: dict[str, Operation],
            run_id: str = "",
            base_directory_path: str = "",
    ) -> tuple[list["OperationTree"], Mapping[str, Dependency.Condition]]:
        """
        For each operation in a given list, create an operation tree
        with that operation as the root.

        The trees are built by a breadth-first search algorithm. The
        root operation node is explored first. When an operation node is
        visited, the required file of each of its file consumer children
        is compared to the produced file of each operation. If a match
        is found, a node is constructed for that operation and added to
        the tree, as well as to the queue of unexplored operation nodes.

        While constructing the tree, the method creates an
        `OperationNode.EnabledCondition` for each operation node. At the
        end, the conditions for each operation are wrapped in an
        `OrCondition` and returned alongside the constructed trees. The
        conditions can be used to enable parameters when at least one
        instance of the operation they belong to is enabled.

        :param operations: a dictionary from ID to operation
        :type operations: dict[str, Operation]

        :param run_id: the initial run ID
        :type run_id: str

        :return: the list of operation trees and the mapping from
        operation ID to condition
        :rtype: tuple[list[OperationTree], Mapping[str, Condition]]
        """
        trees: list[OperationTree] = []
        # Initialize the dictionary from operation ID to list of
        # conditions for operation nodes with that operation.
        operation_id_to_conditions = {
            operation_id: [] for operation_id in operations
        }
        for root_operation_id in operations:
            root_operation = operations[root_operation_id]
            root_node = OperationNode(
                root_operation,
                run_id=run_id,
                base_directory_path=base_directory_path,
            )
            # Create an EnabledCondition for the root node.
            operation_id_to_conditions[root_operation_id].append(
                OperationNode.EnabledCondition(
                    root_node,
                )
            )

            # Create a queue of unexplored operation nodes for BFS.
            unexplored_nodes: list[OperationNode] = [root_node]
            while unexplored_nodes:
                current_node = unexplored_nodes[0]
                unexplored_nodes = unexplored_nodes[1:]

                for file_consumer in current_node.file_consumers:
                    for candidate_id in operations:
                        candidate_operation = operations[candidate_id]
                        if (candidate_operation.produces
                            == file_consumer.requires):
                            operation_node = OperationNode(
                                candidate_operation,
                                run_id=run_id,
                                base_directory_path=base_directory_path,
                            )
                            file_consumer.add_producer(operation_node)
                            unexplored_nodes.append(operation_node)
                            # Create an EnabledCondition for the node.
                            operation_id_to_conditions[candidate_id].append(
                                OperationNode.EnabledCondition(
                                    operation_node,
                                )
                            )
                    # If the consumer is expecting a directory, try
                    # producing that directory from multiple operations.
                    if (isinstance(file_consumer.requires, Directory)
                        and len(file_consumer.requires.contents) > 1):
                        common_parent_dir = CommonParentDirectoryNode(
                            file_consumer.requires,
                        )
                        # There might not be a suitable operation for
                        # every file in the directory, so keep additions
                        # to the queue and dictionary separate for now.
                        possible_unexplored = []
                        possible_conditions = {
                            operation_id: [] for operation_id in operations
                        }
                        operations_exist: bool = True
                        for sub_consumer in common_parent_dir.file_consumers:
                            operation_exists: bool = False
                            for candidate_id in operations:
                                candidate_operation = operations[candidate_id]
                                if (candidate_operation.produces
                                    == sub_consumer.requires):
                                    operation_exists = True
                                    operation_node = OperationNode(
                                        candidate_operation,
                                        run_id=run_id,
                                        base_directory_path=base_directory_path,
                                    )
                                    possible_conditions[candidate_id].append(
                                        OperationNode.EnabledCondition(
                                            operation_node,
                                        )
                                    )
                                    sub_consumer.add_producer(operation_node)
                                    possible_unexplored.append(operation_node)
                            if not operation_exists:
                                operations_exist = False
                                break
                        # If an operation has been found for every file,
                        # add the node to the tree and extend the queue
                        # and condition dictionary.
                        if operations_exist:
                            file_consumer.add_producer(common_parent_dir)
                            unexplored_nodes.extend(possible_unexplored)
                            for operation_id in operations:
                                operation_id_to_conditions[operation_id]\
                                    .extend(possible_conditions[operation_id])

            tree = OperationTree(root_node)
            trees.append(tree)

        # For every operation, take the conditions on its corresponding
        # nodes and wrap them in an OrCondition.
        operation_id_to_condition = {
            operation_id: OrCondition(
                operation_id_to_conditions[operation_id]
            )
            for operation_id in operations
        }

        return trees, operation_id_to_condition

    def reset(self) -> None:
        self.root.reset()

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: list[Parameter],
    ) -> list[str]:
        """
        Get the terminal commands generated by the tree's root node.

        :param parameters: the parameters to use in the commands
        :type parameters: list[Parameter]

        :return: the list of commands
        :rtype: list[str]
        """
        return self.root.to_cli(run_id_parameter, parameters)

    def to_dict(self) -> dict:
        return self.root.to_dict()

    def populate_from_dict(self, values: dict) -> None:
        self.root.populate_from_dict(values)

    @Slot(bool)
    def _root_valid_changed(self, new_valid: bool) -> None:
        self.valid_changed.emit(self.valid)
