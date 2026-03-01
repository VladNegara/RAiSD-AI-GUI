from PySide6.QtCore import QRect
from PySide6.QtWidgets import QMainWindow, QWidget, QRadioButton

from gui.ui.uiMainWindow import Ui_MainWindow
from gui.model.parameter_group_list import ParameterGroupList
from gui.widgets.parameter_form_section import ParameterFormSection


class MainWindow(QMainWindow):
    """
    The main window of the RAiSD-AI GUI application.
    """
    def __init__(self, parameter_group_list: ParameterGroupList):
        """
        Initialize the main window.

        :param parameter_group_list: the parameters to be filled in
        by the user
        :type parameter_group_list: ParameterGroupList
        """
        super().__init__()
        self.parameter_group_list = parameter_group_list

        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect standard signals (buttons)
        self.ui.buttonBox.accepted.connect(self._accepted)

        # TODO: link execute button to command executor
            # TODO: make command executor for terminal commands and
            # virtual environment
        # TODO: link execution done to update_history()

        self._build_parameter_form()

    def _accepted(self) -> None:
        print(self.parameter_group_list.to_cli())

    def _build_parameter_form(self) -> None:
        for parameter_group in self.parameter_group_list.parameter_groups:
            parameter_form_section = ParameterFormSection(parameter_group)
            self.ui.parameterFormVerticalLayout.addWidget(parameter_form_section)
