from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
)

from gui.model.settings import app_settings
from gui.model.run_result import RunResult

class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: lightgreen;")
        layout = QHBoxLayout(self)
        history_label = QLabel("History")
        layout.addWidget(history_label)

    def update_history(self) -> None:
        run_results = RunResult.from_history_file()