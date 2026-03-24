from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
)

from gui.widgets.history_record_widget import HistoryRecordWidget
from gui.model.history_record import HistoryRecord


class HistoryListWidget(QWidget):
    """
    The widget that holds the all operation records to display in history_widget
    """
    run_selected = Signal(HistoryRecord)

    def __init__(
            self,
            history_records: list[HistoryRecord] | None = None,
    ) -> None:
        super().__init__()
        self._history_records = history_records or []

        layout = QVBoxLayout(self)

        title = QLabel("History")
        layout.addWidget(title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            scroll_area.horizontalScrollBarPolicy().ScrollBarAlwaysOff
        )
        layout.addWidget(scroll_area)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()
        scroll_area.setWidget(self._list_container)

        for record in self._history_records:
            self._add_record_widget(record)

    def add_record(self, history_record: HistoryRecord) -> None:
        self._history_records.insert(0, history_record)
        self._add_record_widget(history_record, at_top = True)

    def _add_record_widget(self, history_record: HistoryRecord, at_top: bool = False) -> None:
        widget = HistoryRecordWidget(history_record)
        widget.setMinimumHeight(100)
        widget.mousePressEvent = lambda _: self.run_selected.emit(history_record)
        if at_top:
            self._list_layout.insertWidget(0, widget)
        else:
            count = self._list_layout.count()
            self._list_layout.insertWidget(count - 1, widget)
