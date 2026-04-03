from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)


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

        QVBoxLayout(self)
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
        layout.setContentsMargins(0,0,0,0)
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
