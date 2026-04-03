from PySide6.QtCore import Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QStyleOption,
    QStyle,
)

from .history_record_widget import HistoryRecordWidget
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
        self._history_widgets: list[HistoryRecordWidget] = []
        self.setObjectName('history_list_widget')

        layout = QVBoxLayout(self)

        title = QLabel("History")
        title.setObjectName("history_list_widget_title")
        layout.addWidget(title)

        # The list of history widgets
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            scroll_area.horizontalScrollBarPolicy().ScrollBarAlwaysOff
        )
        layout.addWidget(scroll_area)

        self._list_container = QWidget()
        self._list_container.setObjectName("history_list_container")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()
        scroll_area.setWidget(self._list_container)

        # Add the widgets to the list
        for record in self._history_records:
            widget = self._add_record_widget(record)
            self._history_widgets.append(widget)

    def add_record(self, history_record: HistoryRecord) -> None:
        """
        Adds a history record to the HistoryList.
        """
        self._history_records.insert(0, history_record)
        widget = self._add_record_widget(history_record, at_top = True)
        self._history_widgets.append(widget)

    def _add_record_widget(self, history_record: HistoryRecord, at_top: bool = False) -> HistoryRecordWidget:
        """
        Adds a history record by creating it and setting its size and 
        interactivity.
        """
        widget = HistoryRecordWidget(history_record)
        widget.setMinimumHeight(widget.minimumSizeHint().height())
        widget.mousePressEvent = lambda _: self.run_selected.emit(history_record)
        if at_top:
            self._list_layout.insertWidget(0, widget)
        else:
            count = self._list_layout.count()
            self._list_layout.insertWidget(count - 1, widget)
        return widget

    def update_time(self) -> None:
        """
        Updates the time label of all the history widgets.
        """
        for widget in self._history_widgets:
            widget.update_time()

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
