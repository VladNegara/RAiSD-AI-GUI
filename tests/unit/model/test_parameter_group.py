from pytest import fixture, raises
import re

from gui.model.constraint import (
    IntervalConstraint,
    MaxLengthConstraint,
    RegexConstraint,
)
from gui.model.parameter import ParameterGroup
from gui.model.parameter import StringParameter, BoolParameter

class TestParameterGroup:
    """Tests for ParameterGroup class."""

    @fixture(autouse=True)
    def set_parameter_group(self):
        self.string_param = StringParameter(
            name="string_param",
            description="string_param description",
            flag="-flag_string ",
            operations={'MDL-GEN'},
            default_value="default",
            constraints=[
                MaxLengthConstraint(10),
                RegexConstraint(
                    pattern=re.compile(r"\b[a-z]+\b"),
                    hint="Only lowercase letters."
                ),
            ],
        )
        self.bool_param = BoolParameter(
            name="bool_param",
            description="bool_param description",
            flag="-flag_bool",
            operations={'MDL-GEN'},
            default_value=True,
            enabled=True,
        )
        self.parameters = [self.string_param, self.bool_param]
        self.parameter_group = ParameterGroup(
            name="test_group",
            parameters=self.parameters,
        )

    def test_init_values(self):
        """Test ParameterGroup initialization with default value."""
        group = self.parameter_group
        assert group.name == "test_group"
        assert group.parameters == self.parameters
        assert group._enabled is True

    def test_init_empty_parameters(self):
        """Test ParameterGroup initialization when the parameters list is empty."""
        group = ParameterGroup(name="empty_group")
        assert group.name == "empty_group"
        assert group.parameters == []
        assert group._enabled is False

    def test_init_all_disabled(self):
        """Test ParameterGroup initialization as disabled when the parameters are disabled."""
        param_list = [
            BoolParameter(
                name="disabled_param_1",
                description="desc",
                flag="-a",
                operations={'IMG-GEN'},
                default_value=False,
                enabled=False,
            ),
            BoolParameter(
                name="disabled_param_2",
                description="desc",
                flag="-b",
                operations={'IMG-GEN'},
                default_value=True,
                enabled=False,
            ),
        ]

        group = ParameterGroup(name="disabled_group", parameters=param_list)
        assert group._enabled is False

    def test_add_parameter(self):
        """Test adding parameter to an existing ParameterGroup."""
        group = ParameterGroup(name="empty_group")
        assert len(group.parameters) == 0

        new_param = BoolParameter(
            name="new_param",
            description="desc",
            flag="-new",
            operations={'IMG-GEN'},
            default_value=False,
        )
        group.add_parameter(new_param)

        assert len(group.parameters) == 1
        assert group.parameters[0] is new_param

    def test_add_parameter_connects_enabled_changed(self):
        """Test that add_parameter correctly connects the enabled_changed signal."""
        group = ParameterGroup(name="empty_group")
        new_param = BoolParameter(
            name="new_param",
            description="desc",
            flag="-new",
            operations={'IMG-GEN'},
            default_value=False,
            enabled=False,
        )
        group.add_parameter(new_param)

        self.signal_emitted_counter = 0

        def on_enabled_changed():
            self.signal_emitted_counter += 1

        group.enabled_changed.connect(on_enabled_changed)
        new_param.enabled = True
        new_param.enabled = False
        new_param.enabled = True
        new_param.enabled = False
        assert self.signal_emitted_counter == 4

    def test_valid_all_valid(self):
        """Test validity of ParameterGroup when all parameters are valid."""
        group = self.parameter_group
        assert group.valid is True

    def test_valid_one_invalid(self):
        """Test validity of ParameterGroup when a single parameter is invalid."""
        group = self.parameter_group
        self.string_param.value = "INVALID VALUE!!"
        assert group.valid is False

    def test_enabled_changed_signal_emitted_on_disable(self):
        """Test that enabled_changed is emitted when the last enabled
        parameter becomes disabled."""
        group = self.parameter_group
        self.signal_emitted_counter = 0
        self.emitted_value = None

        def on_enabled_changed(value):
            self.signal_emitted_counter += 1
            self.emitted_value = value

        group.enabled_changed.connect(on_enabled_changed)

        # Disable all parameters — group should become disabled
        self.string_param.enabled = False
        self.bool_param.enabled = False

        assert self.signal_emitted_counter == 1
        assert self.emitted_value is False

    def test_enabled_changed_signal_emitted_on_enable(self):
        """Test that enabled_changed is emitted when the first parameter
        becomes enabled in a fully disabled group."""
        disabled_param = BoolParameter(
            name="p1",
            description="desc",
            flag="-p1",
            operations={'IMG-GEN'},
            default_value=False,
            enabled=False,
        )
        group = ParameterGroup(name="disabled_group", parameters=[disabled_param])
        assert group._enabled is False

        self.signal_emitted_counter = 0
        self.emitted_value = None

        def on_enabled_changed(value):
            self.signal_emitted_counter += 1
            self.emitted_value = value

        group.enabled_changed.connect(on_enabled_changed)

        disabled_param.enabled = True

        assert self.signal_emitted_counter == 1
        assert self.emitted_value is True

    def test_enabled_changed_not_emitted_when_unchanged(self):
        """Test that enabled_changed is not emitted when the enabled
        state of the group doesn't actually change."""
        group = self.parameter_group
        self.signal_emitted_counter = 0

        def on_enabled_changed():
            self.signal_emitted_counter += 1

        group.enabled_changed.connect(on_enabled_changed)
        self.string_param.enabled = False

        assert self.signal_emitted_counter == 0

    def test_to_cli(self):
        """Test to_cli."""
        group = self.parameter_group
        result = group.to_cli('MDL-GEN')
        assert result == "-flag_string default -flag_bool"

    def test_to_cli_irrelevant_operation(self):
        """Test to_cli returns an empty string when parameters none of the parameters
         match the operation."""
        group = self.parameter_group
        result = group.to_cli('SWP-SCN')
        assert result == ""

    def test_to_cli_mixed_operations(self):
        """Test to_cli when only some parameters match the operation."""
        param_a = BoolParameter(
            name="a",
            description="desc",
            flag="-a",
            operations={'IMG-GEN'},
            default_value=True,
        )
        param_b = BoolParameter(
            name="b",
            description="desc",
            flag="-b",
            operations={'MDL-GEN'},
            default_value=True,
        )
        group = ParameterGroup(name="mixed", parameters=[param_a, param_b])

        assert group.to_cli('IMG-GEN') == "-a"
        assert group.to_cli('MDL-GEN') == "-b"

    def test_to_cli_disabled_parameter(self):
        """Test that disabled parameters are excluded from CLI output."""
        group = self.parameter_group
        self.bool_param.enabled = False
        result = group.to_cli('MDL-GEN')
        assert result == "-flag_string default"

    def test_to_cli_empty_group(self):
        """Test to_cli returns an empty string when the parameters list is empty."""
        group = ParameterGroup(name="empty_group")
        result = group.to_cli('MDL-GEN')
        assert result == ""
