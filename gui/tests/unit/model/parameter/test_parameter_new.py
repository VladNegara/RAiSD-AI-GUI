from pytest import fixture, skip

from gui.model.parameter import (
    BoolParameter,
    IntParameter,
    FloatParameter,
    StringParameter,
    EnumParameter,
    FileParameter,
    OptionalParameter,
    MultiParameter,
    CountedMultiParameter,
    StringTableParameter,
)
from gui.model.parameter.constraint import Constraint
from gui.model.parameter.condition import Condition


class TestIntParameter:
    """Unit tests for IntParameter class."""

    @fixture(autouse=True)
    def set_int_param(self, mocker):
        # The typed Signal(Constraint) emit is causing segfaults when the payload is a MagicMock
        def fake_add_constraint(self, constraint, hidden=False):
            if not hidden:
                self._constraints.append(constraint)
            else:
                self._hidden_constraints.append(constraint)
            constraint.value = self.value
            constraint.valid_changed.connect(self._emit_valid_changed)
            constraint.enabled_changed.connect(self._emit_valid_changed)

        mocker.patch.object(IntParameter, "add_constraint", fake_add_constraint)

        self.mock_constraint = mocker.MagicMock(spec=Constraint)
        self.mock_constraint.valid = True
        self.mock_constraint.enabled = True

        self.int_param = IntParameter(
            name="testint",
            description="Test int parameter",
            flag="-testint ",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value=0,
            constraints=[self.mock_constraint],
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.int_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test IntParameter initialization with default value."""
        param = self.int_param
        assert param.name == "testint"
        assert param.description == "Test int parameter"
        assert param.flag == "-testint "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.value == 0
        assert param.default_value == 0
        assert len(param.constraints) == 1
        assert param.constraints[0] is self.mock_constraint

    def test_set_value(self):
        """Test setting IntParameter value."""
        param = self.int_param
        param.value = 5
        assert param.value == 5

    def test_set_value_propagates_to_constraint(self):
        """Setting the value should push it into the constraint."""
        param = self.int_param
        param.value = 7
        assert self.mock_constraint.value == 7

    def test_reset_value(self):
        """Test resetting IntParameter value to default."""
        param = self.int_param
        param.value = 5
        param.reset_value()
        assert param.value == 0

    def test_enabled(self):
        # Arrange
        param = self.int_param

        # Act + Assert
        param._condition.value = False
        assert not param.enabled

        param._condition.value = True
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'IntParameter' is
        emitted when its internal condition reports a change to 'True'.
        """
        # Arrange
        param = self.int_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'IntParameter' is
        emitted when its internal condition reports a change to 'False'.
        """
        # Arrange
        param = self.int_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)

    def test_valid(self):
        """Test IntParameter validity."""
        # Arrange
        param = self.int_param

        # Act + Assert: constraint says valid then parameter is valid
        self.mock_constraint.valid = True
        assert param.valid

        # Act + Assert: constraint says invalid then parameter is invalid
        self.mock_constraint.valid = False
        assert not param.valid

        # Act + Assert: invalid but disabled constraint so parameter is valid
        self.mock_constraint.enabled = False
        assert param.valid

    def test_valid_when_parameter_disabled(self, mocker):
        """A disabled parameter is always valid, even with a failing constraint."""
        # Arrange
        param = self.int_param
        self.mock_constraint.valid = False
        self.mock_constraint.enabled = True
        mocker.patch.object(
            IntParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )

        # Assert
        assert param.valid

    def test_to_cli(self, mocker):
        """Test IntParameter cli representation."""
        # Arrange
        param = self.int_param

        # Act + Assert: enabled + matching operation = flag and value
        assert param.to_cli('IMG-GEN') == f"{param.flag}{param.value}"
        param.value = new_value = 5
        assert param.to_cli('MDL-GEN') == f"{param.flag}{new_value}"

        # Act + Assert: operation not in 'operations' so empty string
        assert param.to_cli('SWP-SCN') == ""

        # Arrange: parameter disabled
        mocker.patch.object(
            IntParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert: disabled so empty string
        assert param.to_cli('IMG-GEN') == ""

    def test_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted when IntParameter value changes."""
        # Arrange
        param = self.int_param
        self.mock_constraint.valid = True
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = 5

        # Assert
        slot.assert_called_once_with(5, True)

    def test_invalid_value_changed_signal_emitted(self, mocker):
        # Arrange
        param = self.int_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)
        self.mock_constraint.valid = False

        # Act
        param.value = 15

        # Assert
        slot.assert_called_once_with(15, False)

    def test_reset_value_emits_value_reset(self, mocker):
        """reset_value emits the value_reset signal."""
        # Arrange
        slot = mocker.MagicMock()
        self.int_param.value_reset.connect(slot)
        self.int_param.value = 5

        # Act
        self.int_param.reset_value()

        # Assert
        slot.assert_called_once()

    def test_to_dict(self):
        """to_dict returns the current value."""
        self.int_param.value = 7
        assert self.int_param.to_dict() == 7

    def test_str(self):
        """__str__ includes name and value."""
        result = str(self.int_param)
        assert "testint" in result
        assert "0" in result

