"""
Utility classes for displaying text with an icon, e.g. as a warning.
"""

from PySide6.QtGui import (
    QColor,
    QPainter
)
from PySide6.QtWidgets import(
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
    layout.
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

        layout = QHBoxLayout(self)

        icon_label = QLabel()
        pixmap = self.style().standardPixmap(pixmapi)
        icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)

        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        layout.addWidget(self.text_label, stretch=1)

    @property
    def text(self) -> str:
        return self.text_label.text()

    @text.setter
    def text(self, new_text: str) -> None:
        self.text_label.setText(new_text)

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
