import pytest

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
        mock_file_producer_node = mocker.MagicMock()
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
        assert file_consumer_node._description == required_file.description
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