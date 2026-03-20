import datetime as dt
from gui.model.run_result import RunResult

class OperationRecord:
    """
    A record of one single operation with all the necessary attributes
    """
    def __init__(
            self,
            name: str,
            operations: set[str],
            input_files: list[str],
            output_folder: str,
            date: dt.datetime,
            run_result: "RunResult | None" = None,
            # TODO: parameters
    ) -> None:
        self.name = name
        self.operations = operations
        self.input_files = input_files
        self.output_folder = output_folder
        self.date = date
        self.run_result = run_result
