"""
A module defining the widgets that allow the user to visualize and
interact with an operation tree.

Other modules only need to import `OperationTreeWidget`.
"""

from PySide6.QtCore import (
    Qt,
    Slot,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QPushButton,
    QRadioButton,
    QWidget,
)

from gui.model.settings import app_settings
from gui.model.operation import (
    FileProducerNode,
    FileConsumerNode,
    CommonParentDirectoryNode,
    FilePickerNode,
    OperationNode,
    OperationTree,
    SingleFile,
    Directory,
)
from gui.components.label import (
    InfoLabel,
)
from gui.widgets import (
    HBoxLayout,
    ResizableStackedWidget,
    StylableWidget,
    VBoxLayout,
)
from gui.components.parameter import ParameterWidget
from gui.style import constants


class FileProducerNodeWidget(StylableWidget):
    """
    An abstract widget class to display a `FileProducerNode`.

    Use the `from_file_producer` class method to construct the suitable
    widget for a `FileProducerNode` instance based on its class.
    """

    @classmethod
    def from_file_producer(
            cls,
            file_producer: FileProducerNode
    ) -> "FileProducerNodeWidget":
        """
        Construct the suitable widget for a file producer node.

        :param file_producer: the file producer node
        :type file_producer: FileProducerNode
        """
        match file_producer:
            case FilePickerNode():
                return FilePickerNodeWidget(file_producer)
            case OperationNode():
                return OperationNodeWidget(file_producer)
            case CommonParentDirectoryNode():
                return CommonParentDirectoryNodeWidget(file_producer)
            case _:
                raise NotImplementedError(
                    "Cannot create widget for unknown file producer node."
                )

    @property
    def button_text(self) -> str:
        """
        The text to be displayed on the button that selects this widget.
        """
        raise NotImplementedError()
    
    def reset(self) -> None:
        raise NotImplementedError()


class FileConsumerNodeWidget(StylableWidget):
    """
    A widget to display a `FileConsumerNode`.

    The widget explains to the user what purpose a file is needed for,
    and presents the options for obtaining that file, i.e. the child
    `FileProducerNode`s. If there are multiple such options, the user
    can select one of them by a menu of radio buttons. The widget for
    the currently selected option is displayed.
    """

    def __init__(self, file_consumer_node: FileConsumerNode):
        """
        Initialize a `FileConsumerNodeWidget` object.

        :param file_consumer_node: the file consumer node to display
        :type file_consumer_node: FileConsumerNode
        """
        super().__init__()
        self.setObjectName("file_consumer_node")
        self._file_consumer_node = file_consumer_node

        layout = VBoxLayout(
            self,
            left=constants.GAP_SMALL,
            top=constants.GAP_TINY,
            bottom=constants.GAP_TINY,
            spacing=constants.GAP_TINY,
        )

        if self._file_consumer_node.label:
            heading = QLabel(self._file_consumer_node.label)
            layout.addWidget(heading)
            heading.setObjectName("heading")

        self.file_producer_widget = ResizableStackedWidget()
        self.file_selectors : list[tuple[QRadioButton | None, FileProducerNodeWidget]] = []
        if len(self._file_consumer_node.producers) == 1:
            # There is only one way to produce the required file, so
            # simply display that to the user.
            producer = self._file_consumer_node.producers[0]
            producer_widget = FileProducerNodeWidget.from_file_producer(
                producer,
            )
            self.file_producer_widget.addWidget(producer_widget)
            self.file_selectors.append((None, producer_widget))
        else:
            # There are multiple options for obtaining the file, so
            # present the user with a choice through radio buttons.
            button_widget = QWidget()
            button_layout = VBoxLayout(button_widget)

            button_heading = QLabel(
                "Select how you want to provide this input file or directory:"
            )
            button_heading.setWordWrap(True)
            button_layout.addWidget(button_heading)

            for i, producer in enumerate(self._file_consumer_node.producers):
                producer_widget = FileProducerNodeWidget.from_file_producer(
                    producer,
                    )
                button = QRadioButton(producer_widget.button_text)
                button.setChecked(i == self._file_consumer_node.selected_index)
                button_layout.addWidget(button)

                self.file_producer_widget.addWidget(producer_widget)
                self.file_selectors.append((button, producer_widget))

                button.clicked.connect(lambda _, i=i: self._button_clicked(i))
            layout.addWidget(button_widget)
        layout.addWidget(self.file_producer_widget)

    def _button_clicked(self, i: int) -> None:
        self._file_consumer_node.selected_index = i
        self.file_producer_widget.current_index = i

    def reset(self) -> None:
        self.file_producer_widget.current_index = 0
        for (i, (button, widget)) in enumerate(self.file_selectors):
            if button:
                button.setChecked(i == self._file_consumer_node.selected_index)
            widget.reset()


