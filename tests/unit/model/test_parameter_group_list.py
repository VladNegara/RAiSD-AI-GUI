from pytest import approx, fixture, raises
import re

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
)

# TODO: make the tests more comprehensive and use mocking

class TestParameterGroupList:
    """Tests for ParameterGroupList class."""

    @fixture(autouse=True)
    def set_parameter_group_list(self):
        self.run_id_parameter = StringParameter (
            name="Run ID",
            description="Fill in a name to identify your run.",
            flag="-n",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value="my_run",
        )
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
                        operations={'IMG-GEN'},
                        default_value='default',
                        constraints=[
                            RegexConstraint(
                                pattern=re.compile(r"\b[a-z]+\b"),
                                hint="Only lowercase letters.",
                            ),
                        ],
                    ),
                ],
            ),
        ]
        self.operations = {
            "MDL-GEN": Operation(
                id="mdl",
                name="Model training",
                description="Perform a model training.",
                cli="-mdl",
                requires=[("Input file", "-I", SingleFile([".ms", ".txt"]))],
                produces=SingleFile([".txt"]),
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
                output_path=[
                    Operation.ConstPathFragment("Model."),
                    Operation.RunIdPathFragment(),
                ],
            ),
        }
        self.operation_trees, _ = OperationTree.build_trees(self.operations)
        self.parameter_group_list = RunRecord(
            run_id_parameter=self.run_id_parameter,
            operation_trees=self.operation_trees,
            parameter_groups=self.parameter_groups,
            dependencies=None,
        )
    
    def test_init_values(self):
        # arrange
        run_id_parameter = self.run_id_parameter
        list = self.parameter_group_list
        groups = self.parameter_groups

        # assert
        assert list.run_id_parameter == run_id_parameter
        assert list.operation_trees == self.operation_trees
        assert list.parameter_groups == groups
        assert list._dependencies == []

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
        assert len(instructions) == 1
        assert instructions == list.selected_operation_tree.to_cli(
            run_id_parameter=self.run_id_parameter,
            parameters=list.parameters,
        )


