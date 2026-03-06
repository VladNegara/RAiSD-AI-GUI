from typing import Any
from abc import ABC

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QCheckBox

from gui.model.parameter import (
    Parameter,
    BoolParameter,
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
        grouped horizontally with a label to be used as a form row.

        The method checks the type of the given parameter in order to
        create the suitable widget (e.g. a dropdown menu for an enum
        parameter). This is the recommended method of creating a
        `ParameterWidget` object.

        The method also creates a label that displays the parameter's
        name and groups it in a horizontal layout alongside the
        `ParameterWidget` object.

        :param parameter: the parameter
        :type parameter: Parameter[Any]

        :return: the label and the widget in a horizontal layout
        :rtype: QWidget
        """
        row = QWidget()
        row.setVisible(parameter.enabled)
        parameter.enabled_changed.connect(
            lambda new_enabled: row.setVisible(new_enabled)
        )
        layout = QHBoxLayout(row)

        label: QWidget = QLabel(parameter.name)
        layout.addWidget(label, stretch=1)

        parameter_widget: ParameterWidget

        if isinstance(parameter, BoolParameter):
            parameter_widget = BoolParameterWidget(parameter)
        # TODO: implement selection of widget subclass for other parameter types
        else:
            raise NotImplementedError(f"ParameterWidget#from_parameter not implemented for {type(parameter)}!")

        layout.addWidget(parameter_widget)

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
