from abc import ABC, abstractmethod

from PySide6.QtWidgets import QWidget

from model.Parameter import Parameter

class ParameterWidget(QWidget):
    def __init__(self):
        # TODO: implement interface classes
        pass


def construct_parameter_widget(parameter:Parameter) -> QWidget:
    print(parameter.name)
    # TODO: implement construction of widget using template widget, parameter type, data
    return None