class CommonParentDirectoryNodeWidget(FileProducerNodeWidget):
    """
    A widget to display a `CommonParentDirectoryNode`.

    The widget displays all files that produce the necessary directory
    in a vertical layout.
    """

    def __init__(self, common_parent_directory: CommonParentDirectoryNode):
        """
        Initialize a `CommonParentDirectoryNodeWidget` object.

        :param common_parent_directory: the common parent directory node to
        display
        :type common_parent_directory: CommonParentDirectoryNode
        """
        super().__init__()
        self.setObjectName("common_parent_directory_node")
        self._common_parent_directory = common_parent_directory

        layout = VBoxLayout(
            self,
            spacing=constants.GAP_SMALL,
        )

        heading = QLabel(
            "You can run the operations below "
            + "to generate the necessary input files:"
        )
        heading.setWordWrap(True)
        layout.addWidget(heading)

        self.widgets : list[FileConsumerNodeWidget]= []
        for file_consumer in self._common_parent_directory.file_consumers:
            file_consumer_widget = FileConsumerNodeWidget(file_consumer)
            layout.addWidget(file_consumer_widget)
            self.widgets.append(file_consumer_widget)

    def reset(self) -> None:
        for widget in self.widgets:
            widget.reset()

    @property
    def button_text(self) -> str:
        return "Run multiple operations to generate the input files."


class FilePickerNodeWidget(FileProducerNodeWidget):
    """
    A widget to display a `FilePickerNode`.

    The widget explains to the user the type of file that is needed, and allows
    the user to browse their files and select a suitable file or directory.
    """

    def __init__(self, file_picker: FilePickerNode):
        """
        Initialize a `FilePickerNodeWidget` object.

        :param file_picker: the file picker node to display
        :type file_picker: FilePickerNode
        """
        super().__init__()
        self._file_picker = file_picker

        layout = VBoxLayout(
            self,
            spacing=constants.GAP_TINY,
        )

        self._is_directory = isinstance(self._file_picker.produces, Directory)
        # TODO: make this code cleaner and more reusable.
        match self._file_picker.produces:
            case SingleFile(formats=[single_format]):
                heading_text = f"Select a {single_format} file."
            case SingleFile(formats=[first_format, *other_formats]):
                # TODO: preserve the order of the formats, maybe.
                heading_text = (
                    f"Select a {", ".join(other_formats)} "
                    + f"or {first_format} file."
                )
            case Directory(
                contents=[
                    SingleFile(
                        formats=[single_format]
                    )
                ]
            ):
                heading_text = (
                    "Select a directory containing " 
                    + f"{single_format} files."
                )
            case Directory(
                contents=[
                    Directory(
                        contents=[
                            SingleFile(
                                formats=[first_format]
                            )
                        ]
                    ),
                    Directory(
                        contents=[
                            SingleFile(
                                formats=[second_format]
                            )
                        ]
                    )
                ]
            ) if first_format == second_format:
                heading_text = (
                    "Select a directory with two subdirectories, each "
                    + f"containing {first_format} files."
                )
            case _:
                heading_text = "Select a file."
        heading = QLabel(heading_text)
        heading.setWordWrap(True)
        layout.addWidget(heading)

        self.button = QPushButton("Browse")
        self.button.setObjectName("file_selector_button")
        self.button.clicked.connect(self._browse_button_clicked) 
        layout.addWidget(self.button)

        self._file_picker.file_changed.connect(self._file_picker_file_changed)

    def reset(self) -> None:
        pass

    @property
    def button_text(self) -> str:
        if self._is_directory:
            return "Choose a directory on your computer."
        return "Choose a file on your computer."

    def _browse_button_clicked(self):
        if self._is_directory:
            new_path = QFileDialog.getExistingDirectory(
                None,
                "Select Directory",
                app_settings.workspace_path.absolutePath(),
                QFileDialog.Option.ShowDirsOnly
            )
        else:
            new_path, _ = QFileDialog.getOpenFileName(
                None,
                "Select File",
                app_settings.workspace_path.absolutePath(),
            )
        if not new_path:  # Check for empty string (canceled)
            return  
        else:
            self._file_picker.file = new_path

    def _file_picker_file_changed(self, new_file: str):
        if new_file == "":
            self.button.setText("Browse")
        else:
            self.button.setText(new_file)


