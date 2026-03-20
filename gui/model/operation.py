from dataclasses import dataclass

from gui.model.file_structure import FileStructure


@dataclass
class Operation():
    id: str
    name: str
    description: str
    cli: str
    requires: list[tuple[str, str, FileStructure]]
    produces: FileStructure
