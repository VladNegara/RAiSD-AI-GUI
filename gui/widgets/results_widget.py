from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFileSystemModel,
    QTreeView,
    QHeaderView
)

from PySide6.QtCore import (
    QDir,
    Slot,
    QUrl
)

from PySide6.QtGui import QDesktopServices

import subprocess

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

        :param parameter_group_list: the parameters filled out by 
        the user
        :type parameter_group_list: ParameterGroupList
        """
        super().__init__()
        self._run_result = run_result
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
        self.folder_structure = QFileSystemModel()
        self.folder_widget = QTreeView()
        self.folder_widget.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self.folder_widget, 1)

        # Parameter widget
        parameters_header = QLabel("Parameters used")
        parameter_form = ParameterForm(self._run_result.parameter_group_list)
        parameters_collapsible = Collapsible(parameters_header, parameter_form)
        layout.addWidget(parameters_collapsible)

    def show_results(self) -> None:
        # Update summary widgets
        self.status_label.setText("This run was completed successfully. For more information, see the info files below.")
        for file in self._run_result.info_files:
            self.info_files_layout.addWidget(QLabel(file))

        # Set folder widget to right folder
        self.folder_structure.setRootPath(QDir.currentPath())
        self.folder_widget.setModel(self.folder_structure)
        self.folder_widget.setRootIndex(self.folder_structure.index(QDir.currentPath()))
        self.folder_widget.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    @Slot(int)
    def _on_double_click(self, index) -> None:
        if not self.folder_structure.isDir(index):
            path = self.folder_structure.filePath(index)
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))