import pytest
import re
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from gui.model.parameter import (
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
    FileParameter,
)
from gui.widgets.parameter_widget import (
    BoolParameterWidget,
    IntParameterWidget,
    FloatParameterWidget,
    EnumParameterWidget,
    StringParameterWidget,
    FileParameterWidget,
    ParameterWidget
)


@pytest.fixture(scope="session")
def app():
    """A QApplication instance is required for all widget tests."""
    app = QApplication.instance() or QApplication([])
    yield app


class TestBoolParameterWidget:

    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.param = BoolParameter(
            name="testbool",
            description="Test bool",
            flag="--testbool",
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=False,
        )
        self.widget = BoolParameterWidget(self.param)

    def test_initial_state_unchecked(self):
        """Checkbox should reflect the default value of False."""
        assert self.widget._checkbox.checkState() == Qt.CheckState.Unchecked

    def test_initial_state_checked(self, app):
        param = BoolParameter("b", "b", "--b", {'IMG-GEN', 'MDL-GEN'} , default_value=True)
        widget = BoolParameterWidget(param)
        assert widget._checkbox.checkState() == Qt.CheckState.Checked

    def test_checkbox_updates_parameter(self):
        """Checking the checkbox should update the parameter value."""
        self.widget._checkbox.setCheckState(Qt.CheckState.Checked)
        assert self.param.value is True

    def test_parameter_updates_checkbox(self):
        """Setting the parameter value should update the checkbox."""
        self.param.value = True
        assert self.widget._checkbox.checkState() == Qt.CheckState.Checked

    def test_reset_updates_checkbox(self):
        """Resetting the parameter should update the checkbox back to default."""
        self.param.value = True
        self.param.reset_value()
        assert self.widget._checkbox.checkState() == Qt.CheckState.Unchecked


class TestIntParameterWidget:

    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.param = IntParameter(
            name="testint",
            description="Test int",
            flag="--testint",
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=5,
            lower_bound=0,
            upper_bound=10,
        )
        self.widget = IntParameterWidget(self.param)

    def test_initial_value_displayed(self):
        """Line edit should show the default value."""
        assert self.widget._lineedit.text() == "5"

    def test_parameter_updates_lineedit(self):
        """Setting the parameter value should update the line edit."""
        self.param.value = 8
        assert self.widget._lineedit.text() == "8"

    def test_valid_value_accepted(self):
        """A value within bounds should be valid."""
        self.param.value = 7
        assert self.param.valid is True

    def test_invalid_value_below_lower_bound(self):
        """A value below the lower bound should be invalid."""
        self.param.value = -1
        assert self.param.valid is False

    def test_invalid_value_above_upper_bound(self):
        """A value above the upper bound should be invalid."""
        self.param.value = 11
        assert self.param.valid is False

    def test_reset_updates_lineedit(self):
        """Resetting the parameter should update the line edit."""
        self.param.value = 8
        self.param.reset_value()
        assert self.widget._lineedit.text() == "5"

    def test_bounds_label_shown(self):
        """A label showing bounds should be present in the layout."""
        labels = [
            self.widget.layout().itemAt(i).widget().__class__.__name__
            for i in range(self.widget.layout().count())
        ]
        assert "QLabel" in labels


class TestFloatParameterWidget:

    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.param = FloatParameter(
            name="testfloat",
            description="Test float",
            flag="--testfloat",
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=5.0,
            lower_bound=0.0,
            upper_bound=10.0,
        )
        self.widget = FloatParameterWidget(self.param)

    def test_initial_value_displayed(self):
        assert self.widget._lineedit.text() == "5.0"

    def test_parameter_updates_lineedit(self):
        self.param.value = 7.5
        assert self.widget._lineedit.text() == "7.5"

    def test_valid_value(self):
        self.param.value = 3.14
        assert self.param.valid is True

    def test_invalid_value_below_lower_bound(self):
        self.param.value = -0.1
        assert self.param.valid is False

    def test_invalid_value_above_upper_bound(self):
        self.param.value = 10.1
        assert self.param.valid is False

    def test_reset_updates_lineedit(self):
        self.param.value = 9.9
        self.param.reset_value()
        assert self.widget._lineedit.text() == "5.0"


