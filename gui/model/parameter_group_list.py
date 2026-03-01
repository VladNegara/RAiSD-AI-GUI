from typing import Self

from gui.model.parameter_group import ParameterGroup
from gui.model.parameter import (
    Parameter,
    BoolParameter,
)


class ParameterGroupList():
    def __init__(
            self,
            command: str,
            parameter_groups: list[ParameterGroup] | None = None,
    ) -> None:
        self.command = command
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
        return cls("./RAiSD-AI", parameter_groups)

    @property
    def parameter_groups(self) -> list[ParameterGroup]:
        return self._parameter_groups

    def add_parameter_group(self, parameter_group: ParameterGroup):
        self._parameter_groups.append(parameter_group)

    def valid(self) -> bool:
        return all([group.valid for group in self.parameter_groups])

    def to_cli(self) -> list[str]:
        return [
            f"{self.command} {param_group.to_cli()}"
            for param_group in self.parameter_groups
        ]
