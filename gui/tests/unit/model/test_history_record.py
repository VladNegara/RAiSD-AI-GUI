import pytest
from datetime import datetime
from gui.model.history_record import HistoryRecord


class TestHistoryRecord:
    """Tests for HistoryRecord class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.name = "name"
        self.commands = ["command1", "command2"]
        self.operations = {
            "index": 0,
            "trees": [{}, {}]
        }
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

    def test_from_dict_name(self):
        """Test that the name attribute is collected correctly from a dict."""
        # Arrange
        dict_empty = {}
        dict_wrong_format = {"name": 5}
        dict_correct = {"name": self.name}

        # Assert
        with pytest.raises(ValueError, match="Missing run name. Expected string."):
            HistoryRecord.from_dict(dict_empty)
        
        with pytest.raises(ValueError, match="Invalid run name: 5. Expected string."):
            HistoryRecord.from_dict(dict_wrong_format)

        with pytest.raises(ValueError, match=r"[^name]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_commands(self):
        """Test that the commands attribute is collected correctly from a dict."""
        # Arrange
        dict_missing = {"name": self.name}
        dict_wrong_format = {"name": self.name, "commands": 5}
        dict_wrong_inner_format = {"name": self.name, "commands": [7, 2]}
        dict_correct = {"name": self.name, "commands": self.commands}

        # Assert
        with pytest.raises(ValueError, match="Missing commands. Expected list."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match="Invalid commands object: 5. Expected list."):
            HistoryRecord.from_dict(dict_wrong_format)

        with pytest.raises(ValueError, match=r"Invalid command type: (7|2). Expected string."):
            HistoryRecord.from_dict(dict_wrong_inner_format)

        with pytest.raises(ValueError, match=r"[^command]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_operations(self):
        """Test that the operations attribute is collected correctly from a dict."""
        # Arrange
        dict_missing = {"name": self.name, "commands": self.commands}
        dict_wrong_format = {"name": self.name, "commands": self.commands, "operations": 5}
        dict_correct = {"name": self.name, "commands": self.commands, "operations": self.operations}

        # Assert
        with pytest.raises(ValueError, match="Missing operations. Expected dict."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match="Invalid operations type: 5. Expected dictionary."):
            HistoryRecord.from_dict(dict_wrong_format)
        
        with pytest.raises(ValueError, match=r"[^operation]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_tree_index(self):
        """Test that the tree index attribute in the operations dictionary is 
        collected correctly."""
        # Arrange
        dict_missing = {"name": self.name, "commands": self.commands, 
                        "operations": {}}
        dict_wrong_format = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": "HI"}}
        dict_correct = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": 1}}
        
        # Assert
        with pytest.raises(ValueError, match="Missing index in operations dictionary. Expected integer."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match="Invalid tree index: HI. Expected integer."):
            HistoryRecord.from_dict(dict_wrong_format)
        
        with pytest.raises(ValueError, match=r"[^index]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_operation_trees(self):
        """Test that the tree index attribute in the operations dictionary is 
        collected correctly."""
        # Arrange
        dict_missing = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": 1}}
        dict_wrong_format = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": 1, "trees": 3}}
        dict_wrong_inner_format = {"name": self.name, "commands": self.commands, 
                        "operations": {"index": 1, "trees": [6]}}
        dict_correct = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations}
        
        # Assert
        with pytest.raises(ValueError, match="Missing trees in operations dictionary. Expected list."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match='Invalid operations type: 3. Expected list.'):
            HistoryRecord.from_dict(dict_wrong_format)

        with pytest.raises(ValueError, match='Invalid operation type: 6. Expected dict.'):
            HistoryRecord.from_dict(dict_wrong_inner_format)
        
        with pytest.raises(ValueError, match=r"[^tree]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_parameters(self):
        # Arrange
        dict_wrong_format = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, "parameters": 6}
        dict_correct = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, "parameters": self.parameters}
        
        # Assert
        with pytest.raises(ValueError, match='Invalid parameter object: 6. Expected dictionary.'):
            HistoryRecord.from_dict(dict_wrong_format)
        
        with pytest.raises(ValueError, match=r"[^parameter]"):
            HistoryRecord.from_dict(dict_correct)

    def test_from_dict_time_completed(self):
        # Arrange
        dict_missing = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, 
                        "parameters": self.parameters}
        dict_wrong_format = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, 
                        "parameters": self.parameters,
                        "time_completed": 6}
        dict_correct = {"name": self.name, "commands": self.commands, 
                        "operations": self.operations, 
                        "parameters": self.parameters,
                        "time_completed": str(self.time_completed)}
        
        # Act
        history_record = HistoryRecord.from_dict(dict_correct)
        
        # Assert
        with pytest.raises(ValueError, match="Missing time_completed. Expected string."):
            HistoryRecord.from_dict(dict_missing)

        with pytest.raises(ValueError, match='Invalid time_completed type: 6. Expected string.'):
            HistoryRecord.from_dict(dict_wrong_format)
        
        assert isinstance(history_record, HistoryRecord)

    def test_from_dict_values(self):
        # Arrange
        dict = {
            "name": self.name, 
            "commands": self.commands, 
            "operations": self.operations, 
            "parameters": self.parameters,
            "time_completed": str(self.time_completed)
        }

        # Act
        history_record = HistoryRecord.from_dict(dict)

        # Assert
        assert history_record.name == self.history_record.name
        assert history_record.commands == self.history_record.commands
        assert history_record.operations == self.history_record.operations
        assert history_record.parameters == self.history_record.parameters
        assert history_record.time_completed == self.history_record.time_completed
        

    def test_save_to_history(self):
        pytest.skip()

    def test_to_dict(self):
        pytest.skip()

    def test_to_and_from_dict(self):
        pytest.skip()