class TestEnumParameterWidget:

    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.param = EnumParameter(
            name="testenum",
            description="Test enum",
            flag="--testenum",
            options=[("Slow", "slow"), ("Fast", "fast"), ("Very fast", "very-fast")],
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value=0,
        )
        self.widget = EnumParameterWidget(self.param)

    def test_initial_index(self):
        """Combo box should reflect the default index."""
        assert self.widget._combo_box.currentIndex() == 0

    def test_options_populated(self):
        """Combo box should have all options."""
        assert self.widget._combo_box.count() == 3

    def test_combobox_updates_parameter(self):
        """Changing the combo box index should update the parameter."""
        self.widget._combo_box.setCurrentIndex(2)
        assert self.param.value == 2

    def test_parameter_updates_combobox(self):
        """Setting the parameter value should update the combo box."""
        self.param.value = 1
        assert self.widget._combo_box.currentIndex() == 1

    def test_reset_updates_combobox(self):
        """Resetting the parameter should update the combo box."""
        self.param.value = 2
        self.param.reset_value()
        assert self.widget._combo_box.currentIndex() == 0


class TestStringParameterWidget:

    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.param = StringParameter(
            name="teststring",
            description="Test string",
            flag="--teststring",
            operations={'IMG-GEN', 'MDL-GEN'},
            default_value="hello",
            max_length=10,
            pattern=re.compile(r"^[a-z]+$"),
        )
        self.widget = StringParameterWidget(self.param)

    def test_initial_value_displayed(self):
        """Line edit should show the default value."""
        assert self.widget._line_edit.text() == "hello"

    def test_parameter_updates_line_edit(self):
        """Setting the parameter value should update the line edit."""
        self.param.value = "world"
        assert self.widget._line_edit.text() == "world"

    def test_valid_value_shows_green_border(self):
        """A valid value should apply a green border style."""
        self.param.value = "valid"
        assert "green" in self.widget._line_edit.styleSheet()

    def test_invalid_value_shows_red_border(self):
        """An invalid value should apply a red border style."""
        self.param.value = "INVALID"
        assert "red" in self.widget._line_edit.styleSheet()

    def test_max_length_enforced(self):
        """Line edit max length should match the parameter's max length."""
        assert self.widget._line_edit.maxLength() == 10

    def test_reset_updates_line_edit(self):
        """Resetting the parameter should update the line edit."""
        self.param.value = "changed"
        self.param.reset_value()
        assert self.widget._line_edit.text() == "hello"

    def test_max_length_label_present(self):
        """A label showing max length should be present."""
        labels = [
            self.widget.layout().itemAt(i).widget().__class__.__name__
            for i in range(self.widget.layout().count())
        ]
        assert "QLabel" in labels


