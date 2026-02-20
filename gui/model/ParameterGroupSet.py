from model.ParameterGroup import ParameterGroup
from model.Parameter import Parameter

class ParameterGroupSet():
    def __init__(self, config_file_path:str):
        self.config_file_path = config_file_path
        self.parameter_groups = []
        self.generate_from_configuration_file()

    def add_parameter_group(self, parameter_group:ParameterGroup):
        self.parameter_groups.append(parameter_group)

    def get_parameter_groups(self) -> list[ParameterGroup]:
        return self.parameter_groups
    
    def generate_from_configuration_file(self):
        # TODO: Implement this method: make parameter_groups, add parameters, add groups to set
        # use self.config_file_path
        pass