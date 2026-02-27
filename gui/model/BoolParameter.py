from gui.model.Parameter import Parameter


class BoolParameter(Parameter[bool]):
    def to_cli(self) -> str:
        if self.value:
            return self.flag
        else:
            return ""
