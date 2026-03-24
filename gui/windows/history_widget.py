import datetime as dt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSplitter,
    QStackedWidget,
    QScrollArea
)
from PySide6.QtCore import Slot, Qt

from gui.widgets.history_record_widget import HistoryRecordWidget
from gui.widgets.history_list_widget import HistoryListWidget
from gui.widgets.results_widget import ResultsWidget


from gui.model.settings import app_settings
from gui.model.run_result import RunResult
from gui.model.history_record import HistoryRecord

class HistoryWidget(QWidget):
    """
    The history page, showing a list of completed runs on the left
    and the details of the selected run on the right.
    """

    def __init__(self):
        super().__init__()
        self._history_list: HistoryListWidget = HistoryListWidget()
        self._run_result = RunResult()
        self._selected = None
        self._setup_ui()

    def _setup_ui(self):
        results_layout = QHBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        results_layout.addWidget(splitter)

        self._history_list.run_selected.connect(self._on_run_selected)

        history_records = HistoryRecord.from_history_file()
        if history_records:
            for op_rec in history_records:
                self._history_list.add_record(op_rec)

        splitter.addWidget(self._history_list)

        self._right_panel = QStackedWidget()
        splitter.addWidget(self._right_panel)

        # Right panel: detail view. This will be changed with results view after it is implemented.
        self.results_panel = QWidget()
        self.results_panel.setStyleSheet("background-color: lightblue;")
        results_layout = QVBoxLayout(self.results_panel)

        run_results_label = QLabel("Run Results")
        results_layout.addWidget(run_results_label)

        self.results_widget = ResultsWidget(self._run_result)

        results_scroll = QScrollArea()
        results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        results_scroll.setWidgetResizable(True)
        results_scroll.setWidget(self.results_widget )
        results_layout.addWidget(results_scroll, 1)
        self._right_panel.addWidget(self.results_panel)
        self.results_panel.hide()

        # Give the list 1/3 and the detail panel 2/3 of the width
        splitter.setSizes([200, 400])

    def add_completed_run(self, history_record: HistoryRecord) -> None:
        """
        Add a completed run to the history list.

        :param op_rec: the completed operation record to add
        :type op_rec: OperationRecord
        """
        self._history_list.add_record(history_record)

    @Slot(RunResult)
    def _on_run_selected(self, history_record: HistoryRecord) -> None:
        """
        Update the detail panel when a record is selected from the list.
        #TODO: this will be changed, once we get the results from actual operation records
        """
        if self._selected == history_record.name:
            self.results_panel.hide()
            self._selected = None
        else:
            self._run_result.populate(history_record)
            self.results_widget.show_results()
            self.results_panel.show()
            self._selected = history_record.name
        

    def update_history(self) -> None:
        #TODO: d not remake the entire list each time, but update as runs are completed
        run_results = HistoryRecord.from_history_file()