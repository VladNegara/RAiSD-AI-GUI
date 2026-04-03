from typing import Any
from abc import ABC
from pathlib import Path

from PySide6.QtGui import QDesktopServices

from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QRegularExpression,
    QUrl
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFileDialog,
    QListWidget,
    QAbstractItemView
)
from PySide6.QtGui import (
    QRegularExpressionValidator,
)

from gui.model.parameter import (
    Parameter,
    OptionalParameter,
    MultiParameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    EnumParameter,
    StringParameter,
    StringPairListParameter,
    FileParameter,
)
from gui.widgets.utils import set_bool_property
from gui.widgets.collapsible import Collapsible


class AbstractQWidgetMeta(type(ABC), type(QWidget)):
    """
    Metaclass for an abstract base QWidget class.
    """

    pass


class ParameterWidget(ABC, QWidget, metaclass=AbstractQWidgetMeta):
    """
    A base class for input widgets to fill in parameters using the GUI.

    The class inherits from `ABC` to make it abstract and from
    `QWidget`.

    A `ParameterWidget` object holds a reference to a `Parameter`
    object, which it updates with values entered by the user.

    `ParameterWidget` objects should not be created directly, but
    through the `from_parameter` factory method.
    """

    class HintLabel(QLabel):
        def __init__(self, text: str) -> None:
            super().__init__(text=text)
            self.setObjectName("parameter_hint")

    class ResetButton(QPushButton):
        """
        A button to reset the value of a given parameter to its default
        value.
        """

        def __init__(self, parameter: Parameter[Any]) -> None:
            """
            Initialize a `ResetButtonWidget` object.

            :param parameter: the parameter to reference
            :type parameter: Parameter[Any]
            """
            super().__init__("Reset")
            self.setObjectName("reset_button")
            self._parameter = parameter

            self.clicked.connect(self._clicked)

        @Slot()
        def _clicked(self) -> None:
            self._parameter.reset_value()

    def __init__(self, parameter: Parameter[Any], editable: bool):
        """
        Initialize a `ParameterWidget` object.

        :param parameter: the parameter to reference
        :type parameter: Parameter[Any]
        """
        super().__init__()
        self._parameter = parameter
        self._editable = editable
        self._touched = False #variable for activating show_validity

        self._layout = QVBoxLayout(self)

        hints_widget = QWidget()
        self._hints_layout = QVBoxLayout(hints_widget)
        self._hints_layout.setContentsMargins(0, 0, 0, 0)
        self._hint_labels = []
        for hint in self._parameter.hints:
            hint_label = self.__class__.HintLabel(hint)
            self._hints_layout.addWidget(hint_label)
            self._hint_labels.append(hint_label)
        self._layout.addWidget(hints_widget)

        # `show_validity` is not annotated as a Slot.
        self._parameter.value_changed.connect(self.show_validity)
        self._parameter.hint_added.connect(self._hint_added)
        self._parameter.constraints_valid_changed.connect(
            self._constraints_valid_changed,
        )

    def show_validity(self) -> None:
        """
        Set the validity property on the relevant widgets.

        The validity is set on this widget's `validity_widgets` and on
        each of its hint labels.

        Validity is only shown if the widget is editable, and if the
        user has interacted with it. Otherwise, it is hidden.
        """
        show: bool = self._editable and self.touched

        parameter_valid = self._parameter.valid
        for widget in self.validity_widgets:
            if show:
                set_bool_property(widget, "valid", parameter_valid)
            else:
                set_bool_property(widget, "valid", None)

        constraints_valid = self._parameter.constraints_valid
        for i, constraint_valid in enumerate(constraints_valid):
            hint_label = self._hint_labels[i]
            if show:
                set_bool_property(hint_label, "valid", constraint_valid)
            else:
                set_bool_property(hint_label, "valid", None)

    @property
    def touched(self) -> bool:
        """
        Whether this widget has been interacted with by the user.

        Setting this property will update the validity displayed on the
        widget accordingly.
        """
        return self._touched

    @touched.setter
    def touched(self, new_touched: bool) -> None:
        self._touched = new_touched
        self.show_validity()

    @property
    def validity_widgets(self) -> list[QWidget]:
        """
        The widgets that show the validity of this parameter widget.
        """
        return []

    @property
    def parameter(self) -> Parameter[Any]:
        """
        The `Parameter` object referenced by the widget.
        """
        return self._parameter

    @classmethod
    def from_parameter(cls, parameter: Parameter[Any], editable: bool) -> "ParameterWidget":
        """
        Create a suitable `ParameterWidget` for a given `Parameter`.

        The method checks the type of the given parameter in order to
        create the suitable widget (e.g. a dropdown menu for an enum
        parameter). This is the recommended method of creating a
        `ParameterWidget` object.

        :param parameter: the parameter to create a widget for
        :type parameter: Parameter[Any]

        :param editable: whether the widget is editable or not
        :type editable: bool

        :return: the corresponding widget
        :rtype: ParameterWidget
        """
        if isinstance(parameter, OptionalParameter):
            return OptionalParameterWidget(parameter, editable)
        if isinstance(parameter, MultiParameter):
            return MultiParameterWidget(parameter, editable)
        if isinstance(parameter, BoolParameter):
            return BoolParameterWidget(parameter, editable)
        if isinstance(parameter, IntParameter):
            return IntParameterWidget(parameter, editable)
        if isinstance(parameter, FloatParameter):
            return FloatParameterWidget(parameter, editable)
        if isinstance(parameter, EnumParameter):
            return EnumParameterWidget(parameter, editable)
        if isinstance(parameter, StringParameter):
            return StringParameterWidget(parameter, editable)
        if isinstance(parameter, FileParameter):
            return FileParameterWidget(parameter, editable)
        if isinstance(parameter, StringPairListParameter):
            return StringPairListParameterWidget(parameter, editable)
        raise NotImplementedError(f"ParameterWidget#from_parameter not implemented for {type(parameter)}!")

    def build_form_row(self) -> QWidget:
        """
        Build the form row containing this widget.

        Call this method only once for a given widget.

        The method creates a label that displays the parameter's
        name and groups it in a horizontal layout alongside the
        `ParameterWidget` object.

        :return: the label and the widget in a horizontal layout
        :rtype: QWidget
        """
        row = QWidget()
        row.setVisible(self.parameter.enabled)
        self.parameter.enabled_changed.connect(
            lambda new_enabled: row.setVisible(new_enabled)
        )
        layout = QHBoxLayout(row)

        label_header = QLabel(self.parameter.name)
        label_header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label_header.setObjectName("label_header")
        label_body = QLabel(self.parameter.description)
        label_body.setObjectName("label_body")
        label: QWidget = Collapsible(
            label_header,
            label_body,
        )
        layout.addWidget(label, stretch=1)

        layout.addWidget(self)

        if self._editable:
            reset_button = ParameterWidget.ResetButton(self.parameter)
            layout.addWidget(reset_button)

        return row

    @Slot(str)
    def _hint_added(self, new_hint: str) -> None:
        hint_label = self.__class__.HintLabel(new_hint)
        self._hints_layout.addWidget(hint_label)
        self._hint_labels.append(hint_label)

    @Slot()
    def _constraints_valid_changed(
            self,
    ) -> None:
        self.show_validity()


