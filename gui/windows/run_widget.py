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
    QMessageBox,
    QStyle,
    QStyleOption,
)

from gui.model.parameter_group_list import ParameterGroupList
from gui.execution.command_executor import CommandExecutor
from gui.widgets.parameter_form import ParameterForm
from gui.windows.dialog import ConfirmDialog, ErrorDialog

from PySide6.QtGui import QPainter


class RunWidget(QWidget):
    """
    A widget for all steps of running RAiSD-AI.
    """

    start_run = Signal()
    run_started = Signal(int)  # number of processes
    run_ended = Signal(bool)  # if run was successful

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
        layout = QVBoxLayout(self)

        # Step button bar
        step_button_bar = QWidget()
        step_button_bar.setObjectName("step_button_bar")
        step_button_bar_layout = QHBoxLayout(step_button_bar)
        layout.addWidget(step_button_bar)
        self._setup_step_button_bar(step_button_bar_layout)

        # Step stacked widget
        stacked_step_widget = QWidget()
        self.stacked_step_widget_layout = QStackedLayout(stacked_step_widget)
        layout.addWidget(stacked_step_widget, 1)
        self._setup_stacked_step_widget(self.stacked_step_widget_layout)

    def _setup_step_button_bar(self, layout: QHBoxLayout):
        """
        Setup the step button bar.
        """
        self.operation_selection_button = QPushButton("Operation Selection")
        self.operation_selection_button.clicked.connect(self._switch_to_operation_selection_widget)
        layout.addWidget(self.operation_selection_button)

        self.parameter_input_button = QPushButton("Parameter Input")
        self.parameter_input_button.clicked.connect(self._switch_to_parameter_input_widget)
        layout.addWidget(self.parameter_input_button)

        self.parameter_confirmation_button = QPushButton("Parameter Confirmation")
        self.parameter_confirmation_button.clicked.connect(self._switch_to_parameter_confirmation_widget)
        layout.addWidget(self.parameter_confirmation_button)

        self.execution_view_button = QPushButton("Run")
        self.execution_view_button.clicked.connect(self._switch_to_run_view_widget)
        layout.addWidget(self.execution_view_button)

        self.results_button = QPushButton("Results")
        self.results_button.clicked.connect(self._switch_to_run_results_widget)
        layout.addWidget(self.results_button)

        self._step_buttons = [
            self.operation_selection_button,
            self.parameter_input_button,
            self.parameter_confirmation_button,
            self.execution_view_button,
            self.results_button,
        ]

    def _set_active_step(self, active_index: int) -> None:
        """
        Update the step_role dynamic property on each step button
        and force Qt to re-evaluate stylesheets.
        """
        for i, button in enumerate(self._step_buttons):
            if i < active_index:
                role = "past_step"
            elif i == active_index:
                role = "active"
            else:
                role = "default"
            button.setProperty("step_role", role)
            button.style().unpolish(button) #Required to apply styling dynamically
            button.style().polish(button)

    def _setup_stacked_step_widget(self, layout: QStackedLayout):
        """
        Set up the stacked step widget.
        """
        # Operation selection widget
        self.operation_selection_widget = OperationSelectionWidget(parameter_group_list=self._parameter_group_list)
        self.operation_selection_widget.next_button.clicked.connect(self._switch_to_parameter_input_widget)
        layout.addWidget(self.operation_selection_widget)

        # Parameter input widget
        self.parameter_input_widget = ParameterInputWidget(parameter_group_list=self._parameter_group_list)
        self.parameter_input_widget.back_button.clicked.connect(self._switch_to_operation_selection_widget)
        self.parameter_input_widget.next_button.clicked.connect(self._switch_to_parameter_confirmation_widget)
        layout.addWidget(self.parameter_input_widget)

        # Parameter confirmation widget
        self.parameter_confirmation_widget = ParameterConfirmationWidget(parameter_group_list=self._parameter_group_list)
        self.parameter_confirmation_widget.edit_button.clicked.connect(self._switch_to_parameter_input_widget)
        # run_button clicked is handled via the start_run signal
        self.parameter_confirmation_widget.start_run.connect(self.start_run)
        self.run_started.connect(self.parameter_confirmation_widget.run_start)
        self.run_ended.connect(self.parameter_confirmation_widget.run_end)
        layout.addWidget(self.parameter_confirmation_widget)

        # Run view widget
        self.run_view_widget = RunViewWidget(self._parameter_group_list, self._command_executor)
        self.run_view_widget.results_button.clicked.connect(self._switch_to_run_results_widget)
        self.run_view_widget.run_ended.connect(self.run_ended)
        self.run_view_widget.run_started.connect(self.run_started)
        self.start_run.connect(self.run_view_widget.start_run)
        self.run_started.connect(self.run_view_widget.run_start)
        self.run_ended.connect(self.run_view_widget.run_end)
        layout.addWidget(self.run_view_widget)

        # Results widget
        self.run_results_widget = RunResultsWidget()
        layout.addWidget(self.run_results_widget)

    # ---------- step button bar switch methods ----------
    @Slot()
    def _switch_to_operation_selection_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.operation_selection_widget)
        self._set_active_step(0)

    @Slot()
    def _switch_to_parameter_input_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.parameter_input_widget)
        self._set_active_step(1)
        self.parameter_input_widget._update_next_button_state()

    @Slot()
    def _switch_to_parameter_confirmation_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.parameter_confirmation_widget)
        self._set_active_step(2)

    @Slot()
    def _switch_to_run_view_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.run_view_widget)
        self._set_active_step(3)

    @Slot()
    def _switch_to_run_results_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.run_results_widget)
        self._set_active_step(4)

    # ---------- Handle signals ----------
    @Slot()
    def _handle_run_start(self) -> None:
        self._switch_to_run_view_widget()
        self.run_view_widget.results_button.setEnabled(False)

    @Slot()
    def _handle_run_end(self, run_successful: bool) -> None:
        if run_successful:
            self._switch_to_run_results_widget()
            self.run_view_widget.results_button.setEnabled(True)
        else:
            self._switch_to_run_view_widget()

