from PySide6.QtCore import Qt, Property
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import QWidget, QSizePolicy


class ProcessIndicator(QWidget):
    """
    A circular indicator widget that displays a step number.
    """
    def __init__(self, number: int, size: int = 60):
        super().__init__()
        self._number = number
        self._size = size
        self._fill_color = QColor()
        self._border_color = QColor()
        self._text_color = QColor()
        self.setFixedSize(size, size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setProperty("indicator_state", "pending")
        self.setObjectName("process_indicator")

    # QSS-accessible properties

    def get_fill_color(self) -> QColor:
        return self._fill_color

    def set_fill_color(self, color: QColor) -> None:
        self._fill_color = QColor(color)
        self.update()

    def get_border_color(self) -> QColor:
        return self._border_color

    def set_border_color(self, color: QColor) -> None:
        self._border_color = QColor(color)
        self.update()

    def get_text_color(self) -> QColor:
        return self._text_color

    def set_text_color(self, color: QColor) -> None:
        self._text_color = QColor(color)
        self.update()

    fillColor = Property(QColor, get_fill_color, set_fill_color)
    borderColor = Property(QColor, get_border_color, set_border_color)
    textColor = Property(QColor, get_text_color, set_text_color)

    # State methods

    @property
    def state(self) -> str:
        return self.property("indicator_state")

    @state.setter
    def state(self, new_state: str) -> None:
        self.setProperty("indicator_state", new_state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    # Painting

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        margin = 3
        diameter = self._size - 2 * margin

        # Fill
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._fill_color)
        painter.drawEllipse(margin, margin, diameter, diameter)

        # Border
        pen = QPen(self._border_color, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(margin, margin, diameter, diameter)

        # Number
        font = QFont()
        font.setPixelSize(int(self._size * 0.4))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(self._text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self._number))

        painter.end()