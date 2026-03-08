from typing import Any
from abc import ABC

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QComboBox,
)

from gui.model.parameter import (
    Parameter,
    BoolParameter,
    EnumParameter,
    StringParameter,
)


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

        label: QWidget = QLabel(parameter.name)
        layout.addWidget(label, stretch=1)

        parameter_widget: ParameterWidget
        reset_button = cls.ResetButton(parameter)

        if isinstance(parameter, BoolParameter):
            parameter_widget = BoolParameterWidget(parameter)
        elif isinstance(parameter, EnumParameter):
            parameter_widget = EnumParameterWidget(parameter)
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


class EnumParameterWidget(ParameterWidget):
    """
    A dropdown widget to edit an enumerated parameter.
    """

    def __init__(self, parameter: EnumParameter):
        """
        Initialize an `EnumParameterWidget` object.

        :param parameter: the enum parameter to reference
        :type parameter: EnumParameter
        """
        super().__init__(parameter)

        layout = QVBoxLayout(self)

        self._combo_box = QComboBox()
        self._combo_box.addItems(parameter.options)
        self._combo_box.setCurrentIndex(parameter.value)
        layout.addWidget(self._combo_box)

        self._combo_box.currentIndexChanged.connect(
            self._combo_box_current_index_changed
        )
        parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(int)
    def _combo_box_current_index_changed(self, new_index: int) -> None:
        self.parameter.value = new_index

    @Slot(int, bool)
    def _parameter_value_changed(self, new_value: int, valid: bool) -> None:
        self._combo_box.setCurrentIndex(new_value)


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
