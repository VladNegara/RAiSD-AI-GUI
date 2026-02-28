from typing import Self
from abc import ABC, abstractmethod

from PySide6.QtWidgets import QWidget

from gui.model.Parameter import Parameter


class ParameterWidget(QWidget):
    def __init__(self, parameter: Parameter[Any]):
        super().__init__()
        self._parameter = parameter

    @property
    def parameter(self) -> Parameter[Any]:
        return self._parameter        

    @classmethod
    def from_parameter(cls, parameter: Parameter) -> Self:
        print(parameter.name)
        # TODO: implement selection of widget subclass using parameter type
        raise NotImplementedError("ParameterWidget#from_parameter not implemented!")


class BoolParameterWidget(ParameterWidget):
    def __init__(self, parameter: Parameter[bool]) -> None:
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
