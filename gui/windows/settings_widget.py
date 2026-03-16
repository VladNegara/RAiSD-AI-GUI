from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background-color: lightyellow;")
        layout = QVBoxLayout(self)
        settings_label = QLabel("Settings")
        layout.addWidget(settings_label)