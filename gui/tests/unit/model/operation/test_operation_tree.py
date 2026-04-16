import pytest

from gui.model.operation import (
    FileConsumerNode,
)
from gui.model.operation import Operation
from gui.model.operation.file_structure import SingleFile, Directory


class TestFileConsumerNode:
    """Tests for FileProducerNode class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        pass

    @pytest.fixture()
    def operation_input_file(self) -> Operation.Input:
        name = "Filename"
        description = "This is a file."
        cli = "-f "
        file = SingleFile([])
        operation_input_file =  Operation.Input(name, description, cli, file)
        return operation_input_file

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