from pytest import approx, fixture, raises
import re

from collections.abc import Sequence

from gui.model.operation import (
    Operation, 
    OperationTree,
)
from gui.model.operation.file_structure import SingleFile
from gui.model.run_record import RunRecord
from gui.model.parameter import (
    IntervalConstraint,
    MaxLengthConstraint,
    RegexConstraint,
    ParameterGroup,
    OptionalParameter,
    MultiParameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
    FileParameter,
    Parameter
)

class TestParameterStructures:
    """Tests the structures in which parameters are held. This includes the 
    RunRecord, Parameter and ParameterGroup."""

    @fixture(autouse=True)
    def set_run_record(self):
        self.run_id_parameter = StringParameter (
            name="Run ID",
            description="Fill in a name to identify your run.",
            flag="-n",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value="my_run",
            constraints=[
                  RegexConstraint(
                      pattern=re.compile(r"[^!]"),
                      hint="No exclamation marks!",
                  ),
              ],
        )
        self.string_parameter = StringParameter(
                        name='name',
                        description='description',
                        flag='-f ',
                        operations={'IMG-GEN'},
                        default_value='default',
                        constraints=[
                            RegexConstraint(
                                pattern=re.compile(r"\b[a-z]+\b"),
                                hint="Only lowercase letters.",
                            ),
                        ],
                    )
        self.optional_parameter = OptionalParameter(
                        name='optional',
                        description='This is optional',
                        operations={'MDL-GEN'},
                        default_value=False,
                        parameter=IntParameter(
                          name='int',
                          description='description',
                          flag='-i ',
                          operations={'MDL-GEN'},
                          default_value=3,
                          constraints=[
                              IntervalConstraint(
                                  lower_bound=2,
                                  lower_bound_inclusive=False,
                                  upper_bound=7,
                                  upper_bound_inclusive=False,
                              ),
                          ],
                      )
                    )
        self.parameters: Sequence[Parameter] = [
                    self.string_parameter,
                    self.optional_parameter
                ]
        self.parameter_groups = [
            ParameterGroup(
                name='img',
                parameters=[]), 
            ParameterGroup(
                name='mdl',
                parameters=self.parameters # type: ignore
            ),
        ]
        self.operations = {
            "MDL-GEN": Operation(
                id="mdl",
                name="Model training",
                description="Perform a model training.",
                cli="-mdl",
                requires=[
                    Operation.Input(
                        name="Input file",
                        description="The input file.",
                        cli="-I",
                        file=SingleFile([".ms", ".txt"]),
                    ),
                ],
                produces=SingleFile([".txt"]),
                output_path=[
                    Operation.ConstPathFragment("Model."),
                    Operation.RunIdPathFragment(),
                ],
                overwrite_parameter_builder=(
                    lambda: BoolParameter(
                        name="Overwrite output?",
                        description="",
                        flag="-overwrite",
                        operations={"mdl"},
                        default_value=False,
                    )
                ),
                parameter_builders={},
                overwrite_path=[
                    Operation.ConstPathFragment("Model."),
                    Operation.RunIdPathFragment(),
                ]
            ),
        }
        self.overwrite_parameter_builder = (
            lambda: BoolParameter(
                name="Overwrite output directory",
                description="Are you sure you want to overwrite?",
                flag="-frm",
                operations={"MDL-GEN"},
                default_value=False,
            )
        )
        self.operation_trees, _ = OperationTree.build_trees(
            self.operations,
            self.overwrite_parameter_builder,
        )
        self.categorized_operation_trees = [
            ('Operations', self.operation_trees),
        ]
        self.run_record = RunRecord(
            run_id_parameter=self.run_id_parameter,
            categorized_operation_trees=self.categorized_operation_trees,
            parameter_groups=self.parameter_groups,
        )

    def test_valid_based_on_params(self):
        """Test whether the validity of parameters is passed along from 
        Parameter to ParameterGroup to RunRecord correctly."""
        # Arrange
        record = self.run_record

        # Act and Assert
        assert record.valid
        self.string_parameter.value = "HI"
        assert not record.valid
        self.string_parameter.reset_value()

        self.optional_parameter.parameter.value = 0
        assert not record.valid
        self.optional_parameter.parameter.reset_value()

        self.run_id_parameter.value = "!"
        assert not record.valid
        self.run_id_parameter.reset_value()
        
    def test_to_cli(self):
        # arrange
        list = self.parameter_group_list

        # act
        instructions = list.to_cli()

        # assert
        assert len(instructions) == 1
        assert instructions == list.selected_operation_tree.to_cli(
            run_id_parameter=self.run_id_parameter,
            parameters=list.parameters,
        )