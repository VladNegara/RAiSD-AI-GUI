from typing import Self
from abc import ABC, abstractmethod

from PySide6.QtWidgets import QWidget

from model.Parameter import Parameter


class ParameterWidget(ABC, QWidget):
    @classmethod
    def from_parameter(cls, parameter: Parameter) -> Self:
        print(parameter.name)
        # TODO: implement selection of widget subclass using parameter type
        raise NotImplementedError("ParameterWidget#from_parameter not implemented!")
