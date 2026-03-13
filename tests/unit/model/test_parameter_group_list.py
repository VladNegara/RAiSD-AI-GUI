from pytest import fixture, raises
import re

from gui.model.parameter_group_list import ParameterGroupList
from gui.model.parameter_group import ParameterGroup
from gui.model.parameter import StringParameter

class TestParameterGroupList:
    """Tests for ParameterGroupList class."""

    @fixture(autouse=True)
    def set_parameter_group_list(self):
        self.parameter_groups = [
            ParameterGroup(
                name='img',
                parameters=[]),
            ParameterGroup(
                name='mdl',
                parameters=[
                    StringParameter(
                        name='name',
                        description='description',
                        flag='-flag',
                        operations={'MDL-GEN'},
                        default_value='default',
                        pattern=re.compile(r"\b[a-z]+\b")
                    )
                ]
            )
        ]
        self.parameter_group_list = ParameterGroupList(
            command="./RAiSD-AI",
            operations={
                'IMG-GEN': True, 
                'MDL-GEN': True, 
                'MDL-TST': False,
                'SWP-SCN': False
            },
            parameter_groups=self.parameter_groups,
            dependencies=None,
        )
    
    def test_init_values(self):
        # arrange
        list = self.parameter_group_list
        groups = self.parameter_groups

        # assert
        assert list.command == "./RAiSD-AI"
        assert list.operations == {'IMG-GEN': True, 
                                    'MDL-GEN': True, 
                                    'MDL-TST': False,
                                    'SWP-SCN': False}
        assert list.parameter_groups == groups
        assert list._dependencies == []

    def test_set_operations(self):
        # arrange
        list = self.parameter_group_list

        # act
        list.set_operation('MDL-TST', True)
        list.set_operation('IMG-GEN', False)

        # assert
        assert list.operations['MDL-TST'] == True
        assert list.operations ['IMG-GEN'] == False
        with raises(Exception, match="Setting an invalid operation: invalid op"):
            list.set_operation('invalid op', True)

    def test_operations_changed_signal_emitted(self):
        # arrange
        list = self.parameter_group_list
        self.signals_emitted = 0

        def on_operations_changed():
            self.signals_emitted += 1

        list.operations_changed.connect(on_operations_changed)

        # act
        list.set_operation('MDL-TST', True)
        list.set_operation('IMG-GEN', False)
        with raises(Exception):
            list.set_operation('invalid op', True)

        # assert
        assert self.signals_emitted == 2

    def test_valid(self):
        list = self.parameter_group_list
        assert list.valid
        list.parameter_groups[1].parameters[0].value = "invalid value"
        assert not list.valid
        
    def test_to_cli(self):
        # arrange
        list = self.parameter_group_list

        # act
        instructions = list.to_cli()

        # assert
        assert len(instructions) == 2
        assert instructions == [
            './RAiSD-AI -op IMG-GEN',
            './RAiSD-AI -op MDL-GEN -flag default'
        ]


