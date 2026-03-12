from pytest import fixture
import re

from gui.model.parameter import Parameter, BoolParameter, IntParameter, FloatParameter, StringParameter

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
        param = self.bool_param
        self.signal_emitted = False
        self.new_value = True

        def on_value_changed(value, valid):
            self.signal_emitted
            self.signal_emitted = True
            assert value == self.new_value
            assert valid is True

        param.value_changed.connect(on_value_changed)
        param.value = self.new_value
        assert self.signal_emitted is True

class TestIntParameter:
    """Tests for IntParameter class."""

    @fixture(autouse=True)
    def set_int_param(self):
        self.int_param = IntParameter(
            name="testint", 
            description="Test int parameter", 
            flag="--testint", 
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
        assert param.flag == "--testint"
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
        assert param.to_cli('IMG-GEN') == f"{param.flag} {param.value}"
        param.value = new_value = 5
        assert param.to_cli('MDL-GEN') == f"{param.flag} {new_value}"
        assert param.to_cli('SWP_SCN') == ""
        param.enabled = False
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when IntParameter value changes."""
        param = self.int_param
        self.signal_emitted = False
        self.new_value = 5

        def on_value_changed(value, valid):
            self.signal_emitted
            self.signal_emitted = True
            assert value == self.new_value
            assert valid is True

        param.value_changed.connect(on_value_changed)
        param.value = self.new_value
        assert self.signal_emitted is True

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when IntParameter value changes."""
        param = self.int_param
        self.signal_emitted = False
        self.new_value = 15

        def on_value_changed(value, valid):
            self.signal_emitted
            self.signal_emitted = True
            assert value == self.new_value
            assert valid is False

        param.value_changed.connect(on_value_changed)
        param.value = self.new_value
        assert self.signal_emitted is True

class TestFloatParameter:
    """Tests for FloatParameter class."""

    @fixture(autouse=True)
    def set_float_param(self):
        self.float_param = FloatParameter(
            name="testfloat", 
            description="Test float parameter", 
            flag="--testfloat", 
            default_value=0.0, 
            lower_bound=-10.0, 
            upper_bound=10.0
        )
    
    def test_init_values(self):
        """Test FloatParameter initialization with default value."""
        param = self.float_param
        assert param.name == "testfloat"
        assert param.description == "Test float parameter"
        assert param.flag == "--testfloat"
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
        assert param.to_cli() == f"{param.flag} {param.value}"
        param.value = new_value = 5.0
        assert param.to_cli() == f"{param.flag} {new_value}"

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when FloatParameter value changes."""
        param = self.float_param
        self.signal_emitted = False
        self.new_value = 5.0

        def on_value_changed(value, valid):
            self.signal_emitted
            self.signal_emitted = True
            assert value == self.new_value
            assert valid is True

        param.value_changed.connect(on_value_changed)
        param.value = self.new_value
        assert self.signal_emitted is True

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when FloatParameter value changes."""
        param = self.float_param
        self.signal_emitted = False
        self.new_value = 15.0

        def on_value_changed(value, valid):
            self.signal_emitted
            self.signal_emitted = True
            assert value == self.new_value
            assert valid is False

        param.value_changed.connect(on_value_changed)
        param.value = self.new_value
        assert self.signal_emitted is True

class TestStringParameter:
    """Tests for StringParameter class."""

    @fixture(autouse=True)
    def set_string_param(self):
        self.string_param = StringParameter(
            name="teststring",
            description="Test string parameter",
            flag="--teststring",
            default_value="default",
            max_length=20,
            pattern=re.compile(r"\b[a-z]+\b")
        )

    def test_init_values(self):
        """Test StringParameter initialization with default value."""
        param = self.string_param
        assert param.name == "teststring"
        assert param.description == "Test string parameter"
        assert param.flag == "--teststring"
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
        assert param.to_cli() == f"{param.flag} {param.value}"
        param.value = new_value = "new_value"
        assert param.to_cli() == f"{param.flag} {new_value}"

    def test_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when StringParameter value changes."""
        param = self.string_param
        self.signal_emitted = False
        self.new_value = "newvalue"

        def on_value_changed(value, valid):
            self.signal_emitted
            self.signal_emitted = True
            assert value == self.new_value
            assert valid is True

        param.value_changed.connect(on_value_changed)
        param.value = self.new_value
        assert self.signal_emitted is True

    def test_invalid_value_changed_signal_emitted(self):
        """Test that value_changed signal is emitted when StringParameter value changes."""
        param = self.string_param
        self.signal_emitted = False
        self.new_value = "invalid value"

        def on_value_changed(value, valid):
            self.signal_emitted
            self.signal_emitted = True
            assert value == self.new_value
            assert valid is False

        param.value_changed.connect(on_value_changed)
        param.value = self.new_value
        assert self.signal_emitted is True