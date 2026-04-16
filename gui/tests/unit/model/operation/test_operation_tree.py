import pytest
from copy import deepcopy

from PySide6.QtCore import (
    QObject,
    Signal,
)

from gui.model.operation import (
    FileConsumerNode,
    FileProducerNode,
)
from gui.model.operation import Operation
from gui.model.operation.file_structure import SingleFile, Directory

from gui.tests.utils.mock_signal import MockSignal

class TestFileConsumerNode:
    """Tests for FileProducerNode class."""

    @pytest.fixture()
    def operation_input_file(self) -> Operation.Input:
        name = "Filename"
        description = "This is a file."
        cli = "-f "
        file = SingleFile([])
        operation_input_file =  Operation.Input(name, description, cli, file)
        return operation_input_file
    
    @pytest.fixture()
    def operation_input_directory(self) -> Operation.Input:
        name = "Directoryname"
        description = "This is a directory."
        cli = "-d "
        file = Directory([])
        operation_input_directory =  Operation.Input(name, description, cli, file)
        return operation_input_directory
    
    @pytest.fixture()
    def file_consumer_node_file(self, operation_input_file) -> FileConsumerNode:
        required_file: Operation.Input = operation_input_file
        file_consumer_node = FileConsumerNode(
            required_file=required_file,
        )
        return file_consumer_node
    
    @pytest.fixture()
    def file_consumer_node_directory(self, operation_input_directory) -> FileConsumerNode:
        required_file: Operation.Input = operation_input_directory
        file_consumer_node = FileConsumerNode(
            required_file=required_file,
        )
        return file_consumer_node
    
    @pytest.fixture()
    def file_producer_node(self, mocker) -> FileProducerNode:
        mock_file_producer_node = mocker.Mock()
        return mock_file_producer_node

    def test_init_values_file(self, operation_input_file):
        """Test FileConsumerNode initialization with a file."""
        # Arrange
        required_file: Operation.Input = operation_input_file
        enabled = True

        # Act
        file_consumer_node = FileConsumerNode(
            required_file=required_file,
            enabled=enabled,
        )

        # Assert
        assert file_consumer_node.producers == []
        assert file_consumer_node.selected_index == 0
        assert file_consumer_node._name == required_file.name
        assert file_consumer_node.name == required_file.name
        assert file_consumer_node._description == required_file.description
        assert file_consumer_node.description == required_file.description
        assert file_consumer_node._cli == required_file.cli
        assert file_consumer_node._requires == required_file.file
        assert file_consumer_node._enabled == enabled

    def test_init_values_directory(self, operation_input_directory):
        """Test FileConsumerNode initialization with a directory."""
        # Arrange
        required_file: Operation.Input = operation_input_directory
        enabled = True

        # Act
        file_consumer_node = FileConsumerNode(
            required_file=required_file,
            enabled=enabled,
        )

        # Assert
        assert file_consumer_node.producers == []
        assert file_consumer_node.selected_index == 0
        assert file_consumer_node._name == required_file.name
        assert file_consumer_node._description == required_file.description
        assert file_consumer_node._cli == required_file.cli
        assert file_consumer_node._requires == required_file.file
        assert file_consumer_node._enabled == enabled

    def test_requires_file(self, operation_input_file):
        """Test the requires method with a file"""
        # Arrange
        required_file: Operation.Input = operation_input_file

        # Act
        file_consumer_node = FileConsumerNode(
            required_file=required_file,
        )

        # Assert
        assert file_consumer_node.requires == required_file.file

    def test_requires_directory(self, operation_input_directory):
        """Test the requires method with a directory"""
        # Arrange
        required_file: Operation.Input = operation_input_directory

        # Act
        file_consumer_node = FileConsumerNode(
            required_file=required_file,
        )

        # Assert
        assert file_consumer_node.requires == required_file.file

    def test_add_producer(self, 
                          file_consumer_node_file:FileConsumerNode, 
                          file_producer_node:FileProducerNode):
        """Test the add_producer method with an arbitrary file_producer_node."""
        # Act
        file_consumer_node_file.add_producer(file_producer_node)

        # Assert
        assert file_consumer_node_file.producers == [file_producer_node]

        # Act
        file_consumer_node_file.add_producer(file_producer_node)

        # Assert
        assert file_consumer_node_file.producers == [file_producer_node, file_producer_node]

    def test_producer_valid_changed(self,
                                    mocker,
                                    file_consumer_node_file:FileConsumerNode, 
                                    file_producer_node:FileProducerNode):
        """Test the connection between valid changed of producer and consumer."""
        # Arrange
        mock_valid_changed = mocker.Mock()
        file_consumer_node_file.valid_changed.connect(mock_valid_changed)

        mock_signal = MockSignal(True)
        file_producer_node.valid_changed.emit = mock_signal.emit
        file_producer_node.valid_changed.connect = mock_signal.connect
        mocker.patch.object(file_producer_node, "valid", return_value = True)
    
        file_consumer_node_file.add_producer(file_producer_node)

        # Act
        file_producer_node.valid_changed.emit(True)

        # Assert
        mock_valid_changed.assert_called_once_with(True)

    def test_cli_parameter(self, file_consumer_node_file: FileConsumerNode):
        """Test cli parameter returning the right flag and file."""
        # Arrange
        required_file_path = file_consumer_node_file.file
        cli = "-f "
        file_consumer_node_file._cli = cli
        cli_parameter = f"{cli}{required_file_path}"

        # Assert
        assert file_consumer_node_file.cli_parameter == cli_parameter

    def test_selected_index_setter(self, 
                                   mocker,
                                   file_consumer_node_file: FileConsumerNode):
        """Test selected index setter."""
        # Arrange
        file_consumer_node_file.enabled = True
        file_producer_node = mocker.Mock()
        file_producer_node2 = mocker.Mock()

        file_producer_node.enabled = True
        file_producer_node.valid = False
        file_producer_node2.enabled = False
        file_producer_node2.valid = True

        file_consumer_node_file.add_producer(file_producer_node)
        file_consumer_node_file.add_producer(file_producer_node2)

        selected_index_spy = mocker.Mock()
        valid_spy = mocker.Mock()
        file_consumer_node_file.selected_index_changed.connect(selected_index_spy)
        file_consumer_node_file.valid_changed.connect(valid_spy)

        # Act
        file_consumer_node_file.selected_index = 1

        # Assert
        assert file_producer_node.enabled is False
        assert file_producer_node2.enabled is True
        selected_index_spy.assert_called_once_with(1)
        valid_spy.assert_called_once_with(True)

    def test_selecting_current_index(self, 
                                   mocker,
                                   file_consumer_node_file: FileConsumerNode):
        """Test selecting the current index."""
        # Arrange
        file_consumer_node_file.enabled = True
        file_producer_node = mocker.Mock()
        file_producer_node.enabled = True
        file_producer_node.valid = False

        file_consumer_node_file.add_producer(file_producer_node)

        selected_index_spy = mocker.Mock()
        valid_spy = mocker.Mock()
        file_consumer_node_file.selected_index_changed.connect(selected_index_spy)
        file_consumer_node_file.valid_changed.connect(valid_spy)

        # Act
        file_consumer_node_file.selected_index = 0

        # Assert
        assert file_consumer_node_file.enabled is True
        assert file_producer_node.enabled is True
        selected_index_spy.assert_called_once_with(0)
        valid_spy.assert_not_called()
    
    def test_selecting_index_out_of_range(self, 
                                   mocker,
                                   file_consumer_node_file: FileConsumerNode):
        """Test selecting an index out of range."""
        # Arrange
        file_consumer_node_file.enabled = True
        file_producer_node = mocker.Mock()
        file_producer_node.enabled = True
        file_producer_node.valid = False

        file_consumer_node_file.add_producer(file_producer_node)

        selected_index_spy = mocker.Mock()
        valid_spy = mocker.Mock()
        file_consumer_node_file.selected_index_changed.connect(selected_index_spy)
        file_consumer_node_file.valid_changed.connect(valid_spy)

        # Act
        with pytest.raises(IndexError):
            file_consumer_node_file.selected_index = 1

        # Assert
        assert file_consumer_node_file.enabled is True
        assert file_producer_node.enabled is False
        selected_index_spy.assert_called_once_with(1) # actually not nice behaviour
        valid_spy.assert_not_called()

    def test_set_run_id(self, 
                        mocker,
                        file_consumer_node_file: FileConsumerNode):
        """Test run_id setter."""
        # Arrange
        run_id = "1234"
        file_producer_node1 = mocker.Mock()
        file_producer_node1.enabled = True
        file_producer_node1.valid = False
        file_producer_node2 = mocker.Mock()
        file_producer_node2.enabled = False
        file_producer_node2.valid = False

        file_consumer_node_file.add_producer(file_producer_node1)
        file_consumer_node_file.add_producer(file_producer_node2)

        # Act
        file_consumer_node_file.run_id = run_id

        # Assert
        assert file_producer_node1.run_id == run_id
        assert file_producer_node2.run_id == run_id

    def test_set_base_directory_path(self, 
                        mocker,
                        file_consumer_node_file: FileConsumerNode):
        """Test base_directory_path setter."""
        # Arrange
        base_directory_path = "/path/to/base/directory"
        file_producer_node1 = mocker.Mock()
        file_producer_node1.enabled = True
        file_producer_node1.valid = False
        file_producer_node2 = mocker.Mock()
        file_producer_node2.enabled = False
        file_producer_node2.valid = False

        file_consumer_node_file.add_producer(file_producer_node1)
        file_consumer_node_file.add_producer(file_producer_node2)

        # Act
        file_consumer_node_file.base_directory_path = base_directory_path

        # Assert
        assert file_producer_node1.base_directory_path == base_directory_path
        assert file_producer_node2.base_directory_path == base_directory_path
        
    def test_set_enabled(self, 
                         mocker,
                         file_consumer_node_file: FileConsumerNode):
        """Test enabled setter."""
        # Arrange
        file_consumer_node_file.enabled = True
        file_producer_node1 = mocker.Mock()
        file_producer_node1.enabled = True
        file_producer_node1.valid = False
        file_producer_node2 = mocker.Mock()
        file_producer_node2.enabled = False
        file_producer_node2.valid = False

        file_consumer_node_file.add_producer(file_producer_node1)
        file_consumer_node_file.add_producer(file_producer_node2)

        # Act
        file_consumer_node_file.enabled = False

        # Assert
        assert file_consumer_node_file.enabled is False
        assert file_producer_node1.enabled is False
        assert file_producer_node2.enabled is False

    def test_get_file(self,
                      mocker,
                      file_consumer_node_file: FileConsumerNode):
        """Test file property."""
        # Arrange
        file_path = "/path/to/file"
        file_producer_node = mocker.Mock()
        file_producer_node.enabled = True
        file_producer_node.valid = True
        file_producer_node.file = file_path

        # Assert
        assert file_consumer_node_file.file is None

        file_consumer_node_file.add_producer(file_producer_node)

        # Assert
        assert file_consumer_node_file.file == file_path

    def test_valid(self,
                   mocker,
                   file_consumer_node_file: FileConsumerNode):
        """Test valid property."""
        # Arrange
        file_producer_node = mocker.Mock()
        file_producer_node.enabled = True
        file_producer_node.valid = True

        # Assert
        assert file_consumer_node_file.valid is False

        file_consumer_node_file.add_producer(file_producer_node)

        # Assert
        assert file_consumer_node_file.valid is True

    def test_reset(self,
                   mocker,
                   file_consumer_node_file: FileConsumerNode):
        """Test reset method."""
        # Arrange
        file_producer_node = mocker.Mock()
        file_producer_node.reset = mocker.Mock()

        file_consumer_node_file.add_producer(file_producer_node)

        # Act
        file_consumer_node_file.reset()

        # Assert
        assert file_consumer_node_file.selected_index == 0
        file_producer_node.reset.assert_called_once()

    def test_get_operation_ids(self,
                               mocker,
                               file_consumer_node_file: FileConsumerNode):
        """Test get_operation_ids method."""
        # Arrange
        operation_ids = ["op1", "op2"]
        file_producer_node1 = mocker.Mock()
        file_producer_node1.get_operation_ids = mocker.Mock(return_value=operation_ids)

        # Assert
        assert file_consumer_node_file.get_operation_ids() is None

        # Arrange
        file_consumer_node_file.add_producer(file_producer_node1)

        # Assert
        assert file_consumer_node_file.get_operation_ids() == operation_ids
        file_producer_node1.get_operation_ids.assert_called_once()

    def test_to_cli(self,
                    mocker,
                    file_consumer_node_file: FileConsumerNode):
        """Test to_cli method."""
        # Arrange
        run_id_parameter = mocker.Mock()
        parameters = [mocker.Mock()]
        file_producer_node = mocker.Mock()
        file_producer_node.to_cli = mocker.Mock(return_value=["producer command"])

        # Assert
        assert file_consumer_node_file.to_cli(run_id_parameter, parameters) == []

        file_consumer_node_file.add_producer(file_producer_node)

        # Act
        result = file_consumer_node_file.to_cli(run_id_parameter, parameters)

        # Assert
        assert result == ["producer command"]
        file_producer_node.to_cli.assert_called_once_with(run_id_parameter, parameters)

    def test_to_dict(self,
                     mocker,
                     file_consumer_node_file: FileConsumerNode):
        """Test to_dict method."""
        # Arrange
        producer_dict = {"producer": "data"}
        file_producer_node = mocker.Mock()
        file_producer_node.to_dict = mocker.Mock(return_value=producer_dict)

        # Act
        file_consumer_node_file.add_producer(file_producer_node)
        result = file_consumer_node_file.to_dict()

        # Assert
        assert result == {
            "selected": 0,
            "file_producers": [producer_dict],
        }
        file_producer_node.to_dict.assert_called_once()

    def test_populate_from_dict(self,
                                mocker,
                                file_consumer_node_file: FileConsumerNode):
        """Test populate_from_dict method."""
        # Arrange
        file_producer_node1 = mocker.Mock()
        file_producer_node1.populate_from_dict = mocker.Mock()
        file_producer_node2 = mocker.Mock()
        file_producer_node2.populate_from_dict = mocker.Mock()

        file_consumer_node_file.add_producer(file_producer_node1)
        file_consumer_node_file.add_producer(file_producer_node2)

        values = {
            "selected": 1,
            "file_producers": [
                {"producer": "one"},
                {"producer": "two"},
            ],
        }

        # Act
        file_consumer_node_file.populate_from_dict(values)

        # Assert
        assert file_consumer_node_file.selected_index == 1
        file_producer_node1.populate_from_dict.assert_called_once_with(
            {"producer": "one"}
        )
        file_producer_node2.populate_from_dict.assert_called_once_with(
            {"producer": "two"}
        )

    def test_populate_from_dict_raises_missing_selected(
                                self,
                                file_consumer_node_file: FileConsumerNode):
        """Test populate_from_dict raises when selected is missing."""
        # Arrange
        values = {
            "file_producers": [
                {"producer": "one"},
            ],
        }

        # Act / Assert
        with pytest.raises(ValueError, match="Missing 'selected' in dict."):
            file_consumer_node_file.populate_from_dict(values)

    def test_populate_from_dict_raises_invalid_selected_type(
                                self,
                                file_consumer_node_file: FileConsumerNode):
        """Test populate_from_dict raises when selected is not an int."""
        # Arrange
        values = {
            "selected": "one",
            "file_producers": [
                {"producer": "one"},
            ],
        }

        # Act / Assert
        with pytest.raises(
            ValueError,
            match="Invalid 'selected' in dict: one. Expected int."
        ):
            file_consumer_node_file.populate_from_dict(values)

    def test_populate_from_dict_raises_missing_file_producers(
                                self,
                                file_consumer_node_file: FileConsumerNode):
        """Test populate_from_dict raises when file_producers is missing."""
        # Arrange
        values = {
            "selected": 0,
        }

        # Act / Assert
        with pytest.raises(ValueError, match="Missing 'file_producers' in dict."):
            file_consumer_node_file.populate_from_dict(values)

    def test_populate_from_dict_raises_invalid_file_producers_type(
                                self,
                                file_consumer_node_file: FileConsumerNode):
        """Test populate_from_dict raises when file_producers is not a list."""
        # Arrange
        values = {
            "selected": 0,
            "file_producers": "not-a-list",
        }

        # Act / Assert
        with pytest.raises(
            ValueError,
            match="Invalid 'file_producers' in dict: not-a-list. Expected a list."
        ):
            file_consumer_node_file.populate_from_dict(values)

    def test_populate_from_dict_raises_mismatched_file_producers_length(
                                self,
                                mocker,
                                file_consumer_node_file: FileConsumerNode):
        """Test populate_from_dict raises when producer list length mismatches."""
        # Arrange
        file_producer_node1 = mocker.Mock()
        file_consumer_node_file.add_producer(file_producer_node1)
        values = {
            "selected": 0,
            "file_producers": [
                {"producer": "one"},
                {"producer": "two"},
            ],
        }

        # Act / Assert
        with pytest.raises(ValueError, match="Mismatch in 'file_producers' length."):
            file_consumer_node_file.populate_from_dict(values)

    def test_populate_from_dict_raises_invalid_file_producer_item_type(
                                self,
                                mocker,
                                file_consumer_node_file: FileConsumerNode):
        """Test populate_from_dict raises when a file producer entry is not a dict."""
        # Arrange
        file_producer_node1 = mocker.Mock()
        file_consumer_node_file.add_producer(file_producer_node1)
        values = {
            "selected": 0,
            "file_producers": [
                "not-a-dict",
            ],
        }

        # Act / Assert
        with pytest.raises(
            ValueError,
            match="Invalid item in 'file_producers': not-a-dict. Expected an object."
        ):
            file_consumer_node_file.populate_from_dict(values)


class TestCommonParentDirectoryNode:
    """Tests for CommonParentDirectoryNode class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        pass

    def test_init_values(self):
        """Test CommonParentDirectoryNode initialization."""
        # TODO: Implement this testing class
        # Arrange

        # Act

        # Assert
        pytest.skip()


class TestFilePickerNode:
    """Tests for FilePickerNode class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        pass

    def test_init_values(self):
        """Test FilePickerNode initialization."""
        # TODO: Implement this testing class
        # Arrange

        # Act

        # Assert
        pytest.skip()


class TestOperationNode:
    """Tests for OperationNode class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        pass

    def test_init_values(self):
        """Test OperationNode initialization."""
        # TODO: Implement this testing class
        # Arrange

        # Act

        # Assert
        pytest.skip()


class TestOperationTree:
    """Tests for OperationTree class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        pass

    def test_init_values(self):
        """Test OperationTree initialization."""
        # TODO: Implement this testing class
        # Arrange

        # Act

        # Assert
        pytest.skip()