class TestParameterGroupListFromYaml:
    """Tests for the `ParameterGroupList#from_yaml` class method."""

    def test_correct(self, mocker):
        # arrange
        mocker.patch(
            "builtins.open",
            mocker.mock_open(
                read_data= """
                modes:
                  - name: standard
                    operations:
                      first-op:
                        name: First operation
                        description: The first operation in the sequence.
                        cli: -op 1
                      second-op:
                        name: Second operation
                        description: The operation that comes after.
                        cli: -op 2
                parameter_groups:
                  - name: Boolean parameters
                    operations:
                      - first-op
                      - second-op
                    parameters:
                      true-bool:
                        name: True bool
                        description: This boolean parameter is true by default.
                        cli: --true-bool
                        type: bool
                        default: true
                      false-bool:
                        name: False bool
                        description: A bool parameter that is false by default.
                        cli: --false-bool
                        type: bool
                        default: true
                  - name: Integer parameters
                    operations:
                      - first-op
                      - second-op
                    parameters:
                      any-int-1:
                        name: Unbounded int
                        description: This integer can take any value.
                        cli: --unbounded-int
                        type: int
                        default: 0
                      any-int-2:
                        name: Another unbounded int
                        description: This time, the bounds are explicitly null.
                        cli: --int-unrestricted
                        type: int
                        min: null
                        max: null
                        default: 100
                      min-int-1:
                        name: Lower-bounded int
                        description: This integer must be at least 50.
                        cli: -i50
                        type: int
                        min: 50
                        default: 75
                      min-int-2:
                        name: Another lower-bounded int
                        description: Values 30+, upper bound is null.
                        cli: -i30
                        type: int
                        min: 30
                        max: null
                        default: 1300
                      max-int-1:
                        name: Upper-bounded int
                        description: This integer must be no more than 10.
                        cli: -i10
                        type: int
                        max: 10
                        default: -19
                      max-int-2:
                        name: Another upper-bounded int
                        description: No more than 15. Lower bound is null.
                        cli: -i15
                        type: int
                        min: null
                        max: 15
                        default: 15
                      bounded-int-1:
                        name: Bounded int
                        description: This int is from 1 to 10.
                        cli: -i1-10
                        type: int
                        min: 1
                        max: 10
                        default: 7
                  - name: Floating-point parameters
                    operations:
                      - first-op
                      - second-op
                    parameters:
                      any-float-1:
                        name: Unbounded float
                        description: This float can take any value.
                        cli: --unbounded-float
                        type: float
                        default: -3.14159
                      any-float-2:
                        name: Another unbounded float
                        description: This time, the bounds are explicitly null.
                        cli: --float-unrestricted
                        type: float
                        min: null
                        max: null
                        default: 123.456
                      min-float-1:
                        name: Lower-bounded float
                        description: This float must be at least 1.5.
                        cli: -f1.5
                        type: float
                        min: 1.5
                        default: 1.9
                      min-float-2:
                        name: Another lower-bounded float
                        description: Values 3.1+, upper bound is null.
                        cli: -f3.1
                        type: float
                        min: 3.1
                        max: null
                        default: 1300
                      max-float-1:
                        name: Upper-bounded float
                        description: This float must be no more than -190.45.
                        cli: -f-190.45
                        type: float
                        max: -190.45
                        default: -199
                      max-float-2:
                        name: Another upper-bounded float
                        description: No more than 13.13. Lower bound is null.
                        cli: -f13.13
                        type: float
                        min: null
                        max: 13.3
                        default: -23094.0
                      bounded-float:
                        name: Bounded float
                        description: This float is between 0 and 1.
                        cli: -f0-1
                        type: float
                        min: 0.0
                        max: 1.0
                        default: 0
                  - name: Enum parameters
                    operations:
                      - first-op
                      - second-op
                    parameters:
                      cli-enum:
                        name: Enum parameter
                        description: Choose from a list of four values.
                        cli: --enum
                        type: enum
                        options:
                          - name: First option
                            cli: one
                          - name: Second option
                            cli: two
                          - name: Third option
                            cli: three
                          - name: Fourth option
                            cli: four
                        default: 2
                      no-cli-enum:
                        name: Dummy enum parameter
                        description: This parameter will not be in the CLI.
                        type: enum
                        options:
                            - name: Choose this...
                            - name: ...or this!
                            - name: Or even this.
                  - name: String parameters
                    operations:
                      - first-op
                      - second-op
                    parameters:
                      any-string:
                        name: String
                        description: Enter a string. Anything goes!
                        cli: -s
                        type: str
                      max-len-str:
                        name: Bounded string
                        description: Type at most 4 characters.
                        cli: --s-max4
                        type: str
                        max_length: 4
                      pattern-str:
                        name: Pattern string
                        description: This parameter must be only A and B
                        cli: --sAB
                        type: str
                        pattern: (A|B)*
                      max-len-pattern-str:
                        name: Bounded pattern string
                        description: This parameter must be at most 10 digits.
                        cli: --phone-number
                        type: str
                        max_length: 10
                        pattern: '\\d*'
                      default-str:
                        name: Default value string
                        description: This string already has a default value.
                        cli: --default-str
                        type: str
                        max: 20
                        default: Hello
            """
            )
        )

        # act
        list = ParameterGroupList.from_yaml('path')

        # assert
        assert len(list.parameter_groups) == 5
