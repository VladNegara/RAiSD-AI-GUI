from typing import Any

from gui.model.parameter import Parameter


class ParameterGroup():
    """
    A group of `Parameter` objects associated with the same command.
    """

    def __init__(
            self,
            name: str,
            parameters: list[Parameter[Any]] | None = None,
            cli_option: str | None = None
    ) -> None:
        """
        Initialize a `ParameterGroup` object.

        :param name: the name of the parameter group
        :type name: str

        :param parameters: the list of parameters in the group
        :type parameters: list[Parameter[Any]] | None

        :param cli_option: the CLI option associated with the group
        :type cli_option: str | None
        """
        self.name = name
        self._parameters = parameters or []
        self.cli_option = cli_option

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

    def to_cli(self) -> str:
        """
        Represent the parameter group for the command line.

        The command-line representation is obtained from the
        representations of the parameters. If the parameter group has
        its own option, it is prepended to the output.

        :return: the command-line representation
        :rtype: str
        """
        cli_params = [self.cli_option] + [p.to_cli() for p in self.parameters]
        nonempty_params = [p for p in cli_params if p]
        return " ".join(nonempty_params)