class TestParameterGroupListFromYaml:
    """Tests for the `ParameterGroupList#from_yaml` class method."""

    def test_correct(self, mocker):
        # TODO: test parsing of exclusive interval constraints
        # arrange
        mocker.patch(
            "builtins.open",
            mocker.mock_open(
                read_data= """
                run_id_parameter:
                  type: str
                  name: Run ID
                  description: The ID of the run.
                modes:
                  - name: standard
                    operations:
                      first-op:
                        name: First operation
                        description: The first operation in the sequence.
                        cli: -op 1
                        overwrite_parameter:
                          name: Overwrite output of operation 1?
                          type: bool
                          default: false
                        input:
                          - name: Input video
                            cli: --mp4
                            file:
                              type: single
                              formats:
                                - .mp4
                        output:
                          type: directory
                          contents:
                            - type: single
                              formats:
                                - .jpg
                        path:
                          - Operation1.
                          - type: run id
                      second-op:
                        name: Second operation
                        description: The operation that comes after.
                        cli: -op 2
                        overwrite_parameter:
                          name: Overwrite output of operation 2?
                          type: bool
                          default: false
                        input:
                          - name: Frames
                            cli: -f
                            file:
                              type: folder
                              contents:
                                - type: single
                                  formats:
                                    - .jpg
                        output:
                          type: single
                          formats:
                            - .txt
                        path:
                          - Operation2.
                          - type: run id
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
                        default: false
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
                        description: This time, the constraints are empty.
                        cli: --int-unrestricted
                        type: int
                        default: 100
                        constraints: []
                      min-int-1:
                        name: Lower-bounded int
                        description: This integer must be at least 50.
                        cli: -i50
                        type: int
                        default: 75
                        constraints:
                          - type: interval
                            min: 50
                      min-int-2:
                        name: Another lower-bounded int
                        description: Values 30+, upper bound is null.
                        cli: -i30
                        type: int
                        min: 30
                        max: null
                        default: 1300
                        constraints:
                          - type: interval
                            min: 30
                            max: null
                      max-int-1:
                        name: Upper-bounded int
                        description: This integer must be no more than 10.
                        cli: -i10
                        type: int
                        default: -19
                        constraints:
                          - type: interval
                            max: 10
                      max-int-2:
                        name: Another upper-bounded int
                        description: No more than 15. Lower bound is null.
                        cli: -i15
                        type: int
                        default: 15
                        constraints:
                          - type: interval
                            min: null
                            max: 15
                      bounded-int-1:
                        name: Bounded int
                        description: This int is from 1 to 10.
                        cli: -i1-10
                        type: int
                        default: 7
                        constraints:
                          - type: interval
                            min: 1
                            max: 10
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
                        description: This time, the constraints are empty.
                        cli: --float-unrestricted
                        type: float
                        default: 123.456
                        constraints: []
                      min-float-1:
                        name: Lower-bounded float
                        description: This float must be at least 1.5.
                        cli: -f1.5
                        type: float
                        default: 1.9
                        constraints:
                          - type: interval
                            min: 1.5
                      min-float-2:
                        name: Another lower-bounded float
                        description: Values 3.1+, upper bound is null.
                        cli: -f3.1
                        type: float
                        default: 1300
                        constraints:
                          - type: interval
                            min: 3.1
                            max: null
                      max-float-1:
                        name: Upper-bounded float
                        description: This float must be no more than -190.45.
                        cli: -f-190.45
                        type: float
                        default: -199
                        constraints:
                          - type: interval
                            max: -190.45
                      max-float-2:
                        name: Another upper-bounded float
                        description: No more than 13.13. Lower bound is null.
                        cli: -f13.13
                        type: float
                        default: -23094.0
                        constraints:
                          - type: interval
                            min: null
                            max: 13.13
                      bounded-float:
                        name: Bounded float
                        description: This float is between 0 and 1.
                        cli: -f0-1
                        type: float
                        min: 0.0
                        max: 1.0
                        default: 0
                        constraints:
                          - type: interval
                            min: 0.0
                            max: 1.0
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
                        constraints:
                          - type: max length
                            length: 4
                      pattern-str:
                        name: Pattern string
                        description: This parameter must be only As and Bs.
                        cli: --sAB
                        type: str
                        constraints:
                          - type: regex
                            pattern: (A|B)*
                            hint: Any number of A or B.
                      max-len-pattern-str:
                        name: Bounded pattern string
                        description: This parameter must be at most 10 digits.
                        cli: --phone-number
                        type: str
                        constraints:
                          - type: max length
                            length: 10
                          - type: regex
                            pattern: '\\d*'
                            hint: Only digits.
                      default-str:
                        name: Default value string
                        description: This string already has a default value.
                        cli: --default-str
                        type: str
                        default: Hello
                        constraints:
                          - type: max length
                            length: 20
                  - name: File parameters
                    operations:
                      - first-op
                      - second-op
                    parameters:
                      any-file:
                        name: Any file
                        description: This allows one file of any type.
                        cli: --any-file
                        type: file
                      any-files:
                        name: Any files
                        description: This allows many files of any type.
                        cli: --any-files
                        type: file
                        multiple: true
                      not-strict:
                        name: Expected type file
                        description: One file of any type, image expected.
                        cli: --image
                        type: file
                        formats:
                          - .png
                          - .jpg
                          - .jpeg
                          - .gif
                          - .webp
                      not-strict-multiple:
                        name: Expected type files
                        description: Multiple files, videos expected.
                        cli: --images
                        type: file
                        formats:
                          - .mp4
                          - .webm
                        multiple: true
                      strict:
                        name: Specific type file
                        description: One audio file.
                        cli: --song
                        type: file
                        formats:
                          - .mp3
                          - .wav
                        strict: true
                      strict-multiple:
                        name: Specific type files
                        description: Multiple document files.
                        cli: --docs
                        type: file
                        formats:
                          - .doc
                          - .docx
                          - .odf
                          - .pdf
                        strict: true
                        multiple: true
                  - name: Optional parameters
                    operations:
                      - first-op
                      - second-op
                    parameters:
                      opt-bool:
                        name: Optional bool
                        description: An optional bool parameter.
                        type: optional
                        parameter:
                          name: Inner bool
                          description: The inner parameter.
                          cli: --opt-bool
                          type: bool
                          default: false
                      opt-int:
                        name: Optional int
                        description: An optional int parameter, default true.
                        type: optional
                        default: true
                        parameter:
                          name: Inner int parameter
                          description: null
                          cli: --opt-int
                          type: int
                          default: 1
                          constraints:
                            - type: interval
                              min: 1
                      opt-float:
                        name: Optional float
                        description: An optional float parameter.
                        type: optional
                        default: false
                        parameter:
                          name: Inner float parameter
                          type: float
                          cli: --opt-float
                          min: null
                          max: null
                          default: -1.1
                      opt-enum:
                        name: Optional enum
                        description: An optional enum parameter.
                        type: optional
                        parameter:
                          description: An inner enum parameter with no name.
                          cli: --opt-enum
                          type: enum
                          options:
                            - name: A
                            - name: B
                            - name: C
                          default: 1
                      opt-str:
                        name: Optional string
                        description: An optional string parameter.
                        type: optional
                        default: null
                        parameter:
                          name: null
                          description: The string.
                          cli: --opt-str
                          type: str
                          default: example
                          constraints:
                            - type: max length
                              length: 20
                      opt-file:
                        name: Optional files
                        description: An optional multi-file parameter.
                        type: optional
                        parameter:
                          cli: --opt-files
                          type: file
                          multiple: true
                  - name: Multi-value parameters
                    operations:
                      - first-op
                      - second-op
                    parameters:
                      int-int-int:
                        name: Three integers
                        description: A parameter with three integer values.
                        cli: -3i
                        type: multi
                        parameters:
                          - name: First integer
                            type: int
                            default: 0
                          - name: Second integer
                            type: int
                            default: 0
                            constraints:
                              - type: interval
                                min: 0
                                max: 10
                          - name: Third integer
                            type: int
                            default: 0
                            constraints:
                              - type: interval
                                min: 0
                      bool-float-file-enum:
                        name: Mixed parameter
                        description: A parameter with four values.
                        cli: "-4"
                        type: multi
                        parameters:
                          - name: The bool
                            type: bool
                            default: true
                          - name: The float
                            description: null
                            type: float
                            default: 1.0
                            constraints:
                              - type: interval
                                min: 0.0
                          - name: The file
                            type: file
                            formats:
                              - .ms
                              - .vcf
                          - name: The enum
                            description: Choose one.
                            type: enum
                            default: 1
                            options:
                                - name: Option 0
                                - name: Option 1
                                - name: Option 2
                  - name: Nested parameters
                    operations:
                      - first-op
                    parameters:
                      opt-multi:
                        name: Optional multi-value
                        description: An optional parameter with two values.
                        type: optional
                        default: true
                        parameter:
                          name: null
                          description: The inner, multi-value parameter.
                          type: multi
                          parameters:
                            - name: A float
                              type: float
                              default: 0.99
                              constraints:
                                - type: interval
                                  min: 0.0
                                  max: 1.0
                            - name: A string
                              description: Type anything.
                              type: str
                      multi-opt:
                        name: Multiple optionals
                        description: A multi parameter where some are optional.
                        type: multi
                        parameters:
                          - type: optional
                            default: false
                            parameter:
                              type: int
                              default: 6
                          - description: This float is required.
                            type: float
                            default: 2.5
                            constraints:
                              - type: interval
                                max: 2.5
                          - name: Another float?
                            type: optional
                            default: true
                            parameter:
                              name: The second float
                              type: float
                              default: 100.8
            """
            )
        )

        # act
        parameter_list = RunRecord.from_yaml('path')

        # assert
        assert len(parameter_list.operation_trees) == 2
        assert len(parameter_list.parameter_groups) == 9

        # Bool
        bool_group = parameter_list.parameter_groups[0]
        assert bool_group.name == "Boolean parameters"
        assert len(bool_group.parameters) == 2

        true_bool = bool_group.parameters[0]
        assert isinstance(true_bool, BoolParameter)
        assert true_bool.name == "True bool"
        assert (
            true_bool.description
            == "This boolean parameter is true by default."
        )
        assert true_bool.flag == "--true-bool"
        assert true_bool.default_value == True
        assert len(true_bool.hints) == 0

        false_bool = bool_group.parameters[1]
        assert isinstance(false_bool, BoolParameter)
        assert false_bool.name == "False bool"
        assert (
            false_bool.description
            == "A bool parameter that is false by default."
        )
        assert false_bool.flag == "--false-bool"
        assert false_bool.default_value == False
        assert len(false_bool.hints) == 0

        # Int
        int_group = parameter_list.parameter_groups[1]
        assert int_group.name == "Integer parameters"
        assert len(int_group.parameters) == 7

        any_int_1 = int_group.parameters[0]
        assert isinstance(any_int_1, IntParameter)
        assert any_int_1.name == "Unbounded int"
        assert (
            any_int_1.description
            == "This integer can take any value."
        )
        assert any_int_1.flag == "--unbounded-int"
        assert any_int_1.default_value == 0
        assert len(any_int_1.hints) == 0

        any_int_2 = int_group.parameters[1]
        assert isinstance(any_int_2, IntParameter)
        assert any_int_2.name == "Another unbounded int"
        assert (
            any_int_2.description
            == "This time, the constraints are empty."
        )
        assert any_int_2.flag == "--int-unrestricted"
        assert any_int_2.default_value == 100
        assert len(any_int_2.hints) == 0

        min_int_1 = int_group.parameters[2]
        assert isinstance(min_int_1, IntParameter)
        assert min_int_1.name == "Lower-bounded int"
        assert (
            min_int_1.description
            == "This integer must be at least 50."
        )
        assert min_int_1.flag == "-i50"
        assert min_int_1.default_value == 75
        assert len(min_int_1.hints) == 1
        # TODO: is there a better way to check this than accessing the
        # private field of the parameter?
        min_int_1_constraint = min_int_1._constraints[0]
        assert isinstance(min_int_1_constraint, IntervalConstraint)
        assert min_int_1_constraint._lower_bound == 50
        assert min_int_1_constraint._lower_bound_inclusive
        assert min_int_1_constraint._upper_bound is None

        min_int_2 = int_group.parameters[3]
        assert isinstance(min_int_2, IntParameter)
        assert min_int_2.name == "Another lower-bounded int"
        assert (
            min_int_2.description
            == "Values 30+, upper bound is null."
        )
        assert min_int_2.flag == "-i30"
        assert min_int_2.default_value == 1300
        assert len(min_int_2.hints) == 1
        min_int_2_constraint = min_int_2._constraints[0]
        assert isinstance(min_int_2_constraint, IntervalConstraint)
        assert min_int_2_constraint._lower_bound == 30
        assert min_int_2_constraint._lower_bound_inclusive
        assert min_int_2_constraint._upper_bound is None

        max_int_1 = int_group.parameters[4]
        assert isinstance(max_int_1, IntParameter)
        assert max_int_1.name == "Upper-bounded int"
        assert (
            max_int_1.description
            == "This integer must be no more than 10."
        )
        assert max_int_1.flag == "-i10"
        assert max_int_1.default_value == -19
        assert len(max_int_1.hints) == 1
        max_int_1_constraint = max_int_1._constraints[0]
        assert isinstance(max_int_1_constraint, IntervalConstraint)
        assert max_int_1_constraint._lower_bound is None
        assert max_int_1_constraint._upper_bound == 10
        assert max_int_1_constraint._upper_bound_inclusive

        max_int_2 = int_group.parameters[5]
        assert isinstance(max_int_2, IntParameter)
        assert max_int_2.name == "Another upper-bounded int"
        assert (
            max_int_2.description
            == "No more than 15. Lower bound is null."
        )
        assert max_int_2.flag == "-i15"
        assert max_int_2.default_value == 15
        assert len(max_int_2.hints) == 1
        max_int_2_constraint = max_int_2._constraints[0]
        assert isinstance(max_int_2_constraint, IntervalConstraint)
        assert max_int_2_constraint._lower_bound is None
        assert max_int_2_constraint._upper_bound == 15
        assert max_int_2_constraint._upper_bound_inclusive

        bounded_int = int_group.parameters[6]
        assert isinstance(bounded_int, IntParameter)
        assert bounded_int.name == "Bounded int"
        assert (
            bounded_int.description
            == "This int is from 1 to 10."
        )
        assert bounded_int.flag == "-i1-10"
        assert bounded_int.default_value == 7
        assert len(bounded_int.hints) == 1
        bounded_int_constraint = bounded_int._constraints[0]
        assert isinstance(bounded_int_constraint, IntervalConstraint)
        assert bounded_int_constraint._lower_bound == 1
        assert bounded_int_constraint._lower_bound_inclusive
        assert bounded_int_constraint._upper_bound == 10
        assert bounded_int_constraint._upper_bound_inclusive

        #Float
        float_group = parameter_list.parameter_groups[2]
        assert float_group.name == "Floating-point parameters"
        assert len(float_group.parameters) == 7

        any_float_1 = float_group.parameters[0]
        assert isinstance(any_float_1, FloatParameter)
        assert any_float_1.name == "Unbounded float"
        assert (
            any_float_1.description
            == "This float can take any value."
        )
        assert any_float_1.flag == "--unbounded-float"
        assert any_float_1.default_value == approx(-3.14159)
        assert len(any_float_1.hints) == 0

        any_float_2 = float_group.parameters[1]
        assert isinstance(any_float_2, FloatParameter)
        assert any_float_2.name == "Another unbounded float"
        assert (
            any_float_2.description
            == "This time, the constraints are empty."
        )
        assert any_float_2.flag == "--float-unrestricted"
        assert any_float_2.default_value == approx(123.456)
        assert len(any_float_2.hints) == 0

        min_float_1 = float_group.parameters[2]
        assert isinstance(min_float_1, FloatParameter)
        assert min_float_1.name == "Lower-bounded float"
        assert (
            min_float_1.description
            == "This float must be at least 1.5."
        )
        assert min_float_1.flag == "-f1.5"
        assert min_float_1.default_value == approx(1.9)
        assert len(min_float_1.hints) == 1
        min_float_1_constraint = min_float_1._constraints[0]
        assert isinstance(min_float_1_constraint, IntervalConstraint)
        assert min_float_1_constraint._lower_bound == approx(1.5)
        assert min_float_1_constraint._lower_bound_inclusive
        assert min_float_1_constraint._upper_bound is None

        min_float_2 = float_group.parameters[3]
        assert isinstance(min_float_2, FloatParameter)
        assert (
            min_float_2.description
            == "Values 3.1+, upper bound is null."
        )
        assert min_float_2.flag == "-f3.1"
        assert min_float_2.default_value == approx(1300)
        assert len(min_float_2.hints) == 1
        min_float_2_constraint = min_float_2._constraints[0]
        assert isinstance(min_float_2_constraint, IntervalConstraint)
        assert min_float_2_constraint._lower_bound == approx(3.1)
        assert min_float_2_constraint._lower_bound_inclusive
        assert min_float_2_constraint._upper_bound is None

        max_float_1 = float_group.parameters[4]
        assert isinstance(max_float_1, FloatParameter)
        assert max_float_1.name == "Upper-bounded float"
        assert (
            max_float_1.description
            == "This float must be no more than -190.45."
        )
        assert max_float_1.flag == "-f-190.45"
        assert max_float_1.default_value == approx(-199)
        assert len(max_float_1.hints) == 1
        max_float_1_constraint = max_float_1._constraints[0]
        assert isinstance(max_float_1_constraint, IntervalConstraint)
        assert max_float_1_constraint._lower_bound is None
        assert max_float_1_constraint._upper_bound == approx(-190.45)
        assert max_float_1_constraint._upper_bound_inclusive

        max_float_2 = float_group.parameters[5]
        assert isinstance(max_float_2, FloatParameter)
        assert max_float_2.name == "Another upper-bounded float"
        assert (
            max_float_2.description
            == "No more than 13.13. Lower bound is null."
        )
        assert max_float_2.flag == "-f13.13"
        assert max_float_2.default_value == approx(-23094)
        assert len(max_float_2.hints) == 1
        max_float_2_constraint = max_float_2._constraints[0]
        assert isinstance(max_float_2_constraint, IntervalConstraint)
        assert max_float_2_constraint._lower_bound is None
        assert max_float_2_constraint._upper_bound == approx(13.13)
        assert max_float_2_constraint._upper_bound_inclusive

        bounded_float = float_group.parameters[6]
        assert isinstance(bounded_float, FloatParameter)
        assert bounded_float.name == "Bounded float"
        assert (
            bounded_float.description
            == "This float is between 0 and 1."
        )
        assert bounded_float.flag == "-f0-1"
        assert bounded_float.default_value == approx(0)
        assert len(bounded_float.hints) == 1
        bounded_float_constraint = bounded_float._constraints[0]
        assert isinstance(bounded_float_constraint, IntervalConstraint)
        assert bounded_float_constraint._lower_bound == approx(0)
        assert bounded_float_constraint._lower_bound_inclusive
        assert bounded_float_constraint._upper_bound == approx(1)
        assert bounded_float_constraint._upper_bound_inclusive

        # Enum
        enum_group = parameter_list.parameter_groups[3]
        assert enum_group.name == "Enum parameters"
        assert len(enum_group.parameters) == 2

        cli_enum = enum_group.parameters[0]
        assert isinstance(cli_enum, EnumParameter)
        assert cli_enum.name == "Enum parameter"
        assert (
            cli_enum.description
            == "Choose from a list of four values."
        )
        assert cli_enum.flag == "--enum"
        assert cli_enum.default_value == 2
        assert cli_enum.options == [
            "First option",
            "Second option",
            "Third option",
            "Fourth option",
        ]
        assert len(cli_enum.hints) == 0

        no_cli_enum = enum_group.parameters[1]
        assert isinstance(no_cli_enum, EnumParameter)
        assert no_cli_enum.name == "Dummy enum parameter"
        assert (
            no_cli_enum.description
            == "This parameter will not be in the CLI."
        )
        assert no_cli_enum.flag == ""
        assert no_cli_enum.default_value == 0
        assert no_cli_enum.options == [
            "Choose this...",
            "...or this!",
            "Or even this.",
        ]
        assert len(no_cli_enum.hints) == 0

        # String
        string_group = parameter_list.parameter_groups[4]
        assert string_group.name == "String parameters"
        assert len(string_group.parameters) == 5

        any_str = string_group.parameters[0]
        assert isinstance(any_str, StringParameter)
        assert any_str.name == "String"
        assert (
            any_str.description
            == "Enter a string. Anything goes!"
        )
        assert any_str.flag == "-s"
        assert any_str.default_value == ""
        assert len(any_str.hints) == 0

        max_len_str = string_group.parameters[1]
        assert isinstance(max_len_str, StringParameter)
        assert max_len_str.name == "Bounded string"
        assert (
            max_len_str.description
            == "Type at most 4 characters."
        )
        assert max_len_str.flag == "--s-max4"
        assert max_len_str.default_value == ""
        assert len(max_len_str.hints) == 1
        max_len_str_constraint = max_len_str._constraints[0]
        assert isinstance(max_len_str_constraint, MaxLengthConstraint)
        assert max_len_str_constraint._max_length == 4

        pattern_str = string_group.parameters[2]
        assert isinstance(pattern_str, StringParameter)
        assert pattern_str.name == "Pattern string"
        assert (
            pattern_str.description
            == "This parameter must be only As and Bs."
        )
        assert pattern_str.flag == "--sAB"
        assert pattern_str.default_value == ""
        assert len(pattern_str.hints) == 1
        pattern_str_constraint = pattern_str._constraints[0]
        assert isinstance(pattern_str_constraint, RegexConstraint)
        assert not pattern_str_constraint.valid("C")
        assert pattern_str_constraint.hint == "Any number of A or B."

        max_len_pattern_str = string_group.parameters[3]
        assert isinstance(max_len_pattern_str, StringParameter)
        assert max_len_pattern_str.name == "Bounded pattern string"
        assert (
            max_len_pattern_str.description
            == "This parameter must be at most 10 digits."
        )
        assert max_len_pattern_str.flag == "--phone-number"
        assert max_len_pattern_str.default_value == ""
        assert len(max_len_pattern_str.hints) == 2
        max_len_constraint = max_len_pattern_str._constraints[0]
        assert isinstance(max_len_constraint, MaxLengthConstraint)
        assert max_len_constraint._max_length == 10
        pattern_constraint = max_len_pattern_str._constraints[1]
        assert isinstance(pattern_constraint, RegexConstraint)
        assert not pattern_constraint.valid("invalid")
        assert pattern_constraint.hint == "Only digits."

        default_str = string_group.parameters[4]
        assert isinstance(default_str, StringParameter)
        assert default_str.name == "Default value string"
        assert (
            default_str.description
            == "This string already has a default value."
        )
        assert default_str.flag == "--default-str"
        assert default_str.default_value == "Hello"
        assert len(default_str.hints) == 1
        default_str_constraint = default_str._constraints[0]
        assert isinstance(default_str_constraint, MaxLengthConstraint)
        assert default_str_constraint._max_length == 20

        # File
        file_group = parameter_list.parameter_groups[5]
        assert file_group.name == "File parameters"
        assert len(file_group.parameters) == 6

        any_file = file_group.parameters[0]
        assert isinstance(any_file, FileParameter)
        assert any_file.name == "Any file"
        assert (
            any_file.description
            == "This allows one file of any type."
        )
        assert any_file.flag == "--any-file"
        assert any_file.default_value == []
        assert not any_file.strict
        assert any_file.accepted_formats is None
        assert any_file.expected_formats is None
        assert not any_file.multiple
        assert len(any_file.hints) == 0

        any_files = file_group.parameters[1]
        assert isinstance(any_files, FileParameter)
        assert any_files.name == "Any files"
        assert (
            any_files.description
            == "This allows many files of any type."
        )
        assert any_files.flag == "--any-files"
        assert any_files.default_value == []
        assert not any_files.strict
        assert any_files.accepted_formats is None
        assert any_files.expected_formats is None
        assert any_files.multiple
        assert len(any_files.hints) == 0

        not_strict_file = file_group.parameters[2]
        assert isinstance(not_strict_file, FileParameter)
        assert not_strict_file.name == "Expected type file"
        assert (
            not_strict_file.description
            == "One file of any type, image expected."
        )
        assert not_strict_file.flag == "--image"
        assert not_strict_file.default_value == []
        assert not not_strict_file.strict
        assert not_strict_file.accepted_formats is None
        assert not_strict_file.expected_formats == [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
        ]
        assert not not_strict_file.multiple
        assert len(not_strict_file.hints) == 0

        not_strict_multiple_files = file_group.parameters[3]
        assert isinstance(not_strict_multiple_files, FileParameter)
        assert not_strict_multiple_files.name == "Expected type files"
        assert (
            not_strict_multiple_files.description
            == "Multiple files, videos expected."
        )
        assert not_strict_multiple_files.flag == "--images"
        assert not_strict_multiple_files.default_value == []
        assert not not_strict_multiple_files.strict
        assert not_strict_multiple_files.accepted_formats is None
        assert not_strict_multiple_files.expected_formats == [
            ".mp4",
            ".webm",
        ]
        assert not_strict_multiple_files.multiple
        assert len(not_strict_multiple_files.hints) == 0

        strict_file = file_group.parameters[4]
        assert isinstance(strict_file, FileParameter)
        assert strict_file.name == "Specific type file"
        assert (
            strict_file.description
            == "One audio file."
        )
        assert strict_file.flag == "--song"
        assert strict_file.default_value == []
        assert strict_file.strict
        assert strict_file.accepted_formats == [
            ".mp3",
            ".wav",
        ]
        assert strict_file.expected_formats is None
        assert not strict_file.multiple
        assert len(strict_file.hints) == 0

        strict_multiple_files = file_group.parameters[5]
        assert isinstance(strict_multiple_files, FileParameter)
        assert strict_multiple_files.name == "Specific type files"
        assert (
            strict_multiple_files.description
            == "Multiple document files."
        )
        assert strict_multiple_files.flag == "--docs"
        assert strict_multiple_files.default_value == []
        assert strict_multiple_files.strict
        assert strict_multiple_files.accepted_formats == [
            ".doc",
            ".docx",
            ".odf",
            ".pdf",
        ]
        assert strict_multiple_files.expected_formats is None
        assert strict_multiple_files.multiple
        assert len(strict_multiple_files.hints) == 0

        # Optional
        optional_group = parameter_list.parameter_groups[6]
        assert optional_group.name == "Optional parameters"
        assert len(optional_group.parameters) == 6

        opt_bool = optional_group.parameters[0]
        assert isinstance(opt_bool, OptionalParameter)
        assert opt_bool.name == "Optional bool"
        assert opt_bool.description == "An optional bool parameter."
        assert not opt_bool.default_value
        assert len(opt_bool.hints) == 0
        inner_bool = opt_bool.parameter
        assert isinstance(inner_bool, BoolParameter)
        assert inner_bool.name == "Inner bool"
        assert inner_bool.description == "The inner parameter."
        assert inner_bool.flag == "--opt-bool"
        assert not inner_bool.default_value
        assert len(inner_bool.hints) == 0

        opt_int = optional_group.parameters[1]
        assert isinstance(opt_int, OptionalParameter)
        assert opt_int.name == "Optional int"
        assert (
            opt_int.description
            == "An optional int parameter, default true."
        )
        assert opt_int.default_value
        assert len(opt_int.hints) == 0
        inner_int = opt_int.parameter
        assert isinstance(inner_int, IntParameter)
        assert inner_int.name == "Inner int parameter"
        assert inner_int.description == ""
        assert inner_int.flag == "--opt-int"
        assert inner_int.default_value == 1
        assert len(inner_int.hints) == 1
        inner_int_constraint = inner_int._constraints[0]
        assert isinstance(inner_int_constraint, IntervalConstraint)
        assert inner_int_constraint._lower_bound == 1
        assert inner_int_constraint._lower_bound_inclusive
        assert inner_int_constraint._upper_bound is None

        opt_float = optional_group.parameters[2]
        assert isinstance(opt_float, OptionalParameter)
        assert opt_float.name == "Optional float"
        assert opt_float.description == "An optional float parameter."
        assert not opt_float.default_value
        assert len(opt_float.hints) == 0
        inner_float = opt_float.parameter
        assert isinstance(inner_float, FloatParameter)
        assert inner_float.name == "Inner float parameter"
        assert inner_float.description == ""
        assert inner_float.default_value == approx(-1.1)
        assert len(inner_float.hints) == 0

        opt_enum = optional_group.parameters[3]
        assert isinstance(opt_enum, OptionalParameter)
        assert opt_enum.name == "Optional enum"
        assert opt_enum.description == "An optional enum parameter."
        assert not opt_enum.default_value
        assert len(opt_enum.hints) == 0
        inner_enum = opt_enum.parameter
        assert isinstance(inner_enum, EnumParameter)
        assert inner_enum.name == ""
        assert (
            inner_enum.description
            == "An inner enum parameter with no name."
        )
        assert inner_enum.flag == "--opt-enum"
        assert inner_enum.default_value == 1
        assert inner_enum.options == ["A", "B", "C"]
        assert len(inner_enum.hints) == 0

        opt_str = optional_group.parameters[4]
        assert isinstance(opt_str, OptionalParameter)
        assert opt_str.name == "Optional string"
        assert opt_str.description == "An optional string parameter."
        assert not opt_str.default_value
        assert len(opt_str.hints) == 0
        inner_str = opt_str.parameter
        assert isinstance(inner_str, StringParameter)
        assert inner_str.name == ""
        assert inner_str.description == "The string."
        assert inner_str.flag == "--opt-str"
        assert inner_str.default_value == "example"
        assert len(inner_str.hints) == 1
        inner_str_constraint = inner_str._constraints[0]
        assert isinstance(inner_str_constraint, MaxLengthConstraint)
        assert inner_str_constraint._max_length == 20

        opt_file = optional_group.parameters[5]
        assert isinstance(opt_file, OptionalParameter)
        assert opt_file.name == "Optional files"
        assert opt_file.description == "An optional multi-file parameter."
        assert not opt_str.default_value
        assert len(opt_str.hints) == 0
        inner_file = opt_file.parameter
        assert isinstance(inner_file, FileParameter)
        assert inner_file.name == ""
        assert inner_file.description == ""
        assert inner_file.flag == "--opt-files"
        assert inner_file.default_value == []
        assert not inner_file.strict
        assert inner_file.multiple
        assert len(inner_file.hints) == 0

        # Multi-value
        multi_group = parameter_list.parameter_groups[7]
        assert multi_group.name == "Multi-value parameters"
        assert len(multi_group.parameters) == 2

        int_int_int = multi_group.parameters[0]
        assert isinstance(int_int_int, MultiParameter)
        assert int_int_int.name == "Three integers"
        assert (
            int_int_int.description
            == "A parameter with three integer values."
        )
        assert int_int_int.flag == "-3i"
        assert len(int_int_int.hints) == 0
        assert len(int_int_int.parameters) == 3
        first_int = int_int_int.parameters[0]
        assert isinstance(first_int, IntParameter)
        assert first_int.name == "First integer"
        assert first_int.description == ""
        assert first_int.default_value == 0
        assert len(first_int.hints) == 0
        second_int = int_int_int.parameters[1]
        assert isinstance(second_int, IntParameter)
        assert second_int.name == "Second integer"
        assert second_int.description == ""
        assert second_int.default_value == 0
        assert len(second_int.hints) == 1
        second_int_constraint = second_int._constraints[0]
        assert isinstance(second_int_constraint, IntervalConstraint)
        assert second_int_constraint._lower_bound == 0
        assert second_int_constraint._lower_bound_inclusive
        assert second_int_constraint._upper_bound == 10
        assert second_int_constraint._upper_bound_inclusive
        third_int = int_int_int.parameters[2]
        assert isinstance(third_int, IntParameter)
        assert third_int.name == "Third integer"
        assert third_int.description == ""
        assert third_int.default_value == 0
        assert len(third_int.hints) == 1
        third_int_constraint = third_int._constraints[0]
        assert isinstance(third_int_constraint, IntervalConstraint)
        assert third_int_constraint._lower_bound == 0
        assert third_int_constraint._lower_bound_inclusive
        assert third_int_constraint._upper_bound is None

        bool_float_file_enum = multi_group.parameters[1]
        assert isinstance(bool_float_file_enum, MultiParameter)
        assert bool_float_file_enum.name == "Mixed parameter"
        assert (
            bool_float_file_enum.description
            == "A parameter with four values."
        )
        assert bool_float_file_enum.flag == "-4"
        assert len(bool_float_file_enum.hints) == 0
        assert len(bool_float_file_enum.parameters) == 4
        bool_child = bool_float_file_enum.parameters[0]
        assert isinstance(bool_child, BoolParameter)
        assert bool_child.name == "The bool"
        assert bool_child.description == ""
        assert bool_child.default_value
        assert len(bool_child.hints) == 0
        float_child = bool_float_file_enum.parameters[1]
        assert isinstance(float_child, FloatParameter)
        assert float_child.name == "The float"
        assert float_child.description == ""
        assert float_child.default_value == approx(1.0)
        assert len(float_child.hints) == 1
        float_child_constraint = float_child._constraints[0]
        assert isinstance(float_child_constraint, IntervalConstraint)
        assert float_child_constraint._lower_bound == approx(0.0)
        assert float_child_constraint._lower_bound_inclusive
        assert float_child_constraint._upper_bound is None
        file_child = bool_float_file_enum.parameters[2]
        assert isinstance(file_child, FileParameter)
        assert file_child.name == "The file"
        assert file_child.description == ""
        assert file_child.default_value == []
        assert not file_child.strict
        assert file_child.accepted_formats is None
        assert file_child.expected_formats == [".ms", ".vcf"]
        assert not file_child.multiple
        assert len(file_child.hints) == 0
        enum_child = bool_float_file_enum.parameters[3]
        assert isinstance(enum_child, EnumParameter)
        assert enum_child.name == "The enum"
        assert enum_child.description == "Choose one."
        assert enum_child.default_value == 1
        assert enum_child.options == ["Option 0", "Option 1", "Option 2"]
        assert len(enum_child.hints) == 0

        # Nested
        nested_group = parameter_list.parameter_groups[8]
        assert nested_group.name == "Nested parameters"
        assert len(nested_group.parameters) == 2

        opt_multi = nested_group.parameters[0]
        assert isinstance(opt_multi, OptionalParameter)
        assert opt_multi.name == "Optional multi-value"
        assert (
            opt_multi.description
            == "An optional parameter with two values."
        )
        assert opt_multi.default_value
        assert len(opt_multi.hints) == 0
        multi_child = opt_multi.parameter
        assert isinstance(multi_child, MultiParameter)
        assert multi_child.name == ""
        assert (
            multi_child.description
            == "The inner, multi-value parameter."
        )
        assert len(multi_child.hints) == 0
        assert len(multi_child.parameters) == 2
        float_grandchild = multi_child.parameters[0]
        assert isinstance(float_grandchild, FloatParameter)
        assert float_grandchild.name == "A float"
        assert float_grandchild.description == ""
        assert float_grandchild.default_value == approx(0.99)
        assert len(float_grandchild.hints) == 1
        float_grandchild_constraint = float_grandchild._constraints[0]
        assert isinstance(float_grandchild_constraint, IntervalConstraint)
        assert float_grandchild_constraint._lower_bound == approx(0)
        assert float_grandchild_constraint._lower_bound_inclusive
        assert float_grandchild_constraint._upper_bound == approx(1)
        assert float_grandchild_constraint._upper_bound_inclusive
        str_grandchild = multi_child.parameters[1]
        assert isinstance(str_grandchild, StringParameter)
        assert str_grandchild.name == "A string"
        assert str_grandchild.description == "Type anything."
        assert str_grandchild.default_value == ""
        assert len(str_grandchild.hints) == 0

        multi_opt = nested_group.parameters[1]
        assert isinstance(multi_opt, MultiParameter)
        assert multi_opt.name == "Multiple optionals"
        assert (
            multi_opt.description
            == "A multi parameter where some are optional."
        )
        assert multi_opt.flag == ""
        assert len(multi_opt.hints) == 0
        assert len(multi_opt.parameters) == 3
        first_child = multi_opt.parameters[0]
        assert isinstance(first_child, OptionalParameter)
        assert first_child.name == ""
        assert first_child.description == ""
        assert not first_child.default_value
        assert len(first_child.hints) == 0
        int_grandchild = first_child.parameter
        assert isinstance(int_grandchild, IntParameter)
        assert int_grandchild.name == ""
        assert int_grandchild.description == ""
        assert int_grandchild.flag == ""
        assert int_grandchild.default_value == 6
        assert len(int_grandchild.hints) == 0
        second_child = multi_opt.parameters[1]
        assert isinstance(second_child, FloatParameter)
        assert second_child.name == ""
        assert second_child.description == "This float is required."
        assert second_child.flag == ""
        assert second_child.default_value == approx(2.5)
        assert len(second_child.hints) == 1
        second_child_constraint = second_child._constraints[0]
        assert isinstance(second_child_constraint, IntervalConstraint)
        assert second_child_constraint._lower_bound is None
        assert second_child_constraint._upper_bound == approx(2.5)
        assert second_child_constraint._upper_bound_inclusive
        third_child = multi_opt.parameters[2]
        assert isinstance(third_child, OptionalParameter)
        assert third_child.name == "Another float?"
        assert third_child.description == ""
        assert third_child.default_value
        assert len(third_child.hints) == 0
        float_grandchild = third_child.parameter # Reused variable
        assert isinstance(float_grandchild, FloatParameter)
        assert float_grandchild.name == "The second float"
        assert float_grandchild.description == ""
        assert float_grandchild.default_value == approx(100.8)
        assert len(float_grandchild.hints) == 0
