from PySide6.QtCore import (
    Slot,
)
from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy,
    QStackedWidget,
)


class ResizableStackedWidget(QStackedWidget):
    def __init__(self) -> None:
        super().__init__()
        self.currentChanged.connect(self._on_current_changed)

    def addWidget(self, w: QWidget) -> int:
        w.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Ignored,
        )
        return super().addWidget(w)

    @Slot(int)
    def _on_current_changed(self, index: int) -> None:
        for i in range(self.count()):
            w = self.widget(i)
            if w is None:
                # This is not supposed to happen
                continue
            if i == index:
                w.setSizePolicy(
                    QSizePolicy.Policy.Minimum,
                    QSizePolicy.Policy.Minimum,
                )
            else:
                w.setSizePolicy(
                    QSizePolicy.Policy.Ignored,
                    QSizePolicy.Policy.Ignored,
                )
            w.adjustSize()
        self.adjustSize()
