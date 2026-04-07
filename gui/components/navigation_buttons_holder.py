from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QStyle,
    QStyleOption,
)
from PySide6.QtGui import (
    QPainter,
)

class NavigationButtonsHolder(QWidget):
    """
    A widget to hold the navigation buttons for a RunPageTab, and to allow
    for consistent styling and layout of these buttons across different tabs.
    """
    def __init__(
            self, 
            left_button: QPushButton | None = None, 
            middle_button: QPushButton | None = None, 
            right_button: QPushButton | None = None
            ) -> None:
        super().__init__()
        self.left_button = left_button
        self.middle_button = middle_button
        self.right_button = right_button

        self.setObjectName("navigation_buttons_holder")

        layout = QHBoxLayout(self)
        for button, alignment in ((self.left_button, Qt.AlignmentFlag.AlignLeft), 
                                  (self.middle_button, Qt.AlignmentFlag.AlignHCenter), 
                                  (self.right_button, Qt.AlignmentFlag.AlignRight)):
            if button:
                layout.addWidget(button, alignment=alignment)
            else:
                layout.addWidget(QWidget(), 1)

    def paintEvent(self, event) -> None:
        """
        Override paintEvent so that QSS styling (background, border,
        etc.) is applied to this plain QWidget subclass.
        """
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)