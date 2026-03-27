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
    QRadioButton,
    QLabel,
    QTextEdit,
    QMessageBox,
    QStyle,
    QStyleOption,
    QListWidget,
    QAbstractItemView,
    QSplitter
)

from PySide6.QtGui import (
    QGuiApplication,
    QPainter
)

import json

from gui.model.parameter import MultiParameter, OptionalParameter, Parameter
from gui.model.settings import app_settings
from gui.model.run_record import RunRecord
from gui.model.history_record import HistoryRecord
from gui.execution.command_executor import CommandExecutor
from gui.widgets.parameter_widget import ParameterWidget
from gui.widgets.operation_tree_widget import OperationTreeWidget
from gui.widgets.resizable_stacked_widget import ResizableStackedWidget
from gui.widgets.parameter_form import ParameterForm
from gui.windows.dialog import ConfirmDialog, ErrorDialog
from gui.widgets.results_widget import ResultsWidget
from gui.widgets.process_indicator_widget import ProcessIndicator, IndicatorState

class RunWidget(QWidget):
    """
    A widget for all steps of running RAiSD-AI.
    """

    start_run = Signal()
    run_started = Signal(int)  # number of processes
    run_ended = Signal(bool)  # if run was successful
    run_saved = Signal(HistoryRecord)

    def __init__(self, run_record: RunRecord, command_executor: CommandExecutor):
        """
        Initialize a `RunWidget` object.
        """
        super().__init__()
        self._run_record = run_record
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
        self.operation_selection_button.setProperty("step_role", "active")
        layout.addWidget(self.operation_selection_button)

        self.parameter_input_button = QPushButton("Parameter Input")
        self.parameter_input_button.clicked.connect(self._switch_to_parameter_input_widget)
        self.parameter_input_button.setEnabled(False)
        layout.addWidget(self.parameter_input_button)

        self.parameter_confirmation_button = QPushButton("Parameter Confirmation")
        self.parameter_confirmation_button.clicked.connect(self._switch_to_parameter_confirmation_widget)
        self.parameter_confirmation_button.setEnabled(False)
        layout.addWidget(self.parameter_confirmation_button)

        self.execution_view_button = QPushButton("Run")
        self.execution_view_button.clicked.connect(self._switch_to_run_view_widget)
        self.execution_view_button.setEnabled(False)
        layout.addWidget(self.execution_view_button)

        self.results_button = QPushButton("Results")
        self.results_button.clicked.connect(self._switch_to_run_results_widget)
        self.results_button.setEnabled(False)
        self.results_button.setProperty("highlight", "false")
        self.results_button.style().unpolish(self.results_button)
        self.results_button.style().polish(self.results_button)
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
                button.setEnabled(True)
            elif i == active_index:
                role = "active"
            else:
                role = "default"
                button.setEnabled(False)
            button.setProperty("step_role", role)
            button.style().unpolish(button) #Required to apply styling dynamically
            button.style().polish(button)

    def _setup_stacked_step_widget(self, layout: QStackedLayout):
        """
        Set up the stacked step widget.
        """
        # Operation selection widget
        self.operation_selection_widget = OperationSelectionWidget(run_record=self._run_record)
        self.operation_selection_widget.next_button.clicked.connect(self._switch_to_parameter_input_widget)
        layout.addWidget(self.operation_selection_widget)

        # Parameter input widget
        self.parameter_input_widget = ParameterInputWidget(run_record=self._run_record)
        self.parameter_input_widget.back_button.clicked.connect(self._switch_to_operation_selection_widget)
        self.parameter_input_widget.navigate_next.connect(self._switch_to_parameter_confirmation_widget)
        layout.addWidget(self.parameter_input_widget)

        # Parameter confirmation widget
        self.parameter_confirmation_widget = ParameterConfirmationWidget(run_record=self._run_record)
        self.parameter_confirmation_widget.edit_button.clicked.connect(self._switch_to_parameter_input_widget)
        # run_button clicked is handled via the start_run signal
        self.parameter_confirmation_widget.start_run.connect(self.start_run)
        self.run_started.connect(self.parameter_confirmation_widget.run_start)
        self.run_ended.connect(self.parameter_confirmation_widget.run_end)
        layout.addWidget(self.parameter_confirmation_widget)

        # Run view widget
        self.run_view_widget = RunViewWidget(run_record=self._run_record, command_executor=self._command_executor)
        self.run_view_widget.results_button.clicked.connect(self._switch_to_run_results_widget)
        self.run_view_widget.run_ended.connect(self.run_ended)
        self.run_view_widget.run_started.connect(self.run_started)
        self.start_run.connect(self.run_view_widget.start_run)
        self.run_started.connect(self.run_view_widget.run_start)
        self.run_ended.connect(self.run_view_widget.run_end)
        layout.addWidget(self.run_view_widget)

        # Results widget
        self.run_results_widget = RunResultsWidget(run_record=self._run_record)
        self.run_ended.connect(self.run_results_widget.run_end)
        layout.addWidget(self.run_results_widget)

    # ---------- step button bar switch methods ----------
    @Slot()
    def _switch_to_operation_selection_widget(self) -> None:
        self.parameter_input_widget.reset_touched()
        self.stacked_step_widget_layout.setCurrentWidget(self.operation_selection_widget)
        self._set_active_step(0)

    @Slot()
    def _switch_to_parameter_input_widget(self) -> None:
        self.stacked_step_widget_layout.setCurrentWidget(self.parameter_input_widget)
        self._set_active_step(1)
        self.parameter_input_widget.update_next_button_state()

    @Slot()
    def _switch_to_parameter_confirmation_widget(self) -> None:
        self.parameter_confirmation_widget.update_commands()
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
        self.run_view_widget.results_button.setProperty("highlight", "false")
        self.run_view_widget.results_button.style().unpolish(self.run_view_widget.results_button)
        self.run_view_widget.results_button.style().polish(self.run_view_widget.results_button)

    @Slot()
    def _handle_run_end(self, run_successful: bool) -> None:
        if run_successful:
            history_record = self._run_record.to_history_record() 
            history_record.save_to_history()     
            self.run_saved.emit(history_record)
            self._switch_to_run_results_widget()
            self.run_view_widget.results_button.setEnabled(True)
            self.run_view_widget.results_button.setProperty("highlight", "true")
            self.run_view_widget.results_button.style().unpolish(self.run_view_widget.results_button)
            self.run_view_widget.results_button.style().polish(self.run_view_widget.results_button)
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
    A widget that allows the user to select operations to be run.
    """

    def __init__(self, run_record: RunRecord):
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("operation_selection_widget")
        layout = QVBoxLayout(widget)

        operation_selection_label = QLabel("Operation Selection")
        operation_selection_label.setObjectName("operation_selection_label")
        layout.addWidget(operation_selection_label)

        run_id_parameter_widget = ParameterWidget.from_parameter(
            self._run_record.run_id_parameter,
            editable=True,
        )
        run_id_widget = run_id_parameter_widget.build_form_row()
        layout.addWidget(run_id_widget)

        self.operation_selector = self.__class__.OperationSelector(
            self._run_record
        )
        layout.addWidget(self.operation_selector, stretch=1000)

        layout.addStretch(1)

        # Show operation selector only if run ID is valid
        self.operation_selector.setVisible(
            self._run_record.run_id_valid,
        )
        self._run_record.run_id_valid_changed.connect(
            self._run_id_valid_changed,
        )

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsWidget:
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("next_button")
        self._update_next_button_state()
        self._run_record.run_id_valid_changed.connect(
            self._update_next_button_state,
        )
        self._run_record.operations_valid_changed.connect(
            self._update_next_button_state,
        )
        return NavigationButtonsWidget(right_button=self.next_button)

    class OperationSelector(QWidget):
        def __init__(self, run_record: RunRecord):
            super().__init__()

            self._run_record = run_record

            layout = QHBoxLayout(self)

            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)

            tree_scroll = QScrollArea()
            tree_scroll.setObjectName("tree_scroll")
            tree_scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            tree_scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            tree_scroll.setWidgetResizable(True)

            self.tree_stacked_widget = ResizableStackedWidget()
            self.tree_stacked_widget.setObjectName("tree_stacked_widget")
            for i, tree in enumerate(
                    self._run_record.operation_trees
            ):
                button = QRadioButton(tree.root.name)
                button.setChecked(
                    i
                    == self._run_record.selected_operation_tree_index
                )
                button_layout.addWidget(button)

                widget = OperationTreeWidget(tree)
                self.tree_stacked_widget.addWidget(widget)

                button.clicked.connect(lambda _, i=i: self._button_clicked(i))
            tree_scroll.setWidget(self.tree_stacked_widget)

            button_layout.addStretch()

            layout.addWidget(button_widget)
            layout.addWidget(tree_scroll)

        def _button_clicked(self, i: int) -> None:
            self._run_record.selected_operation_tree_index = i
            self.tree_stacked_widget.current_index = i

    @Slot()
    def _run_id_valid_changed(self, new_valid) -> None:
        self.operation_selector.setVisible(new_valid)

    @Slot()
    def _update_next_button_state(self) -> None:
        valid = (
            self._run_record.run_id_valid
            and self._run_record.operations_valid
        )
        self.next_button.setEnabled(valid)
        if valid:
            self.next_button.setProperty("highlight", "true")
        else:
            self.next_button.setProperty("highlight", "false")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)


class ParameterInputWidget(RunSubWidget):
    navigate_next = Signal()
    def __init__(self, run_record: RunRecord):
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("parameter_input_widget")
        layout = QVBoxLayout(widget)
        parameter_input_label = QLabel("Parameter Input")
        parameter_input_label.setObjectName("parameter_input_label")
        layout.addWidget(parameter_input_label)

        self._parameter_form = ParameterForm(self._run_record, editable=True)
        self._parameter_form.setObjectName("parameter_form")

        parameter_form_scroll = QScrollArea()
        parameter_form_scroll.setObjectName("parameter_form_scroll")
        parameter_form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        parameter_form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        parameter_form_scroll.setWidgetResizable(True)
        parameter_form_scroll.setWidget(self._parameter_form)
        layout.addWidget(parameter_form_scroll)

        self._validity_label = QLabel("")
        self._validity_label.setObjectName("validity_label")
        layout.addWidget(self._validity_label)

        check_param_button = QPushButton("Check parameters")
        check_param_button.clicked.connect(self._check_param_button_clicked)
        layout.addWidget(check_param_button)
        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsWidget:
        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("next_button")
        self.next_button.clicked.connect(self._next_button_clicked)

        self.update_next_button_state()
        # TODO: make this just connect to a signal on the parameter group list
        self._run_record.run_id_parameter.value_changed.connect(
            self.update_next_button_state
        )
        for group in self._run_record.parameter_groups:
            for parameter in group.parameters:
                self._connect_parameter_to_update_next_button_state(parameter)
                
        return NavigationButtonsWidget(left_button=self.back_button, right_button=self.next_button)

    def _connect_parameter_to_update_next_button_state(self, parameter: Parameter) -> None:
        """
        Helper function to connect `value_changed` to `update_next_button_state` on all parameter types.
        """
        if isinstance(parameter, MultiParameter):
            for child in parameter.parameters:
                self._connect_parameter_to_update_next_button_state(child)
        elif isinstance(parameter, OptionalParameter):
            parameter.value_changed.connect(self.update_next_button_state)
            self._connect_parameter_to_update_next_button_state(parameter.parameter)
        else:
            parameter.value_changed.connect(self.update_next_button_state)

    def update_next_button_state(self) -> None:
        """
        Helper function to display the error that makes the next_button inactive
        """
        valid = self._run_record.valid
        if valid:
            self._validity_label.setText("")
        else:
            invalid_params = []
            for group in self._run_record.parameter_groups:
                for parameter in group.parameters:
                    if isinstance(parameter, MultiParameter):
                        for child_parameter in parameter.parameters:
                            if not child_parameter.valid and child_parameter.enabled:
                                invalid_params.append(child_parameter.name)
                    else:
                        if not parameter.valid and parameter.enabled:
                            invalid_params.append(parameter.name)
            self._validity_label.setText(
                "Cannot continue. Invalid parameters:" + "".join(f"  - {name}" for name in invalid_params)
            )

    def _next_button_clicked(self) -> None:
        """
        Helper function that decides next buttons function based on parameter validity
        """
        valid = self._run_record.valid
        if valid:
            self.navigate_next.emit()
        else:
            self._parameter_form.touch_all()

    def reset_touched(self) -> None:
        """
        Helper function to make touched false for all parameters
        """
        self._parameter_form.untouch_all()

    @Slot()
    def _check_param_button_clicked(self) -> None:
        """
        Prints the current result of `run_record.to_cli()`.
        """
        print("check parameters:")
        print(self._run_record.to_cli())


class ParameterConfirmationWidget(RunSubWidget):
    start_run = Signal()

    def __init__(self, run_record: RunRecord):
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        """
        Setup a ParameterConfirmationWidget, including a header,
        a section for the commands to be run, and the ParameterForm,
        in locked form.
        """
        widget = QWidget()
        widget.setObjectName("parameter_confirmation_widget")
        layout = QVBoxLayout(widget)

        # Header
        parameter_confirmation_label = QLabel("Parameter Confirmation")
        parameter_confirmation_label.setObjectName("parameter_confirmation_label")
        layout.addWidget(parameter_confirmation_label)

        # Commands
        commands_widget = QWidget()
        commands_layout = QVBoxLayout(commands_widget)

        commands_header = QWidget()
        commands_header_layout = QHBoxLayout(commands_header)

        commands_label = QLabel("Commands generated from the input:")
        commands_header_layout.addWidget(commands_label, 1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_all)
        commands_header_layout.addWidget(copy_button)
        commands_layout.addWidget(commands_header)

        self.commands_view = QListWidget()
        self.commands_view.setObjectName("commands_view")
        self.commands_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.commands_view.clicked.connect(self._copy_command)
        commands_layout.addWidget(self.commands_view)
        layout.addWidget(commands_widget)

        # Parameters
        parameter_form = ParameterForm(self._run_record, editable=False)
        parameter_form.setObjectName("parameter_form")

        parameter_form_scroll = QScrollArea()
        parameter_form_scroll.setObjectName("parameter_form_scroll")
        parameter_form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        parameter_form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        parameter_form_scroll.setWidgetResizable(True)
        parameter_form_scroll.setWidget(parameter_form)
        layout.addWidget(parameter_form_scroll, 1)

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsWidget:
        self.edit_button = QPushButton("Edit")
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._run_button_clicked)
        return NavigationButtonsWidget(left_button=self.edit_button, right_button=self.run_button)

    def update_commands(self) -> None:
        """
        Updates the ParameterConfirmationWidget with the commands from
        the RunResult.
        """
        self.commands_view.clear()
        if self._run_record.to_cli():
            self.commands_view.addItems([app_settings.executable_file_path.absoluteFilePath() + " " + command for command in self._run_record.to_cli()])
            self.commands_view.setMaximumHeight(self.commands_view.sizeHintForRow(0)*(self.commands_view.count()+1))

    @Slot(int)
    def _copy_command(self, index) -> None:
        """
        Copies a singular command from the QTreeWidget to the clipboard.
        """
        command = self.commands_view.itemFromIndex(index).text()
        cb = QGuiApplication.clipboard()
        cb.setText(command)

    @Slot()
    def _copy_all(self) -> None:
        """
        Copies all commands from the run result to the clipboard.
        """
        if self._run_record.to_cli():
            string = '; '.join(self._run_record.to_cli())
            cb = QGuiApplication.clipboard()
            cb.setText(string)

    @Slot()
    def _run_button_clicked(self) -> None:
        if self._run_record.valid:
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

    def __init__(self, run_record: RunRecord, command_executor: CommandExecutor):
        self._run_record = run_record
        self._command_executor = command_executor

        self.confirm_stop_execution_dialog = None
        self.execution_still_running_dialog = None
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("run_view_widget")
        layout = QVBoxLayout(widget)

        run_view_label = QLabel("Run View")
        run_view_label.setObjectName("run_view_label")
        layout.addWidget(run_view_label, alignment=Qt.AlignmentFlag.AlignTop)

        step_widget = QWidget()
        step_widget.setObjectName("step_widget")
        self.step_layout = QHBoxLayout(step_widget)
        self.run_indicators = []
        layout.addWidget(step_widget,1)

        self.output_widget = QSplitter()
        layout.addWidget(self.output_widget,1)

        self.execution_output = QTextEdit(readOnly=True)
        self.execution_output.setObjectName("execution_output")
        self.output_widget.addWidget(self.execution_output)

        self.error_output = QTextEdit(readOnly=True)
        self.error_output.setObjectName("error_output")
        self.output_widget.addWidget(self.error_output)
        self.output_widget.setVisible(False)

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
        self.stop_run_button.setProperty("highlight", "false")
        self.stop_run_button.clicked.connect(self._stop_run_button_clicked)

        self.toggle_console_button = QPushButton("Toggle Console")
        self.toggle_console_button.setEnabled(True)
        self.toggle_console_button.clicked.connect(self._toggle_console_button_clicked)

        self.results_button = QPushButton("Results")
        self.results_button.setEnabled(False)
        self.results_button.setProperty("highlight", "false")

        return NavigationButtonsWidget(left_button=self.stop_run_button, middle_button=self.toggle_console_button, right_button=self.results_button)

    def _stop_run_button_clicked(self) -> None:
        self._stop_execution()

    def _toggle_console_button_clicked(self) -> None:
        previous_visibility = self.output_widget.isVisible()
        self.output_widget.setVisible(not previous_visibility)

        layout = self.output_widget.parent().layout()
        step_widget_index = 1

        if previous_visibility:
            layout.setStretch(step_widget_index, 1)
            for indicator in self.run_indicators:
                indicator.set_indicator_size(120)
        else:
            layout.setStretch(step_widget_index, 0)
            for indicator in self.run_indicators:
                indicator.set_indicator_size(90)

    # methods
    @Slot()
    def start_run(self):
        self.clear_outputs()
        self._start_execution()

    @Slot(int)
    def run_start(self, number_of_processes: int) -> None:
        self.setup_execution_indicators(number_of_processes)
        self.stop_run_button.setEnabled(True)
        self.stop_run_button.setProperty("highlight", "true")
        self.stop_run_button.style().unpolish(self.stop_run_button)
        self.stop_run_button.style().polish(self.stop_run_button)

    @Slot(bool)
    def run_end(self, run_successful: bool) -> None:
        """
        Update the execution buttons and close an open confirm dialog.
        """
        self.stop_run_button.setEnabled(False)
        self.stop_run_button.setProperty("highlight", "false")
        self.stop_run_button.style().unpolish(self.stop_run_button)
        self.stop_run_button.style().polish(self.stop_run_button)
        if self.confirm_stop_execution_dialog is not None:
            self.confirm_stop_execution_dialog.close()
        if self.execution_still_running_dialog is not None:
            self.execution_still_running_dialog.close()

    def _start_execution(self):
        commands = self._run_record.to_cli()
        try:
            self._command_executor.start_execution(commands)
        except Exception:
            self.execution_still_running_dialog = ErrorDialog(self, "Execution still running", "A process is still running, try again later.")
            self.execution_still_running_dialog.exec()

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
            elif idx < number_of_processes and idx >= number_of_indicators:
                self.add_indicator_widget(idx)
                continue
            elif idx >= number_of_processes and idx < number_of_indicators:
                self.run_indicators[idx].setVisible(False)

    def add_indicator_widget(self, index: int) -> None:
        """
        Add an indicator widget to self.step_layout.
        """
        indicator = ProcessIndicator(number=index + 1, size=120)
        self._command_executor.process_started.connect(lambda idx=index: self._process_started(idx))
        self._command_executor.process_finished.connect(lambda idx=index: self._process_finished(idx))
        self.step_layout.addWidget(indicator)
        self.run_indicators.append(indicator)

    def set_execution_view_indicator(self, index: int, state: IndicatorState) -> None:
        """
        Set the indicator to the given state.

        :param index: the index of the indicator
        :type index: int

        :param state: the new state of the indicator
        :type state: str
        """
        self.run_indicators[index].state = state

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
        self.set_execution_view_indicator(process_index, IndicatorState.RUNNING)
    @Slot(int)
    def _process_finished(self, process_index: int) -> None:
        """
        Handle CommandExecutor.process_finished.
        """
        self.set_execution_view_indicator(process_index, IndicatorState.FINISHED)

    @Slot(int, QProcess.ProcessError)
    def _process_failed(self, process_index: int, process_error: QProcess.ProcessError) -> None:
        """
        Handle CommandExecutor.process_failed.
        """
        self.set_execution_view_indicator(process_index, IndicatorState.FAILED)

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
        self.set_execution_view_indicator(process_index, IndicatorState.STOPPED)


class RunResultsWidget(RunSubWidget):
    def __init__(self, run_record: RunRecord):
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("run_results_widget")
        layout = QVBoxLayout(widget)

        run_results_label = QLabel("Run Results")
        run_results_label.setObjectName("run_results_label")
        layout.addWidget(run_results_label)

        self.results_widget = ResultsWidget(self._run_record)

        results_scroll = QScrollArea()
        results_scroll.setObjectName("results_scroll")
        results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        results_scroll.setWidgetResizable(True)
        results_scroll.setWidget(self.results_widget )
        layout.addWidget(results_scroll, 1)
        return widget

    @Slot(bool)
    def run_end(self, run_successful: bool) -> None:
        if (run_successful):
            self.results_widget.show_results()

    def _setup_navigation_buttons(self) -> QWidget:
        return QWidget()
        # TODO: Implement
        # raise NotImplementedError
