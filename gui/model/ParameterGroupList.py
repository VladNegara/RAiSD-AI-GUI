from typing import Self

from gui.model.ParameterGroup import ParameterGroup
from gui.model.Parameter import Parameter
from gui.model.BoolParameter import BoolParameter


class ParameterGroupList():
    def __init__(self, parameter_groups: list[ParameterGroup] | None = None):
        self._parameter_groups = parameter_groups or []

    @classmethod
    def from_configuration_file(cls, file_path: str) -> Self:
        # TODO: Implement this method: make parameter_groups, add parameters, add groups to set

        # Create a dummy parameter
        dummy_true_bool_param = BoolParameter(
            'Make PDFs',
            'If this is checked, PDFs of the output will be created.',
            '-pdf',
            True,
        )
        dummy_false_bool_param = BoolParameter(
            'Print to console',
            'If this is checked, output will be printed to console.',
            '--print-to-console',
            False,
        )
        parameter_groups = [
            ParameterGroup(
                'Important parameters',
                [dummy_true_bool_param, dummy_false_bool_param],
            )
        ]
        return cls(parameter_groups)

    @property
    def parameter_groups(self) -> list[ParameterGroup]:
        return self._parameter_groups

    def add_parameter_group(self, parameter_group: ParameterGroup):
        self._parameter_groups.append(parameter_group)

    def valid(self) -> bool:
        return all([group.valid for group in self.parameter_groups])
