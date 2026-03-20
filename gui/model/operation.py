from dataclasses import dataclass

from gui.model.file_structure import FileStructure


@dataclass
class Operation():
    name: str
    description: str
    cli: str
    requires: list[tuple[str, str, FileStructure]]
    produces: FileStructure
