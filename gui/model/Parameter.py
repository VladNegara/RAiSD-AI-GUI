from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from PySide6.QtCore import QObject, Signal

T = TypeVar("T")


class AbstractQObjectMeta(type(ABC), type(QObject)):
    """
    Metaclass for an abstract base QObject class.
    """

    pass


class Parameter(ABC, QObject, Generic[T], metaclass=AbstractQObjectMeta):
    value_changed: Signal

    def __init__(
            self,
            name: str, description: str, flag: str,
            default_value: T,
    ) -> None:
        super().__init__(self)
        self.name = name
        self.description = description
        self.default_value = default_value
        self._value = default_value
        self.flag = flag

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new_value: T) -> None:
        self._value = new_value
        self.value_changed.emit(self.value, True)

    def reset_value(self) -> None:
        self._value = self.default_value

    @property
    def valid(self) -> bool:
        return True

    @abstractmethod
    def to_cli(self) -> str:
        pass
