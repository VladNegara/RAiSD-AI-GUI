from typing import Any

from gui.model.Parameter import Parameter


class ParameterGroup():
    def __init__(self, name: str, parameters: list[Parameter[Any]]):
        self.name = name
        self._parameters = parameters or []

    @property
    def parameters(self) -> list[Parameter[Any]]:
        return self._parameters

    def add_parameter(self, parameter: Parameter[Any]) -> None:
        self._parameters.append(parameter)
    
    @property
    def valid(self) -> bool:
        return all([param.valid for param in self.parameters])
