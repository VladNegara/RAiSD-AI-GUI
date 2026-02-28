from PySide6.QtCore import Signal

from gui.model.Parameter import Parameter


class BoolParameter(Parameter[bool]):
    """
    A boolean parameter in the GUI.

    The value of a boolean parameter is always valid.
    """

    value_changed = Signal(bool, bool)

    def to_cli(self) -> str:
        # A boolean parameter is represented in the command line by the
        # presence or absence of its flag.
        if self.value:
            return self.flag
        else:
            return ""
    
    def __str__(self) -> str:
        return (
            f'BoolParameter('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )