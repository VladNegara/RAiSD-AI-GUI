from typing import Mapping, Protocol

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
from gui.model.parameter import (
    Parameter,
)
from gui.model.dependency import (
    Dependency,
    OrCondition,
)


class FileProducerNode(Protocol):
    @property
    def produces(self) -> FileStructure:
        ...

    @property
    def file(self) -> str | None:
        ...

    @property
    def valid(self) -> bool:
        ...

    @property
    def enabled(self) -> bool:
        ...

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        ...

    def to_cli(self, parameters: list[Parameter]) -> list[str]:
        ...


class FileConsumerNode():
    def __init__(
            self,
            requires: FileStructure,
            label: str,
            cli: str,
            enabled: bool = False
    ) -> None:
        self._requires = requires
        self._producers = []
        self._selected_index = 0
        self._label = label
        self._cli = cli
        self._enabled = enabled

    @property
    def requires(self) -> FileStructure:
        return self._requires

    def add_producer(self, producer: FileProducerNode) -> None:
        self._producers.append(producer)

    @property
    def producers(self) -> list[FileProducerNode]:
        return self._producers

    @property
    def label(self) -> str:
        return self._label

    @property
    def cli_parameter(self) -> str:
        return f"{self._cli} {self.file}"

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @selected_index.setter
    def selected_index(self, new_selected_index: int) -> None:
        self.selected_producer.enabled = False
        self._selected_index = new_selected_index
        self.selected_producer.enabled = self.enabled

    @property
    def selected_producer(self) -> FileProducerNode:
        return self.producers[self.selected_index]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        self._enabled = new_enabled
        self.selected_producer.enabled = self.enabled

    @property
    def file(self) -> str | None:
        return self.selected_producer.file

    @property
    def valid(self) -> bool:
        return self.selected_producer.valid
    
    def to_cli(self, parameters: list[Parameter]) -> list[str]:
        return self.selected_producer.to_cli(parameters)


class CommonParentDirectoryNode():
    def __init__(
            self,
            produces: Directory,
            enabled: bool = False,
    ) -> None:
        self._produces = produces
        self._file_consumers = []
        for file_structure in self._produces.contents:
            file_consumer = FileConsumerNode(
                Directory([file_structure]),
                "Output inside common parent directory",
                "",
            )
            self._file_consumers.append(file_consumer)
        self._enabled = enabled

    @property
    def produces(self) -> FileStructure:
        return self._produces

    @property
    def file_consumers(self) -> list[FileConsumerNode]:
        return self._file_consumers

    @property
    def file(self) -> str | None:
        return self.file_consumers[0].file

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled) -> None:
        self._enabled = new_enabled
        for file_consumer in self.file_consumers:
            file_consumer.enabled = self.enabled

    @property
    def valid(self) -> bool:
        if not all(consumer.valid for consumer in self.file_consumers):
            return False

        # All child nodes must produce files with the same parent directory
        return len(set(consumer.file for consumer in self.file_consumers)) == 1

    def to_cli(self, parameters: list[Parameter]) -> list[str]:
        commands = []
        for consumer in self.file_consumers:
            commands.extend(consumer.to_cli(parameters))
        return commands


class FilePickerNode(QObject):
    file_changed = Signal(str)

    def __init__(
            self,
            produces: FileStructure,
            enabled: bool = False,
    ) -> None:
        super().__init__()
        self._produces = produces
        self._file: str | None = None
        self._enabled = enabled

    @property
    def produces(self) -> FileStructure:
        return self._produces

    @property
    def file(self) -> str | None:
        return self._file

    @file.setter
    def file(self, new_file: str | None) -> None:
        self._file = new_file
        self.file_changed.emit(self._file)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled) -> None:
        self._enabled = new_enabled

    @property
    def valid(self) -> bool:
        if self.file is None:
            return False
        return self.produces.matches(self.file)

    def to_cli(self, parameters: list[Parameter]) -> list[str]:
        return []


