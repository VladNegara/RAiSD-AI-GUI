from typing import Self

from model.ParameterGroup import ParameterGroup
from model.Parameter import Parameter

class ParameterGroupList():
    def __init__(self, parameter_groups: list[ParameterGroup] | None = None):
        self._parameter_groups = parameter_groups or []

    @classmethod
    def from_configuration_file(cls, file_path: str) -> Self:
        # TODO: Implement this method: make parameter_groups, add parameters, add groups to set
        parameter_groups = []
        return cls(parameter_groups)

    @property
    def parameter_groups(self) -> list[ParameterGroup]:
        return self._parameter_groups

    def add_parameter_group(self, parameter_group: ParameterGroup):
        self._parameter_groups.append(parameter_group)
