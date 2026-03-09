from re import compile

from gui.model.parameter_group import ParameterGroup
from gui.model.parameter import (
    Parameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
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
        dummy_dependency = Dependency(
            BoolParameterTrueCondition(
                dummy_true_bool_param,
            ),
            ParameterEnabledEffect(
                dummy_false_bool_param,
            ),
        )
        other_dummy_param = BoolParameter(
            'Use PyTorch',
            'If this is checked, PyTorch will be used instead of TensorFlow',
            '--use-pt',
            True,
        )

        parameter_groups = [
            ParameterGroup(
                'Additional options',
                [
                    EnumParameter(
                        'Mode',
                        'This option determines how fast the program will be.',
                        '-m',
                        [
                            ('Slow', 'slow'),
                            ('Regular', 'normal'),
                            ('Fast', 'fast'),
                            ('Super fast', 'very-fast'),
                        ],
                        1,
                    ),
                ],
            ),
            ParameterGroup(
                'Personal data',
                [
                    StringParameter(
                        'Your name',
                        'Enter your first and last name.',
                        '--name',
                        '',
                    ),
                    StringParameter(
                        'Phone number',
                        'Enter your phone number. Ten digits.',
                        '--phone-number',
                        '0123456789',
                        10,
                        compile(r"^\d{10}$"),
                    )
                ],
            ),
            ParameterGroup(
                'Image generation',
                [dummy_true_bool_param, dummy_false_bool_param],
                '-op=IMG_GEN',
            ),
            ParameterGroup(
                'Model training',
                [other_dummy_param],
                '-op=MDL_GEN',
            ),
            ParameterGroup(
                'Grid size',
                [
                    IntParameter(
                        'Unbounded int',
                        'This int can take any value.',
                        '--unbounded-int',
                        5,
                    ),
                    IntParameter(
                        'Lower bounded int',
                        'Bla Bla Bla',
                        '--lowerbounded-int',
                        6,
                        5,
                    ),
                    IntParameter(
                        'Upper bounded int',
                        'Bla Bla Bla',
                        '--upperbounded-int',
                        6,
                        upper_bound = 50,
                    ),                   
                    IntParameter(
                        'Bounded int',
                        'This int can take any value.',
                        '--bounded-int',
                        5,
                        1,
                        10000,
                    ),
                ],
            ),
            ParameterGroup(
                'Power size',
                [
                    FloatParameter(
                        'Unbounded float',
                        'This float can take any value.',
                        '--unbounded-float',
                        8.5,
                    ),
                    FloatParameter(
                        'Lower bounded float',
                        'Bla Bla Bla',
                        '--lowerbounded-float',
                        6.6,
                        5.0,
                    ),
                    FloatParameter(
                        'Upper bounded float',
                        'Bla Bla Bla',
                        '--upperbounded-float',
                        6.9,
                        upper_bound = 50.0,
                    ),                   
                    FloatParameter(
                        'Bounded float',
                        'This float can take any value.',
                        '--bounded-float',
                        5,
                        1.67,
                        10000,
                    ),
                ],
            ),
        ]
        dependencies = [dummy_dependency]
        return cls("./RAiSD-AI", parameter_groups, dependencies)

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
