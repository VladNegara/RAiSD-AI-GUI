from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)

from PySide6.QtCore import Slot

from gui.model.parameter_group_list import ParameterGroupList
from gui.widgets.parameter_form_section import ParameterFormSection


class ParameterForm(QWidget):
    """
    A form of parameters to be filled in by the user.
    """

    def __init__(self, parameter_group_list: ParameterGroupList, editable: bool):
        """
        Initialize a `ParameterForm` object.

        :param parameter_group_list: the parameters to be filled in by
        the user
        :type parameter_group_list: ParameterGroupList
        """
        super().__init__()
        self._editable = editable
        self._parameter_group_list = parameter_group_list
        self._parameter_form_sections = []
        layout = QVBoxLayout(self)

        heading = QLabel("RAiSD-AI parameters")
        layout.addWidget(heading)

        for parameter_group in self._parameter_group_list:
            parameter_form_section = ParameterFormSection(parameter_group, editable=self._editable)
            layout.addWidget(parameter_form_section)
            self._parameter_form_sections.append(parameter_form_section)

    def touch_all(self) -> None:
        for section in self._parameter_form_sections:
            section.touch_all()

    def untouch_all(self) -> None:
        for section in self._parameter_form_sections:
            section.untouch_all()