class NavigationButtonsWidget(QWidget):
    def __init__(self, left_button: QPushButton | None = None, middle_button: QPushButton | None = None, right_button: QPushButton | None = None):
        super().__init__()
        self.left_button = left_button
        self.middle_button = middle_button
        self.right_button = right_button

        self.setObjectName("navigation_buttons_widget")

        layout = QHBoxLayout(self)
        for button, alignment in ((self.left_button, Qt.AlignmentFlag.AlignLeft), (self.middle_button, Qt.AlignmentFlag.AlignHCenter), (self.right_button, Qt.AlignmentFlag.AlignRight)):
            if button:
                print(alignment)
                layout.addWidget(button, alignment=alignment)
            else:
                layout.addWidget(QWidget(), 1)

    def paintEvent(self, event) -> None:
        """
        Override paintEvent so that QSS styling (background, border,
        etc.) is applied to this plain QWidget subclass.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)


class RunSubWidget(QWidget):

    def __init__(self):
        super().__init__()
        widget = self._setup_widget()
        navigation = self._setup_navigation_buttons()
        self._setup_layout(widget, navigation)

    def _setup_layout(self, widget: QWidget, navigation: QWidget) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widget, 1)
        layout.addWidget(navigation)
        pass

    def _setup_widget(self) -> QWidget:
        raise NotImplementedError

    def _setup_navigation_buttons(self) -> QWidget:
        raise NotImplementedError


class OperationSelectionWidget(RunSubWidget):
    """
    
    """    
    def __init__(self, parameter_group_list: ParameterGroupList):
        self._parameter_group_list = parameter_group_list
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(widget)

        operation_selection_label = QLabel("Operation Selection")
        layout.addWidget(operation_selection_label)

        operation_selection_widget = self._setup_operation_selection_widget()
        layout.addWidget(operation_selection_widget, 1)

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsWidget:
        self.next_button = QPushButton("Next")
        return NavigationButtonsWidget(right_button=self.next_button)

    def _setup_operation_selection_widget(self) -> QWidget:
        """
        Creates the widget with operation selectors and their descriptions.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        for operation, enabled in self._parameter_group_list.operations.items():
            operation_selector = self._operation_selector(operation, enabled, f"perform: {operation}") # TODO: Set description.
            layout.addWidget(operation_selector)
            
        return widget 

    def _operation_selector(self, operation: str, enabled: bool, description: str) -> QWidget:
        """
        An operation selector widget containing a checkbox linked to the parameter_group_list and a description.
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)

        operation_button = QCheckBox(operation)
        operation_button.setCheckState(
            Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked
        )
        operation_button.checkStateChanged.connect(
            lambda s: self._operation_selector_clicked(operation, s)
            )
        layout.addWidget(operation_button)
        
        description_label = QLabel(description)
        layout.addWidget(description_label, 1)

        return widget
    
    def _operation_selector_clicked(self, operation: str, state: Qt.CheckState) -> None:
        """
        Set the operation using the given checkbox state.
        """
        if state == Qt.CheckState.Checked:
            self._parameter_group_list.set_operation(operation, True)
        elif state == Qt.CheckState.Unchecked:
            self._parameter_group_list.set_operation(operation, False)



class ParameterInputWidget(RunSubWidget):    
    def __init__(self, parameter_group_list: ParameterGroupList):
        self._parameter_group_list = parameter_group_list
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("parameter_input_widget")
        layout = QVBoxLayout(widget)
        parameter_input_label = QLabel("Parameter Input")
        parameter_input_label.setObjectName("parameter_input_label")
        layout.addWidget(parameter_input_label)

        parameter_form = ParameterForm(self._parameter_group_list)
        parameter_form.setObjectName("parameter_form")

        parameter_form_scroll = QScrollArea()
        parameter_form_scroll.setObjectName("parameter_form_scroll")
        parameter_form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        parameter_form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        parameter_form_scroll.setWidgetResizable(True)
        parameter_form_scroll.setWidget(parameter_form)
        layout.addWidget(parameter_form_scroll)

        self._validity_label = QLabel("")
        self._validity_label.setStyleSheet("QLabel { color: red; }")
        layout.addWidget(self._validity_label)

        check_param_button = QPushButton("Check parameters")
        check_param_button.clicked.connect(self._check_param_button_clicked)
        layout.addWidget(check_param_button)
        return widget
    
    def _setup_navigation_buttons(self) -> NavigationButtonsWidget:
        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("next_button")

        self._update_next_button_state()
        for group in self._parameter_group_list.parameter_groups:
            for parameter in group.parameters:
                parameter.value_changed.connect(self._update_next_button_state)
                
        return NavigationButtonsWidget(left_button=self.back_button, right_button=self.next_button)

    def _update_next_button_state(self) -> None:
        """
        Helper function to display the error that makes the next_button inactive
        """
        valid = self._parameter_group_list.valid
        self.next_button.setEnabled(valid)
        if valid:
            self.next_button.setProperty("enabled", "true")
            self._validity_label.setText("")
        else:
            self.next_button.setProperty("enabled", "false")
            self._validity_label.setText("Cannot continue: one or more parameters are invalid.")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)

    @Slot()
    def _check_param_button_clicked(self) -> None:
        """
        Prints the current result of `parameter_group_list.to_cli()`.
        """
        print("check parameters:")
        print(self._parameter_group_list.to_cli())


class ParameterConfirmationWidget(RunSubWidget):
    start_run = Signal()

    def __init__(self, parameter_group_list: ParameterGroupList):
        self._parameter_group_list = parameter_group_list
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(widget)

        parameter_confirmation_label = QLabel("Parameter Confirmation")
        layout.addWidget(parameter_confirmation_label)

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsWidget:
        self.edit_button = QPushButton("Edit")
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._run_button_clicked)
        return NavigationButtonsWidget(left_button=self.edit_button, right_button=self.run_button)

    @Slot()
    def _run_button_clicked(self) -> None:
        if self._parameter_group_list.valid:
            self.start_run.emit()
        else:
            dialog = ErrorDialog(self, "Invalid input", "Input parameters are invalid")
            dialog.exec()
        pass

    @Slot()
    def run_start(self) -> None:
        self.run_button.setEnabled(False)
        self.run_button.setText("Running")

    @Slot(bool)
    def run_end(self, run_successful: bool) -> None:
        self.run_button.setEnabled(True)
        self.run_button.setText("Submit")


class RunViewWidget(RunSubWidget):
    run_started = Signal(int)  # Number of processes
    run_ended = Signal(bool)  # Run successful

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

        self._command_executor.output.connect(self._command_executor_output)
        self._command_executor.err_output.connect(self._command_executor_err_output)
        self._command_executor.execution_started.connect(self._execution_started)
        self._command_executor.execution_finished.connect(self._execution_finished)
        self._command_executor.execution_stopped.connect(self._execution_stopped)
        self._command_executor.execution_failed.connect(self._execution_failed)
        # process_started and process_finished are connected to the indicator widgets
        self._command_executor.process_failed.connect(self._process_failed)
        self._command_executor.process_stopped.connect(self._process_stopped)

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsWidget:
        self.stop_run_button = QPushButton("Stop Run")
        self.stop_run_button.setEnabled(False)
        self.stop_run_button.setStyleSheet(f"background-color: purple;")
        self.stop_run_button.clicked.connect(self._stop_run_button_clicked)
        
        self.results_button = QPushButton("Results")
        self.results_button.setEnabled(False)

        return NavigationButtonsWidget(middle_button=self.stop_run_button, right_button=self.results_button)

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
        button = self.confirm_stop_execution_dialog.exec()
        if button == QMessageBox.StandardButton.Yes:
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
    @Slot(int)
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

    @Slot(int, QProcess.ProcessError)
    def _execution_failed(self, exit_code: int, process_error: QProcess.ProcessError) -> None:
        """
        Handle CommandExecutor.execution_failed.
        """
        print(f"Execution failed with exit code '{exit_code}'")

        self.run_ended.emit(False)        

        if process_error is None: # otherwise _process_failed will show an error dialog:
            self.execution_output.append(f"Execution failed with exit code '{exit_code}'")
            self.execution_error_dialog = ErrorDialog(self, f"Execution Failed ({exit_code})", f"Execution failed with exit code '{exit_code}'")
            self.execution_error_dialog.exec()
    
    @Slot()
    def _execution_stopped(self) -> None:
        """
        Handle CommandExecutor.execution_stopped.
        """
        print("Execution stopped.")
        self.run_ended.emit(False)

    @Slot(int)
    def _process_started(self, process_index: int) -> None:
        """
        Handle CommandExecutor.process_started.
        """
        self.set_execution_view_indicator(process_index, "yellow")

    @Slot(int)
    def _process_finished(self, index: int) -> None:
        """
        Handle CommandExecutor.process_finished.
        """
        self.set_execution_view_indicator(index, "green")

    @Slot(int, QProcess.ProcessError)
    def _process_failed(self, process_index: int, process_error: QProcess.ProcessError) -> None:
        """
        Handle CommandExecutor.process_failed.
        """
        self.set_execution_view_indicator(process_index, "red")

        if process_error is not None:
            print(f"Process '{process_index}' failed with process error '{process_error}'")
            self.execution_output.append(f"Process '{process_index}' failed with process error '{process_error}'")
            process_error_dialog = ErrorDialog(self, f"Process Failed ({process_error})", f"Process '{process_index}' failed with process error '{process_error}'")
            process_error_dialog.exec()

    @Slot(int)
    def _process_stopped(self, process_index: int) -> None:
        """
        Handle CommandExecutor.process_stopped.
        """
        self.set_execution_view_indicator(process_index, "purple")
    
class RunResultsWidget(RunSubWidget):
    def __init__(self):
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout(widget)

        run_results_label = QLabel("Run Results")
        layout.addWidget(run_results_label)

        return widget

    def _setup_navigation_buttons(self) -> QWidget:
        return QWidget()
        # TODO: Implement
        # raise NotImplementedError
