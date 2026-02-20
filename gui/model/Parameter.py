from abc import ABC, abstractmethod

class Parameter(ABC):
    def __init__(self, name:str, description:str, default_value, flag:str):   
        self.name = name
        self.description = description
        self.default_value = default_value
        self.value = default_value
        self.flag = flag

    @abstractmethod
    def set_value(self, value):
        self.value = value

    @abstractmethod
    def get_value(self):
        return self.value
    
    def reset_value(self):
        self.value = self.default_value

    @abstractmethod
    def get_flag_with_value(self):
        pass