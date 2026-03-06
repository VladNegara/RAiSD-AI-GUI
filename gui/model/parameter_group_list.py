from gui.model.parameter_group import ParameterGroup
from gui.model.parameter import (
    Parameter,
    BoolParameter,
)
from gui.model.dependency import (
    Dependency,
    BoolParameterTrueCondition,
    ParameterEnabledEffect,
)


class ParameterGroupList():
    """
    A list of parameters for a terminal command.

    The parameters are organized in `ParameterGroup` objects, based on
    the operation mode they correspond to and how they relate.
    """

    def __init__(
            self,
            command: str,
            parameter_groups: list[ParameterGroup] | None = None,
            dependencies: list[Dependency] | None = None
    ) -> None:
        """
        Initialize a `ParameterGroupList` object.

        :param command: the terminal command to use
        :type command: str

        :param parameter_groups: the groups of parameters
        :type parameter_groups: list[ParameterGroup] | None
        """
        self.command = command
        self._parameter_groups = parameter_groups or []
        self._dependencies = dependencies or []

    @classmethod
    def from_configuration_file(cls, file_path: str) -> "ParameterGroupList":
        """
        Create a list of parameters from a configuration file.

        Please note: this method is not currently implemented. Instead,
        it returns mock data.

        :param file_path: the path to the configuration file
        :type file_path: str

        :return: the parameter list
        :rtype: Self
        """
        # TODO: Implement this method:
        # - make parameter_groups
        # - add parameters
        # - add groups to list

        # Create dummy parameters
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
        other_dummy_param = BoolParameter(
            'Use PyTorch',
            'If this is checked, PyTorch will be used instead of TensorFlow',
            '--use-pt',
            True,
        )
        parameter_groups = [
            ParameterGroup(
                'Image generation',
                [dummy_true_bool_param, dummy_false_bool_param],
                '-op=IMG_GEN',
            ),
            ParameterGroup(
                'Model training',
                [other_dummy_param],
                '-op=MDL_GEN',
            )
        ]
        return cls("./RAiSD-AI", parameter_groups)

    @property
    def parameter_groups(self) -> list[ParameterGroup]:
        """
        The list of groups in the parameter list.
        """
        return self._parameter_groups

    def add_parameter_group(self, parameter_group: ParameterGroup) -> None:
        """
        Add a group of parameters to the list.

        :param parameter_group: the group to be added
        :type parameter_group: ParameterGroup
        """
        self._parameter_groups.append(parameter_group)

    @property
    def valid(self) -> bool:
        """
        Whether the current parameter values are valid.

        The list is valid if and only if every group is valid.
        """
        return all([group.valid for group in self.parameter_groups])

    def to_cli(self) -> list[str]:
        """
        Produce command-line instructions for the current parameter
        values.

        A separate instruction is produced for each parameter group. The
        command is obtained by prepending the list's command to the
        group's CLI representation.

        :return: the list of instructions
        :rtype: list[str]
        """
        return [
            f"{self.command} {param_group.to_cli()}"
            for param_group in self.parameter_groups
        ]
