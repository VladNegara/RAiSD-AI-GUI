"""
A module containing base UI classes.

The classes extend default PySide widgets and layouts to make them
stylable and remove margins and spacing.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QStyle,
    QStyleOption,
    QSplashScreen,
)
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QColor,
)

from gui.style import constants


class StylableWidget(QWidget):
    """
    A base class for `QWidgets` that will be targeted by an object name
    selector in QSS.

    `QWidget` subclasses that use the `setObjectName` should instead
    subclass `StylableWidget` to have `paintEvent` automatically
    overriden. This ensures QSS is applied to the widget.
    """

    def paintEvent(self, event) -> None:
        # Override paintEvent so that QSS styling is applied.
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(
            QStyle.PrimitiveElement.PE_Widget,
            opt,
            painter,
            self,
        )


class HBoxLayout(QHBoxLayout):
    """
    A wrapper around `QHBoxLayout` with no margins or spacing.
    """

    def __init__(
            self,
            parent: QWidget,
            *,
            left: int = 0,
            top: int = 0,
            right: int = 0,
            bottom: int = 0,
            spacing: int = 0,
    ) -> None:
        """
        Initialize an `HBoxLayout` object.

        :param parent: the parent widget of this layout
        :type parent: QWidget

        :param left: the left margin
        :type left: int

        :param top: the top margin
        :type top: int

        :param right: the right margin
        :type right: int

        :param bottom: the bottom margin
        :type bottom: int

        :param spacing: the spacing between children
        :type spacing: int
        """
        super().__init__(parent)
        self.setContentsMargins(left, top, right, bottom)
        self.setSpacing(spacing)


class VBoxLayout(QVBoxLayout):
    """
    A wrapper around `QVBoxLayout` with no margins or spacing.
    """

    def __init__(
            self,
            parent: QWidget,
            *,
            left: int = 0,
            top: int = 0,
            right: int = 0,
            bottom: int = 0,
            spacing: int = 0,
    ) -> None:
        """
        Initialize a `VBoxLayout` object.

        :param parent: the parent widget of this layout
        :type parent: QWidget

        :param left: the left margin
        :type left: int

        :param top: the top margin
        :type top: int

        :param right: the right margin
        :type right: int

        :param bottom: the bottom margin
        :type bottom: int

        :param spacing: the spacing between children
        :type spacing: int
        """
        super().__init__(parent)
        self.setContentsMargins(left, top, right, bottom)
        self.setSpacing(spacing)


class ResizableStackedWidget(QWidget):
    """
    A stacked widget that scales to the size of the current widget.
    """

    def __init__(
            self,
    ) -> None:
        """
        Initialize a `ResizableStackedWidget` object.
        """
        super().__init__()

        VBoxLayout(self)
        self._widgets : list[QWidget] = []
        self._current_index = 0

    @property
    def current_index(self) -> int:
        """
        The index of the child widget currently displayed.
        """
        return self._current_index

    @current_index.setter
    def current_index(self, new_index: int) -> None:
        self._current_index = new_index
        self._show_current_widget()

    def addWidget(self, widget: QWidget) -> None:
        layout = self.layout()
        if not layout:
            return
        layout.addWidget(widget)
        self._widgets.append(widget)
        self._show_current_widget()

    def _show_current_widget(self) -> None:
        layout = self.layout()
        if not layout:
            return
        if layout.count() == 0:
            return
        for widget in self._widgets:
            widget.hide()
        self._widgets[self.current_index].show()
        self.updateGeometry()

class SplashScreen(QSplashScreen):
    """
    A splash screen that displays the RAiSD-AI GUI splash image with
    support for showing messages in the bottom-left corner.
    """

    def __init__(self, text_color: QColor = QColor(10,13,79), alignment : int =  Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom) -> None:
        """
        Initialize a `SplashScreen` object.
        """
        self._message = ""
        self._text_color = text_color
        self._alignment = alignment

        pixmap = QPixmap("gui/style/resources/Raisd_ai_splash_screen.png")
        super().__init__(pixmap)
        self.setWindowFlag(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)

    def drawContents(self, painter: QPainter) -> None:
        """
        Override drawContents to render the message with a margin.
        """
        painter.setPen(self._text_color)
        rect = self.rect().adjusted(
            constants.GAP_TINY,   # left
            constants.GAP_TINY,   # top
            0,  # right
            0,  # bottom
        )
        painter.drawText(
            rect,
            self._alignment,
            self._message,
        )

    def showMessage(self, message: str, /, alignment: int = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom, color: QColor = QColor(10,13,79)) -> None:
        """
        Show a message in the bottom-left corner of the splash screen.

        :param message: the message to display
        :type message: str

        :param alignment: the alignment of the message
        :type alignment: int

        :param color: the text color
        :type color: QColor
        """
        self._message = message
        self._text_color = color
        self.repaint()