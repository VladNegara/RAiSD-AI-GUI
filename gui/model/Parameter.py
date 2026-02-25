from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class Parameter(ABC, Generic[T]):
    def __init__(self, name:str, description:str, default_value:T, flag:str):   
        self.name = name
        self.description = description
        self.default_value = default_value
        self.value = default_value
        self.flag = flag

    @abstractmethod
    def set_value(self, value:T) -> None:
        self.value = value

    @abstractmethod
    def get_value(self) -> T:
        return self.value
    
    def reset_value(self):
        self.value = self.default_value

    @abstractmethod
    def get_flag_with_value(self):
        pass