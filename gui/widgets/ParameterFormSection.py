from typing import Self
from PySide6.QtWidgets import QWidget, QFormLayout

from model.ParameterGroup import ParameterGroup
from widgets.ParameterWidget import ParameterWidget

class ParameterFormSection(QWidget):
    @classmethod
    def from_parameter_group(
            cls,
            parameter_form_section_widget: QWidget,
            parameter_group: ParameterGroup
    ) -> Self:
        # TODO: Add section title with parameter group name
        form_layout = QFormLayout(parameter_form_section_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        for parameter in parameter_group.parameters:
            parameter_widget = ParameterWidget.from_parameter(parameter)
            form_layout.addWidget(parameter_widget)

        parameter_form_section = cls()
        parameter_form_section.setLayout(form_layout)
        return parameter_form_section
