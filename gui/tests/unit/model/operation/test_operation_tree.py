from pathlib import Path

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

from gui.model.operation.operation_tree import CommonParentDirectoryNode
from gui.model.parameter.parameter import BoolParameter
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

    def test_add_producer(
            self,
            file_consumer_node_file:FileConsumerNode, 
            file_producer_node:FileProducerNode
        ):
        """Test the add_producer method with an arbitrary file_producer_node."""
        # Act
        file_consumer_node_file.add_producer(file_producer_node)

        # Assert
        assert file_consumer_node_file.producers == [file_producer_node]

        # Act
        file_consumer_node_file.add_producer(file_producer_node)

        # Assert
        assert file_consumer_node_file.producers == [file_producer_node, file_producer_node]

    def test_producer_valid_changed(
            self,
            mocker,
            file_consumer_node_file:FileConsumerNode, 
            file_producer_node:FileProducerNode
        ):
        """Test the connection between valid changed of producer and consumer."""
        # Arrange
        mock_valid_changed = mocker.Mock()
        file_consumer_node_file.valid_changed.connect(mock_valid_changed)

        mock_signal = MockSignal()
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

    def test_selected_index_setter(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_selecting_current_index(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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
    
    def test_selecting_index_out_of_range(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_set_run_id(
            self, 
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_set_base_directory_path(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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
        
    def test_set_enabled(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_get_file(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_valid(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_reset(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_get_operation_ids(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_to_cli(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_to_dict(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    def test_populate_from_dict(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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
            file_consumer_node_file: FileConsumerNode
        ):
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
            file_consumer_node_file: FileConsumerNode
        ):
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
            file_consumer_node_file: FileConsumerNode
        ):
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
            file_consumer_node_file: FileConsumerNode
        ):
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
            file_consumer_node_file: FileConsumerNode
        ):
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
        with pytest.raises(
            ValueError, 
            match="Mismatch in 'file_producers' length: 2 in dict vs 1 in node."
            ):
            file_consumer_node_file.populate_from_dict(values)

    def test_populate_from_dict_raises_invalid_file_producer_item_type(
            self,
            mocker,
            file_consumer_node_file: FileConsumerNode
        ):
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

    @pytest.fixture()
    def common_parent_directory_node(self, mocker):
        file_structure1 = SingleFile([".png"])
        file_structure2 = SingleFile([".jpg"])
        produces = Directory([file_structure1, file_structure2])
        overwrite_parameter = mocker.Mock(spec=BoolParameter)
        overwrite_parameter_builder = mocker.Mock(return_value=overwrite_parameter)
        enabled = True

        common_parent_directory_node = CommonParentDirectoryNode(
            produces=produces,
            overwrite_parameter_builder=overwrite_parameter_builder,
            enabled=enabled,
        )

        return common_parent_directory_node

    def test_init_values(self, mocker):
        """Test CommonParentDirectoryNode initialization."""
        # Arrange
        file_structure = SingleFile([".png"])
        produces = Directory([file_structure])
        overwrite_parameter = mocker.Mock(spec=BoolParameter)
        overwrite_parameter_builder = mocker.Mock(return_value=overwrite_parameter)
        enabled = True

        # Act
        common_parent_directory_node = CommonParentDirectoryNode(
            produces=produces,
            overwrite_parameter_builder=overwrite_parameter_builder,
            enabled=enabled,
        )

        # Assert
        assert len(common_parent_directory_node.file_consumers) == 1
        assert (common_parent_directory_node.file_consumers[0].requires == file_structure)
        assert common_parent_directory_node.produces == produces
        assert common_parent_directory_node.enabled == enabled
        assert common_parent_directory_node.overwrite_parameter == overwrite_parameter
        overwrite_parameter.add_condition.assert_called_once()
        condition = overwrite_parameter.add_condition.call_args.args[0]
        assert isinstance(condition, FileProducerNode.OverwriteCondition)
        assert condition._file_producer_node == common_parent_directory_node
        assert condition._target_value is True

    def test_consumer_valid_changed(
            self,
            mocker,
            common_parent_directory_node: CommonParentDirectoryNode,
        ):
        """Test the connection between valid changed of producer and consumer."""
        # Arrange
        mock_valid_changed = mocker.Mock()
        common_parent_directory_node.valid_changed.connect(mock_valid_changed)

        # Act
        common_parent_directory_node.file_consumers[0].valid_changed.emit(True)

        # Assert
        mock_valid_changed.assert_called_once_with(True)

    def test_enabled_setter_disables_child_consumers(
            self, 
            mocker, 
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test enabled setter propagates False to child consumers."""
        # Arrange
        file_producer_node1 = mocker.Mock()
        file_producer_node1.enabled = True
        file_producer_node1.valid = True

        file_producer_node2 = mocker.Mock()
        file_producer_node2.enabled = True
        file_producer_node2.valid = True

        common_parent_directory_node.file_consumers[0].add_producer(
            file_producer_node1
        )
        common_parent_directory_node.file_consumers[1].add_producer(
            file_producer_node2
        )

        # Act
        common_parent_directory_node.enabled = False

        # Assert
        assert common_parent_directory_node.enabled is False
        assert common_parent_directory_node.file_consumers[0].enabled is False
        assert common_parent_directory_node.file_consumers[1].enabled is False
        assert file_producer_node1.enabled is False
        assert file_producer_node2.enabled is False

    def test_enabled_setter_enables_child_consumers(
            self, 
            mocker, 
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test enabled setter propagates True to child consumers."""
        
        common_parent_directory_node.enabled = False

        file_producer_node1 = mocker.Mock()
        file_producer_node1.enabled = False
        file_producer_node1.valid = True

        file_producer_node2 = mocker.Mock()
        file_producer_node2.enabled = False
        file_producer_node2.valid = True

        common_parent_directory_node.file_consumers[0].add_producer(
            file_producer_node1
        )
        common_parent_directory_node.file_consumers[1].add_producer(
            file_producer_node2
        )

        common_parent_directory_node.enabled = True

        assert common_parent_directory_node.enabled is True
        assert common_parent_directory_node.file_consumers[0].enabled is True
        assert common_parent_directory_node.file_consumers[1].enabled is True
        assert file_producer_node1.enabled is True
        assert file_producer_node2.enabled is True

    def test_init_no_bool_overwrite_parameter(self, mocker):
        """Test CommonParentDirectoryNode initialization without a bool overwrite parameter."""
        # Arrange
        file_structure = SingleFile([".png"])
        produces = Directory([file_structure])
        overwrite_parameter_builder = mocker.Mock(return_value=None)
        enabled = True

        # Act / Assert
        with pytest.raises(ValueError, 
            match="Invalid overwrite parameter for " \
            "common parent directory node: None. " \
            "Expected a bool parameter."):
            common_parent_directory_node = CommonParentDirectoryNode(
                produces=produces,
                overwrite_parameter_builder=overwrite_parameter_builder,
                enabled=enabled,
            )

    def test_file_returns_none_when_no_child_output_selected(
            self, 
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test the file property returns None when children have no selected output."""
        # Assert
        assert common_parent_directory_node.file is None

    def test_file_returns_common_parent_directory(
            self, 
            mocker, 
            tmp_path, 
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test the file property returns the shared parent directory."""
        # Arrange
        output_dir = tmp_path / "shared"
        output_dir.mkdir(parents=True, exist_ok=True)

        producer1 = mocker.Mock()
        producer1.file = str(output_dir / "image1.png")
        producer1.valid = True
        producer1.valid_changed = mocker.Mock()

        producer2 = mocker.Mock()
        producer2.file = str(output_dir / "image2.jpg")
        producer2.valid = True
        producer2.valid_changed = mocker.Mock()

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)

        # Assert
        assert common_parent_directory_node.file == str(output_dir)

    def test_file_returns_none_when_child_outputs_differ(
            self, 
            mocker, 
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test the file property returns None when child outputs do not share the same directory."""
        # Arrange
        first_dir = tmp_path / "one"
        first_dir.mkdir(parents=True, exist_ok=True)
        second_dir = tmp_path / "two"
        second_dir.mkdir(parents=True, exist_ok=True)

        producer1 = mocker.Mock()
        producer1.file = str(first_dir / "image1.png")
        producer1.valid = True
        producer1.valid_changed = mocker.Mock()

        producer2 = mocker.Mock()
        producer2.file = str(second_dir / "image2.jpg")
        producer2.valid = True
        producer2.valid_changed = mocker.Mock()

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)

        # Assert
        assert common_parent_directory_node.file is None

    def test_watched_files_no_file_selected(
            self,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test watched_files returns an empty list when no file is selected."""
        # Assert
        assert common_parent_directory_node.watched_files == []

    def test_watched_files_file_selected(
            self,
            mocker,
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test watched_files returns the produced directory when available."""
        # Arrange
        output_dir = tmp_path / "shared"
        output_dir.mkdir(parents=True, exist_ok=True)

        producer1 = mocker.Mock()
        producer1.file = str(output_dir / "image1.png")
        producer1.valid = True
        producer1.valid_changed = mocker.Mock()

        producer2 = mocker.Mock()
        producer2.file = str(output_dir / "image2.jpg")
        producer2.valid = True
        producer2.valid_changed = mocker.Mock()

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)

        # Assert
        assert common_parent_directory_node.watched_files == [str(output_dir)]

    def test_overwrite_no_file_selected(
            self,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test overwrite returns False when no produced directory is available."""
        # Assert
        assert common_parent_directory_node.overwrite is False

    def test_overwrite_output_directory_exists(
            self,
            mocker,
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test overwrite returns True when the produced directory exists."""
        # Arrange
        output_dir = tmp_path / "shared"
        output_dir.mkdir(parents=True, exist_ok=True)

        producer1 = mocker.Mock()
        producer1.file = str(output_dir / "image1.png")
        producer1.valid = True
        producer1.valid_changed = mocker.Mock()

        producer2 = mocker.Mock()
        producer2.file = str(output_dir / "image2.jpg")
        producer2.valid = True
        producer2.valid_changed = mocker.Mock()

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)

        # Assert
        assert common_parent_directory_node.overwrite is True

    def test_run_id_setter_no_change(
            self,
            mocker,
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test run_id is propagated to child file consumers."""
        # Arrange
        file_path1 = str(tmp_path / "file1.png")
        file_path2 = str(tmp_path / "file2.jpg")

        file_producer_node1 = mocker.Mock()
        file_producer_node1.file = file_path1
        file_producer_node2 = mocker.Mock()
        file_producer_node2.file = file_path2

        common_parent_directory_node.file_consumers[0].add_producer(file_producer_node1)
        common_parent_directory_node.file_consumers[1].add_producer(file_producer_node2)

        file_changed_spy = mocker.Mock()
        overwrite_changed_spy = mocker.Mock()
        common_parent_directory_node.file_changed.connect(file_changed_spy)
        common_parent_directory_node.overwrite_changed.connect(overwrite_changed_spy)

        # Act
        common_parent_directory_node.run_id = "new_run_id"

        # Assert
        assert file_producer_node1.run_id == "new_run_id"
        assert file_producer_node2.run_id == "new_run_id"
        file_changed_spy.assert_not_called()
        overwrite_changed_spy.assert_not_called()

    def test_run_id_setter_file_and_workspace_changed(
            self,
            mocker,
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test run_id is propagated to child file consumers and triggers path change signals."""
        # Arrange
        old_dir = tmp_path / "old"
        old_dir.mkdir(parents=True, exist_ok=True)

        class PathChangingProducer(FileProducerNode):
            def __init__(self, directory: Path, name):
                super().__init__()
                self._directory = directory
                self._name = name
                self.valid_changed = mocker.Mock()

            @property
            def file(self):
                return str(self._directory / self._name)

            def _get_run_id(self):
                return self._directory.name

            def _set_run_id(self, new_run_id):
                self._directory = self._directory.parent / new_run_id

            run_id = property(_get_run_id, _set_run_id)

        file_producer_node1 = PathChangingProducer(old_dir, "file1.png")
        file_producer_node2 = PathChangingProducer(old_dir, "file2.jpg")

        common_parent_directory_node.file_consumers[0].add_producer(file_producer_node1)
        common_parent_directory_node.file_consumers[1].add_producer(file_producer_node2)

        file_changed_spy = mocker.Mock()
        overwrite_changed_spy = mocker.Mock()
        common_parent_directory_node.file_changed.connect(file_changed_spy)
        common_parent_directory_node.overwrite_changed.connect(overwrite_changed_spy)
    
        # Act
        common_parent_directory_node.run_id = "new_run_id"

        # Assert
        assert file_producer_node1.run_id == "new_run_id"
        assert file_producer_node2.run_id == "new_run_id"
        file_changed_spy.assert_called_once_with(str(tmp_path / "new_run_id"))
        overwrite_changed_spy.assert_called_once_with(False)
    
    def test_base_directory_path_setter_no_change(
            self,
            mocker,
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test base_directory_path is propagated to child file consumers."""
        # Arrange
        file_path1 = str(tmp_path / "file1.png")
        file_path2 = str(tmp_path / "file2.jpg")

        file_producer_node1 = mocker.Mock()
        file_producer_node1.file = file_path1
        file_producer_node2 = mocker.Mock()
        file_producer_node2.file = file_path2

        common_parent_directory_node.file_consumers[0].add_producer(file_producer_node1)
        common_parent_directory_node.file_consumers[1].add_producer(file_producer_node2)

        file_changed_spy = mocker.Mock()
        overwrite_changed_spy = mocker.Mock()
        common_parent_directory_node.file_changed.connect(file_changed_spy)
        common_parent_directory_node.overwrite_changed.connect(overwrite_changed_spy)

        # Act
        common_parent_directory_node.base_directory_path = str(tmp_path / "new_base_directory")

        # Assert
        assert file_producer_node1.base_directory_path == str(tmp_path / "new_base_directory")
        assert file_producer_node2.base_directory_path == str(tmp_path / "new_base_directory")
        file_changed_spy.assert_not_called()
        overwrite_changed_spy.assert_not_called()

    def test_base_directory_path_setter_file_and_workspace_changed(
            self,
            mocker,
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test base_directory_path is propagated to child file consumers and triggers path change signals."""
        # Arrange
        old_dir = tmp_path / "old"
        old_dir.mkdir(parents=True, exist_ok=True)

        class PathChangingProducer(FileProducerNode):
            def __init__(self, directory: Path, name):
                super().__init__()
                self._directory = directory
                self._name = name
                self.valid_changed = mocker.Mock()

            @property
            def file(self):
                return str(self._directory / self._name)

            def _get_base_directory_path(self):
                return str(self._directory)

            def _set_base_directory_path(self, new_base_directory_path):
                self._directory = Path(new_base_directory_path)

            base_directory_path = property(_get_base_directory_path, _set_base_directory_path)

        file_producer_node1 = PathChangingProducer(old_dir, "file1")
        file_producer_node2 = PathChangingProducer(old_dir, "file2")

        common_parent_directory_node.file_consumers[0].add_producer(file_producer_node1)
        common_parent_directory_node.file_consumers[1].add_producer(file_producer_node2)

        file_changed_spy = mocker.Mock()
        overwrite_changed_spy = mocker.Mock()
        common_parent_directory_node.file_changed.connect(file_changed_spy)
        common_parent_directory_node.overwrite_changed.connect(overwrite_changed_spy)
    
        # Act
        common_parent_directory_node.base_directory_path = str(tmp_path / "new_base_directory")

        # Assert
        assert file_producer_node1.base_directory_path == str(tmp_path / "new_base_directory")
        assert file_producer_node2.base_directory_path == str(tmp_path / "new_base_directory")
        file_changed_spy.assert_called_once_with(str(tmp_path / "new_base_directory"))
        overwrite_changed_spy.assert_called_once_with(False)

    def test_valid_consumer_invalid(
            self,
            mocker,
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test valid is False when a child producer is invalid."""
        # Arrange
        output_dir = tmp_path / "shared"

        producer1 = mocker.Mock()
        producer1.file = str(output_dir / "image1.png")
        producer1.valid = False
        producer1.valid_changed = mocker.Mock()

        producer2 = mocker.Mock()
        producer2.file = str(output_dir / "image2.jpg")
        producer2.valid = True
        producer2.valid_changed = mocker.Mock()

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)
        common_parent_directory_node.overwrite_parameter.value = False

        # Assert
        assert common_parent_directory_node.valid is False

    def test_valid_no_file_consumers(
            self,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test valid is False when there are no file consumers."""
        # Arrange
        common_parent_directory_node._file_consumers = []

        # Assert
        assert common_parent_directory_node.valid is False

    def test_valid_overwrite_parameter_true(
            self,
            mocker,
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test valid is True when overwrite parameter is True."""
        # Arrange
        output_dir = tmp_path / "shared"

        producer1 = mocker.Mock()
        producer1.file = str(output_dir / "image1.png")
        producer1.valid = True

        producer2 = mocker.Mock()
        producer2.file = str(output_dir / "image2.jpg")
        producer2.valid = True        
        
        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)
        common_parent_directory_node.overwrite_parameter.value = True

        # Assert
        assert common_parent_directory_node.valid is True

    def test_valid_overwrite_false(
            self,
            mocker,
            tmp_path,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test valid is True when overwrite is False."""
        # Arrange
        output_dir = tmp_path / "shared"

        producer1 = mocker.Mock()
        producer1.file = str(output_dir / "image1.png") # A new file, so no overwrite.
        producer1.valid = True

        producer2 = mocker.Mock()
        producer2.file = str(output_dir / "image2.jpg")
        producer2.valid = True        
        
        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)
        common_parent_directory_node.overwrite_parameter.value = False

        # Assert
        assert common_parent_directory_node.valid is True

    def test_reset(
            self,
            mocker,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test reset method."""
        # Arrange
        file_producer_node = mocker.Mock()
        file_producer_node.reset = mocker.Mock()
        
        common_parent_directory_node.file_consumers[0].add_producer(file_producer_node)

        # Act
        common_parent_directory_node.reset()

        # Assert
        file_producer_node.reset.assert_called_once()
    
    def test_get_operation_ids_aggregates_child_operation_ids(
            self,
            mocker,
            common_parent_directory_node: CommonParentDirectoryNode):
        """Test get_operation_ids returns operation ids from all child producers."""
        # Arrange
        producer1 = mocker.Mock()
        producer1.get_operation_ids.return_value = ["file1"]
        producer1.valid_changed = mocker.Mock()

        producer2 = mocker.Mock()
        producer2.get_operation_ids.return_value = ["file2"]
        producer2.valid_changed = mocker.Mock()

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)

        # Act
        operation_ids = common_parent_directory_node.get_operation_ids()

        # Assert
        assert operation_ids == ["file1", "file2"]
    
    def test_to_cli(
            self,
            mocker,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test to_cli method."""
        # Arrange
        run_id_parameter = mocker.Mock()
        parameters = [mocker.Mock()]

        producer1 = mocker.Mock()
        producer1.to_cli = mocker.Mock(return_value=["producer1 command"])

        producer2 = mocker.Mock()
        producer2.to_cli = mocker.Mock(return_value=["producer2 command"])

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)
        common_parent_directory_node.overwrite_parameter.to_cli = mocker.Mock(
            return_value="overwrite command"
        )

        # Act
        result = common_parent_directory_node.to_cli(run_id_parameter, parameters)

        # Assert
        assert result == ["producer1 command overwrite command", "producer2 command"]
        producer1.to_cli.assert_called_once_with(run_id_parameter, parameters)
        producer2.to_cli.assert_called_once_with(run_id_parameter, parameters)

    def test_to_dict(
            self,
            mocker,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test to_dict method."""
        # Arrange
        producer_dict1 = {"producer1": "data"}
        producer_dict2 = {"producer2": "data"}
        
        producer1 = mocker.Mock()
        producer1.to_dict = mocker.Mock(return_value=producer_dict1)

        producer2 = mocker.Mock()
        producer2.to_dict = mocker.Mock(return_value=producer_dict2)

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)

        # Act
        result = common_parent_directory_node.to_dict()

        # Assert
        assert result == {
            'file_consumers': [
                {
                    'file_producers': [
                        {'producer1': 'data'}
                    ], 
                    'selected': 0
                }, 
                {
                    'file_producers': [
                        {'producer2': 'data'}
                    ], 
                    'selected': 0
                }
            ]
        }

    def test_populate_from_dict(
            self,
            mocker,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test the populate_from_dict method."""
        # Arrange
        dict_data = {
            'file_consumers': [
                {
                    'file_producers': [
                        {'producer1': 'data'}
                    ],
                    'selected': 0
                },
                {
                    'file_producers': [
                        {'producer2': 'data'}
                    ],
                    'selected': 0
                }
            ]
        }

        producer1 = mocker.Mock()
        producer1.populate_from_dict = mocker.Mock()

        producer2 = mocker.Mock()
        producer2.populate_from_dict = mocker.Mock()

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[1].add_producer(producer2)

        # Act
        common_parent_directory_node.populate_from_dict(dict_data)

        # Assert
        assert len(common_parent_directory_node.file_consumers) == 2
        file_producer_node1 = common_parent_directory_node.file_consumers[0]._producers[0]
        file_producer_node2 = common_parent_directory_node.file_consumers[1]._producers[0]
        file_producer_node1.populate_from_dict.assert_called_once_with({'producer1': 'data'})
        file_producer_node2.populate_from_dict.assert_called_once_with({'producer2': 'data'})

    def test_populate_from_dict_raises_missing_file_consumers(
            self,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test populate_from_dict raises when file_consumers is missing."""
        # Arrange
        dict_data = {}

        # Act / Assert
        with pytest.raises(ValueError, match="Missing 'file_consumers' key in dict."):
            common_parent_directory_node.populate_from_dict(dict_data)

    def test_populate_from_dict_raises_invalid_file_consumers_type(
            self,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test populate_from_dict raises when file_consumers is not a list."""
        # Arrange
        dict_data = {
            'file_consumers': "not-a-list"
        }

        # Act / Assert
        with pytest.raises(ValueError, match="Invalid 'file_consumers' in dict: not-a-list. Expected a list."):
            common_parent_directory_node.populate_from_dict(dict_data)

    def test_populate_from_dict_raises_mismatched_file_consumers_length(
            self,
            mocker,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test populate_from_dict raises when file_consumers list length mismatches."""
        # Arrange
        dict_data = {
            'file_consumers': [
                {
                    'file_producers': [
                        {'producer1': 'data'}
                    ],
                    'selected': 0
                },
            ]
        }

        producer1 = mocker.Mock()
        producer1.populate_from_dict = mocker.Mock()

        producer2 = mocker.Mock()
        producer2.populate_from_dict = mocker.Mock()

        common_parent_directory_node.file_consumers[0].add_producer(producer1)
        common_parent_directory_node.file_consumers[0].add_producer(producer2)

        # Act / Assert
        with pytest.raises(
            ValueError, 
            match="Mismatch in 'file_consumers' length: 1 in dict vs 2 in node."
            ):
            common_parent_directory_node.populate_from_dict(dict_data)

    def test_populate_from_dict_raises_invalid_file_consumer_item_type(
            self,
            mocker,
            common_parent_directory_node: CommonParentDirectoryNode
        ):
        """Test populate_from_dict raises when a file consumer entry is not a dict."""
        # Arrange
        dict_data = {
            'file_consumers': [
                "not-a-dict",
            ]
        }

        producer1 = mocker.Mock()
        producer1.populate_from_dict = mocker.Mock()

        common_parent_directory_node._file_consumers = [
            common_parent_directory_node.file_consumers[0]
        ]
        common_parent_directory_node.file_consumers[0].add_producer(producer1)

        # Act / Assert
        with pytest.raises(
            ValueError,
            match="Invalid item in 'file_consumers': not-a-dict. Expected a dict."
        ):
            common_parent_directory_node.populate_from_dict(dict_data)



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