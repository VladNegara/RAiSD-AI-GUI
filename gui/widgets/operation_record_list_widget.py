from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
)

from gui.widgets.operation_record_widget import OperationRecord, OperationRecordWidget


class OperationRecordList(QWidget):
    """
    The widget that holds the all operation records to display in history_widget
    """
    run_selected = Signal(OperationRecord)

    def __init__(
            self,
            op_records: list[OperationRecord] | None = None,
    ) -> None:
        super().__init__()
        self._op_records = op_records or []

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

        for record in self._op_records:
            self._add_record_widget(record)

    def add_record(self, op_rec: OperationRecord) -> None:
        self._op_records.insert(0, op_rec)
        self._add_record_widget(op_rec, at_top = True)

    def _add_record_widget(self, op_rec: OperationRecord, at_top: bool = False) -> None:
        widget = OperationRecordWidget(op_rec)
        widget.setMinimumHeight(100)
        widget.mousePressEvent = lambda _: self.run_selected.emit(op_rec)
        if at_top:
            self._list_layout.insertWidget(0, widget)
        else:
            count = self._list_layout.count()
            self._list_layout.insertWidget(count - 1, widget)
