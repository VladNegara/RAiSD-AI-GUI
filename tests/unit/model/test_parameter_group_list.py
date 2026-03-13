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
                        min: null
                        max: null
                        default: 100
                      min-int-1:
                        name: Lower-bounded int
                        description: This integer must be at least 50.
                        cli: -i50
                        min: 50
                        default: 75
                      min-int-2:
                        name: Another lower-bounded int
                        description: Values 30+, upper bound is null.
                        cli: -i30
                        min: 30
                        max: null
                        default: 1300
            """
            )
        )

        # act
        list = ParameterGroupList.from_yaml('path')

        # assert
        assert len(list.parameter_groups) == 1
