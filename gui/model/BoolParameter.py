from model.Parameter import Parameter

class BoolParameter(Parameter):
    def __init__(self, name, description, default_value:bool, flag:str):
        super().__init__(name, description, default_value, flag)

    def set_value(self, value:bool):
        return super().set_value(value)
    
    def get_value(self) -> bool:
        return super().get_value()
    
    def get_flag_with_value(self):
        if self.value:
            return self.flag
        else:
            return ""