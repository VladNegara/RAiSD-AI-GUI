from typing import Any

from gui.model.Parameter import Parameter


class ParameterGroup():
    def __init__(
            self,name: str,
            parameters: list[Parameter[Any]] | None = None,
            cli_option: str | None = None
    ) -> None:
        self.name = name
        self._parameters = parameters or []
        self.cli_option = cli_option

    @property
    def parameters(self) -> list[Parameter[Any]]:
        return self._parameters

    def add_parameter(self, parameter: Parameter[Any]) -> None:
        self._parameters.append(parameter)
    
    @property
    def valid(self) -> bool:
        return all([param.valid for param in self.parameters])

    def to_cli(self) -> str:
        cli_params = " ".join([param.to_cli() for param in self.parameters])
        if self.cli_option:
            return f"{self.cli_option} {cli_params}"
        return cli_params
