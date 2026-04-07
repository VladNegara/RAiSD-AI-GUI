from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QSplitter,
    QStackedWidget,
    QScrollArea,
)
from PySide6.QtCore import Slot, Qt

from ..page import Page
from gui.model.settings import app_settings
from gui.model.run_record import RunRecord
from gui.model.history_record import HistoryRecord
from gui.widgets import (
    HBoxLayout,
    VBoxLayout,
)
from gui.components.history import HistoryListWidget
from gui.components.results import ResultsWidget
from gui.style import constants

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
        self._run_record = RunRecord.from_yaml(app_settings.config_path.absoluteFilePath())
        self._selected : HistoryRecord | None = None
        self._setup_ui()
        self._history_list.setObjectName("history_list")

    def _setup_ui(self):
        # Main layout with a splitter
        layout = HBoxLayout(
            self,
            left=constants.GAP_MEDIUM,
            top=constants.GAP_MEDIUM,
            right=constants.GAP_MEDIUM,
            bottom=constants.GAP_MEDIUM,
        )

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        self._history_list.run_selected.connect(self._on_run_selected)

        # Left panel with history records
        self.populate_history_list_widget()
        splitter.addWidget(self._history_list)

        # Right panel has results detail view
        self._right_panel = QStackedWidget()
        splitter.addWidget(self._right_panel)
        self.results_panel = QWidget()
        results_layout = VBoxLayout(
            self.results_panel,
            spacing=constants.GAP_SMALL,
        )

        results_title_label = QLabel("Results")
        results_title_label.setProperty("title", "true")
        results_layout.addWidget(results_title_label)

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

    def reset_page(self) -> None:
        """
        Reset the page to its initial state.
        """
        self._history_list.clear()

        self.populate_history_list_widget()

        self.selected = None

    def populate_history_list_widget(self) -> None:
        """
        Obtain the history records from the file and
        populate the history list widget of the HistoryPage.
        """
        history_records = HistoryRecord.from_history_file()
        for op_rec in history_records:
            self._history_list.add_record(op_rec)

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
        if self.selected == history_record:
            self.selected = None
        else:
            self.selected = history_record

    def update_history_time(self) -> None:
        """
        Update the time labels of the history record widgets
        """
        self._history_list.update_time()
    
    @property
    def selected(self) -> HistoryRecord | None:
        return self._selected
    
    @selected.setter
    def selected(self, value : HistoryRecord | None) -> None:
        self._selected = value
        if value:
            self._run_record.populate(value)
            self.results_widget.show_results()
            self.results_panel.show()
        else:
            self.results_panel.hide()