class OptionalParameterWidget(ParameterWidget):
    """
    A widget to edit an optional parameter.
    """

    def __init__(self, parameter: OptionalParameter, editable: bool) -> None:
        """
        Initialize an `OptionalParameterWidget` object.

        :param parameter: the optional parameter to reference
        :type parameter: OptionalParameter

        :param editable: whether the widget is editable
        :type editable: bool
        """
        super().__init__(parameter, editable)
        self._child_widget: ParameterWidget | None = None

        self._checkbox = QCheckBox()
        self._checkbox.setCheckState(
            Qt.CheckState.Checked
            if parameter.value
            else Qt.CheckState.Unchecked
        )
        self._checkbox.setEnabled(self._editable)
        self._layout.insertWidget(0, self._checkbox)

        self._checkbox.checkStateChanged.connect(self._check_state_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    def build_form_row(self) -> QWidget:
        row = QWidget()
        layout = QVBoxLayout(row)

        own_row = super().build_form_row()
        layout.addWidget(own_row)

        # `self.parameter`` should always be of type OptionalParameter,
        # even though the type checker doesn't agree.
        self._child_widget = ParameterWidget.from_parameter(
            self.parameter.parameter, # type: ignore
            self._editable
        )
        child_row = self._child_widget.build_form_row()
        layout.addWidget(child_row)

        return row

    @Slot(Qt.CheckState)
    def _check_state_changed(self, new_check_state: Qt.CheckState) -> None:
        match new_check_state:
            case Qt.CheckState.Checked:
                self.parameter.value = True
            case Qt.CheckState.Unchecked:
                self.parameter.value = False

    @Slot(bool, bool)
    def _parameter_value_changed(self, new_value: bool, valid: bool) -> None:
        self._checkbox.setChecked(new_value)

    @ParameterWidget.touched.setter
    def touched(self, new_touched: bool) -> None:
        ParameterWidget.touched.__set__(self, new_touched)
        if self._child_widget is not None:
            self._child_widget.touched = self.touched


class MultiParameterWidget(ParameterWidget):
    """
    A widget to edit a multi-value parameter.
    """

    def __init__(self, parameter: MultiParameter, editable: bool):
        """
        Initialize a `MultiParameterWidget` object.

        :param parameter: the optional parameter to reference
        :type parameter: MultiParameter

        :param editable: whether the widget is editable
        :type editable: bool
        """
        super().__init__(parameter, editable)
        self._child_widgets: list[ParameterWidget] = []

    def build_form_row(self) -> QWidget:
        row = QWidget()
        layout = QVBoxLayout(row)

        own_row = super().build_form_row()
        layout.addWidget(own_row)

        # This should always work, since the constructor is given a
        # MultiParameter object.
        for child_parameter in self.parameter.parameters: # type: ignore
            child_widget = ParameterWidget.from_parameter(child_parameter, self._editable)
            self._child_widgets.append(child_widget)
            child_row = child_widget.build_form_row()
            layout.addWidget(child_row)

        return row

    @ParameterWidget.touched.setter
    def touched(self, new_touched: bool) -> None:
        ParameterWidget.touched.__set__(self, new_touched)
        for child in self._child_widgets:
            child.touched = self.touched


class BoolParameterWidget(ParameterWidget):
    """
    A widget to edit a boolean parameter.
    """

    def __init__(self, parameter: Parameter[bool], editable: bool) -> None:
        """
        Initialize a `BoolParameterWidget` object.

        :param parameter: the boolean parameter to reference
        :type parameter: Parameter[bool]

        :param editable: whether the widget is editable
        :type editable: bool
        """
        super().__init__(parameter, editable)

        self._checkbox = QCheckBox()
        self._checkbox.setCheckState(
            Qt.CheckState.Checked
            if parameter.value
            else Qt.CheckState.Unchecked
        )
        self._checkbox.setEnabled(self._editable)
        self._layout.insertWidget(0, self._checkbox)

        self._checkbox.checkStateChanged.connect(self._check_state_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(Qt.CheckState)
    def _check_state_changed(self, new_check_state: Qt.CheckState) -> None:
        self.touched = True
        match new_check_state:
            case Qt.CheckState.Checked:
                self.parameter.value = True
            case Qt.CheckState.Unchecked:
                self.parameter.value = False

    @Slot(bool, bool)
    def _parameter_value_changed(self, new_value: bool, valid: bool) -> None:
        self._checkbox.setChecked(new_value)


class IntParameterWidget(ParameterWidget):
    """
    A widget to edit an integer parameter.
    """

    def __init__(self, parameter: IntParameter, editable: bool) -> None:
        """
        Initialize an `IntParameterWidget` object.

        :param parameter: the integer parameter to reference
        :type parameter: IntParameter

        :param editable: whether the widget is editable
        :type editable: bool
        """
        super().__init__(parameter, editable)

        self._line_edit = QLineEdit()
        self._line_edit.setText(str(parameter.value))
        # Allow an arbitrary length integer.
        regex = QRegularExpression(R"^(-)?[0-9]*$")
        validator = QRegularExpressionValidator(regex)
        self._line_edit.setValidator(validator)
        self._line_edit.setReadOnly(not self._editable)
        self._layout.insertWidget(0, self._line_edit)

        self._line_edit.textChanged.connect(self._text_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(str)
    def _text_changed(self) -> None:
        self.touched = True
        try:
            self.parameter.value = int(self._line_edit.text())
        except:
            pass

    @Slot(int, bool)
    def _parameter_value_changed(self, new_value: int, valid: bool) -> None:
        self.touched = True
        try:
            current = int(self._line_edit.text())
            values_differ = current != new_value
        except ValueError:
            values_differ = True
        if values_differ:
            self._line_edit.setText(str(new_value))

    @property
    def validity_widgets(self) -> list[QWidget]:
        return [self._line_edit]


class FloatParameterWidget(ParameterWidget):
    """
    A widget to edit a float parameter.
    """

    def __init__(self, parameter: FloatParameter, editable: bool) -> None:
        """
        Initialize a `FloatParameterWidget` object.

        :param parameter: the float parameter to reference
        :type parameter: FloatParameter

        :param editable: whether the widget is editable
        :type editable: bool
        """
        super().__init__(parameter, editable)

        self._line_edit = QLineEdit()
        self._line_edit.setText(str(parameter.value))
        # Allow an arbitrary length integer, optionally followed by a
        # decimal point and an arbitrary length fractional part.
        regex = QRegularExpression(
            R"^(-)?[0-9]*([.][0-9]*)?$"
        )
        validator = QRegularExpressionValidator(regex)
        self._line_edit.setValidator(validator)
        self._line_edit.setReadOnly(not self._editable)
        self._layout.insertWidget(0, self._line_edit)

        self._line_edit.textChanged.connect(self._text_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(str)
    def _text_changed(self) -> None:
        self.touched = True
        try:
            self.parameter.value = float(self._line_edit.text())
        except:
            pass

    @Slot(float, bool)
    def _parameter_value_changed(self, new_value: float, valid: bool) -> None:
        try:
            current = float(self._line_edit.text())
            values_differ = current != new_value
        except ValueError:
           values_differ = True
        if values_differ:
            self._line_edit.setText(str(new_value))

    @property
    def validity_widgets(self) -> list[QWidget]:
        return [self._line_edit]


class EnumParameterWidget(ParameterWidget):
    """
    A dropdown widget to edit an enumerated parameter.
    """

    def __init__(self, parameter: EnumParameter, editable: bool):
        """
        Initialize an `EnumParameterWidget` object.

        :param parameter: the enum parameter to reference
        :type parameter: EnumParameter
        """
        super().__init__(parameter, editable)

        self._combo_box = QComboBox()
        self._combo_box.addItems(parameter.options)
        self._combo_box.setCurrentIndex(parameter.value)
        self._combo_box.setEnabled(self._editable)
        self._layout.insertWidget(0, self._combo_box)

        self._combo_box.currentIndexChanged.connect(
            self._combo_box_current_index_changed
        )
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(int)
    def _combo_box_current_index_changed(self, new_index: int) -> None:
        self.touched = True
        self.parameter.value = new_index

    @Slot(int, bool)
    def _parameter_value_changed(self, new_value: int, valid: bool) -> None:
        self._combo_box.setCurrentIndex(new_value)


class StringParameterWidget(ParameterWidget):
    """
    A widget to edit a string parameter.
    """

    def __init__(self, parameter: StringParameter, editable: bool) -> None:
        """
        Initialize a `StringParameterWidget` object.

        If the parameter has a maximum length, the length is enforced on
        the input field and displayed to the user in a label.

        :param parameter: the string parameter to reference
        :type parameter: StringParameter

        :param editable: whether the widget is editable
        :type editable: bool
        """
        super().__init__(parameter, editable)

        self._line_edit = QLineEdit()
        self._line_edit.setText(parameter.value)
        self._line_edit.setReadOnly(not self._editable)
        self._layout.insertWidget(0, self._line_edit)

        self._line_edit.textChanged.connect(self._text_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(str)
    def _text_changed(self) -> None:
        self.touched = True
        self.parameter.value = self._line_edit.text()

    @Slot(str, bool)
    def _parameter_value_changed(self, new_value: str, valid: bool) -> None:
        self._line_edit.setText(new_value)

    @property
    def validity_widgets(self) -> list[QWidget]:
        return [self._line_edit]


class StringPairListParameterWidget(ParameterWidget):
    class Row(QWidget):
        values_edited = Signal(str, str)
        delete_button_clicked = Signal()

        def __init__(
                self,
                editable: bool,
                values: tuple[str, str] = ("", ""),
                delete_button_visible: bool = True,
        ) -> None:
            super().__init__()
            self._editable = editable

            layout = QHBoxLayout(self)

            self._left_line_edit = QLineEdit()
            self._left_line_edit.setText(values[0])
            self._left_line_edit.setReadOnly(not self._editable)
            self._left_line_edit.editingFinished.connect(
                self._editing_finished,
            )
            layout.addWidget(self._left_line_edit)

            self._right_line_edit = QLineEdit()
            self._right_line_edit.setText(values[1])
            self._right_line_edit.setReadOnly(not self._editable)
            self._right_line_edit.editingFinished.connect(
                self._editing_finished,
            )
            layout.addWidget(self._right_line_edit)

            self._delete_button = QPushButton("Delete row")
            self._delete_button.clicked.connect(self.delete_button_clicked)
            self._delete_button.setVisible(
                delete_button_visible and self._editable
            )
            layout.addWidget(self._delete_button)

        @property
        def left_line_edit(self) -> QLineEdit:
            return self._left_line_edit

        @property
        def right_line_edit(self) -> QLineEdit:
            return self._right_line_edit

        @property
        def values(self) -> tuple[str, str]:
            return (
                self._left_line_edit.text(),
                self._right_line_edit.text(),
            )

        @values.setter
        def values(self, new_values: tuple[str, str]) -> None:
            self._left_line_edit.setText(new_values[0])
            self._right_line_edit.setText(new_values[1])

        @property
        def delete_button_visible(self) -> bool:
            return self._delete_button.isVisible()

        @delete_button_visible.setter
        def delete_button_visible(self, new_visible: bool) -> None:
            self._delete_button.setVisible(new_visible and self._editable)

        @Slot()
        def _editing_finished(self) -> None:
            self.values_edited.emit(*self.values)

    def __init__(
            self,
            parameter: StringPairListParameter,
            editable: bool = True,
    ) -> None:
        super().__init__(
            parameter=parameter,
            editable=editable,
        )

        self.rows: list[StringPairListParameterWidget.Row] = []
        row_widget = QWidget()
        self.row_layout = QVBoxLayout(row_widget)
        self._parameter: StringPairListParameter
        delete_button_visible = (
            len(self._parameter.value) > self._parameter.min_count
        )
        for i, pair in enumerate(self._parameter.value):
            row = self.__class__.Row(self._editable, pair)
            row.delete_button_visible = delete_button_visible
            row.values_edited.connect(
                lambda l, r, i=i: self._row_values_edited(i, l, r)
            )
            row.delete_button_clicked.connect(
                lambda i=i: self._delete_button_clicked(i)
            )
            self.rows.append(row)
            self.row_layout.addWidget(row)
        self._layout.insertWidget(0, row_widget)

        if self._editable:
            add_pair_button = QPushButton("Add another row")
            add_pair_button.clicked.connect(self._add_clicked)
            self._layout.insertWidget(1, add_pair_button)

        self._parameter.value_changed.connect(
            self._parameter_value_changed,
        )
        self._parameter.pair_valid_changed.connect(
            self._pair_valid_changed,
        )

    @Slot()
    def _add_clicked(self) -> None:
        self._parameter.add_pair()

    @Slot()
    def _parameter_value_changed(
            self,
            new_value: list[tuple[str, str]],
            new_valid: bool,
    ) -> None:
        current_count = len(self.rows)
        new_count = len(new_value)

        delete_button_visible = (
            new_count > self._parameter.min_count
        )

        for i in range(min(current_count, new_count)):
            self.rows[i].values = new_value[i]
            self.rows[i].delete_button_visible = delete_button_visible

        if new_count < current_count:
            for i in range(new_count, current_count):
                row = self.rows[i]
                row.values_edited.disconnect()
                row.delete_button_clicked.disconnect()
                self.row_layout.removeWidget(row)
                row.destroy()
            self.rows = self.rows[:new_count]
        if new_count > current_count:
            for i in range(current_count, new_count):
                new_row = self.__class__.Row(
                    self._editable,
                    new_value[i],
                )
                new_row.delete_button_visible = delete_button_visible
                new_row.values_edited.connect(
                    lambda l, r, i=i: self._row_values_edited(i, l, r)
                )
                new_row.delete_button_clicked.connect(
                    lambda i=i: self._delete_button_clicked(i)
                )
                self.rows.append(new_row)
                self.row_layout.addWidget(new_row)

    @Slot(int, bool, bool)
    def _pair_valid_changed(
        self,
        index: int,
        new_left_valid: bool, 
        new_right_valid: bool,
    ) -> None:
        set_bool_property(
            self.rows[index].left_line_edit,
            "valid",
            new_left_valid,
        )
        set_bool_property(
            self.rows[index].right_line_edit,
            "valid",
            new_right_valid,
        )

    @Slot(int, str, str)
    def _row_values_edited(self, index: int, left: str, right: str) -> None:
        self._parameter.set_pair(index, (left, right))

    @Slot(int)
    def _delete_button_clicked(self, index: int) -> None:
        self._parameter.delete_pair(index)


class FileParameterWidget(ParameterWidget):
    """
    A widget to edit a file parameter.

    Provides a browse button that opens a file dialog that is filtered with
    file types that are allowed file types. Depending on the state of multiple
    flags, the file dialog enforces multiple or singular file selection.
    Displays the currently selected file path(s).
    """

    def __init__(self, parameter: FileParameter, editable: bool) -> None:
        """
        Initialize a `FileParameter` object.

        If the parameter has a maximum length, the length is enforced on
        the input field and displayed to the user in a label.

        :param parameter: the string parameter to reference
        :type parameter: StringParameter

        :param editable: whether the widget is editable
        :type editable: bool
        """
        super().__init__(parameter, editable)

        parameter.value_changed.connect(self._parameter_value_changed)

        # If the widget is locked: create a list with the selected files
        if not self._editable:
            self.list_widget = QListWidget()
            self.list_widget.collapsible = False
            self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            self.list_widget.setSortingEnabled(True)
            if self.parameter.value:
                self.list_widget.addItems(self.parameter.value)
            else:
                self.list_widget.addItem("No files selected")
            self.list_widget.setMinimumWidth(int(self.list_widget.sizeHintForColumn(0)*1.01))
            self.list_widget.setMaximumHeight(self.list_widget.sizeHintForRow(0)*self.list_widget.count())
            self.list_widget.doubleClicked.connect(self._on_double_click)
            self._layout.insertWidget(0, self.list_widget)
            return

        # If the widget is not locked:
        self.setFixedWidth(300)
        self._path_label = QLabel("No file selected")
        self._layout.insertWidget(0, self._path_label)

        self._file_browse = QPushButton('Browse')
        self._file_browse.clicked.connect(self._open_file_dialog)

        self._layout.insertWidget(1, self._file_browse)

        mode = "multiple files" if parameter.multiple else "one file"

        if parameter.strict and parameter.accepted_formats is not None:
            allowed = ', '.join(parameter.accepted_formats)
            hint = QLabel(f"Select {mode} — Allowed types: {allowed}")
            hint.setWordWrap(True)
            self._layout.insertWidget(1, hint)
        elif (not parameter.strict
              and parameter.accepted_formats is None
              and parameter.expected_formats is not None):
            self._error_label = QLabel("")
            self._error_label.setProperty("valid", "false")
            self._error_label.style().unpolish(self)
            self._error_label.style().polish(self)
            self._layout.insertWidget(1, self._error_label)
            expected = ', '.join(parameter.expected_formats)
            hint = QLabel(f"Select {mode} — Expected file types: {expected}. "
                          + f"You can still upload a different file.")
            hint.setWordWrap(True)
            self._layout.insertWidget(2, hint)
        elif (parameter.strict is False
              and parameter.accepted_formats is None
              and parameter.expected_formats is None):
            hint = QLabel(f"Select {mode} — Allowed types: any type.")
            hint.setWordWrap(True)
            self._layout.insertWidget(1, hint)

    @Slot(int)
    def _on_double_click(self, index) -> None:
        """
        Handles a double click on a list item; a file. The file
        is opened in the system's default file editor.
        """
        if self.parameter.value:
            path = self.list_widget.itemFromIndex(index).text()
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    @Slot(list, bool)
    def _parameter_value_changed(
        self,
        file_paths: list[str],
        valid: bool
    ) -> None:
        # If the widget is locked add the files to the list
        if not self._editable:
            self.list_widget.clear()
            if file_paths:
                self.list_widget.addItems(file_paths)
            else:
                self.list_widget.addItem("No files selected")
            self.list_widget.setMinimumWidth(int(self.list_widget.sizeHintForColumn(0)*1.01))
            self.list_widget.setMinimumHeight(self.list_widget.sizeHintForRow(0)*self.list_widget.count())
            self.list_widget.setMaximumHeight(self.list_widget.sizeHintForRow(0)*self.list_widget.count())
            self.list_widget.setVisible(True)
            return

        # If the widget is not locked
        if file_paths:
            self._path_label.setText("\n".join(file_paths))
            full_text = "\n".join(file_paths)
            self._path_label.setToolTip(full_text)
            display = "\n".join(Path(f).name for f in file_paths)
            self._path_label.setText(display)
        else:
            self._path_label.setText("No file selected")

        if not valid and file_paths:
            allowed = (
                ', '.join(self.parameter.accepted_formats)
                if self.parameter.accepted_formats
                else ""
            )
            self._error_label.setText(f"Invalid file type. Allowed: {allowed}")
        elif not self.parameter.matches_expected and file_paths:
            if self.parameter.expected_formats:
                expected = ', '.join(self.parameter.expected_formats)
                self._error_label.setText(
                    f"Warning: unexpected file type. "
                    + f"Expected: {expected}. You can still proceed."
                )
        else:
            pass

    @Slot()
    def _open_file_dialog(self) -> None:
        """
        Helper function that opens the OS file picker. If `multiple`
        is `True`, it uses `getOpenFileNames` to allow for multiple
        file selection. Otherwise, it uses `getOpenFileName` to allow
        only a single file.
        """
        self.touched = True
        if self.parameter.multiple:
            filenames, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Files",
                self.parameter.value[0] if self.parameter.value else "",
                self._build_filter()
            )
        else:
            single, _ = QFileDialog.getOpenFileName(
                self,
                "Select File",
                self.parameter.value[0] if self.parameter.value else "",
                self._build_filter()
            )
            filenames = [single] if single else []

        if filenames:
            self.parameter.value = [Path(f).as_posix() for f in filenames]

    def _build_filter(self) -> str:
        """
        Helper function to filter and show only allowed file types to
        the user.
        """
        if self.parameter.accepted_formats is None:
            return "All files (*)"
        extensions = " ".join(
            f"*{ext}" for ext in self.parameter.accepted_formats
        )
        return f"Allowed files ({extensions})"

    @property
    def validity_widgets(self) -> list[QWidget]:
        if self._editable and self._file_browse is not None:
            return [self._file_browse]
        return []
