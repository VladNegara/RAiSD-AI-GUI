import datetime as dt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSplitter,
    QStackedWidget,
)
from PySide6.QtCore import Slot, Qt

from gui.widgets.operation_record_widget import OperationRecord
from gui.widgets.operation_record_list_widget import OperationRecordList
from gui.widgets.results_widget import ResultsWidget


from gui.model.settings import app_settings
from gui.model.run_result import RunResult

class HistoryWidget(QWidget):
    """
    The history page, showing a list of completed runs on the left
    and the details of the selected run on the right.
    """

    def __init__(self):
        super().__init__()
        self._history_list: OperationRecordList = OperationRecordList()
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self._history_list.run_selected.connect(self._on_run_selected)

        dummy_records = RunResult.from_history_file()
        if dummy_records:
            for op_rec in dummy_records:
                self._history_list.add_record(op_rec)

        splitter.addWidget(self._history_list)

        self._right_panel = QStackedWidget()
        splitter.addWidget(self._right_panel)

        # Right panel: detail view. This will be changed with results view after it is implemented.
        self._detail_panel = QWidget()
        detail_layout = QVBoxLayout(self._detail_panel)
        self._detail_label = QLabel("Select a run to see details.")
        self._detail_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._detail_label.setWordWrap(True)
        detail_layout.addWidget(self._detail_label)
        detail_layout.addStretch()
        self._right_panel.addWidget(self._detail_panel)

        # Give the list 1/3 and the detail panel 2/3 of the width
        splitter.setSizes([200, 400])


    def add_completed_run(self, op_rec: OperationRecord) -> None:
        """
        Add a completed run to the history list.

        :param op_rec: the completed operation record to add
        :type op_rec: OperationRecord
        """
        self._history_list.add_record(op_rec)

    @Slot(OperationRecord)
    def _on_run_selected(self, op_rec: OperationRecord) -> None:
        """
        Update the detail panel when a record is selected from the list.
        #TODO: this will be changed, once we get the results from actual operation records
        """
        current = self._right_panel.currentWidget()
        if current is not self._detail_panel:
            self._right_panel.removeWidget(current)
            current.deleteLater()

        if op_rec.run_result is not None:
            results_widget = ResultsWidget(op_rec.run_result)
            results_widget.show_results()
            self._right_panel.addWidget(results_widget)
            self._right_panel.setCurrentWidget(results_widget)
        else:
            self._detail_label.setText(
                f"Name: {op_rec.name}\n"
                f"Date: {op_rec.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Operations: {', '.join(op_rec.operations)}\n"
                f"Input files:\n" + "\n".join(f"  - {f}" for f in op_rec.input_files) + "\n"
                                                                                        f"Output folder: {op_rec.output_folder}"
            )
            self._right_panel.setCurrentWidget(self._detail_panel)
    def update_history(self) -> None:
        run_results = RunResult.from_history_file()