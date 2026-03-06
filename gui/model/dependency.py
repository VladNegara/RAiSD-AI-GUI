from abc import ABC, abstractmethod

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from gui.model.meta import AbstractQObjectMeta
from gui.model.parameter import Parameter


class Dependency(QObject):
    class Condition(ABC, QObject, metaclass=AbstractQObjectMeta):
        changed = Signal(bool)

    class Effect(ABC, QObject, metaclass=AbstractQObjectMeta):
        @Slot(bool)
        @abstractmethod
        def condition_changed(self, value: bool) -> None:
            pass

    def __init__(
            self,
            source: Condition,
            target: Effect,
    ) -> None:
        self._source = source
        self._target = target

        self._source.changed.connect(self._target)
