from abc import ABC, abstractmethod
from typing import Any

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from gui.model.meta import AbstractQObjectMeta


class Dependency(QObject):
    class Condition(ABC, QObject, metaclass=AbstractQObjectMeta):
        changed = Signal(bool)

        def __init__(
                self,
                value: bool = False,
                parent: QObject | None = None
        ) -> None:
            super().__init__(parent=parent)
            self._value = value

        @property
        def value(self) -> bool:
            return self._value

        @value.setter
        def value(self, new_value: bool) -> None:
            self._value = new_value
            self.changed.emit(self._value)

    class Effect(ABC, QObject, metaclass=AbstractQObjectMeta):
        @Slot(bool)
        @abstractmethod
        def condition_changed(self, value: bool) -> None:
            pass

    def __init__(
            self,
            source: Condition,
            target: Effect,
            parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._source = source
        self._target = target

        self._target.condition_changed(self._source.value)
        self._source.changed.connect(self._target.condition_changed)


class AndCondition(Dependency.Condition):
    def __init__(
            self,
            conditions: list[Dependency.Condition],
            parent: QObject | None = None,
    ) -> None:
        self._conditions = conditions
        super().__init__(all([condition.value for condition in self._conditions]), parent)

        for condition in self._conditions:
            condition.changed.connect(self._condition_changed)

    @Slot(bool)
    def _condition_changed(self, _: bool) -> None:
        self.value = all([condition.value for condition in self._conditions])


class OrCondition(Dependency.Condition):
    def __init__(
            self,
            conditions: list[Dependency.Condition],
            parent: QObject | None = None,
    ) -> None:
        self._conditions = conditions
        super().__init__(any([condition.value for condition in self._conditions]), parent)

        for condition in self._conditions:
            condition.changed.connect(self._condition_changed)

    @Slot(bool)
    def _condition_changed(self, _: bool) -> None:
        self.value = any([condition.value for condition in self._conditions])
