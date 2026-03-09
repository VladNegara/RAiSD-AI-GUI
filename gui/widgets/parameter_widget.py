from typing import Any
from abc import ABC

from PySide6.QtCore import (
    Qt,
    Slot,
    QRegularExpression,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QLineEdit,
    QPushButton,
)
from PySide6.QtGui import (
    QRegularExpressionValidator,
)

from gui.model.parameter import (
    Parameter,
    BoolParameter,
    IntParameter,
    FloatParameter,
    StringParameter,
)
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
            self._parameter = parameter

            self.clicked.connect(self._clicked)

        @Slot()
        def _clicked(self) -> None:
            self._parameter.reset_value()

    def __init__(self, parameter: Parameter[Any]):
        """
        Initialize a `ParameterWidget` object.

        :param parameter: the parameter to reference
        :type parameter: Parameter[Any]
        """
        super().__init__()
        self._parameter = parameter

    @property
    def parameter(self) -> Parameter[Any]:
        """
        The `Parameter` object referenced by the widget.
        """
        return self._parameter        

    @classmethod
    def from_parameter(cls, parameter: Parameter[Any]) -> QWidget:
        """
        Create a suitable `ParameterWidget` for a given `Parameter`,
        along with a label.

        The method checks the type of the given parameter in order to
        create the suitable widget (e.g. a dropdown menu for an enum
        parameter). This is the recommended method of creating a
        `ParameterWidget` object.

        The method also creates a label that displays the parameter's
        name and returns it alongside the `ParameterWidget` object.

        :param parameter: the parameter
        :type parameter: Parameter[Any]

        :return: the label and the widget
        :rtype: tuple[QWidget, ParameterWidget]
        """
        row = QWidget()
        layout = QHBoxLayout(row)

        label_header = QLabel(parameter.name)
        label_header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label_body = QLabel(parameter.description)
        label: QWidget = Collapsible(
            label_header,
            label_body,
        )
        layout.addWidget(label, stretch=1)

        parameter_widget: ParameterWidget
        reset_button = cls.ResetButton(parameter)

        if isinstance(parameter, BoolParameter):
            parameter_widget = BoolParameterWidget(parameter)
        elif isinstance(parameter, IntParameter):
            parameter_widget = IntParameterWidget(parameter)
        elif isinstance(parameter, FloatParameter):
            parameter_widget = FloatParameterWidget(parameter)
        elif isinstance(parameter, StringParameter):
            parameter_widget = StringParameterWidget(parameter)
        else:
            # TODO: implement selection of widget subclass for other parameter types
            raise NotImplementedError(f"ParameterWidget#from_parameter not implemented for {type(parameter)}!")

        layout.addWidget(parameter_widget)
        layout.addWidget(reset_button)

        return row

