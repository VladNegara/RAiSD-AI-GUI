from PySide6.QtCore import QRect
from PySide6.QtWidgets import QMainWindow, QWidget, QRadioButton

from ui.uiMainWindow import Ui_MainWindow
from model.ParameterGroupSet import ParameterGroupSet
from widgets.ParameterFormSection import ParameterFormSection

class MainWindow(QMainWindow):
    def __init__(self, parameter_group_set:ParameterGroupSet):
        super().__init__()
        self.parameter_group_set = parameter_group_set
        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # connect standard signals (buttons)
        self.ui.buttonBox.accepted.connect(self.click)

        # TODO: link execute button to command builder & executor
            # TODO: make command builder (using parametergroupset)
            # TODO: make command executor for terminal commands and virtual environment
        # TODO: link execution done to update_history()

        self.build_parameter_form()

    def click(self):
        print("smth clicked")

    def build_parameter_form(self):
        for parameter_group in self.parameter_group_set.get_parameter_groups():
            parameter_form_section_widget = QWidget(self.ui.parameterFormWidget)
            width = self.ui.parameterFormWidget.size().width()
            height = self.ui.parameterFormWidget.size().height()
            parameter_form_section_widget.setGeometry(QRect(0,0,width,height))
            parameter_form_section = ParameterFormSection()
            parameter_form_section.construct_section(parameter_form_section_widget, parameter_group)
            self.ui.parameterFormVerticalLayout.addWidget(parameter_form_section_widget)

