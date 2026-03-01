from typing import Self
from PySide6.QtWidgets import QWidget, QLabel, QFormLayout, QVBoxLayout

from gui.model.parameter_group import ParameterGroup
from gui.widgets.parameter_widget import ParameterWidget


class ParameterFormSection(QWidget):
    def __init__(
            self,
            parameter_group: ParameterGroup
    ) -> None:
        super().__init__()

        self._parameter_group = parameter_group

        heading = QLabel(self._parameter_group.name)

        form_body = QWidget()
        form_layout = QFormLayout(form_body)
        form_layout.setContentsMargins(0, 0, 0, 0)
        for parameter in parameter_group.parameters:
            label, widget = ParameterWidget.from_parameter(parameter)
            form_layout.addRow(label, widget)
        
        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(form_body)
