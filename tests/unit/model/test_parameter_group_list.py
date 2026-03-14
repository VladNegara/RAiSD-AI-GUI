from pytest import approx, fixture, raises
import re

from gui.model.parameter_group_list import ParameterGroupList
from gui.model.parameter_group import ParameterGroup
from gui.model.parameter import (
    OptionalParameter,
    MultiParameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
    FileParameter,
)

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
                        max: 13.13
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
                        description: This parameter must be only As and Bs.
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
                        max_length: 20
                        default: Hello
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
                        cli: --opt-bool
                        type: optional
                        parameter:
                          name: Inner bool
                          description: The inner parameter.
                          type: bool
                          default: false
                      opt-int:
                        name: Optional int
                        description: An optional int parameter, default true.
                        cli: --opt-int
                        type: optional
                        default: true
                        parameter:
                          name: Inner int parameter
                          description: null
                          type: int
                          min: 1
                          default: 1
                      opt-float:
                        name: Optional float
                        description: An optional float parameter.
                        cli: --opt-float
                        type: optional
                        default: false
                        parameter:
                          name: Inner float parameter
                          type: float
                          min: null
                          max: null
                          default: -1.1
                      opt-enum:
                        name: Optional enum
                        description: An optional enum parameter.
                        cli: --opt-enum
                        type: optional
                        parameter:
                          description: An inner enum parameter with no name.
                          type: enum
                          options:
                            - name: A
                            - name: B
                            - name: C
                          default: 1
                      opt-str:
                        name: Optional string
                        description: An optional string parameter.
                        cli: --opt-str
                        type: optional
                        default: null
                        parameter:
                          name: null
                          description: The string.
                          type: str
                          default: example
                          max_length: 20
                      opt-file:
                        name: Optional files
                        description: An optional multi-file parameter.
                        cli: --opt-files
                        type: optional
                        parameter:
                            type: file
                            multiple: true
                  - name: Multi-value parameters
                    operations:
                      - first-op
                      - second-op
                    parameters:
                      int-int-int:
                        name: Three integers
                        descriptions: A parameter with three integer values.
                        cli: -3i
                        type: multi
                        parameters:
                          - name: First integer
                            type: int
                            default: 0
                          - name: Second integer
                            type: int
                            min: 0
                            max: 10
                            default: 0
                          - name: Third integer
                            type: int
                            default: 0
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
                            min: 0.0
                            default: 1.0
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
                              min: 0.0
                              max: 1.0
                              default: 0.99
                            - name: A string
                              description: Type anything
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
                            max: 2.5
                            default: 2.5
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
        parameter_list = ParameterGroupList.from_yaml('path')

        # assert
        assert parameter_list.operations == {
            "first-op": True,
            "second-op": True,
        }
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

        false_bool = bool_group.parameters[1]
        assert isinstance(false_bool, BoolParameter)
        assert false_bool.name == "False bool"
        assert (
            false_bool.description
            == "A bool parameter that is false by default."
        )
        assert false_bool.flag == "--false-bool"
        assert false_bool.default_value == False

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
        assert any_int_1.lower_bound is None
        assert any_int_1.upper_bound is None

        any_int_2 = int_group.parameters[1]
        assert isinstance(any_int_2, IntParameter)
        assert any_int_2.name == "Another unbounded int"
        assert (
            any_int_2.description
            == "This time, the bounds are explicitly null."
        )
        assert any_int_2.flag == "--int-unrestricted"
        assert any_int_2.default_value == 100
        assert any_int_2.lower_bound is None
        assert any_int_2.upper_bound is None

        min_int_1 = int_group.parameters[2]
        assert isinstance(min_int_1, IntParameter)
        assert min_int_1.name == "Lower-bounded int"
        assert (
            min_int_1.description
            == "This integer must be at least 50."
        )
        assert min_int_1.flag == "-i50"
        assert min_int_1.default_value == 75
        assert min_int_1.lower_bound == 50
        assert min_int_1.upper_bound is None

        min_int_2 = int_group.parameters[3]
        assert isinstance(min_int_2, IntParameter)
        assert min_int_2.name == "Another lower-bounded int"
        assert (
            min_int_2.description
            == "Values 30+, upper bound is null."
        )
        assert min_int_2.flag == "-i30"
        assert min_int_2.default_value == 1300
        assert min_int_2.lower_bound == 30
        assert min_int_2.upper_bound is None

        max_int_1 = int_group.parameters[4]
        assert isinstance(max_int_1, IntParameter)
        assert max_int_1.name == "Upper-bounded int"
        assert (
            max_int_1.description
            == "This integer must be no more than 10."
        )
        assert max_int_1.flag == "-i10"
        assert max_int_1.default_value == -19
        assert max_int_1.lower_bound is None
        assert max_int_1.upper_bound == 10

        max_int_2 = int_group.parameters[5]
        assert isinstance(max_int_2, IntParameter)
        assert max_int_2.name == "Another upper-bounded int"
        assert (
            max_int_2.description
            == "No more than 15. Lower bound is null."
        )
        assert max_int_2.flag == "-i15"
        assert max_int_2.default_value == 15
        assert max_int_2.lower_bound is None
        assert max_int_2.upper_bound == 15

        bounded_int = int_group.parameters[6]
        assert isinstance(bounded_int, IntParameter)
        assert bounded_int.name == "Bounded int"
        assert (
            bounded_int.description
            == "This int is from 1 to 10."
        )
        assert bounded_int.flag == "-i1-10"
        assert bounded_int.default_value == 7
        assert bounded_int.lower_bound == 1
        assert bounded_int.upper_bound == 10

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
        assert any_float_1.lower_bound is None
        assert any_float_1.upper_bound is None

        any_float_2 = float_group.parameters[1]
        assert isinstance(any_float_2, FloatParameter)
        assert any_float_2.name == "Another unbounded float"
        assert (
            any_float_2.description
            == "This time, the bounds are explicitly null."
        )
        assert any_float_2.flag == "--float-unrestricted"
        assert any_float_2.default_value == approx(123.456)
        assert any_float_2.lower_bound is None
        assert any_float_2.upper_bound is None

        min_float_1 = float_group.parameters[2]
        assert isinstance(min_float_1, FloatParameter)
        assert min_float_1.name == "Lower-bounded float"
        assert (
            min_float_1.description
            == "This float must be at least 1.5."
        )
        assert min_float_1.flag == "-f1.5"
        assert min_float_1.default_value == approx(1.9)
        assert min_float_1.lower_bound == approx(1.5)
        assert min_float_1.upper_bound is None

        min_float_2 = float_group.parameters[3]
        assert isinstance(min_float_2, FloatParameter)
        assert (
            min_float_2.description
            == "Values 3.1+, upper bound is null."
        )
        assert min_float_2.flag == "-f3.1"
        assert min_float_2.default_value == approx(1300)
        assert min_float_2.lower_bound == approx(3.1)
        assert min_float_2.upper_bound is None

        max_float_1 = float_group.parameters[4]
        assert isinstance(max_float_1, FloatParameter)
        assert max_float_1.name == "Upper-bounded float"
        assert (
            max_float_1.description
            == "This float must be no more than -190.45."
        )
        assert max_float_1.flag == "-f-190.45"
        assert max_float_1.default_value == approx(-199)
        assert max_float_1.lower_bound is None
        assert max_float_1.upper_bound == approx(-190.45)

        max_float_2 = float_group.parameters[5]
        assert isinstance(max_float_2, FloatParameter)
        assert max_float_2.name == "Another upper-bounded float"
        assert (
            max_float_2.description
            == "No more than 13.13. Lower bound is null."
        )
        assert max_float_2.flag == "-f13.13"
        assert max_float_2.default_value == approx(-23094)
        assert max_float_2.lower_bound is None
        assert max_float_2.upper_bound == approx(13.13)

        bounded_float = float_group.parameters[6]
        assert isinstance(bounded_float, FloatParameter)
        assert bounded_float.name == "Bounded float"
        assert (
            bounded_float.description
            == "This float is between 0 and 1."
        )
        assert bounded_float.flag == "-f0-1"
        assert bounded_float.default_value == approx(0)
        assert bounded_float.lower_bound == approx(0)
        assert bounded_float.upper_bound == approx(1)

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
        assert any_str.max_length is None

        max_len_str = string_group.parameters[1]
        assert isinstance(max_len_str, StringParameter)
        assert max_len_str.name == "Bounded string"
        assert (
            max_len_str.description
            == "Type at most 4 characters."
        )
        assert max_len_str.flag == "--s-max4"
        assert max_len_str.default_value == ""
        assert max_len_str.max_length == 4

        pattern_str = string_group.parameters[2]
        assert isinstance(pattern_str, StringParameter)
        assert pattern_str.name == "Pattern string"
        assert (
            pattern_str.description
            == "This parameter must be only As and Bs."
        )
        assert pattern_str.flag == "--sAB"
        assert pattern_str.default_value == ""
        assert pattern_str.max_length is None
        pattern_str.value = "C"
        assert not pattern_str.valid

        max_len_pattern_str = string_group.parameters[3]
        assert isinstance(max_len_pattern_str, StringParameter)
        assert max_len_pattern_str.name == "Bounded pattern string"
        assert (
            max_len_pattern_str.description
            == "This parameter must be at most 10 digits."
        )
        assert max_len_pattern_str.flag == "--phone-number"
        assert max_len_pattern_str.default_value == ""
        assert max_len_pattern_str.max_length == 10
        max_len_pattern_str.value = "invalid"
        assert not max_len_pattern_str.valid

        default_str = string_group.parameters[4]
        assert isinstance(default_str, StringParameter)
        assert default_str.name == "Default value string"
        assert (
            default_str.description
            == "This string already has a default value."
        )
        assert default_str.flag == "--default-str"
        assert default_str.default_value == "Hello"
        assert default_str.max_length == 20
