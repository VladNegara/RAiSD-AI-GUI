"""
A module containing the `Operation` class.
"""

from dataclasses import dataclass
from typing import Any, Callable

from gui.model.file_structure import FileStructure
from gui.model.parameter import Parameter


@dataclass
class Operation():
    """
    A data class which holds the details of an operation.

    This class is used to hold intermediate information about operations
    between parsing and building the operation tree.
    """

    class PathFragment:
        pass

    @dataclass
    class ConstPathFragment(PathFragment):
        value: str

    class RunIdPathFragment(PathFragment):
        pass

    class SlashPathFragment(PathFragment):
        pass

    @dataclass
    class ParameterValuePathFragment(PathFragment):
        parameter_id: str

    id: str
    name: str
    description: str
    cli: str
    requires: list[tuple[str, str, FileStructure]]
    produces: FileStructure
    output_path: list[PathFragment]
    overwrite_parameter_builder: Callable[[], Parameter[Any]]
    parameter_builders: dict[str, Callable[[], Parameter[Any]]]
