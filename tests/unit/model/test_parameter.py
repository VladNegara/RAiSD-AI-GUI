from pytest import fixture
import re

from gui.model.parameter import (
    Parameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    StringParameter,
    EnumParameter,
    FileParameter,
    OptionalParameter,
    MultiParameter,
)

class TestBoolParameter:
    """Tests for BoolParameter class."""

    @fixture(autouse=True)
    def set_bool_param(self):
        self.bool_param = BoolParameter(
            name="testbool", 
            description="Test bool parameter", 
            flag="--testbool", 
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=False
        )

    def test_init_values(self):
        """Test BoolParameter initialization with default value."""
        param = self.bool_param
        assert param.name == "testbool"
        assert param.description == "Test bool parameter"
        assert param.flag == "--testbool"
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value is False
        assert param.default_value is False

    def test_set_value(self):
        """Test setting BoolParameter value."""
        param = self.bool_param
        param.value = True
        assert param.value is True

    def test_reset_value(self):
        """Test resetting BoolParameter value to default."""
        param = self.bool_param
        param.value = True
        param.reset_value()
        assert param.value is False

    def test_valid(self):
        """Test BoolParameter validity."""
        param = self.bool_param
        assert param.valid is True

    def test_to_cli(self):
        """Test BoolParameter command-line representation."""
        param = self.bool_param
        assert param.to_cli('IMG-GEN') == ""
        param.value = True
        assert param.to_cli('SWP-SCN') == ""
        assert param.to_cli('IMG-GEN') == param.flag
        assert param.to_cli('MDL-GEN') == param.flag
        param.enabled = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when BoolParameter value changes."""
        # arrange
        param = self.bool_param
        self.signal_emitted = False
        self.new_value = True
        self.value = False
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted is True
        assert self.value == self.new_value
        assert self.valid == True

class TestIntParameter:
    """Tests for IntParameter class."""

    @fixture(autouse=True)
    def set_int_param(self):
        self.int_param = IntParameter(
            name="testint", 
            description="Test int parameter", 
            flag="--testint ", 
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=0, 
            lower_bound=-10, 
            upper_bound=10
        )
    
    def test_init_values(self):
        """Test IntParameter initialization with default value."""
        param = self.int_param
        assert param.name == "testint"
        assert param.description == "Test int parameter"
        assert param.flag == "--testint "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == 0
        assert param.default_value == 0
        assert param.lower_bound == -10
        assert param.upper_bound == 10

    def test_set_value(self):
        """Test setting IntParameter value."""
        param = self.int_param
        param.value = 5
        assert param.value == 5

    def test_reset_value(self):
        """Test resetting IntParameter value to default."""
        param = self.int_param
        param.value = 5
        param.reset_value()
        assert param.value == 0

    def test_valid(self):
        """Test IntParameter validity."""
        param = self.int_param
        assert param.valid is True
        param.value = -15
        assert param.valid is False
        param.value = 15
        assert param.valid is False
        param.value = 5
        assert param.valid is True

    def test_to_cli(self):
        """Test IntParameter command-line representation."""
        param = self.int_param
        assert param.to_cli('IMG-GEN') == f"{param.flag}{param.value}"
        param.value = new_value = 5
        assert param.to_cli('MDL-GEN') == f"{param.flag}{new_value}"
        assert param.to_cli('SWP_SCN') == ""
        param.enabled = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when IntParameter value changes."""
        # arrange
        param = self.int_param
        self.signal_emitted = False
        self.value = 1
        self.new_value = 5
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted is True
        assert self.value == self.new_value
        assert self.valid == True

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when IntParameter value changes."""
        # arrange
        param = self.int_param
        self.signal_emitted = False
        self.value = 1
        self.new_value = 15
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        # act
        param.value_changed.connect(on_value_changed)
        param.value = self.new_value

        # assert
        assert self.signal_emitted is True
        assert self.value == self.new_value
        assert self.valid == False

class TestFloatParameter:
    """Tests for FloatParameter class."""

    @fixture(autouse=True)
    def set_float_param(self):
        self.float_param = FloatParameter(
            name="testfloat", 
            description="Test float parameter", 
            flag="--testfloat ", 
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=0.0, 
            lower_bound=-10.0, 
            upper_bound=10.0
        )
    
    def test_init_values(self):
        """Test FloatParameter initialization with default value."""
        param = self.float_param
        assert param.name == "testfloat"
        assert param.description == "Test float parameter"
        assert param.flag == "--testfloat "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == 0.0
        assert param.default_value == 0.0
        assert param.lower_bound == -10.0
        assert param.upper_bound == 10.0

    def test_set_value(self):
        """Test setting FloatParameter value."""
        param = self.float_param
        param.value = 5.0
        assert param.value == 5.0

    def test_reset_value(self):
        """Test resetting FloatParameter value to default."""
        param = self.float_param
        param.value = 5.0
        param.reset_value()
        assert param.value == 0.0

    def test_valid(self):
        """Test FloatParameter validity."""
        param = self.float_param
        assert param.valid is True
        param.value = -15.0
        assert param.valid is False
        param.value = 15.0
        assert param.valid is False
        param.value = 5.0
        assert param.valid is True

    def test_to_cli(self):
        """Test FloatParameter command-line representation."""
        param = self.float_param
        assert param.to_cli('IMG-GEN') == f"{param.flag}{param.value}"
        param.value = new_value = 5.0
        assert param.to_cli('MDL-GEN') == f"{param.flag}{new_value}"
        assert param.to_cli('SWP-SCN') == ""
        param.enabled = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when FloatParameter value changes."""
        # arrange
        param = self.float_param
        self.signal_emitted = False
        self.value = 1.0
        self.new_value = 5.0
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted is True
        assert self.value == self.new_value
        assert self.valid == True

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when FloatParameter value changes."""
        # arrange
        param = self.float_param
        self.signal_emitted = False
        self.value = 1.0
        self.new_value = 15.0
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted is True
        assert self.value == self.new_value
        assert self.valid == False

class TestStringParameter:
    """Tests for StringParameter class."""

    @fixture(autouse=True)
    def set_string_param(self):
        self.string_param = StringParameter(
            name="teststring",
            description="Test string parameter",
            flag="--teststring ",
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value="default",
            max_length=20,
            pattern=re.compile(r"\b[a-z]+\b")
        )

    def test_init_values(self):
        """Test StringParameter initialization with default value."""
        param = self.string_param
        assert param.name == "teststring"
        assert param.description == "Test string parameter"
        assert param.flag == "--teststring "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == "default"
        assert param.default_value == "default"
        assert param.max_length == 20

    def test_set_value(self):
        """Test setting StringParameter value."""
        param = self.string_param
        param.value = "new_value"
        assert param.value == "new_value"

    def test_reset_value(self):
        """Test resetting StringParameter value to default."""
        param = self.string_param
        param.value = "new_value"
        param.reset_value()
        assert param.value == "default"

    def test_valid_length(self):
        """Test StringParameter length validity."""
        param = self.string_param
        assert param.valid is True
        param.value = "2invalidvaluesarewalkingonthestreet"
        assert param.valid is False
        param.value = "validvalue"
        assert param.valid is True

    def test_valid_pattern(self):
        """Test StringParameter pattern validity."""
        param = self.string_param
        assert param.valid is True
        param.value = "invalid value"
        assert param.valid is False
        param.value = "validvalue"
        assert param.valid is True

    def test_to_cli(self):
        """Test StringParameter command-line representation."""
        param = self.string_param
        assert param.to_cli('IMG-GEN') == f"{param.flag}{param.value}"
        param.value = new_value = "new_value"
        assert param.to_cli('MDL-GEN') == f"{param.flag}{new_value}"
        assert param.to_cli('SWP-SCN') == ""
        param.enabled = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when StringParameter value changes."""
        # arrange
        param = self.string_param
        self.signal_emitted = False
        self.value = ""
        self.new_value = "newvalue"
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted is True
        assert self.value == self.new_value
        assert self.valid == True

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when StringParameter value changes."""
        # arrange
        param = self.string_param
        self.signal_emitted = False
        self.value = "a"
        self.new_value = "invalid value"
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted is True
        assert self.value == self.new_value
        assert self.valid == False

class TestEnumParameter:
    """Tests for EnumParameter class."""

    @fixture(autouse=True)
    def set_enum_param(self):
        self.enum_param = EnumParameter(
            name="testenum",
            description="Test enum parameter",
            flag="--testenum ",
            operations={'IMG-GEN', 'MDL-GEN'},
            options=[("discard SNP", "D"), ("input N per SNP", "I"), ("represent N through a mask", "M 2"), ("ignore allele pairs with N", "A")],
            default_value= 0,
        )

    def test_init_values(self):
        """Test EnumParameter initialization with default value"""
        param = self.enum_param
        assert param.name == "testenum"
        assert param.description == "Test enum parameter"
        assert param.flag == "--testenum "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.options[1] == "input N per SNP"
        assert param.default_value == 0

    def test_set_value(self):
        """Test setting EnumParameter value."""
        param = self.enum_param
        param.value = 1
        assert param.value == 1
    
    def rest_reset_value(self):
        """Test resetting EnumParameter value."""
        param = self.enum_param
        param.value = 1
        param.reset_value()
        assert param.value == 0
    
    def test_to_cli(self):
        """Test EnumParameter command-line representation."""
        param = self.enum_param
        assert param.to_cli('IMG-GEN') == "--testenum D"
        param.value = new_value = 3
        assert param.to_cli('MDL-GEN') == "--testenum A"
        assert param.to_cli('SWP-SCN') == ""
        param.enabled = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when EnumParameter value changes."""
        # arrange
        param = self.enum_param
        self.signal_emitted = False
        self.value = 5
        self.new_value = 3
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert self.valid

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when EnumParameter value changes."""
        # arrange
        param = self.enum_param
        self.signal_emitted = False
        self.value = 0
        self.new_value = 5
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert not self.valid

class TestFileParameter:
    """Tests for FileParameter class."""

    @fixture(autouse=True)
    def set_file_param(self, tmp_path):

        self.valid_file = tmp_path / "sample.vcf"
        self.valid_file.write_text("data")
        self.second_valid_file = tmp_path / "test.vcf"
        self.second_valid_file.write_text("data")
        self.invalid_file = tmp_path / "sample.txt"
        self.invalid_file.write_text("data")

        self.file_param = FileParameter(
            name="testfile",
            description="Test file parameter",
            flag="--testfile ",
            operations={'IMG-GEN', 'MDL-GEN'},
            accepted_formats=[".vcf"],
            strict=True,
            multiple=True,
            default_value=[str(self.valid_file)]
        )

    def test_init_values(self):
        """Test FileParameter initialization with default value."""
        param = self.file_param
        assert param.name == "testfile"
        assert param.description == "Test file parameter"
        assert param.flag == "--testfile "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.accepted_formats == [".vcf"]
        assert param.strict
        assert param.multiple

    def test_set_value(self):
        """Test setting FileParameter value."""
        param = self.file_param
        param.value = [str(self.valid_file)]
        assert param.value == [str(self.valid_file)]

    def test_reset_value(self):
        """Test resetting FileParameter value to default."""
        param = self.file_param
        param.value = ["newfile.txt"]
        param.reset_value()
        assert param.value == [str(self.valid_file)]

    def test_valid_format(self):
        """Test FileParameter format validity."""
        param = self.file_param
        param.value = [str(self.valid_file)]
        assert param.valid

    def test_valid_file_count(self):
        """Test FileParameter validity when no file is selected."""
        param = self.file_param
        param.value = [str(self.invalid_file)]
        assert not param.valid
    
    def test_multiple_false_rejects_two_files(self):
        """Two files should be invalid when multiple=False."""
        param = FileParameter(
            name="testfile",
            description="Test file parameter",
            flag="--testfile",
            operations={'IMG-GEN', 'MDL-GEN'},
            accepted_formats=[".vcf"],
            strict=True,
            multiple=False,
            default_value=[str(self.valid_file)]
        )
        param.value = [str(self.valid_file), str(self.valid_file)]
        assert not param.valid

    def test_multiple_true_accepts_two_files(self):
        """Two valid files should be valid when multiple=True."""
        param = self.file_param
        param.value = [str(self.valid_file), str(self.second_valid_file)]
        assert param.valid

    def test_to_cli(self):
        """Test FileParameter command-line representation."""
        param = self.file_param
        # Doesn't make much sense, but it's expected behavior.
        assert (
            param.to_cli('IMG-GEN')
            == f"--testfile {self.valid_file}"
        )


    def test_value_changed_emitted(self):
        """Test that value_changed signal is emitted when FileParameter value changes."""
        # For now, no way to test for valid value. Maybe we make a temp file?
        # arrange
        param = self.file_param
        self.signal_emitted = False
        self.value = []
        self.new_value = [str(self.second_valid_file)]
        self.valid = True

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert self.valid

class TestOptionalParameter:
    """Tests for OptionalParameter class."""

    @fixture(autouse=True)
    def set_optional_parameter(self):
        self.int_param = IntParameter(
            name="testint", 
            description="Test int parameter", 
            flag="--testint ", 
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=0, 
            lower_bound=-10, 
            upper_bound=10
            )
        self.optional_param = OptionalParameter(
            name="testoptional",
            description="Test optional parameter",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value = True,
            parameter=self.int_param
        )

    def test_init_values(self):
        """Test OptionalParameter initialization with default value."""
        param = self.optional_param
        assert param.name == "testoptional"
        assert param.description == "Test optional parameter"
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.default_value
        assert param.parameter == self.int_param
        assert self.int_param.enabled

    def test_set_value(self):
        """Test setting OptionalParameter value."""
        param = self.optional_param
        param.value = False
        assert not self.int_param.enabled

    def test_reset_value(self):
        """Test resetting OptionalParameter value."""
        param = self.optional_param
        param.value = False
        param.reset_value()
        assert self.int_param.enabled

    def test_valid(self):
        """Test OptionalParameter validity."""
        param = self.optional_param
        assert param.valid
        param.value = False
        assert param.valid
        self.int_param.value = -11
        assert param.valid
        param.value = True
        assert not param.valid

    def test_to_cli(self):
        """Test OptionalParameter comand-line representation."""
        param = self.optional_param
        # If OptionalParameter value is true, to_cli gives the cli
        # represenation of the inner parameter.
        assert param.to_cli('IMG-GEN') == "--testint 0"
        assert param.to_cli('SWP-SCN') == ""
        param.value = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when OptionalParameter values changes."""
        # arrange
        param = self.optional_param
        self.signal_emitted = False
        self.value = True
        self.new_value = False
        self.valid = False

        def on_value_changed(value, valid):
            self.signal_emitted = True
            self.value = value
            self.valid = valid

        param.value_changed.connect(on_value_changed)

        # act
        param.value = self.new_value

        # assert
        assert self.signal_emitted
        assert self.value == self.new_value
        assert self.valid