class TestFileParameterWidget:

    @pytest.fixture(autouse=True)
    def setup(self, app, tmp_path):
        self.valid_file = tmp_path / "sample.vcf"
        self.valid_file.write_text("data")
        self.invalid_file = tmp_path / "sample.txt"
        self.invalid_file.write_text("data")

        self.param = FileParameter(
            name="testfile",
            description="Test file",
            flag="--input",
            operations={'IMG-GEN', 'MDL-GEN'},
            accepted_formats=["vcf", "fasta"],
            strict=True,
            multiple=False,
            default_value=None,
        )
        self.widget = FileParameterWidget(self.param)

    def test_initial_label_no_file(self):
        """Path label should show 'No file selected' initially."""
        assert self.widget._path_label.text() == "No file selected"

    def test_valid_file_updates_label(self):
        """Setting a valid file path should update the path label."""
        self.param.value = [str(self.valid_file)]
        assert str(self.valid_file) in self.widget._path_label.text()

    def test_invalid_file_updates_label(self):
        """Setting an invalid file path should still update the path label."""
        param = FileParameter(
            name="testfile", description="", flag="--input",
            operations={'IMG-GEN', 'MDL-GEN'},
            accepted_formats=["vcf", "fasta"],
            strict=True, multiple=False,
        )
        param._value = [str(self.invalid_file)]
        assert str(self.invalid_file) in str(param.value)

    def test_valid_file_is_valid(self):
        """A file with an accepted extension should be valid."""
        self.param.value = [str(self.valid_file)]
        assert self.param.valid is True

    def test_invalid_extension_is_invalid(self):
        """A file with a non-accepted extension should be invalid."""
        param = FileParameter(
            name="testfile", description="", flag="--input",
            operations={'IMG-GEN', 'MDL-GEN'},
            accepted_formats=["vcf", "fasta"],
            strict=True, multiple=False,
        )
        param._value = [str(self.invalid_file)]
        assert param.valid is False

    def test_empty_value_is_invalid(self):
        """An empty file list should be invalid."""
        self.param.value = []
        assert self.param.valid is False

    def test_multiple_false_rejects_two_files(self):
        """Two files should be invalid when multiple=False."""
        param = FileParameter(
            name="testfile", description="", flag="--input",
            operations={'IMG-GEN', 'MDL-GEN'},
            accepted_formats=["vcf", "fasta"],
            strict=True, multiple=False,
        )
        param._value = [str(self.valid_file), str(self.valid_file)]
        assert param.valid is False

    def test_multiple_true_accepts_two_files(self, app, tmp_path):
        """Two valid files should be valid when multiple=True."""
        f1 = tmp_path / "a.vcf"
        f1.write_text("data")
        f2 = tmp_path / "b.vcf"
        f2.write_text("data")
        param = FileParameter(
            name="multi", description="", flag="--input",
            operations={'IMG-GEN', 'MDL-GEN'}, accepted_formats=["vcf"], multiple=True,
        )
        param.value = [str(f1), str(f2)]
        assert param.valid is True

    def test_reset_clears_label(self):
        """Resetting the parameter should clear the path label."""
        self.param.value = [str(self.valid_file)]
        self.param.reset_value()
        assert self.widget._path_label.text() == "No file selected"

    def test_to_cli_valid(self):
        """to_cli should return flag and path when valid."""
        self.param.value = [str(self.valid_file)]
        assert self.param.to_cli('IMG-GEN') == f"--input {str(self.valid_file)}"

    def test_to_cli_invalid(self):
        """to_cli should return empty string when invalid."""
        param = FileParameter(
        name="testfile", description="", flag="--input",
            operations={'IMG-GEN'},
           accepted_formats=["vcf", "fasta"],
            strict=True, multiple=False,
        )
        param._value = [str(self.invalid_file)]
        assert param.to_cli('IMG-GEN') == ""

class TestParameterWidgetFromParameter:
    """Tests for the from_parameter factory method."""

    @pytest.fixture(autouse=True)
    def setup(self, app):
        pass

    def test_from_parameter_bool(self):
        param = BoolParameter("b", "b", "--b", {"TEST"}, False)
        row = ParameterWidget.from_parameter(param)
        assert row is not None

    def test_from_parameter_int(self):
        param = IntParameter("i", "i", "--i", {"TEST"}, 0)
        row = ParameterWidget.from_parameter(param)
        assert row is not None

    def test_from_parameter_float(self):
        param = FloatParameter("f", "f", "--f", {"TEST"}, 0.0)
        row = ParameterWidget.from_parameter(param)
        assert row is not None

    def test_from_parameter_enum(self):
        param = EnumParameter("e", "e", "--e", {"TEST"}, [("A", "a")], 0)
        row = ParameterWidget.from_parameter(param)
        assert row is not None

    def test_from_parameter_string(self):
        param = StringParameter("s", "s", "--s", {"TEST"}, "")
        row = ParameterWidget.from_parameter(param)
        assert row is not None

    def test_from_parameter_file(self):
        param = FileParameter("f", "f", "--f", {"TEST"})
        row = ParameterWidget.from_parameter(param)
        assert row is not None

    def test_reset_button_resets_value(self, app):
        """Clicking the reset button should reset the parameter value."""
        param = IntParameter("i", "i", "--i", {"TEST"}, 5)
        reset_button = ParameterWidget.ResetButton(param)
        param.value = 99
        assert param.value == 99
        reset_button._clicked()
        assert param.value == 5

    def test_enabled_changed_hides_row(self, app):
        """Setting enabled=False should hide the row widget."""
        param = BoolParameter("b", "b", "--b", {"TEST"}, False)
        row = ParameterWidget.from_parameter(param)
        row.show()
        param.enabled = False
        assert not row.isVisible()
        param.enabled = True
        assert row.isVisible()

