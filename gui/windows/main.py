from PySide6.QtCore import (
    Slot,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QPushButton,
)

from gui.model.parameter_group_list import ParameterGroupList
from gui.widgets.parameter_form import ParameterForm


class MainWindow(QMainWindow):
    """
    The main window of the RAiSD-AI GUI application.
    """
    def __init__(self, parameter_group_list: ParameterGroupList):
        """
        Initialize the main window.

        :param parameter_group_list: the parameters to be filled in by
        the user
        :type parameter_group_list: ParameterGroupList
        """
        super().__init__()
        self._parameter_group_list = parameter_group_list

        # Create a central widget with a horizontal layout (i.e.
        # sidebars to the left and right of the parameter form).
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        # Create the parameter form and add it to the layout.
        parameter_form = ParameterForm(parameter_group_list)
        layout.addWidget(parameter_form)

        # Create the submit button and add it to the layout.
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self._submit_button_clicked)
        layout.addWidget(submit_button)

        # Set the central widget.
        self.setCentralWidget(central_widget)

        # TODO: link execute button to command executor
            # TODO: make command executor for terminal commands and
            # virtual environment
        # TODO: link execution done to update_history()

    @Slot()
    def _submit_button_clicked(self) -> None:
        print(self._parameter_group_list.to_cli())
