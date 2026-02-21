from PySide6.QtWidgets import QWidget, QFormLayout

from model.ParameterGroup import ParameterGroup
from widgets.ParameterWidget import ParameterWidget, construct_parameter_widget

class ParameterFormSection(QWidget):
    def __init__(self):
        pass

    def construct_section(self, parameter_form_section_widget:QWidget, parameter_group:ParameterGroup):
        # TODO: Add section title with parameter group name
        form_layout = QFormLayout(parameter_form_section_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        for parameter in parameter_group.get_parameters():
            parameter_widget = construct_parameter_widget(parameter=parameter)
            form_layout.addWidget(parameter_widget)
