from abc import ABC, abstractmethod
from typing import Any

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


class BoolParameterTrueCondition(Dependency.Condition):
    def __init__(
            self,
            parameter: Parameter[bool],
            parent: QObject | None = None,
    ) -> None:
        super().__init__(value=parameter.value, parent=parent)
        self._parameter = parameter

        self._parameter.value_changed.connect(self._parameter_value_changed)

    @Slot(bool, bool)
    def _parameter_value_changed(
        self,
        new_value: bool,
        _: bool,
    ) -> None:
        self.changed.emit(new_value)


class ParameterEnabledEffect(Dependency.Effect):
    def __init__(
            self,
            parameter: Parameter[Any],
            parent: QObject | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._parameter = parameter
        

    def condition_changed(self, new_value: bool) -> None:
        self._parameter.enabled = new_value
