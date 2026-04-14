import pytest
from datetime import datetime
from gui.model.history_record import HistoryRecord


class TestHistoryRecord:
    """Tests for HistoryRecord class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.name = "name"
        self.commands = ["command1", "command2"]
        self.operations = {}
        self.parameters = {}
        self.time_completed = datetime.now()

        self.history_record = HistoryRecord(
            name=self.name,
            commands=self.commands,
            operations=self.operations,
            parameters=self.parameters,
            time_completed=self.time_completed
        )

    def test_init_values(self):
        """Test HistoryRecord values are set correcly through init."""
        assert self.history_record.name == self.name
        assert self.history_record.commands == self.commands
        assert self.history_record.operations == self.operations
        assert self.history_record.parameters == self.parameters
        assert self.history_record.time_completed == self.time_completed
    
    def test_from_history_file(self):
        pytest.skip()

    def test_from_dict(self):
        pytest.skip()

    def test_save_to_history(self):
        pytest.skip()

    def test_to_dict(self):
        pytest.skip()