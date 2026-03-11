from typing import Any

from PySide6.QtCore import QObject, Signal, Slot

from gui.model.parameter import Parameter


class ParameterGroup(QObject):
    """
    A group of `Parameter` objects associated with the same command.
    """

    def __init__(
            self,
            name: str,
            parameters: list[Parameter[Any]] | None = None,
    ) -> None:
        """
        Initialize a `ParameterGroup` object.

        :param name: the name of the parameter group
        :type name: str

        :param parameters: the list of parameters in the group
        :type parameters: list[Parameter[Any]] | None
        """
        super().__init__()
        self.name = name
        self._parameters = parameters or []

    @property
    def parameters(self) -> list[Parameter[Any]]:
        """
        The list of parameters in the group.
        """
        return self._parameters

    def add_parameter(self, parameter: Parameter[Any]) -> None:
        """
        Add a parameter to the group.
        """
        self._parameters.append(parameter)
    
    @property
    def valid(self) -> bool:
        """
        Whether the current parameter values are valid.

        The group is valid if and only if every parameter in the group
        is valid.
        """
        return all([param.valid for param in self.parameters])

    def to_cli(self, operation: str) -> str:
        """
        Represent the parameter group for the command line.

        The command-line representation is obtained from the
        representations of the parameters. If the parameter group has
        its own option, it is prepended to the output.

        :return: the command-line representation
        :rtype: str
        """
        cli_params = [p.to_cli(operation) for p in self.parameters]
        nonempty_params = [p for p in cli_params if p]
        return " ".join(nonempty_params)

    def __str__(self) -> str:
        return f"{self.name}: {self.to_cli()}"
