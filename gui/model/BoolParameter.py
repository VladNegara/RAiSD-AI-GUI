from PySide6.QtCore import Signal

from gui.model.Parameter import Parameter


class BoolParameter(Parameter[bool]):
    value_changed = Signal(bool, bool)

    def to_cli(self) -> str:
        if self.value:
            return self.flag
        else:
            return ""