class TestBoolParameter:
    """Unit tests for BoolParameter class."""

    @fixture(autouse=True)
    def set_bool_param(self, mocker):
        self.bool_param = BoolParameter(
            name="testbool",
            description="Test bool parameter",
            flag="-testbool",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value=False,
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.bool_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test BoolParameter initialization with default value."""
        param = self.bool_param
        assert param.name == "testbool"
        assert param.description == "Test bool parameter"
        assert param.flag == "-testbool"
        assert param.operations == {"IMG-GEN", "MDL-GEN"}
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

    def test_enabled(self):
        # Arrange
        param = self.bool_param

        # Act + Assert
        param._condition.value = False
        assert not param.enabled

        param._condition.value = True
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'BoolParameter' is
        emitted when its internal condition reports a change to 'True'.
        """
        # Arrange
        param = self.bool_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'BoolParameter' is
        emitted when its internal condition reports a change to 'False'.
        """
        # Arrange
        param = self.bool_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)

    def test_valid(self):
        """BoolParameter is always valid since it has no constraints."""
        param = self.bool_param
        assert param.valid
        param.value = True
        assert param.valid

    def test_to_cli(self, mocker):
        """Test BoolParameter cli representation."""
        # Arrange
        param = self.bool_param

        # Act + Assert: value is False so nothing is emitted even on a matching operation.
        assert param.to_cli("IMG-GEN") == ""

        # Act + Assert: value is True so the flag is emitted on matching operations.
        param.value = True
        assert param.to_cli("IMG-GEN") == param.flag
        assert param.to_cli("MDL-GEN") == param.flag

        # Act + Assert: operation not in 'operations' so empty string
        assert param.to_cli("SWP-SCN") == ""

        # Arrange: parameter disabled
        mocker.patch.object(
            BoolParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert: disabled so empty string
        assert param.to_cli("IMG-GEN") == ""

    def test_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted when BoolParameter value changes."""
        # Arrange
        param = self.bool_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = True

        # Assert
        slot.assert_called_once_with(True, True)

    def test_reset_value_emits_value_reset(self, mocker):
        """reset_value emits the value_reset signal."""
        # Arrange
        slot = mocker.MagicMock()
        self.bool_param.value_reset.connect(slot)
        self.bool_param.value = True

        # Act
        self.bool_param.reset_value()

        # Assert
        slot.assert_called_once()

    def test_to_dict(self):
        """to_dict returns the current value."""
        self.bool_param.value = True
        assert self.bool_param.to_dict() is True

    def test_str(self):
        """__str__ includes name and value."""
        result = str(self.bool_param)
        assert "testbool" in result
        assert "False" in result


class TestFloatParameter:
    """Unit tests for FloatParameter class."""

    @fixture(autouse=True)
    def set_float_param(self, mocker):
        def fake_add_constraint(self, constraint, hidden=False):
            if not hidden:
                self._constraints.append(constraint)
            else:
                self._hidden_constraints.append(constraint)
            constraint.value = self.value
            constraint.valid_changed.connect(self._emit_valid_changed)
            constraint.enabled_changed.connect(self._emit_valid_changed)

        mocker.patch.object(FloatParameter, "add_constraint", fake_add_constraint)

        self.mock_constraint = mocker.MagicMock(spec=Constraint)
        self.mock_constraint.valid = True
        self.mock_constraint.enabled = True

        self.float_param = FloatParameter(
            name="testfloat",
            description="Test float parameter",
            flag="-testfloat",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value=0.0,
            constraints=[self.mock_constraint],
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.float_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test FloatParameter initialization with default value."""
        param = self.float_param
        assert param.name == "testfloat"
        assert param.description == "Test float parameter"
        assert param.flag == "-testfloat"
        assert param.operations == {"IMG-GEN", "MDL-GEN"}
        assert param.value == 0.0
        assert param.default_value == 0.0
        assert len(param.constraints) == 1
        assert param.constraints[0] is self.mock_constraint

    def test_set_value(self):
        """Test setting FloatParameter value."""
        param = self.float_param
        param.value = 5.0
        assert param.value == 5.0

    def test_set_value_propagates_to_constraint(self):
        """Setting the value should push it into the constraint."""
        param = self.float_param
        param.value = 3.14
        assert self.mock_constraint.value == 3.14

    def test_reset_value(self):
        """Test resetting FloatParameter value to default."""
        param = self.float_param
        param.value = 5.0
        param.reset_value()
        assert param.value == 0.0

    def test_enabled(self):
        # Arrange
        param = self.float_param

        # Act + Assert
        param._condition.value = False
        assert not param.enabled

        param._condition.value = True
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'FloatParameter' is
        emitted when its internal condition reports a change to 'True'.
        """
        # Arrange
        param = self.float_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'FloatParameter' is
        emitted when its internal condition reports a change to 'False'.
        """
        # Arrange
        param = self.float_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)

    def test_valid(self):
        """Test FloatParameter validity."""
        # Arrange
        param = self.float_param

        # Act + Assert: constraint says valid then parameter is valid
        self.mock_constraint.valid = True
        assert param.valid

        # Act + Assert: constraint says invalid then parameter is invalid
        self.mock_constraint.valid = False
        assert not param.valid

        # Act + Assert: invalid but disabled constraint so parameter is valid
        self.mock_constraint.enabled = False
        assert param.valid

    def test_valid_when_parameter_disabled(self, mocker):
        """A disabled parameter is always valid, even with a failing constraint."""
        # Arrange
        param = self.float_param
        self.mock_constraint.valid = False
        self.mock_constraint.enabled = True
        mocker.patch.object(
            FloatParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )

        # Assert
        assert param.valid

    def test_to_cli(self, mocker):
        """Test FloatParameter cli representation."""
        # Arrange
        param = self.float_param

        # Act + Assert: enabled + matching operation = flag and value
        assert param.to_cli("IMG-GEN") == f"{param.flag}{param.value}"
        param.value = new_value = 5.5
        assert param.to_cli("MDL-GEN") == f"{param.flag}{new_value}"

        # Act + Assert: operation not in 'operations' so empty string
        assert param.to_cli("SWP-SCN") == ""

        # Arrange: parameter disabled
        mocker.patch.object(
            FloatParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert: disabled so empty string
        assert param.to_cli("IMG-GEN") == ""

    def test_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted when FloatParameter value changes."""
        # Arrange
        param = self.float_param
        self.mock_constraint.valid = True
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = 5.5

        # Assert
        slot.assert_called_once_with(5.5, True)

    def test_invalid_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted with valid=False when the constraint fails."""
        # Arrange
        param = self.float_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)
        self.mock_constraint.valid = False

        # Act
        param.value = 15.0

        # Assert
        slot.assert_called_once_with(15.0, False)

    def test_reset_value_emits_value_reset(self, mocker):
        """reset_value emits the value_reset signal."""
        # Arrange
        slot = mocker.MagicMock()
        self.float_param.value_reset.connect(slot)
        self.float_param.value = 5.0

        # Act
        self.float_param.reset_value()

        # Assert
        slot.assert_called_once()

    def test_to_dict(self):
        """to_dict returns the current value."""
        self.float_param.value = 3.14
        assert self.float_param.to_dict() == 3.14

    def test_str(self):
        """__str__ includes name and value."""
        result = str(self.float_param)
        assert "testfloat" in result
        assert "0.0" in result


class TestStringParameter:
    """Unit tests for StringParameter class."""

    @fixture(autouse=True)
    def set_string_param(self, mocker):
        def fake_add_constraint(self, constraint, hidden=False):
            if not hidden:
                self._constraints.append(constraint)
            else:
                self._hidden_constraints.append(constraint)
            constraint.value = self.value
            constraint.valid_changed.connect(self._emit_valid_changed)
            constraint.enabled_changed.connect(self._emit_valid_changed)

        mocker.patch.object(StringParameter, "add_constraint", fake_add_constraint)

        # Two mock constraints to mirror the integration tests that use a MaxLengthConstraint + RegexConstraint pair.
        self.mock_length_constraint = mocker.MagicMock(spec=Constraint)
        self.mock_length_constraint.valid = True
        self.mock_length_constraint.enabled = True

        self.mock_regex_constraint = mocker.MagicMock(spec=Constraint)
        self.mock_regex_constraint.valid = True
        self.mock_regex_constraint.enabled = True

        self.string_param = StringParameter(
            name="teststring",
            description="Test string parameter",
            flag="-teststring ",
            operations={"IMG-GEN", "MDL-GEN"},
            default_value="default",
            constraints=[self.mock_length_constraint, self.mock_regex_constraint],
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.string_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test StringParameter initialization with default value."""
        param = self.string_param
        assert param.name == "teststring"
        assert param.description == "Test string parameter"
        assert param.flag == "-teststring "
        assert param.operations == {"IMG-GEN", "MDL-GEN"}
        assert param.value == "default"
        assert param.default_value == "default"
        assert len(param.constraints) == 2

    def test_set_value(self):
        """Test setting StringParameter value."""
        param = self.string_param
        param.value = "new_value"
        assert param.value == "new_value"

    def test_set_value_propagates_to_constraints(self):
        """Setting the value should push it into every constraint."""
        param = self.string_param
        param.value = "hello"
        assert self.mock_length_constraint.value == "hello"
        assert self.mock_regex_constraint.value == "hello"

    def test_reset_value(self):
        """Test resetting StringParameter value to default."""
        param = self.string_param
        param.value = "new_value"
        param.reset_value()
        assert param.value == "default"

    def test_enabled(self):
        # Arrange
        param = self.string_param

        # Act + Assert
        param._condition.value = False
        assert not param.enabled

        param._condition.value = True
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'StringParameter' is
        emitted when its internal condition reports a change to 'True'.
        """
        # Arrange
        param = self.string_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'StringParameter' is
        emitted when its internal condition reports a change to 'False'.
        """
        # Arrange
        param = self.string_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)

    def test_valid_all_constraints_pass(self):
        """Valid when every enabled constraint reports valid."""
        param = self.string_param
        self.mock_length_constraint.valid = True
        self.mock_regex_constraint.valid = True
        assert param.valid

    def test_valid_one_constraint_fails(self):
        """Invalid as soon as one enabled constraint reports invalid."""
        param = self.string_param
        self.mock_length_constraint.valid = True
        self.mock_regex_constraint.valid = False
        assert not param.valid

    def test_valid_failing_constraint_disabled(self):
        """A failing constraint that is disabled does not break validity."""
        param = self.string_param
        self.mock_regex_constraint.valid = False
        self.mock_regex_constraint.enabled = False
        assert param.valid

    def test_valid_when_parameter_disabled(self, mocker):
        """A disabled parameter is always valid, even with a failing constraint."""
        # Arrange
        param = self.string_param
        self.mock_length_constraint.valid = False
        self.mock_length_constraint.enabled = True
        mocker.patch.object(
            StringParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )

        # Assert
        assert param.valid

    def test_to_cli(self, mocker):
        """Test StringParameter cli representation."""
        # Arrange
        param = self.string_param

        # Act + Assert: enabled + matching operation = flag and value
        assert param.to_cli("IMG-GEN") == f"{param.flag}{param.value}"
        new_value = "hello"
        param.value = new_value
        assert param.to_cli("MDL-GEN") == f"{param.flag}{new_value}"

        # Act + Assert: operation not in 'operations' so empty string
        assert param.to_cli("SWP-SCN") == ""

        # Arrange: parameter disabled
        mocker.patch.object(
            StringParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert: disabled so empty string
        assert param.to_cli("IMG-GEN") == ""

    def test_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted when StringParameter value changes."""
        # Arrange
        param = self.string_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = "hello"

        # Assert
        slot.assert_called_once_with("hello", True)

    def test_invalid_value_changed_signal_emitted(self, mocker):
        """Test that value_changed signal is emitted with valid=False when a constraint fails."""
        # Arrange
        param = self.string_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)
        self.mock_regex_constraint.valid = False

        # Act
        param.value = "invalid value"

        # Assert
        slot.assert_called_once_with("invalid value", False)

    def test_reset_value_emits_value_reset(self, mocker):
        """reset_value emits the value_reset signal."""
        # Arrange
        slot = mocker.MagicMock()
        self.string_param.value_reset.connect(slot)
        self.string_param.value = "new_value"

        # Act
        self.string_param.reset_value()

        # Assert
        slot.assert_called_once()

    def test_to_dict(self):
        """to_dict returns the current value."""
        self.string_param.value = "hello"
        assert self.string_param.to_dict() == "hello"

    def test_str(self):
        """__str__ includes name and value."""
        result = str(self.string_param)
        assert "teststring" in result
        assert "default" in result


class TestEnumParameter:
    """Unit tests for EnumParameter class."""

    @fixture(autouse=True)
    def set_enum_param(self, mocker):
        self.enum_param = EnumParameter(
            name="testenum",
            description="Test enum parameter",
            flag="-testenum ",
            operations={'IMG-GEN', 'MDL-GEN'},
            options=[("discard SNP", "D"), ("input N per SNP", "I"), ("represent N through a mask", "M 2"),
                     ("ignore allele pairs with N", "A")],
            default_value=0,
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.enum_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test EnumParameter initialization with default value."""
        param = self.enum_param
        assert param.name == "testenum"
        assert param.description == "Test enum parameter"
        assert param.flag == "-testenum "
        assert param.operations == {'IMG-GEN', 'MDL-GEN'}
        assert param.options[1] == "input N per SNP"
        assert param.default_value == 0

    def test_set_value(self):
        """Test setting EnumParameter value (index)."""
        param = self.enum_param
        param.value = 1
        assert param.value == 1

    def test_reset_value(self):
        """Test resetting EnumParameter value to default."""
        param = self.enum_param
        param.value = 1
        param.reset_value()
        assert param.value == 0

    def test_option_return(self):
        """'option' returns the display name for the current index
        and None if index is out of range
        """
        param = self.enum_param
        assert param.option == "discard SNP"
        param.value = 1
        assert param.option == "input N per SNP"
        param.value = 99
        assert param.option is None

    def test_options_returns_display_names(self):
        """'options' exposes only the display names, not the CLI forms."""
        param = self.enum_param
        assert param.options == [
            "discard SNP",
            "input N per SNP",
            "represent N through a mask",
            "ignore allele pairs with N",
        ]

    def test_enabled(self):
        # Arrange
        param = self.enum_param

        # Act + Assert
        param._condition.value = False
        assert not param.enabled

        param._condition.value = True
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """enabled_changed fires when the condition flips to True."""
        # Arrange
        param = self.enum_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """enabled_changed fires when the condition flips to False."""
        # Arrange
        param = self.enum_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)

    def test_to_cli(self, mocker):
        """to_cli emits the flag followed by the CLI form of the selected option."""
        # Arrange
        param = self.enum_param

        # Act + Assert: enabled + matching operation = flag and cli of the option
        assert param.to_cli("IMG-GEN") == "-testenum D"
        param.value = 3
        assert param.to_cli("MDL-GEN") == "-testenum A"

        # Act + Assert: operation not in 'operations' so empty string
        assert param.to_cli("SWP-SCN") == ""

        # Arrange: parameter disabled
        mocker.patch.object(
            EnumParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )
        # Assert: disabled so empty string
        assert param.to_cli("IMG-GEN") == ""

    def test_value_changed_signal_emitted(self, mocker):
        """value_changed fires on value change."""
        # Arrange
        param = self.enum_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = 3

        # Assert
        slot.assert_called_once_with(3, True)

    def test_invalid_value_changed_signal_emitted(self, mocker):
        """value_changed fires with valid=False when the new index is below zero."""
        # Arrange
        param = self.enum_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)

        # Act
        param.value = -1

        # Assert
        slot.assert_called_once_with(-1, False)

    def test_reset_value_emits_value_reset(self, mocker):
        """reset_value emits the value_reset signal."""
        # Arrange
        slot = mocker.MagicMock()
        self.enum_param.value_reset.connect(slot)
        self.enum_param.value = 2

        # Act
        self.enum_param.reset_value()

        # Assert
        slot.assert_called_once()

    def test_to_dict(self):
        """to_dict returns the current index."""
        self.enum_param.value = 1
        assert self.enum_param.to_dict() == 1

    def test_str(self):
        """__str__ includes name and selected option."""
        result = str(self.enum_param)
        assert "testenum" in result
        assert "discard SNP" in result