class BoolParameterWidget(ParameterWidget):
    """
    A widget to edit a boolean parameter.
    """

    def __init__(self, parameter: Parameter[bool]) -> None:
        """
        Initialize a `BoolParameterWidget` object.

        :param parameter: the boolean parameter to reference
        :type parameter: Parameter[bool]
        """
        super().__init__(parameter)

        layout = QVBoxLayout(self)
        self._checkbox = QCheckBox()
        self._checkbox.setCheckState(
            Qt.CheckState.Checked
            if parameter.value
            else Qt.CheckState.Unchecked
        )
        layout.addWidget(self._checkbox)

        self._checkbox.checkStateChanged.connect(self._check_state_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

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


class IntParameterWidget(ParameterWidget):
    """
    A widget to edit an integer parameter.
    """

    def __init__(self, parameter: IntParameter) -> None:
        """
        Initialize an `IntParameterWidget` object.

        :param parameter: the integer parameter to reference
        :type parameter: IntParameter
        """
        super().__init__(parameter)

        layout = QVBoxLayout(self)

        self._lineedit = QLineEdit()
        self._lineedit.setText(str(parameter.value))
        # Allow an arbitrary length integer.
        regex = QRegularExpression(R"^(-)?[0-9]*$")
        validator = QRegularExpressionValidator(regex)
        self._lineedit.setValidator(validator)
        layout.addWidget(self._lineedit)

        match (parameter.lower_bound is None, parameter.upper_bound is None):
            case (False, False):
                label = QLabel(f'(between {parameter.lower_bound}'
                               + f' and {parameter.upper_bound})')
                layout.addWidget(label)
            case (False, True):
                label = QLabel(f'(minimum {parameter.lower_bound})')
                layout.addWidget(label)
            case (True, False):
                label = QLabel(f'(maximum {parameter.upper_bound})')
                layout.addWidget(label)
    
        self._lineedit.editingFinished.connect(self._text_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(str)
    def _text_changed(self) -> None:
        try: 
            self.parameter.value = int(self._lineedit.text())
        except:
            self._lineedit.setText(str(self.parameter.value))

    @Slot(int, bool)
    def _parameter_value_changed(self, new_value: int, valid: bool) -> None:
        self._lineedit.setText(str(new_value))


class FloatParameterWidget(ParameterWidget):
    """
    A widget to edit a float parameter.
    """

    def __init__(self, parameter: FloatParameter) -> None:
        """
        Initialize a `FloatParameterWidget` object.

        :param parameter: the float parameter to reference
        :type parameter: FloatParameter
        """
        super().__init__(parameter)

        layout = QVBoxLayout(self)

        self._lineedit = QLineEdit()
        self._lineedit.setText(str(parameter.value))
        # Allow an arbitray length integer, optionally followed by a
        # decimal point and an arbitrary length fractional part.
        regex = QRegularExpression(
            R"^(-)?[0-9]*([.][0-9]*)?$"
        )
        validator = QRegularExpressionValidator(regex)
        self._lineedit.setValidator(validator)
        layout.addWidget(self._lineedit)

        match (parameter.lower_bound is None, parameter.upper_bound is None):
            case (False, False):
                label = QLabel(f'(between {parameter.lower_bound}'
                               + f' and {parameter.upper_bound})')
                layout.addWidget(label)
            case (False, True):
                label = QLabel(f'(minimum {parameter.lower_bound})')
                layout.addWidget(label)
            case (True, False):
                label = QLabel(f'(maximum {parameter.upper_bound})')
                layout.addWidget(label)
    
        self._lineedit.editingFinished.connect(self._text_changed)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(str)
    def _text_changed(self) -> None:
        try:
            self.parameter.value = float(self._lineedit.text())
        except:
            self._lineedit.setText(str(self.parameter.value))

    @Slot(float, bool)
    def _parameter_value_changed(self, new_value: float, valid: bool) -> None:
        self._lineedit.setText(str(new_value))


class StringParameterWidget(ParameterWidget):
    """
    A widget to edit a string parameter.
    """

    def __init__(self, parameter: StringParameter) -> None:
        """
        Initialize a `StringParameterWidget` object.

        If the parameter has a maximum length, the length is enforced on
        the input field and displayed to the user in a label.

        :param parameter: the string parameter to reference
        :type parameter: StringParameter
        """
        super().__init__(parameter)

        layout = QVBoxLayout(self)

        self._line_edit = QLineEdit()
        self._line_edit.setText(parameter.value)
        layout.addWidget(self._line_edit)

        if parameter.max_length is not None:
            self._line_edit.setMaxLength(parameter.max_length)
            hint = QLabel(f"Max length: {parameter.max_length}")
            layout.addWidget(hint)

        self._line_edit.editingFinished.connect(self._editing_finished)
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(str)
    def _editing_finished(self) -> None:
        self.parameter.value = self._line_edit.text()

    @Slot(str, bool)
    def _parameter_value_changed(self, new_value: str, valid: bool) -> None:
        self._line_edit.setText(new_value)
        if valid: # Styling can be changed in the future
            self._line_edit.setStyleSheet("QLineEdit { border: 1px solid green; }")
        else:
            self._line_edit.setStyleSheet("QLineEdit { border: 1px solid red; }")
