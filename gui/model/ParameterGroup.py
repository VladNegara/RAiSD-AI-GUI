from model.Parameter import Parameter

class ParameterGroup():
    def __init__(self, name:str):
        self.name = name
        self.parameters = []

    def add_parameter(self, parameter:Parameter):
        self.parameters.append(parameter)

    def get_parameters(self) -> list[Parameter]:
        return self.parameters