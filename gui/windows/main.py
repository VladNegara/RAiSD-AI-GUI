from PySide6.QtCore import QRect
from PySide6.QtWidgets import QMainWindow, QWidget, QRadioButton

from gui.ui.uiMainWindow import Ui_MainWindow
from gui.model.parameter_group_list import ParameterGroupList
from gui.widgets.parameter_form_section import ParameterFormSection


class MainWindow(QMainWindow):
    def __init__(self, parameter_group_list: ParameterGroupList):
        super().__init__()
        self.parameter_group_list = parameter_group_list
        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # connect standard signals (buttons)
        self.ui.buttonBox.accepted.connect(self._accepted)

        # TODO: link execute button to command builder & executor
            # TODO: make command builder (using parametergrouplist)
            # TODO: make command executor for terminal commands and virtual environment
        # TODO: link execution done to update_history()

        self.build_parameter_form()

    def _accepted(self) -> None:
        print(self.parameter_group_list.to_cli())

    def build_parameter_form(self) -> None:
        for parameter_group in self.parameter_group_list.parameter_groups:
            parameter_form_section = ParameterFormSection(parameter_group)
            self.ui.parameterFormVerticalLayout.addWidget(parameter_form_section)