class TestMultiParameter:
    """Tests for MultiParameter class."""

    @fixture(autouse=True)
    def set_multi_param(self):
        self.int_param = IntParameter(
            name="testint", 
            description="Test int parameter", 
            flag="", 
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=0, 
            lower_bound=-10, 
            upper_bound=10
            )
        self.bool_param = BoolParameter(
            name="testbool", 
            description="Test bool parameter", 
            flag="--testbool", 
            operations={'IMG-GEN'},
            default_value=False
            )
        self.multi_param = MultiParameter(
            name="testmulti",
            description="Test multi parameter",
            flag="--testmulti",
            operations={"IMG-GEN", "MDL-GEN"},
            parameters=[self.int_param, self.bool_param]
        )

    def test_init_values(self):
        """Test MultiParameter initial values"""
        param = self.multi_param
        assert param.name == "testmulti"
        assert param.description == "Test multi parameter"
        assert param.flag == "--testmulti"
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == ()

    def test_reset_value(self):
        """Test resetting MultiParameter's inner parameters to default."""
        param=self.multi_param
        self.int_param.value = 5
        self.bool_param.value = True
        param.reset_value()
        assert self.int_param.value == 0
        assert self.bool_param.value == False

    def test_valid(self):
        """Test MultiParameter validity."""
        param = self.multi_param
        assert param.valid
        self.int_param.value = -11
        assert not param.valid

    def test_to_cli(self):
        """Test MultiParameter command-line representation."""
        param = self.multi_param
        assert param.to_cli('IMG-GEN') == f"{param.flag}{self.int_param.value}"
        self.bool_param.value = True
        assert param.to_cli('IMG-GEN') == f"{param.flag}{self.int_param.value} {self.bool_param.flag}"
        assert param.to_cli('SWP_SCN') == ""
