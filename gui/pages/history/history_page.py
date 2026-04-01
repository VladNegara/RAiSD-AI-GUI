from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSplitter,
    QStackedWidget,
    QScrollArea,
    QStyleOption,
    QStyle
)
from PySide6.QtCore import Slot, Qt

from ..page import Page
from gui.components.history import HistoryListWidget
from gui.components.results import ResultsWidget
from gui.model.settings import app_settings
from gui.model.run_record import RunRecord
from gui.model.history_record import HistoryRecord

class HistoryPage(Page):
    """
    The history page of the RAiSD-AI GUI application,
    showing a list of completed runs on the left and
    the details of the selected run on the right.
    """

    def __init__(self):
        """
        Initialize a `HistoryPage` object.
        """
        super().__init__()
        self._history_list: HistoryListWidget = HistoryListWidget()
        self._run_record = RunRecord.from_yaml(app_settings.config_path)
        self._selected : HistoryRecord | None = None
        self._setup_ui()
        self.setObjectName("history_widget")
        self._history_list.setObjectName("history_list")

    def _setup_ui(self):
        # Main layout with a splitter
        results_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        results_layout.addWidget(splitter)

        self._history_list.run_selected.connect(self._on_run_selected)

        # Left panel with history records
        history_records = HistoryRecord.from_history_file()
        for op_rec in history_records:
            self._history_list.add_record(op_rec)
        splitter.addWidget(self._history_list)

        # Right panel has results detail view
        self._right_panel = QStackedWidget()
        splitter.addWidget(self._right_panel)
        self.results_panel = QWidget()
        results_layout = QVBoxLayout(self.results_panel)

        run_results_label = QLabel("Run Results")
        run_results_label.setObjectName("run_results_label")
        results_layout.addWidget(run_results_label)

        self.results_widget = ResultsWidget(self._run_record)
        results_scroll = QScrollArea()
        results_scroll.setObjectName("history_results_scroll")
        results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        results_scroll.setWidgetResizable(True)
        results_scroll.setWidget(self.results_widget)
        results_layout.addWidget(results_scroll, 1)
        self._right_panel.addWidget(self.results_panel)
        self.results_panel.hide()

        # Give the list 1/3 and the detail panel 2/3 of the width
        splitter.setSizes([200, 400])

    @Slot(HistoryRecord)
    def add_completed_run(self, history_record: HistoryRecord) -> None:
        """
        Add a completed run to the history list.

        :param op_rec: the completed operation record to add
        :type op_rec: OperationRecord
        """
        self._history_list.add_record(history_record)

    @Slot(HistoryRecord)
    def _on_run_selected(self, history_record: HistoryRecord) -> None:
        """
        Update the detail panel when a record is selected from the list.
        """
        if self._selected == history_record:
            self.results_panel.hide()
            self._selected = None
        else:
            self._run_record.populate(history_record)
            self.results_widget.show_results()
            self.results_panel.show()
            self._selected = history_record

    def update_history_time(self) -> None:
        """
        Update the time labels of the history record widgets
        """
        self._history_list.update_time()

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)