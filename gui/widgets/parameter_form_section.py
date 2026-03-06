from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from gui.model.parameter_group import ParameterGroup
from gui.widgets.parameter_widget import ParameterWidget


class ParameterFormSection(QWidget):
    """
    A section of the parameter form.

    Every section corresponds to a `ParameterGroup` object.
    """

    def __init__(
            self,
            parameter_group: ParameterGroup
    ) -> None:
        """
        Initialize a `ParameterFormSection` object.

        The method creates a `ParameterWidget` object for each
        parameter in the group by calling the `from_parameter` factory
        method. The widgets are placed in a form layout along with their
        labels.

        :param parameter_group: the parameter group to reference
        :type parameter_group: ParameterGroup
        """
        super().__init__()

        self._parameter_group = parameter_group

        heading = QLabel(self._parameter_group.name)

        form_body = QWidget()
        form_layout = QVBoxLayout(form_body)
        form_layout.setContentsMargins(0, 0, 0, 0)
        for parameter in parameter_group.parameters:
            form_row = ParameterWidget.from_parameter(parameter)
            form_layout.addWidget(form_row)
        
        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(form_body)
