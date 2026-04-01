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
    RunPageTab,
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
        Set up the general run page.

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

        self.button_tab_pairs: dict[QPushButton, RunPageTab] = {
            self.operation_selection_button: self.operation_tab,
            self.parameter_input_button: self.parameter_tab,
            self.parameter_confirmation_button: self.confirmation_tab,
            self.execution_view_button: self.view_tab,
            self.results_button: self.results_tab,
        }

        self._set_active_tab(self.operation_tab)

    def _setup_step_button_bar(self, layout: QHBoxLayout):
        """
        Setup the step button bar.
        """
        self.operation_selection_button = QPushButton("Operation Selection")
        self.operation_selection_button.clicked.connect(self._switch_to_operation_tab)
        layout.addWidget(self.operation_selection_button)

        self.parameter_input_button = QPushButton("Parameter Input")
        self.parameter_input_button.clicked.connect(self._switch_to_parameter_tab)
        layout.addWidget(self.parameter_input_button)

        self.parameter_confirmation_button = QPushButton("Parameter Confirmation")
        self.parameter_confirmation_button.clicked.connect(self._switch_to_confirmation_tab)
        layout.addWidget(self.parameter_confirmation_button)

        self.execution_view_button = QPushButton("Run")
        self.execution_view_button.clicked.connect(self._switch_to_view_tab)
        layout.addWidget(self.execution_view_button)

        self.results_button = QPushButton("Results")
        self.results_button.clicked.connect(self._switch_to_results_tab)
        layout.addWidget(self.results_button)

    def _setup_stacked_step_widget(self, layout: QStackedLayout):
        """
        Set up the stacked step widget.
        """
        # Operation selection tab
        self.operation_tab = OperationTab(run_record=self._run_record)
        self.operation_tab.navigate_next.connect(self._switch_to_parameter_tab)
        layout.addWidget(self.operation_tab)

        # Parameter input tab
        self.parameter_tab = ParameterTab(run_record=self._run_record)
        self.parameter_tab.navigate_back.connect(self._switch_to_operation_tab)
        self.parameter_tab.navigate_next.connect(self._switch_to_confirmation_tab)
        layout.addWidget(self.parameter_tab)

        # Parameter confirmation tab
        self.confirmation_tab = ConfirmationTab(run_record=self._run_record)
        self.confirmation_tab.navigate_back.connect(self._switch_to_parameter_tab)
        self.confirmation_tab.start_run.connect(self.start_run)
        self.run_started.connect(self.confirmation_tab.run_started)
        self.run_ended.connect(self.confirmation_tab.run_ended)
        layout.addWidget(self.confirmation_tab)

        # Run view tab
        self.view_tab = ViewTab(run_record=self._run_record, command_executor=self._command_executor)
        self.view_tab.navigate_next.connect(self._switch_to_results_tab)
        self.view_tab.run_started.connect(self.run_started)
        self.view_tab.run_ended.connect(self.run_ended)
        self.start_run.connect(self.view_tab.start_run)
        layout.addWidget(self.view_tab)

        # Results tab
        self.results_tab = ResultsTab(run_record=self._run_record)
        self.results_tab.new_run_button.clicked.connect(self._new_run)
        self.results_tab.edit_run_button.clicked.connect(self._switch_to_operation_tab)
        self.run_ended.connect(self.results_tab.run_ended)
        layout.addWidget(self.results_tab)

    def _set_active_tab(self, active_tab: RunPageTab) -> None:
        """
        Update the active tab. 
        Both the button styles and the displayed tab are updated.
        """
        for i, (button, tab) in enumerate(self.button_tab_pairs.items()):
            if tab == active_tab:
                role = "active"
                tab.refresh()
                self.stacked_step_widget_layout.setCurrentWidget(tab)
            elif i < list(self.button_tab_pairs.values()).index(active_tab):
                role = "past_step"
                button.setEnabled(True)
            else:
                role = "default"
                button.setEnabled(False)
            button.setProperty("step_role", role)
            button.style().unpolish(button) # Required to apply styling dynamically
            button.style().polish(button)

    # ---------- step button bar switch methods ----------
    @Slot()
    def _switch_to_operation_tab(self) -> None:
        self._set_active_tab(self.operation_tab)

    @Slot()
    def _switch_to_parameter_tab(self) -> None:
        self._set_active_tab(self.parameter_tab)

    @Slot()
    def _switch_to_confirmation_tab(self) -> None:
        self._set_active_tab(self.confirmation_tab)

    @Slot()
    def _switch_to_view_tab(self) -> None:
        self._set_active_tab(self.view_tab)

    @Slot()
    def _switch_to_results_tab(self) -> None:
        self._set_active_tab(self.results_tab)

    # ---------- Handle events ----------
    @Slot()
    def _handle_run_start(self) -> None:
        self._switch_to_view_tab()

    @Slot()
    def _handle_run_end(self, run_successful: bool) -> None:
        if run_successful:
            history_record = self._run_record.to_history_record() 
            history_record.save_to_history()     
            self.run_saved.emit(history_record)
            self._switch_to_results_tab()

    @Slot()
    def _new_run(self) -> None:
        self._run_record.reset()
        self.operation_tab.reset()
        self._switch_to_operation_tab()

