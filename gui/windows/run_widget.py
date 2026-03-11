from PySide6.QtCore import (
    Qt,
    QProcess,
    Slot,
)
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QScrollArea,
    QPushButton,
    QLabel,
    QTextEdit,
)

from gui.model.parameter_group_list import ParameterGroupList
from gui.execution.command_executor import CommandExecutor
from gui.widgets.parameter_form import ParameterForm
from gui.windows.dialog import ConfirmDialog, ErrorDialog

class RunWidget(QWidget):
    """
    Widget that displays all steps of a mode.
    """
    def __init__(self, parameter_group_list: ParameterGroupList, command_executor: CommandExecutor):
        """
        Initialize `RunWidget` object.
        """
        super().__init__()
        self._parameter_group_list = parameter_group_list
        self.command_executor = command_executor
        self.command_executor.output.connect(self._command_executor_output)
        self.command_executor.err_output.connect(self._command_executor_err_output)
        self.command_executor.execution_started.connect(self._execution_started)
        self.command_executor.execution_finished.connect(self._execution_finished)
        self.command_executor.execution_stopped.connect(self._execution_stopped)
        self.command_executor.execution_failed.connect(self._execution_failed)
        self.command_executor.process_failed.connect(self._process_failed)

        self._setup_ui()

    def _setup_ui(self):
        """
        Setup the general run widget.

        Includes the step button bar and the stacked step widget.
        """
        self.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(self)

        # Step button bar
        step_button_bar = QWidget()
        step_button_bar.setStyleSheet("background-color: lightgray;")
        step_button_bar_layout = QHBoxLayout(step_button_bar)
        layout.addWidget(step_button_bar)
        self._setup_step_button_bar(step_button_bar_layout)

        # Step stacked widget
        stacked_step_widget = QWidget()
        stacked_step_widget.setStyleSheet("background-color: lightgray;")
        self.stacked_step_widget_layout = QStackedLayout(stacked_step_widget)
        layout.addWidget(stacked_step_widget, 1)
        self._setup_stacked_step_widget(self.stacked_step_widget_layout)
        

    def _setup_step_button_bar(self, layout:QHBoxLayout):
        """
        Setup the step button bar.
        """
        parameter_input_button = QPushButton("Parameter Input")
        parameter_input_button.clicked.connect(self._parameter_input_button_clicked)
        layout.addWidget(parameter_input_button)

        parameter_confirmation_button = QPushButton("Parameter Confirmation")
        parameter_confirmation_button.setEnabled(False) # TODO: Implement
        parameter_confirmation_button.clicked.connect(self._parameter_confirmation_button_clicked)
        layout.addWidget(parameter_confirmation_button)

        self.execution_view_button = QPushButton("Execution View")
        self.execution_view_button.setEnabled(False) # Only when execution started show?
        self.execution_view_button.clicked.connect(self.execution_view_button_clicked)
        layout.addWidget(self.execution_view_button)

        self.results_button = QPushButton("Results")
        self.results_button.setEnabled(False) # Only when run is finished show results?
        self.results_button.clicked.connect(self.results_button_clicked)
        layout.addWidget(self.results_button)

    def _setup_stacked_step_widget(self, layout:QStackedLayout):
        """
        Setup the stacked step widget.
        """
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
        """
        Setup the parameter input widget.
        """
        parameter_input_label = QLabel("Parameter Input")
        layout.addWidget(parameter_input_label)

        parameter_form = ParameterForm(self._parameter_group_list)

        parameter_form_scroll = QScrollArea()
        parameter_form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        parameter_form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        parameter_form_scroll.setWidgetResizable(True)
        parameter_form_scroll.setWidget(parameter_form)
        layout.addWidget(parameter_form_scroll)

        self.start_execution_button = QPushButton("Submit")
        self.start_execution_button.clicked.connect(self._parameter_input_submit_button_clicked)
        layout.addWidget(self.start_execution_button)

        check_param_button = QPushButton("Check parameters")
        check_param_button.clicked.connect(self._parameter_input_check_param_button_clicked)
        layout.addWidget(check_param_button)

    def _setup_parameter_confirmation_widget(self, layout:QVBoxLayout) -> None:
        """
        Setup the parameter confirmation widget.
        """
        parameter_confirmation_label = QLabel("Parameter Confirmation")
        layout.addWidget(parameter_confirmation_label)
        pass
    
    def _setup_execution_view_widget(self, layout:QVBoxLayout) -> None:
        """
        Setup the execution view widget.
        """
        execution_view_label = QLabel("Execution View")
        layout.addWidget(execution_view_label)

        step_widget = QWidget()
        self.step_layout = QHBoxLayout(step_widget)
        self.execution_indicators = []
        layout.addWidget(step_widget)

        output_widget = QWidget()
        output_widget_layout = QHBoxLayout(output_widget)
        layout.addWidget(output_widget)

        self.execution_output = QTextEdit(readOnly=True)
        output_widget_layout.addWidget(self.execution_output)

        self.error_output = QTextEdit(readOnly=True)
        output_widget_layout.addWidget(self.error_output)

        self.stop_execution_button = QPushButton("Stop Execution")
        self.stop_execution_button.setEnabled(False)
        self.stop_execution_button.setStyleSheet(f"background-color: purple;")
        self.stop_execution_button.clicked.connect(self._stop_execution)
        layout.addWidget(self.stop_execution_button)

    def _setup_results_widget(self, layout:QVBoxLayout) -> None:
        """
        Setup the results widget.
        """
        results_label = QLabel("Results")
        layout.addWidget(results_label)

    # ---------- step button bar methods ----------
    @Slot()
    def _parameter_input_button_clicked(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.parameter_input_widget)

    @Slot()
    def _parameter_confirmation_button_clicked(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.parameter_confirmation_widget)

    @Slot()
    def execution_view_button_clicked(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.execution_view_widget)

    @Slot()
    def results_button_clicked(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.results_widget)

    # ---------- Parameter input widget methods ----------
    @Slot()
    def _parameter_input_submit_button_clicked(self) -> None:
        """
        Run the commands from parameter_group_list when submit button is clicked.
        """
        print("submit")
        # TODO: self.command_executor.start_execution(self._parameter_group_list.to_cli())
        self.command_executor.start_execution([
            "echo No way!",
            "ping utwente.nl -c 2",
            "./RAiSD-AI -n TrainingData2DSNP -I datasets/train/msneutral1_100sims.out -L 100000 -its 50000 -op IMG-GEN -icl neutralTR -f -frm -O",
            "echo Shaboom!",
        ])

    @Slot()
    def _parameter_input_check_param_button_clicked(self) -> None:
        """
        Prints the current result of `parameter_group_list.to_cli()`.
        """
        print("check parameters:")
        print(self._parameter_group_list.to_cli())

    # ---------- Parameter confirmation widget methods ----------
    # TODO

    # ---------- Execution view widget methods ----------
    @Slot()
    def _stop_execution(self):
        """
        Stop the current execution after confirmation.
        """
        self.confirm_stop_execution_dialog = ConfirmDialog(self, "Stop Execution", "You are about to stop the current execution, are you sure?")
        if self.confirm_stop_execution_dialog.exec():
            self.command_executor.stop_execution()

    @Slot(str)
    def _command_executor_output(self, output: str) -> None:
        """
        Append the output from the command_executor to execution_output.
        """
        self.execution_output.append(output)
        
    @Slot(str)
    def _command_executor_err_output(self, output:str) -> None:
        """
        Append the error output from the command_executor to error_output.
        """
        self.error_output.append(output)

    def setup_execution_indicators(self, number_of_processes:int) -> None:
        """
        Set the execution indicators.

        reset current ones and add more or hide when needed.
        """
        number_of_indicators = len(self.execution_indicators)
        for idx in range(max([number_of_indicators, number_of_processes])):
            if idx + 1 <= number_of_processes and idx + 1 <= number_of_indicators:
                self.execution_indicators[idx].setVisible(True)
                self.execution_indicators[idx].setStyleSheet("background-color: lightgray;")
            elif idx + 1 <= number_of_processes and idx + 1 > number_of_indicators:
                self.add_indicator_widget(idx)
                continue
            elif idx + 1 > number_of_processes and idx + 1 <= number_of_indicators:
                self.execution_indicators[idx].setVisible(False)

    def add_indicator_widget(self, index:int) -> None:
        """
        Add an indicator widget to self.step_layout.
        """
        widget = QWidget()
        widget.setFixedSize(50, 50)
        widget.setStyleSheet("background-color: lightgray;")
        widget.setObjectName(f"process_{index}")
        self.command_executor.process_started.connect(lambda idx=index: self._process_started(idx))
        self.command_executor.process_finished.connect(lambda idx=index: self._process_finished(idx))
        self.step_layout.addWidget(widget)
        self.execution_indicators.append(widget)

    def set_execution_view_indicator(self, index:int, color:str) -> None:
        """
        Set the indicator to the given color.

        :param index: the index of the indicator.
        :type index: int

        :param color: the new color of the indicator.
        :type color: str
        """
        self.execution_indicators[index].setStyleSheet(f"background-color: {color};")

    def clear_outputs(self) -> None:
        """
        Clears the output fields.
        """
        self.execution_output.clear()
        self.error_output.clear()

    # ---------- Results widget methods ----------
    # TODO

    # ---------- Command executor slots ----------
    @Slot()
    def _execution_started(self, number_of_processes:int) -> None:
        """
        Handle CommandExecutor.execution_started.
        """
        print("Execution started")
        self.set_execution_buttons(running=True)
        self.clear_outputs()
        self.setup_execution_indicators(number_of_processes)
        self.execution_view_button.setEnabled(True)
        self.results_button.setEnabled(False)
        self.stacked_step_widget_layout.setCurrentWidget(self.execution_view_widget)

    @Slot()
    def _execution_finished(self) -> None:
        """
        Handle CommandExecutor.execution_finshed.
        """
        print("Execution finished")
        self.set_execution_buttons(running=False)
        self.results_button.setEnabled(True)
        self.confirm_stop_execution_dialog.close()
        self.stacked_step_widget_layout.setCurrentWidget(self.results_widget)

    @Slot()
    def _execution_stopped(self) -> None:
        """
        Handle CommandExecutor.execution_stopped.
        """
        print("Execution stopped")
        self.execution_done()
        self.set_execution_view_indicator(self.current_process, "purple")

    @Slot(int)
    def _execution_failed(self, exit_code: int) -> None:
        """
        Handle CommandExecutor.execution_failed.
        """
        print(f"Execution failed with exit code {exit_code}")
        self.execution_done()
        self.set_execution_view_indicator(self.current_process, "red")
        error_dialog = ErrorDialog(self, f"Execution Failed ({exit_code})", f"Execution failed with exit code {exit_code}")
        error_dialog.exec()
        self.execution_output.append(f"Execution failed with exit code {exit_code}")
    
    @Slot(QProcess.ProcessError)
    def _process_failed(self, process_error:QProcess.ProcessError) -> None:
        """
        Handle CommandExecutor.process_failed.
        """
        print(f"Execution failed with process error {process_error}")
        self.execution_done()
        self.set_execution_view_indicator(self.current_process, "red")
        error_dialog = ErrorDialog(self, f"Execution Failed ({process_error})", f"Execution failed with process error {process_error}")
        error_dialog.exec
        self.execution_output.append(f"Execution failed with process error {process_error}")

    @Slot(int)
    def _process_started(self, index: int) -> None:
        """
        Handle CommandExecutor.process_started.
        """
        self.set_execution_view_indicator(index, "yellow")
        self.current_process = index

    @Slot(int)
    def _process_finished(self, index: int) -> None:
        """
        Handle CommandExecutor.process_finished.
        """
        self.set_execution_view_indicator(index, "green")

    # ---------- Helper functions ----------
    def set_execution_buttons(self, running: bool) -> None:
        """
        Set the execution buttons.

        When running is true the start execution button will be off 
        and the stop execution on. Otherwise it is inverted.
        """
        self.stop_execution_button.setEnabled(running)
        self.start_execution_button.setEnabled(not running)

    def execution_done(self) -> None:
        """
        Update the execution buttons and Close an open confirm dialog.
        """
        self.set_execution_buttons(running=False)
        if hasattr(self, "confirm_stop_execution_dialog"):
            self.confirm_stop_execution_dialog.close()