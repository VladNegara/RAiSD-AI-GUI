"""
Utility classes for displaying text with an icon, e.g. as a warning.

The text is hidden by default. Clicking the icon toggles the text
and background visibility.
"""

from PySide6.QtGui import (
    QPainter,
    QMouseEvent,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QStyle,
    QWidget,
    QStyleOption,
)


class IconLabel(QWidget):
    """
    Base class for icon labels.

    An `IconLabel` combines the provided icon and text in a horizontal
    layout. The text is hidden by default — clicking the icon toggles
    the text and styled background on and off.
    """

    def __init__(
            self,
            pixmapi: QStyle.StandardPixmap,
            text: str,
    ) -> None:
        """
        Initialize an `IconLabel` object.

        :param pixmapi: the standard pixmap enum value
        :type pixmapi: QStyle.StandardPixmap

        :param text: the text to display
        :type text: str
        """
        super().__init__()
        self._expanded = False

        layout = QHBoxLayout(self)

        self._icon_label = QLabel()
        self._icon_label.setCursor(Qt.CursorShape.PointingHandCursor)
        pixmap = self.style().standardPixmap(pixmapi)
        self._icon_label.setPixmap(pixmap)
        self._icon_label.setToolTip("Click to see more")
        layout.addWidget(self._icon_label, alignment=Qt.AlignmentFlag.AlignTop)

        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        self.text_label.setVisible(False)
        layout.addWidget(self.text_label, stretch=1)

        # Start collapsed
        self.setProperty("expanded", "false")

    @property
    def text(self) -> str:
        return self.text_label.text()

    @text.setter
    def text(self, new_text: str) -> None:
        self.text_label.setText(new_text)

    @property
    def expanded(self) -> bool:
        return self._expanded

    @expanded.setter
    def expanded(self, value: bool) -> None:
        self._expanded = value
        self.text_label.setVisible(value)
        if value:
            self._icon_label.setToolTip("Click to hide")
        else:
            self._icon_label.setToolTip("Click to see more")
        self.setProperty("expanded", "true" if value else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.updateGeometry()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.expanded = not self.expanded
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)


class InfoLabel(IconLabel):
    """
    A label with an 'i' (info) icon.
    """

    def __init__(self, text: str) -> None:
        """
        Initialize an `InfoLabel` object.

        :param text: the text to display
        :type text: str
        """
        super().__init__(
            pixmapi=QStyle.StandardPixmap.SP_MessageBoxInformation,
            text=text,
        )
        self.setObjectName("info_label")


class WarningLabel(IconLabel):
    """
    A label with a warning sign icon.
    """

    def __init__(self, text: str) -> None:
        """
        Initialize a `WarningLabel` object.

        :param text: the text to display
        :type text: str
        """
        super().__init__(
            pixmapi=QStyle.StandardPixmap.SP_MessageBoxWarning,
            text=text,
        )
        self.setObjectName("warning_label")


class ErrorLabel(IconLabel):
    """
    A label with an error icon.
    """

    def __init__(self, text: str) -> None:
        """
        Initialize an `ErrorLabel` object.

        :param text: the text to display
        :type text: str
        """
        super().__init__(
            pixmapi=QStyle.StandardPixmap.SP_MessageBoxCritical,
            text=text,
        )
        self.setObjectName("error_label")