from PySide6.QtCore import (
    Qt,
    Slot,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QScrollArea,
    QPushButton,
    QLabel,
)

from gui.model.parameter_group_list import ParameterGroupList
from gui.execution.command_executor import CommandExecutor
from gui.widgets.parameter_form import ParameterForm

class RunWidget(QWidget):
    def __init__(self, parameter_group_list: ParameterGroupList, command_executor: CommandExecutor):
        super().__init__()
        self._parameter_group_list = parameter_group_list
        self.command_executor = command_executor
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(self)

        # Step button bar
        step_button_bar = QWidget()
        step_button_bar.setStyleSheet("background-color: lightgray;")
        step_button_bar_layout = QHBoxLayout(step_button_bar)
        layout.addWidget(step_button_bar)
        self._setup_step_button_bar(step_button_bar_layout)

        # Step stacked widget
        step_stacked_widget = QWidget()
        step_stacked_widget.setStyleSheet("background-color: lightgray;")
        self.step_stacked_widget_layout = QStackedLayout(step_stacked_widget)
        layout.addWidget(step_stacked_widget, 1)
        self._setup_step_stacked_widget(self.step_stacked_widget_layout)
        

    def _setup_step_button_bar(self, layout:QHBoxLayout):
        parameter_input_button = QPushButton("Parameter Input")
        parameter_input_button.clicked.connect(self._parameter_input_button_clicked)
        layout.addWidget(parameter_input_button)

        parameter_confirmation_button = QPushButton("Parameter Confirmation")
        parameter_confirmation_button.clicked.connect(self._parameter_confirmation_button_clicked)
        layout.addWidget(parameter_confirmation_button)

        execution_view_button = QPushButton("Execution View")
        execution_view_button.clicked.connect(self.execution_view_button_clicked)
        layout.addWidget(execution_view_button)

        results_button = QPushButton("Results")
        results_button.clicked.connect(self.results_button_clicked)
        layout.addWidget(results_button)

    def _setup_step_stacked_widget(self, layout:QStackedLayout):
        # Parameter input widget
        self.parameter_input_widget = QWidget()
        self.parameter_input_widget.setStyleSheet("background-color: lightblue;")
        parameter_input_layout = QVBoxLayout(self.parameter_input_widget)
        layout.addWidget(self.parameter_input_widget)
        self._setup_parameter_input_widget(parameter_input_layout)

        # Parameter confirmation widget
        self.parameter_confirmation_widget = QWidget()
        self.parameter_confirmation_widget.setStyleSheet("background-color: lightblue;")
        parameter_confirmation_layout = QVBoxLayout(self.parameter_confirmation_widget)
        layout.addWidget(self.parameter_confirmation_widget)
        self._setup_parameter_confirmation_widget(parameter_confirmation_layout)
    
        # Execution view widget
        self.execution_view_widget = QWidget()
        self.execution_view_widget.setStyleSheet("background-color: lightblue;")
        execution_view_layout = QVBoxLayout(self.execution_view_widget)
        layout.addWidget(self.execution_view_widget)
        self._setup_execution_view_widget(execution_view_layout)

        # Results widget
        self.results_widget = QWidget()
        self.results_widget.setStyleSheet("background-color: lightblue;")
        results_layout = QVBoxLayout(self.results_widget)
        layout.addWidget(self.results_widget)
        self._setup_results_widget(results_layout)

    def _setup_parameter_input_widget(self, layout:QVBoxLayout) -> None:
        parameter_input_label = QLabel("Parameter Input")
        layout.addWidget(parameter_input_label)

        parameter_form = ParameterForm(self._parameter_group_list)

        parameter_form_scroll = QScrollArea()
        parameter_form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        parameter_form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        parameter_form_scroll.setWidgetResizable(True)
        parameter_form_scroll.setWidget(parameter_form)
        layout.addWidget(parameter_form_scroll)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self._parameter_input_submit_button_clicked)
        layout.addWidget(submit_button)

        check_param_button = QPushButton("Check parameters")
        check_param_button.clicked.connect(self._parameter_input_check_param_button_clicked)
        layout.addWidget(check_param_button)

    def _setup_parameter_confirmation_widget(self, layout:QVBoxLayout) -> None:
        parameter_confirmation_label = QLabel("Parameter Confirmation")
        layout.addWidget(parameter_confirmation_label)
        pass
    
    def _setup_execution_view_widget(self, layout:QVBoxLayout) -> None:
        execution_view_label = QLabel("Execution View")
        layout.addWidget(execution_view_label)
        pass

    def _setup_results_widget(self, layout:QVBoxLayout) -> None:
        results_label = QLabel("Results")
        layout.addWidget(results_label)
        pass

    @Slot()
    def _parameter_input_button_clicked(self) -> None:
        self.step_stacked_widget_layout.setCurrentWidget(self.parameter_input_widget)

    @Slot()
    def _parameter_confirmation_button_clicked(self) -> None:
        self.step_stacked_widget_layout.setCurrentWidget(self.parameter_confirmation_widget)

    @Slot()
    def execution_view_button_clicked(self) -> None:
        self.step_stacked_widget_layout.setCurrentWidget(self.execution_view_widget)

    @Slot()
    def results_button_clicked(self) -> None:
        self.step_stacked_widget_layout.setCurrentWidget(self.results_widget)

    @Slot()
    def _parameter_input_submit_button_clicked(self) -> None:
        print("submit")
        self.command_executor.start_execution(self._parameter_group_list.to_cli())

    @Slot()
    def _parameter_input_check_param_button_clicked(self) -> None:
        print("check parameters")
        print(self._parameter_group_list.to_cli())
