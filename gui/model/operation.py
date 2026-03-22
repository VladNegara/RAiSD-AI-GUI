"""
A module containing the `Operation` class.
"""

from dataclasses import dataclass

from gui.model.file_structure import FileStructure


@dataclass
class Operation():
    """
    A data class which holds the details of an operation.

    This class is used to hold intermediate information about operations
    between parsing and building the operation tree.
    """

    id: str
    name: str
    description: str
    cli: str
    requires: list[tuple[str, str, FileStructure]]
    produces: FileStructure
