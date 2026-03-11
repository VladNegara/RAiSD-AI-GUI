from re import compile

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from gui.model.parameter_group import ParameterGroup
from gui.model.parameter import (
    Parameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
    FileParameter,
)
from gui.model.dependency import (
    Dependency,
    BoolParameterTrueCondition,
    ParameterEnabledEffect,
)


class ParameterGroupList(QObject):
    """
    A list of parameters for a terminal command.

    The parameters are organized in `ParameterGroup` objects, based on
    the operation mode they correspond to and how they relate.
    """

    operations_changed = Signal()

    def __init__(
            self,
            command: str,
            operations: dict[str, bool] | None,
            parameter_groups: list[ParameterGroup] | None = None,
            dependencies: list[Dependency] | None = None,
    ) -> None:
        """
        Initialize a `ParameterGroupList` object.

        :param command: the terminal command to use
        :type command: str

        :param parameter_groups: the groups of parameters
        :type parameter_groups: list[ParameterGroup] | None
        """
        super().__init__()
        self.command = command
        self._operations = operations
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
            {'IMG-GEN'},
            True,
        )
        dummy_false_bool_param = BoolParameter(
            'Print to console',
            'If this is checked, output will be printed to console.',
            '--print-to-console',
            {'IMG-GEN'},
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
            {'MDL-GEN'},
            True,
        )
        dummy_file_selection_param = FileParameter(
            "Browse",
            "Input your files",
            "",
            {'MDL-GEN'},
            ["vcf", "fasta", "pdf"],
            False,
            True,
            None
        )

        parameter_groups = [
            ParameterGroup(
                'Additional options',
                [
                    EnumParameter(
                        'Mode',
                        'This option determines how fast the program will be.',
                        '-m',
                        {'RSD-DEF', 'IMG-GEN', 'MDL-GEN', 'MDL-TST', 'SWP-SCN'},
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
                        {'SWP-SCN'},
                        '',
                    ),
                    StringParameter(
                        'Phone number',
                        'Enter your phone number. Ten digits.',
                        '--phone-number',
                        {'SWP-SCN'},
                        '0123456789',
                        10,
                        compile(r"^\d{10}$"),
                    )
                ],
            ),
            ParameterGroup(
                'Image generation',
                [dummy_true_bool_param, dummy_false_bool_param],
            ),
            ParameterGroup(
                'Model training',
                [other_dummy_param],
            ),
            ParameterGroup(
                "Input files",
              [dummy_file_selection_param],
            ),
            ParameterGroup(
                'Grid size',
                [
                    IntParameter(
                        'Unbounded int',
                        'This int can take any value.',
                        '--unbounded-int',
                        {'RSD-DEF', 'IMG-GEN', 'MDL-GEN', 'MDL-TST', 'SWP-SCN'},
                        5,
                    ),
                    IntParameter(
                        'Lower bounded int',
                        'Bla Bla Bla',
                        '--lowerbounded-int',
                        {'RSD-DEF', 'IMG-GEN', 'MDL-GEN', 'MDL-TST', 'SWP-SCN'},
                        6,
                        5,
                    ),
                    IntParameter(
                        'Upper bounded int',
                        'Bla Bla Bla',
                        '--upperbounded-int',
                        {'RSD-DEF', 'IMG-GEN', 'MDL-GEN', 'MDL-TST', 'SWP-SCN'},
                        6,
                        upper_bound = 50,
                    ),                   
                    IntParameter(
                        'Bounded int',
                        'This int can take any value.',
                        '--bounded-int',
                        {'RSD-DEF', 'IMG-GEN', 'MDL-GEN', 'MDL-TST', 'SWP-SCN'},
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
                        {'RSD-DEF', 'IMG-GEN', 'MDL-GEN', 'MDL-TST', 'SWP-SCN'},
                        8.5,
                    ),
                    FloatParameter(
                        'Lower bounded float',
                        'Bla Bla Bla',
                        '--lowerbounded-float',
                        {'RSD-DEF', 'IMG-GEN', 'MDL-GEN', 'MDL-TST', 'SWP-SCN'},
                        6.6,
                        5.0,
                    ),
                    FloatParameter(
                        'Upper bounded float',
                        'Bla Bla Bla',
                        '--upperbounded-float',
                        {'RSD-DEF', 'IMG-GEN', 'MDL-GEN', 'MDL-TST', 'SWP-SCN'},
                        6.9,
                        upper_bound = 50.0,
                    ),                   
                    FloatParameter(
                        'Bounded float',
                        'This float can take any value.',
                        '--bounded-float',
                        {'RSD-DEF', 'IMG-GEN', 'MDL-GEN', 'MDL-TST', 'SWP-SCN'},
                        5,
                        1.67,
                        10000,
                    ),
                ],
            ),
        ]
        dependencies = [dummy_dependency]
        return cls("./RAiSD-AI", {'RSD-DEF': False, 'IMG-GEN': True, 'MDL-GEN': True, 'MDL-TST': False, 'SWP-SCN': False}, parameter_groups, dependencies)

    @property
    def operations(self) -> dict[str,bool]:
        """
        The active operations of the parameter list.

        """
        return self._operations

    def set_operation(self, operation: str, value: bool) -> None:
        """
        Set an operation to active or not.

        :param operation: the operation to set.
        :type operation: str

        :param value: the value to set the operation to.
        :type value: bool
        """

        if not operation in self._operations:
            raise Exception(f"Setting an invalid operation: {operation}.")
        self._operations[operation] = value

        self.operations_changed.emit()


    @property
    def parameter_groups(self) -> list[ParameterGroup]:
        """
        The list of groups in the parameter list.
        """
        return self._parameter_groups

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

        A separate instruction is produced for each active operation. The
        command is obtained by prepending the list command to the operations's 
        command to the combination of applicable groups' CLI representations.

        :return: the list of instructions
        :rtype: list[str]
        """

        instructions = []
        operations = [operation for operation in self._operations if self._operations[operation]]
        for operation in operations:
            # For each operation get the cli representation from all param_groups
            # The paramgroups handle the operation by passing it to the parameters
            instruction = f"{self.command} -op {operation}"
            for param_group in self._parameter_groups:
                instruction = f"{instruction} {param_group.to_cli(operation)}"
            instructions.append(instruction)

        return instructions
