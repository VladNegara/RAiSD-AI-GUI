from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from PySide6.QtCore import Signal, Slot

from gui.model.parameter_group import ParameterGroup
from gui.widgets.parameter_widget import ParameterWidget


class ParameterFormSection(QWidget):
    """
    A section of the parameter form.

    Every section corresponds to a `ParameterGroup` object.
    """

    def __init__(
            self,
            parameter_group: ParameterGroup,
            locked: bool
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
        self._parameter_group.enabled_changed.connect(self._parameter_group_enabled_changed)
        self._locked = locked

        # Make widgets
        heading = QLabel(self._parameter_group.name)

        form_body = QWidget()
        form_layout = QVBoxLayout(form_body)
        form_layout.setContentsMargins(0, 0, 0, 0)
        for parameter in parameter_group:
            form_row = ParameterWidget.from_parameter(parameter).build_form_row()
            form_layout.addWidget(form_row)

        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(form_body)

        self.setVisible(self._parameter_group.enabled)

    @property
    def parameter_group(self) -> ParameterGroup:
        """
        The ParameterGroup of the ParameterFormSection.
        """
        return self._parameter_group
    
    @Slot(bool)
    def _parameter_group_enabled_changed(self, new_value: bool) -> None:
        """
        Handle an enabled_changed from the ParameterGroup by setting 
        visibility accordingly.
        
        :new_value param: the new value of enabled of the ParameterGroup
        :new_value type: bool
        """
        self.setVisible(new_value)
