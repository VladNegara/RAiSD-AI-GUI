from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
)

class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: lightgreen;")
        layout = QHBoxLayout(self)
        history_label = QLabel("History")
        layout.addWidget(history_label)