class OperationNodeWidget(FileProducerNodeWidget):
    """
    A widget to display an `OperationNode`.

    The widget displays the name and description of the operation. The
    necessary input files are displayed side by side below.
    """

    output_label_text = "The output of the operation will be stored at: "

    def __init__(self, operation_node: OperationNode):
        """
        Initialize an `OperationNodeWidget` object.

        :param operation_node: the operation node to display
        :type operation_node: OperationNode
        """
        super().__init__()
        self._operation_node = operation_node
        self.setObjectName("operation_node")

        layout = VBoxLayout(
            self,
            spacing=constants.GAP_TINY,
        )

        name = QLabel(operation_node.name)
        name.setObjectName("heading")
        name.setWordWrap(True)
        layout.addWidget(name)

        description = QLabel(operation_node.description)
        description.setWordWrap(True)
        layout.addWidget(description)

        if self._operation_node.parameters:
            parameter_rows_widget = QWidget()
            parameter_rows_layout = VBoxLayout(parameter_rows_widget)

            self.parameter_widgets : list[ParameterWidget] = []
            for parameter in self._operation_node.parameters.values():
                parameter_widget = ParameterWidget.from_parameter(
                    parameter=parameter,
                    editable=True,
                )
                self.parameter_widgets.append(parameter_widget)
                parameter_row = parameter_widget.build_form_row()
                parameter_rows_layout.addWidget(parameter_row)
            layout.addWidget(parameter_rows_widget)

        self._output_info_label = InfoLabel(
            self.output_label_text + self._operation_node.file
        )
        layout.addWidget(self._output_info_label)

        input_files_widget = QWidget()
        input_files_layout = HBoxLayout(
            input_files_widget,
            spacing=constants.GAP_MEDIUM,
        )

        self.file_consumer_widgets: list[FileConsumerNodeWidget] = []
        for file_consumer in operation_node.file_consumers:
            file_consumer_widget = FileConsumerNodeWidget(file_consumer)
            self.file_consumer_widgets.append(file_consumer_widget)
            input_files_layout.addWidget(
                file_consumer_widget,
                alignment=Qt.AlignmentFlag.AlignTop,
                stretch=1,
            )
        layout.addWidget(input_files_widget)

        self._operation_node.file_changed.connect(self._file_changed)

    def reset(self) -> None:
        for widget in self.parameter_widgets:
            widget.parameter.reset_value()
        for file_consumer in self.file_consumer_widgets:
            file_consumer.reset()

    @property
    def button_text(self) -> str:
        return (
            f"Run {self._operation_node.name} to generate the input file or "
            + "directory."
        )

    @Slot(str)
    def _file_changed(self, new_file: str) -> None:
        self._output_info_label.text = self.output_label_text + new_file


class OperationTreeWidget(StylableWidget):
    """
    A widget to display an `OperationTree`.

    A widget is created for the root operation, which hierarchically
    creates widgets for the other nodes in the tree.
    """

    def __init__(self, operation_tree: OperationTree):
        """
        Initialize an `OperationTreeWidget` object.

        :param operation_tree: the operation tree to display
        :type operation_tree: OperationTree
        """
        super().__init__()
        self.setObjectName("operation_tree")
        self._operation_tree = operation_tree

        layout = HBoxLayout(
            self,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_SMALL,
        )

        self.body = OperationNodeWidget(self._operation_tree.root)
        layout.addWidget(
            self.body,
            alignment=Qt.AlignmentFlag.AlignTop,
        )

    def reset(self) -> None:
        self.body.reset()
