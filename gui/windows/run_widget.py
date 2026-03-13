from PySide6.QtCore import (
    Qt,
    QProcess,
    Signal,
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
    QCheckBox,
)

from gui.model.parameter_group_list import ParameterGroupList
from gui.execution.command_executor import CommandExecutor
from gui.widgets.parameter_form import ParameterForm
from gui.windows.dialog import ConfirmDialog, ErrorDialog
from gui.widgets.results_widget import ResultsWidget

class RunWidget(QWidget):
    """
    A widget for all steps of running RAiSD-AI.
    """

    start_run = Signal()
    run_started = Signal(int)     # number of processes
    run_ended = Signal(bool)      # if run was successful

    def __init__(self, parameter_group_list: ParameterGroupList, command_executor: CommandExecutor):
        """
        Initialize a `RunWidget` object.
        """
        super().__init__()
        self._parameter_group_list = parameter_group_list
        self._command_executor = command_executor
        self._setup_ui()
        self.run_started.connect(self._handle_run_start)
        self.run_ended.connect(self._handle_run_end)

    def _setup_ui(self):
        """
        Set up the general run widget.

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
        operation_selection_button = QPushButton("Operation Selection")
        operation_selection_button.clicked.connect(self._switch_to_operation_selection_widget)
        layout.addWidget(operation_selection_button)

        parameter_input_button = QPushButton("Parameter Input")
        parameter_input_button.clicked.connect(self._switch_to_parameter_input_widget)
        layout.addWidget(parameter_input_button)

        parameter_confirmation_button = QPushButton("Parameter Confirmation")
        parameter_confirmation_button.clicked.connect(self._switch_to_parameter_confirmation_widget)
        layout.addWidget(parameter_confirmation_button)

        self.execution_view_button = QPushButton("Run")
        self.execution_view_button.clicked.connect(self._switch_to_run_view_widget)
        layout.addWidget(self.execution_view_button)

        self.results_button = QPushButton("Results")
        self.results_button.clicked.connect(self._switch_to_run_results_widget)
        layout.addWidget(self.results_button)

    def _setup_stacked_step_widget(self, layout: QStackedLayout):
        """
        Set up the stacked step widget.
        """
        # Operation selection widget
        self.operation_selection_widget = OperationSelectionWidget()
        layout.addWidget(self.operation_selection_widget)

        # Parameter input widget
        self.parameter_input_widget = ParameterInputWidget(parameter_group_list=self._parameter_group_list)
        self.parameter_input_widget.start_run.connect(self.start_run)
        self.run_started.connect(self.parameter_input_widget.run_start)
        self.run_ended.connect(self.parameter_input_widget.run_end)
        layout.addWidget(self.parameter_input_widget)

        # Parameter confirmation widget
        self.parameter_confirmation_widget = ParameterConfirmationWidget()
        layout.addWidget(self.parameter_confirmation_widget)
    
        # Run view widget
        self.run_view_widget = RunViewWidget(self._parameter_group_list, self._command_executor)
        self.run_view_widget.run_ended.connect(self.run_ended)
        self.run_view_widget.run_started.connect(self.run_started)
        self.start_run.connect(self.run_view_widget.start_run)
        self.run_started.connect(self.run_view_widget.run_start)
        self.run_ended.connect(self.run_view_widget.run_end)
        layout.addWidget(self.run_view_widget)

        # Results widget
        self.run_results_widget = RunResultsWidget(self._parameter_group_list)
        layout.addWidget(self.run_results_widget)

    # ---------- step button bar switch methods ----------
    @Slot()
    def _switch_to_operation_selection_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.operation_selection_widget)

    @Slot()
    def _switch_to_parameter_input_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.parameter_input_widget)

    @Slot()
    def _switch_to_parameter_confirmation_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.parameter_confirmation_widget)

    @Slot()
    def _switch_to_run_view_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.run_view_widget)

    @Slot()
    def _switch_to_run_results_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.run_results_widget)

    # ---------- Handle signals ----------
    @Slot()
    def _handle_run_start(self) -> None:
        self._switch_to_run_view_widget()

    @Slot()
    def _handle_run_end(self, run_successful: bool) -> None:
        if run_successful:
            self._switch_to_run_results_widget()
        else:
            self._switch_to_run_view_widget()


class RunSubWidget(QWidget):
    def __init__(self):
        super().__init__()
        widget = self._setup_widget()
        navigation = self._setup_navigation_buttons()
        self._setup_layout(widget, navigation)

    def _setup_layout(self, widget: QWidget, navigation: QWidget) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(widget, 1)
        layout.addWidget(navigation)
        pass

    def _setup_widget(self) -> QWidget:
        raise NotImplementedError

    def _setup_navigation_buttons(self) -> QWidget:
        raise NotImplementedError

# TODO: IMPLEMENT   
class NavigationButtonsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_layout()

    def _setup_layout(self) -> None:
        layout = QHBoxLayout(self)
        pass

class OperationSelectionWidget(RunSubWidget):
    
    def __init__(self):
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(widget)

        parameter_confirmation_label = QLabel("Operation Selection")
        layout.addWidget(parameter_confirmation_label)

        # TODO: dynamicly add operation selection buttons

        return widget

    def _setup_navigation_buttons(self) -> QWidget: # TODO: change to NavigationButtonsWidget when implemented
        return QWidget()
        # TODO: Implement
        # raise NotImplementedError

class ParameterInputWidget(RunSubWidget):

    start_run = Signal()
    
    def __init__(self, parameter_group_list: ParameterGroupList):
        self._parameter_group_list = parameter_group_list
        super().__init__()
        
    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(widget)
        parameter_input_label = QLabel("Parameter Input")
        layout.addWidget(parameter_input_label)

        ## Add checkbox for imgage gen selection
        mode_select_widget = QWidget()
        mode_select_layout = QHBoxLayout(mode_select_widget)
        layout.addWidget(mode_select_widget)
        
        img_gen_checkbox = QCheckBox()
        img_gen_checkbox.setChecked(True)
        mode_select_layout.addWidget(img_gen_checkbox)

        img_gen_label = QLabel("Perform IMG-GEN")
        mode_select_layout.addWidget(img_gen_label, 1)

        img_gen_checkbox.checkStateChanged.connect(self._img_gen_checkbox_clicked)

        parameter_form = ParameterForm(self._parameter_group_list)

        parameter_form_scroll = QScrollArea()
        parameter_form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        parameter_form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        parameter_form_scroll.setWidgetResizable(True)
        parameter_form_scroll.setWidget(parameter_form)
        layout.addWidget(parameter_form_scroll)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self._submit_button_clicked)
        layout.addWidget(self.submit_button)

        check_param_button = QPushButton("Check parameters")
        check_param_button.clicked.connect(self._check_param_button_clicked)
        layout.addWidget(check_param_button)
        return widget
    
    def _setup_navigation_buttons(self) -> QWidget:
        return QWidget()
        # TODO: Implement
        # raise NotImplementedError

    @Slot()
    def _img_gen_checkbox_clicked(self, state) -> None:
        if state == Qt.CheckState.Checked:
            self._parameter_group_list.set_operation("IMG-GEN", True)
            print("IMG-GEN checked")
        elif state == Qt.CheckState.Unchecked:
            self._parameter_group_list.set_operation("IMG-GEN", False)
            print("IMG-GEN unchecked")
        
    @Slot()
    def _submit_button_clicked(self) -> None:
        # TODO: Check input valid
        self.start_run.emit()
        pass

    @Slot()
    def _check_param_button_clicked(self) -> None:
        """
        Prints the current result of `parameter_group_list.to_cli()`.
        """
        print("check parameters:")
        print(self._parameter_group_list.to_cli())

    @Slot()
    def run_start(self) -> None:
        self.submit_button.setEnabled(False)
        self.submit_button.setText("Running")

    @Slot(bool)
    def run_end(self, run_successful: bool) -> None:
        self.submit_button.setEnabled(True)
        self.submit_button.setText("Submit")

class ParameterConfirmationWidget(RunSubWidget):
    def __init__(self):
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(widget)

        parameter_confirmation_label = QLabel("Parameter Confirmation")
        layout.addWidget(parameter_confirmation_label)

        return widget

    def _setup_navigation_buttons(self) -> QWidget:
        return QWidget()
        # TODO: Implement
        # raise NotImplementedError

class RunViewWidget(RunSubWidget):

    run_started = Signal(int)   # Number of processes
    run_ended = Signal(bool)    # Run successful

    def __init__(self, parameter_group_list: ParameterGroupList, command_executor: CommandExecutor):
        self._parameter_group_list = parameter_group_list
        self._command_executor = command_executor
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(widget)

        run_view_label = QLabel("Run View")
        layout.addWidget(run_view_label)

        step_widget = QWidget()
        self.step_layout = QHBoxLayout(step_widget)
        self.run_indicators = []
        layout.addWidget(step_widget)

        output_widget = QWidget()
        output_widget_layout = QHBoxLayout(output_widget)
        layout.addWidget(output_widget)

        self.execution_output = QTextEdit(readOnly=True)
        output_widget_layout.addWidget(self.execution_output)

        self.error_output = QTextEdit(readOnly=True)
        output_widget_layout.addWidget(self.error_output)

        self.stop_run_button = QPushButton("Stop Run")
        self.stop_run_button.setEnabled(False)
        self.stop_run_button.setStyleSheet(f"background-color: purple;")
        self.stop_run_button.clicked.connect(self._stop_run_button_clicked)
        layout.addWidget(self.stop_run_button)

        self._command_executor.output.connect(self._command_executor_output)
        self._command_executor.err_output.connect(self._command_executor_err_output)
        self._command_executor.execution_started.connect(self._execution_started)
        self._command_executor.execution_finished.connect(self._execution_finished)
        self._command_executor.execution_stopped.connect(self._execution_stopped)
        self._command_executor.execution_failed.connect(self._execution_failed)
        self._command_executor.process_failed.connect(self._process_failed)

        return widget

    def _setup_navigation_buttons(self) -> QWidget:
        return QWidget()
        # TODO: Implement
        # raise NotImplementedError

    def _stop_run_button_clicked(self) -> None:
        self._stop_execution()

    # methods
    @Slot()
    def start_run(self):
        self.clear_outputs()
        self._start_execution()

    @Slot(int)
    def run_start(self, number_of_processes: int) -> None:
        self.setup_execution_indicators(number_of_processes)
        self.stop_run_button.setEnabled(True)

    @Slot(bool)
    def run_end(self, run_successful: bool) -> None:
        """
        Update the execution buttons and close an open confirm dialog.
        """
        self.stop_run_button.setEnabled(False)
        if hasattr(self, "confirm_stop_execution_dialog"):
            if self.confirm_stop_execution_dialog is not None:
                self.confirm_stop_execution_dialog.close()

    def _start_execution(self):
        # self._command_executor.start_execution(self._parameter_group_list.to_cli())
        self._command_executor.start_execution([
            "./RAiSD-AI -n TrainingData2DSNP -I ./datasets/train/msneutral1_100sims.out -L 100000 -its 50000 -op IMG-GEN -icl neutralTR -f -frm -O",
            "./RAiSD-AI -n TrainingData2DSNP -I datasets/train/msselection1_100sims.out -L 100000 -its 50000 -op IMG-GEN -icl sweepTR -f -O",
            "./RAiSD-AI -n TestData2DSNP -I datasets/test/msneutral1_10sims.out -L 100000 -its 50000 -op IMG-GEN -icl neutralTE -f -frm -O",
            "./RAiSD-AI -n TestData2DSNP -I datasets/test/msselection1_10sims.out -L 100000 -its 50000 -op IMG-GEN -icl neutralTE -f -frm -O",
            "./RAiSD-AI -n FAST-NN-PT-2DSNP -I RAiSD_Images.TrainingData2DSNP -f -op MDL-GEN -O -frm -e 3",
            "./RAiSD-AI -n FAST-NN-PT-2DSNP-SCAN -mdl RAiSD_Model.FAST-NN-PT-2DSNP -f -op SWP-SCN -I datasets/train/msselection1_100sims.out -L 100000 -frm -T 50000 -d 1000 -G 20 -pci 1 1 -O",
        ])

    @Slot()
    def _stop_execution(self):
        """
        Stop the current execution after confirmation.
        """
        self.confirm_stop_execution_dialog = ConfirmDialog(self, "Stop Execution", "You are about to stop the current execution. Are you sure?")
        if self.confirm_stop_execution_dialog.exec():
            self._command_executor.stop_execution()

    @Slot(str)
    def _command_executor_output(self, output: str) -> None:
        """
        Append the output from the command_executor to execution_output.
        """
        self.execution_output.append(output)
        
    @Slot(str)
    def _command_executor_err_output(self, output: str) -> None:
        """
        Append the error output from the command_executor to error_output.
        """
        self.error_output.append(output)

    def setup_execution_indicators(self, number_of_processes: int) -> None:
        """
        Set the execution indicators.

        reset current ones and add more or hide when needed.
        """
        number_of_indicators = len(self.run_indicators)
        for idx in range(max([number_of_indicators, number_of_processes])):
            if idx < number_of_processes and idx < number_of_indicators:
                self.run_indicators[idx].setVisible(True)
                self.run_indicators[idx].setStyleSheet("background-color: lightgray;")
            elif idx < number_of_processes and idx >= number_of_indicators:
                self.add_indicator_widget(idx)
                continue
            elif idx >= number_of_processes and idx < number_of_indicators:
                self.run_indicators[idx].setVisible(False)

    def add_indicator_widget(self, index: int) -> None:
        """
        Add an indicator widget to self.step_layout.
        """
        widget = QWidget()
        widget.setFixedSize(50, 50)
        widget.setStyleSheet("background-color: lightgray;")
        widget.setObjectName(f"process_{index}")
        self._command_executor.process_started.connect(lambda idx=index: self._process_started(idx))
        self._command_executor.process_finished.connect(lambda idx=index: self._process_finished(idx))
        self.step_layout.addWidget(widget)
        self.run_indicators.append(widget)

    def set_execution_view_indicator(self, index: int, color: str) -> None:
        """
        Set the indicator to the given color.

        :param index: the index of the indicator
        :type index: int

        :param color: the new color of the indicator
        :type color: str
        """
        self.run_indicators[index].setStyleSheet(f"background-color: {color};")

    def clear_outputs(self) -> None:
        """
        Clear the output fields.
        """
        self.execution_output.clear()
        self.error_output.clear()
    
    # SLOTS
    @Slot()
    def _execution_started(self, number_of_processes: int) -> None:
        """
        Handle CommandExecutor.execution_started.
        """
        print("Execution started")
        self.run_started.emit(number_of_processes)

    @Slot()
    def _execution_finished(self) -> None:
        """
        Handle CommandExecutor.execution_finshed.
        """
        print("Execution finished")
        self.run_ended.emit(True)

    @Slot()
    def _execution_stopped(self) -> None:
        """
        Handle CommandExecutor.execution_stopped.
        """
        print("Execution stopped")
        self.run_ended.emit(False)
        self.set_execution_view_indicator(self.current_process, "purple")

    @Slot(int)
    def _execution_failed(self, exit_code: int) -> None:
        """
        Handle CommandExecutor.execution_failed.
        """
        print(f"Execution failed with exit code {exit_code}")
        self.run_ended.emit(False)
        self.set_execution_view_indicator(self.current_process, "red")
        error_dialog = ErrorDialog(self, f"Execution Failed ({exit_code})", f"Execution failed with exit code {exit_code}")
        error_dialog.exec()
        self.execution_output.append(f"Execution failed with exit code {exit_code}")
    
    @Slot(QProcess.ProcessError)
    def _process_failed(self, process_error: QProcess.ProcessError) -> None:
        """
        Handle CommandExecutor.process_failed.
        """
        print(f"Execution failed with process error {process_error}")

        self.set_execution_view_indicator(self.current_process, "red")
        self.execution_output.append(f"Execution failed with process error {process_error}")
        error_dialog = ErrorDialog(self, f"Execution Failed ({process_error})", f"Execution failed with process error {process_error}")
        error_dialog.exec()

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
    
class RunResultsWidget(RunSubWidget):
    def __init__(self, parameter_group_list: ParameterGroupList):
        self._parameter_group_list = parameter_group_list
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(widget)

        parameter_confirmation_label = QLabel("Run Results")
        layout.addWidget(parameter_confirmation_label)

        results_widget = ResultsWidget(self._parameter_group_list)
        layout.addWidget(results_widget, 1)
        return widget

    def _setup_navigation_buttons(self) -> QWidget:
        return QWidget()
        # TODO: Implement
        # raise NotImplementedError