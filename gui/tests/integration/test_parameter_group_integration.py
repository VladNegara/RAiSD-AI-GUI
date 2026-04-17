from pytest import fixture
import re

from gui.model.parameter import (
    Condition,
    MaxLengthConstraint,
    RegexConstraint,
    ParameterGroup,
    StringParameter,
    BoolParameter,
)

class TestParameterGroupIntegration:

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

        self.string_param_condition = Condition(True)
        self.string_param.add_condition(self.string_param_condition)

        self.bool_param = BoolParameter(
            name="bool_param",
            description="bool_param description",
            flag="-flag_bool",
            operations={'MDL-GEN'},
            default_value=True,
        )

        self.bool_param_condition = Condition(True)
        self.bool_param.add_condition(self.bool_param_condition)

        self.parameters = [self.string_param, self.bool_param]
        self.parameter_group = ParameterGroup(
            name="test_group",
            parameters=self.parameters,
        )

    def test_all_disabled(self):
        """
        Test `ParameterGroup`'s `enabled` property when all parameters
        are disabled.
        """
        # Arrange
        group = self.parameter_group
        string_param_condition = self.string_param_condition
        bool_param_condition = self.bool_param_condition

        # Act
        string_param_condition.value = False
        bool_param_condition.value = False

        # Assert
        assert not group.enabled

    def test_valid_invalid_and_disabled_param(self):
        """Test that an invalid but disabled parameter does not make the group invalid."""
        group = self.parameter_group
        self.string_param.value = "INVALID VALUE!!"
        self.string_param_condition.value = False
        assert group.valid is True

    def test_add_parameter_connects_enabled_changed(self):
        """Test that add_parameter correctly connects the enabled_changed signal."""
        group = self.parameter_group
        string_param_condition = self.string_param_condition
        bool_param_condition = self.bool_param_condition

        string_param_condition.value = False
        bool_param_condition.value = False

        new_param = BoolParameter(
            name="new_param",
            description="desc",
            flag="-new",
            operations={'IMG-GEN'},
            default_value=False,
        )
        new_param_condition = Condition(False)
        new_param.add_condition(new_param_condition)
        group.add_parameter(new_param)

        self.signal_emitted_counter = 0

        def on_enabled_changed():
            self.signal_emitted_counter += 1

        group.enabled_changed.connect(on_enabled_changed)
        new_param_condition.value = True
        new_param_condition.value = False
        new_param_condition.value = True
        new_param_condition.value = False
        assert self.signal_emitted_counter == 4

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
        self.string_param_condition.value = False
        self.bool_param_condition.value = False

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
        )
        disabled_param_condition = Condition(False)
        disabled_param.add_condition(disabled_param_condition)
        group = ParameterGroup(name="disabled_group", parameters=[disabled_param])
        assert group._enabled is False

        self.signal_emitted_counter = 0
        self.emitted_value = None

        def on_enabled_changed(value):
            self.signal_emitted_counter += 1
            self.emitted_value = value

        group.enabled_changed.connect(on_enabled_changed)

        disabled_param_condition.value = True

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
        self.string_param_condition.value = False

        assert self.signal_emitted_counter == 0

    def test_to_cli_disabled_parameter(self):
        """Test that disabled parameters are excluded from CLI output."""
        group = self.parameter_group
        self.bool_param_condition.value = False
        result = group.to_cli('MDL-GEN')
        assert result == "-flag_string default"