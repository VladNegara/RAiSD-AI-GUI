from PySide6.QtCore import (
    Qt,
    Slot,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QPushButton,
    QLabel,
)

from .run_page_tab import RunPageTab, NavigationButtonsHolder
from gui.model.run_record import RunRecord
from gui.widgets.results import ResultsWidget


class ResultsTab(RunPageTab):
    """
    A tab to display the results of a run, and to allow the user
    to start a new run or edit the current run.
    """
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

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        self.new_run_button = QPushButton("New Run")
        self.new_run_button.setEnabled(True)

        self.edit_run_button = QPushButton("Edit Run")
        self.edit_run_button.setEnabled(True)

        return NavigationButtonsHolder(left_button=self.new_run_button, right_button=self.edit_run_button)

    @Slot(bool)
    def run_end(self, run_successful: bool) -> None:
        if (run_successful):
            self.results_widget.show_results()
