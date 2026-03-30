from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
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


class RunPageTab(QWidget):
    """
    An abstract base class for tabs in the run page.
     
    Which includes a widget for the main content of the tab and 
    a NavigationButtonsHolder for the navigation buttons. 
    
    Subclasses should implement the `_setup_widget` and
    `_setup_navigation_buttons` methods.
    """
    def __init__(self):
        super().__init__()
        widget = self._setup_widget()
        navigation = self._setup_navigation_buttons()
        self._setup_layout(widget, navigation)

    def _setup_layout(self, widget: QWidget, navigation: QWidget) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widget, 1)
        layout.addWidget(navigation)
        pass

    def _setup_widget(self) -> QWidget:
        """
        Set up the main content widget for the tab.
        
        This method should be implemented by each subclass.

        :return: the main content widget for the tab
        :rtype: QWidget
        """
        raise NotImplementedError()

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        """
        Set up the navigation buttons for the tab.

        This method should be implemented by each subclass.

        :return: a NavigationButtonsHolder 
        :rtype: NavigationButtonsHolder
        """
        raise NotImplementedError()

    def update_ui(self) -> None:
        """
        Update the UI elements of the tab when it is shown.
        """
        raise NotImplementedError()