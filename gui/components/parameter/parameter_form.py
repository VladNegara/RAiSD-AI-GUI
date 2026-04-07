from PySide6.QtWidgets import (
    QWidget,
)

from PySide6.QtCore import Slot

from .parameter_form_section import ParameterFormSection
from gui.model.run_record import RunRecord
from gui.widgets import VBoxLayout
from gui.style import constants


class ParameterForm(QWidget):
    """
    A form of parameters to be filled in by the user.
    """

    def __init__(self, run_record: RunRecord, editable: bool):
        """
        Initialize a `ParameterForm` object.

        :param run_record: the `RunRecord` holding the parameters to be filled in by
        the user
        :type run_record: RunRecord
        """
        super().__init__()
        self._editable = editable
        self._run_record = run_record
        self._parameter_form_sections = []
        layout = VBoxLayout(
            self,
            spacing=constants.GAP_TINY,
        )

        for parameter_group in self._run_record.parameter_groups:
            parameter_form_section = ParameterFormSection(parameter_group, editable=self._editable)
            layout.addWidget(parameter_form_section)
            self._parameter_form_sections.append(parameter_form_section)

        layout.addStretch()

    def touch_all(self) -> None:
        for section in self._parameter_form_sections:
            section.touch_all()

    def untouch_all(self) -> None:
        for section in self._parameter_form_sections:
            section.untouch_all()