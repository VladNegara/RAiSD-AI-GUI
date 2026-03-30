from PySide6.QtCore import (
    Signal,
    Slot,
)
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QPushButton,
)

from ..page import Page
from ..run import (
    OperationTab,
    ParameterTab,
    ConfirmationTab,
    ViewTab,
    ResultsTab,
)
from gui.model.run_record import RunRecord
from gui.model.history_record import HistoryRecord
from gui.execution.command_executor import CommandExecutor


class RunPage(Page):
    """
    The page to display all steps of running the RAiSD-AI-GUI application.
    """

    start_run = Signal()
    run_started = Signal(int)  # number of processes
    run_ended = Signal(bool)  # if run was successful
    run_saved = Signal(HistoryRecord)

    def __init__(self, run_record: RunRecord, command_executor: CommandExecutor):
        """
        Initialize a `RunPage` object.
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

    def update_ui(self) -> None:
        """
        Update the UI elements of the page when it is shown.
        """
        pass

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
        self.operation_selection_widget = OperationTab(run_record=self._run_record)
        self.operation_selection_widget.next_button.clicked.connect(self._switch_to_parameter_input_widget)
        layout.addWidget(self.operation_selection_widget)

        # Parameter input widget
        self.parameter_input_widget = ParameterTab(run_record=self._run_record)
        self.parameter_input_widget.back_button.clicked.connect(self._switch_to_operation_selection_widget)
        self.parameter_input_widget.navigate_next.connect(self._switch_to_parameter_confirmation_widget)
        layout.addWidget(self.parameter_input_widget)

        # Parameter confirmation widget
        self.parameter_confirmation_widget = ConfirmationTab(run_record=self._run_record)
        self.parameter_confirmation_widget.edit_button.clicked.connect(self._switch_to_parameter_input_widget)
        # run_button clicked is handled via the start_run signal
        self.parameter_confirmation_widget.start_run.connect(self.start_run)
        self.run_started.connect(self.parameter_confirmation_widget.run_start)
        self.run_ended.connect(self.parameter_confirmation_widget.run_end)
        layout.addWidget(self.parameter_confirmation_widget)

        # Run view widget
        self.run_view_widget = ViewTab(run_record=self._run_record, command_executor=self._command_executor)
        self.run_view_widget.results_button.clicked.connect(self._switch_to_run_results_widget)
        self.run_view_widget.run_ended.connect(self.run_ended)
        self.run_view_widget.run_started.connect(self.run_started)
        self.start_run.connect(self.run_view_widget.start_run)
        self.run_started.connect(self.run_view_widget.run_start)
        self.run_ended.connect(self.run_view_widget.run_end)
        layout.addWidget(self.run_view_widget)

        # Results widget
        self.run_results_widget = ResultsTab(run_record=self._run_record)
        self.run_ended.connect(self.run_results_widget.run_end)
        self.run_results_widget.new_run_button.clicked.connect(self._new_run_button_clicked)
        self.run_results_widget.edit_run_button.clicked.connect(self._switch_to_operation_selection_widget)
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

    @Slot()
    def _new_run_button_clicked(self) -> None:
        self._run_record.reset()
        self.operation_selection_widget.reset()
        self._switch_to_operation_selection_widget()

