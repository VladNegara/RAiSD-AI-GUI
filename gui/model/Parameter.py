from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class Parameter(ABC, Generic[T]):
    def __init__(self, name:str, description:str, default_value:T, flag:str):   
        self.name = name
        self.description = description
        self.default_value = default_value
        self._value = default_value
        self.flag = flag

    @property
    def value(self) -> T:
        return self.value

    @value.setter
    def value(self, new_value:T) -> None:
        self._value = new_value
    
    def reset_value(self):
        self._value = self.default_value

    @abstractmethod
    def get_flag_with_value(self):
        pass