class OperationNode(QObject):
    class EnabledCondition(Dependency.Condition):
        def __init__(
                self,
                operation_node: "OperationNode",
                target_value: bool = True,
                parent: QObject | None = None,
        ) -> None:
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
        enabled: bool = False,
    ) -> None:
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
        self._enabled = enabled

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def produces(self) -> FileStructure:
        return self._produces

    @property
    def file_consumers(self) -> list[FileConsumerNode]:
        return self._file_consumers

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled: bool):
        self._enabled = new_enabled
        for file_consumer in self.file_consumers:
            file_consumer.enabled = self.enabled
        self.enabled_changed.emit(self.enabled)

    @property
    def file(self) -> str | None:
        return "RAiSD_Images.runID"

    @property
    def valid(self) -> bool:
        return all([consumer.valid for consumer in self._file_consumers])

    def to_cli(self, parameters: list[Parameter]) -> list[str]:
        commands = []
        own_command_pieces = ["./RAiSD-AI", self._cli]

        for file_consumer in self.file_consumers:
            commands.extend(file_consumer.to_cli(parameters))
            own_command_pieces.append(file_consumer.cli_parameter)

        for parameter in parameters:
            own_command_pieces.append(parameter.to_cli(self.id))

        own_command_pieces = [piece for piece in own_command_pieces if piece]
        own_command = " ".join(own_command_pieces)
        commands.append(own_command)

        return commands


class OperationTree(QObject):
    def __init__(
            self,
            root: OperationNode,
            enabled: bool = False,
    ) -> None:
        self._root = root
        self.root.enabled = enabled

    @property
    def root(self) -> OperationNode:
        return self._root

    @property
    def enabled(self) -> bool:
        return self.root.enabled

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        self.root.enabled = new_enabled

    @classmethod
    def build_trees(
            cls,
            operations: dict[str, Operation],
    ) -> tuple[list["OperationTree"], Mapping[str, Dependency.Condition]]:
        trees: list[OperationTree] = []
        operation_id_to_all_conditions = {operation_id: [] for operation_id in operations}
        for root_operation_id, root_operation in operations.items():
            root_node = OperationNode(root_operation)
            operation_id_to_all_conditions[root_operation_id].append(
                OperationNode.EnabledCondition(
                    root_node,
                )
            )
            unexplored_nodes: list[OperationNode] = [root_node]
            while unexplored_nodes:
                current_node = unexplored_nodes[0]
                unexplored_nodes = unexplored_nodes[1:]

                for file_consumer in current_node.file_consumers:
                    for candidate_operation_id, candidate_operation in operations.items():
                        if candidate_operation.produces == file_consumer.requires:
                            operation_node = OperationNode(candidate_operation)
                            operation_id_to_all_conditions[candidate_operation_id].append(
                                OperationNode.EnabledCondition(
                                    operation_node,
                                )
                            )
                            file_consumer.add_producer(operation_node)
                            unexplored_nodes.append(operation_node)
                    # If the consumer is expecting a directory, try
                    # producing that directory from multiple operations.
                    if isinstance(file_consumer.requires, Directory):
                        common_parent_dir = CommonParentDirectoryNode(file_consumer.requires)
                        possible_unexplored = []
                        possible_conditions = {operation_id: [] for operation_id in operations}
                        operations_exist: bool = True
                        for sub_consumer in common_parent_dir.file_consumers:
                            operation_exists: bool = False
                            for candidate_operation_id, candidate_operation in operations.items():
                                if candidate_operation.produces == sub_consumer.requires:
                                    operation_exists = True
                                    operation_node = OperationNode(candidate_operation)
                                    possible_conditions[candidate_operation_id].append(
                                        OperationNode.EnabledCondition(
                                            operation_node,
                                        )
                                    )
                                    sub_consumer.add_producer(operation_node)
                                    possible_unexplored.append(operation_node)
                            if not operation_exists:
                                operations_exist = False
                                break
                        if operations_exist:
                            file_consumer.add_producer(common_parent_dir)
                            unexplored_nodes.extend(possible_unexplored)
                            for operation_id in operations:
                                operation_id_to_all_conditions[operation_id].extend(possible_conditions[operation_id])

            tree = OperationTree(root_node)
            trees.append(tree)

        operation_id_to_condition = {
            operation_id: OrCondition(
                operation_id_to_all_conditions[operation_id]
            )
            for operation_id in operations
        }

        return trees, operation_id_to_condition


    def to_cli(self, parameters: list[Parameter]) -> list[str]:
        return self.root.to_cli(parameters)