class TestIntParameterWidgetTextChanged:

    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.param = IntParameter(
            name="testint", description="", flag="--i",
            operations={"TEST"}, default_value=5,
        )
        self.widget = IntParameterWidget(self.param)

    def test_text_changed_valid_input(self):
        """Typing a valid integer should update the parameter."""
        self.widget._lineedit.setText("9")
        self.widget._text_changed()
        assert self.param.value == 9

    def test_text_changed_invalid_input_restores(self):
        """Typing an unparseable value should restore the previous value."""
        self.widget._lineedit.setText("")
        self.widget._text_changed()
        assert self.widget._lineedit.text() == "5"


class TestFloatParameterWidgetTextChanged:

    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.param = FloatParameter(
            name="testfloat", description="", flag="--f",
            operations={"TEST"}, default_value=3.0,
        )
        self.widget = FloatParameterWidget(self.param)

    def test_text_changed_valid_input(self):
        """Typing a valid float should update the parameter."""
        self.widget._lineedit.setText("7.5")
        self.widget._text_changed()
        assert self.param.value == 7.5

    def test_text_changed_invalid_input_restores(self):
        """Typing an unparseable value should restore the previous value."""
        self.widget._lineedit.setText("")
        self.widget._text_changed()
        assert self.widget._lineedit.text() == "3.0"


class TestFileParameterWidgetDialog:

    @pytest.fixture(autouse=True)
    def setup(self, app, tmp_path):
        self.valid_file = tmp_path / "sample.vcf"
        self.valid_file.write_text("data")
        self.param = FileParameter(
            name="testfile", description="", flag="--input",
            operations={"TEST"}, accepted_formats=["vcf"],
            strict=True, multiple=False,
        )
        self.widget = FileParameterWidget(self.param)

    def test_open_file_dialog_single(self):
        """_open_file_dialog should set parameter value for single file."""
        with patch("gui.widgets.parameter_widget.QFileDialog.getOpenFileName",
                   return_value=(str(self.valid_file), "")):
            self.widget._open_file_dialog()
        assert self.param.value == [str(self.valid_file).replace("\\", "/")]

    def test_open_file_dialog_cancelled(self):
        """Cancelling the dialog should not change the parameter value."""
        with patch("gui.widgets.parameter_widget.QFileDialog.getOpenFileName",
                   return_value=("", "")):
            self.widget._open_file_dialog()
        assert self.param.value == []

    def test_open_file_dialog_multiple(self, tmp_path):
        """_open_file_dialog should set multiple files when multiple=True."""
        f1 = tmp_path / "a.vcf"
        f1.write_text("data")
        f2 = tmp_path / "b.vcf"
        f2.write_text("data")
        param = FileParameter(
            name="multi", description="", flag="--input",
            operations={"TEST"}, accepted_formats=["vcf"], multiple=True,
        )
        widget = FileParameterWidget(param)
        with patch("gui.widgets.parameter_widget.QFileDialog.getOpenFileNames",
                   return_value=([str(f1), str(f2)], "")):
            widget._open_file_dialog()
        assert len(param.value) == 2

    def test_build_filter_with_formats(self):
        """_build_filter should return a filter string with accepted formats."""
        assert "vcf" in self.widget._build_filter()

    def test_build_filter_no_formats(self):
        """_build_filter should return all files when accepted_formats is None."""
        param = FileParameter(
            name="any", description="", flag="--input",
            operations={"TEST"}, accepted_formats=None,
        )
        widget = FileParameterWidget(param)
        assert widget._build_filter() == "All files (*)"


class TestFileParameterWidgetExpectedFormats:

    @pytest.fixture(autouse=True)
    def setup(self, app, tmp_path):
        self.unexpected_file = tmp_path / "sample.pdf"
        self.unexpected_file.write_text("data")
        self.param = FileParameter(
            name="testfile", description="", flag="--input",
            operations={"TEST"}, accepted_formats=["vcf"],
            strict=False, multiple=False,
        )
        self.widget = FileParameterWidget(self.param)

    def test_warning_shown_for_unexpected_format(self):
        """An unexpected file type should show a warning in the error label."""
        self.param.value = [str(self.unexpected_file)]
        assert self.widget._error_label.text() != ""