class TestFileParameter:
    """Unit tests for FileParameter class."""

    @fixture(autouse=True)
    def set_file_param(self, tmp_path, mocker):
        self.valid_file = tmp_path / "sample.vcf"
        self.valid_file.write_text("data")
        self.second_valid_file = tmp_path / "test.vcf"
        self.second_valid_file.write_text("data")
        self.invalid_file = tmp_path / "sample.txt"
        self.invalid_file.write_text("data")

        self.file_param = FileParameter(
            name="testfile",
            description="Test file parameter",
            flag="-testfile ",
            operations={"IMG-GEN", "MDL-GEN"},
            accepted_formats=[".vcf"],
            strict=True,
            multiple=True,
            default_value=[str(self.valid_file)],
        )

        self.mock_condition = mocker.MagicMock(spec=Condition)
        self.mock_condition.value = True
        self.file_param.add_condition(self.mock_condition)

    def test_init_values(self):
        """Test FileParameter initialization with default value."""
        param = self.file_param
        assert param.name == "testfile"
        assert param.description == "Test file parameter"
        assert param.flag == "-testfile "
        assert param.operations == {"IMG-GEN", "MDL-GEN"}
        assert param.accepted_formats == [".vcf"]
        assert param.strict
        assert param.multiple
        assert param.value == [str(self.valid_file)]

    def test_set_value(self):
        """Test setting FileParameter value."""
        param = self.file_param
        param.value = [str(self.second_valid_file)]
        assert param.value == [str(self.second_valid_file)]

    def test_reset_value(self):
        """Test resetting FileParameter value to default."""
        param = self.file_param
        param.value = [str(self.second_valid_file)]
        param.reset_value()
        assert param.value == [str(self.valid_file)]

    def test_enabled(self):
        # Arrange
        param = self.file_param

        # Act + Assert
        param._condition.value = False
        assert not param.enabled

        param._condition.value = True
        assert param.enabled

    def test_enabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'FileParameter' is
        emitted when its internal condition reports a change to True.
        """
        # Arrange
        param = self.file_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(True)

        # Assert
        slot.assert_called_once_with(True)

    def test_disabled_signal(self, mocker):
        """
        Test that the 'enabled_changed' signal of 'FileParameter' is
        emitted when its internal condition reports a change to False.
        """
        # Arrange
        param = self.file_param
        slot = mocker.MagicMock()
        param.enabled_changed.connect(slot)

        # Act
        param._condition.changed.emit(False)

        # Assert
        slot.assert_called_once_with(False)
        
    def test_value_changed_signal_emitted(self, mocker):
        """value_changed fires on value change."""
        # Arrange
        param = self.file_param
        slot = mocker.MagicMock()
        param.value_changed.connect(slot)
        new_value = [str(self.second_valid_file)]

        # Act
        param.value = new_value

        # Assert
        slot.assert_called_once_with(new_value, True)

    def test_valid_with_accepted_format(self):
        """Valid when file exists and has an accepted extension."""
        param = self.file_param
        param.value = [str(self.valid_file)]
        assert param.valid

    def test_invalid_with_rejected_format(self):
        """Invalid when file exists but extension is not accepted."""
        param = self.file_param
        param.value = [str(self.invalid_file)]
        assert not param.valid

    def test_invalid_when_empty(self):
        """Invalid when no file is selected."""
        param = self.file_param
        param.value = []
        assert not param.valid

    def test_multiple_false_rejects_two_files(self):
        """Two files should be invalid when multiple=False."""
        # Arrange: a new parameter with multiple=False
        param = FileParameter(
            name="testfile",
            description="Test file parameter",
            flag="-testfile",
            operations={"IMG-GEN", "MDL-GEN"},
            accepted_formats=[".vcf"],
            strict=True,
            multiple=False,
            default_value=[str(self.valid_file)],
        )

        # Act
        param.value = [str(self.valid_file), str(self.second_valid_file)]

        # Assert
        assert not param.valid

    def test_multiple_true_accepts_two_files(self):
        """Two valid files should be valid when multiple=True."""
        param = self.file_param
        param.value = [str(self.valid_file), str(self.second_valid_file)]
        assert param.valid

    def test_valid_when_parameter_disabled(self, mocker):
        """A disabled parameter is always valid, even with an invalid file."""
        # Arrange
        param = self.file_param
        param.value = [str(self.invalid_file)]
        mocker.patch.object(
            FileParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )

        # Assert
        assert param.valid

    def test_file_extensions_property(self):
        """'file_extensions' returns the suffix of each selected file."""
        param = self.file_param
        param.value = [str(self.valid_file), str(self.invalid_file)]
        assert param.file_extensions == [".vcf", ".txt"]

    def test_matches_expected_when_not_strict(self, tmp_path, mocker):
        """'matches_expected' returns whether files hit the expected format (non-strict)."""
        # Arrange: non-strict parameter with an expected format
        vcf_file = tmp_path / "ok.vcf"
        vcf_file.write_text("data")
        txt_file = tmp_path / "not_ok.txt"
        txt_file.write_text("data")

        param = FileParameter(
            name="testfile",
            description="Test file parameter",
            flag="-testfile ",
            operations={"IMG-GEN", "MDL-GEN"},
            accepted_formats=[".vcf"],
            strict=False,
            multiple=True,
        )

        # Act + Assert: matching format
        param.value = [str(vcf_file)]
        assert param.matches_expected

        # Act + Assert: non-matching format
        param.value = [str(txt_file)]
        assert not param.matches_expected

    def test_to_cli(self):
        """to_cli gives one '{flag}{path}' per selected file."""
        param = self.file_param
        param.value = [str(self.valid_file)]
        assert param.to_cli("IMG-GEN") == f"-testfile {self.valid_file}"

    def test_to_cli_multiple_files(self):
        """to_cli repeats the flag for each file when multiple files are selected."""
        param = self.file_param
        param.value = [str(self.valid_file), str(self.second_valid_file)]
        expected = f"-testfile {self.valid_file} -testfile {self.second_valid_file}"
        assert param.to_cli("IMG-GEN") == expected

    def test_to_cli_when_disabled(self, mocker):
        """to_cli returns empty string when the parameter is disabled."""
        # Arrange
        param = self.file_param
        mocker.patch.object(
            FileParameter,
            "enabled",
            new_callable=mocker.PropertyMock,
            return_value=False,
        )

        # Assert
        assert param.to_cli("IMG-GEN") == ""

    def test_to_cli_when_operation_not_in_operations(self):
        """to_cli returns empty string when the operation is not in the parameter's operations."""
        param = self.file_param
        assert param.to_cli("SWP-SCN") == ""

    def test_str(self):
        """__str__ includes name and value."""
        result = str(self.file_param)
        assert "testfile" in result
        assert str(self.valid_file) in result

