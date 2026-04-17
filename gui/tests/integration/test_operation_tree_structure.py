from pytest import approx, fixture, raises, skip
from unittest.mock import PropertyMock
from gui.tests.utils.mock_signal import MockSignal
import re

from collections.abc import Sequence

from gui.model.operation import (
    Operation, 
    OperationTree,
)

from PySide6.QtCore import QDir

from gui.model.operation.file_structure import SingleFile
from gui.model.run_record import RunRecord
import gui.model.run_record as rrecord
from gui.model.parameter import (
    IntervalConstraint,
    RegexConstraint,
    ParameterGroup,
    OptionalParameter,
    MultiParameter,
    BoolParameter,
    IntParameter,
    EnumParameter,
    StringParameter,
    FileParameter,
    Parameter
)

class TestOperationTreeStructures:
    """Tests for the structures to do with the OperationTree class. That 
    includes the RunRecord who holds it and the classes inside the tree."""

    @fixture()
    def operation_trees(self):
        self.operations = {
            "IMG-GEN": Operation(
                id="IMG-GEN",
                name="Image generation",
                description="Generates an image.",
                cli="-mdl",
                requires=[
                    Operation.Input(
                        name="Input file",
                        description="The input file.",
                        cli="-I ",
                        file=SingleFile([".ms", ".txt"]),
                    ),
                ],
                produces=SingleFile([".png"]),
                output_path=[
                    Operation.ConstPathFragment("Image."),
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
                    Operation.ConstPathFragment("Image."),
                    Operation.RunIdPathFragment(),
                ]
            ),
            "MDL-GEN": Operation(
                id="MDL-GEN",
                name="Model training",
                description="Perform a model training.",
                cli="-mdl",
                requires=[
                    Operation.Input(
                        name="Input file",
                        description="The input file.",
                        cli="-I ",
                        file=SingleFile([".png"]),
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
        self.trees, _ = OperationTree.build_trees(
            self.operations,
            self.overwrite_parameter_builder,
        )
        self.categorized_operation_trees = [
            ('Operations', self.trees),
        ]
    
    @fixture()
    def run_record(self, mocker, operation_trees):
        # Parameters
        self.run_id_parameter = StringParameter(
            name='name',
            description='description',
            flag='-f ',
            operations={'MDL-GEN'},
            default_value='default',
            constraints=[
                RegexConstraint(
                    pattern=re.compile(r"\b[a-z]+\b"),
                    hint="Only lowercase letters.",
                ),
            ],
        )
        self.enum_parameter = EnumParameter (
            name="Run ID",
            description="Fill in a name to identify your run.",
            flag="-n ",
            operations={"IMG-GEN", "MDL-GEN"},
            options=[("name1", "1"),("name2","2")],
            default_value=0,
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
        self.file_parameter = FileParameter (
            name="file",
            description="file",
            flag="-fi ",
            operations={"IMG-GEN"}
        )
        self.multi_parameter = MultiParameter ( #type: ignore
                    name="multi",
                    description="descr",
                    flag="-m ",
                    operations={'IMG-GEN'},
                    parameters=[self.file_parameter]
                )
        
        # Parameter groups
        self.parameters_group1: Sequence[Parameter] = [
            self.multi_parameter
        ]
        self.parameters_group2: Sequence[Parameter] = [
            self.enum_parameter,
            self.optional_parameter
        ]
        self.parameter_groups = [
            ParameterGroup(
                name='img',
                parameters=self.parameters_group1 # type: ignore
                ), 
            ParameterGroup(
                name='mdl',
                parameters=self.parameters_group2 # type: ignore
            ),
        ]

        # RunRecord
        self.record = RunRecord(
            run_id_parameter=self.run_id_parameter,
            categorized_operation_trees=self.categorized_operation_trees,
            parameter_groups=self.parameter_groups,
        )

        print(self.record.operation_trees)
        for tree in self.record.operation_trees:
            print(tree.to_dict())

        # Mock workspace else it will lead to errors
        mocker.patch.object(
            type(rrecord.app_settings),
            "workspace_path",
            new_callable=PropertyMock,
            return_value=QDir.current()
        )

    def test_operation_trees_structure(self, run_record):
        """Test OperationTree initialization."""
        # Arrange
        record = self.record

        # Act

        # Assert
        skip()