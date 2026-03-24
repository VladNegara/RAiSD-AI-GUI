from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFileSystemModel,
    QTreeView,
    QHeaderView,
    QPushButton,
    QStyleOption,
    QStyle
)

from PySide6.QtCore import (
    QDir,
    Slot,
    QUrl
)

from PySide6.QtGui import QDesktopServices, QPainter


from gui.model.settings import app_settings
from gui.model.parameter_group_list import ParameterGroupList
from gui.widgets.parameter_form import ParameterForm
from gui.widgets.collapsible import Collapsible
from gui.model.run_result import RunResult

class ResultsWidget(QWidget):
    """
    The results of a completed execution shown.
    """
    def __init__(self, run_result: RunResult):
        """
        Initialize a `ResultsWidget` object.

        :param run_result: the result to display
        :type run_result: RunResult
        """
        super().__init__()
        self._run_result = run_result
        self.setObjectName('results_widget')
        layout = QVBoxLayout(self)

        # Summary widget
        results_summary_body = QWidget()
        results_summary_layout = QVBoxLayout(results_summary_body)
        self.status_label = QLabel()
        results_summary_layout.addWidget(self.status_label)
        layout.addWidget(results_summary_body)
        info__files_widget = QWidget()
        self.info_files_layout = QVBoxLayout(info__files_widget)
        layout.addWidget(info__files_widget)

        # Folder widget
        files_widget = QWidget()
        files_layout = QVBoxLayout(files_widget)
        files_label = QLabel("Files in the generated directory")
        files_layout.addWidget(files_label)
        self.folder_structure = QFileSystemModel()
        self.folder_widget = QTreeView()
        self.folder_widget.setObjectName("folder_widget")
        self.folder_widget.doubleClicked.connect(self._on_double_click)
        files_layout.addWidget(self.folder_widget)
        layout.addWidget(files_widget, 1)

        # Parameter widget
        parameters_header = QLabel("Parameters used")
        parameter_form = ParameterForm(self._run_result.parameter_group_list, editable=False)
        parameters_collapsible = Collapsible(parameters_header, parameter_form)
        layout.addWidget(parameters_collapsible)

    def show_results(self) -> None:
        """
        Updates the ResultWidget with results in the RunResult.
        """
        # Update summary widgets
        self.status_label.setText("This run was completed successfully. For more information, see the info files below.")

        info_files = [] # TODO implement infofile gen logic
        for file in info_files:
            button = QPushButton(file)
            button.setObjectName("file_button")
            path = self._run_result.path.absoluteFilePath(file)
            button.clicked.connect(lambda _, p=path: self.open_file(p))
            self.info_files_layout.addWidget(button)

        # Set folder widget to right folder
        path = app_settings.workspace_path.filePath(self._run_result.name)
        self.folder_structure.setRootPath(path)
        self.folder_widget.setModel(self.folder_structure)
        self.folder_widget.setRootIndex(self.folder_structure.index(path))
        self.folder_widget.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def open_file(self, path) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    @Slot(int)
    def _on_double_click(self, index) -> None:
        if not self.folder_structure.isDir(index):
            path = self.folder_structure.filePath(index)
            self.open_file(path)

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)