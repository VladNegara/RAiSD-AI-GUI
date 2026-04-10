from PySide6.QtCore import (
    Qt,
    QDir,
    Slot,
    QUrl
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFileSystemModel,
    QTreeView,
    QHeaderView,
)
from PySide6.QtGui import QDesktopServices

from gui.model.settings import app_settings
from gui.model.run_record import RunRecord
from gui.widgets import (
    StylableWidget,
    VBoxLayout,
)
from gui.components.parameter import ParameterForm
from gui.components.collapsible import Collapsible
from gui.style import constants


class ResultsWidget(StylableWidget):
    """
    The results of a completed execution shown.
    """
    def __init__(self, run_record: RunRecord):
        """
        Initialize a `ResultsWidget` object.

        :param run_record: the result to display
        :type run_record: RunResult
        """
        super().__init__()
        self._run_record = run_record
        self.setObjectName('results_widget')
        layout = VBoxLayout(
            self,
            spacing=constants.GAP_TINY,
        )

        # Folder widget
        self.files_widget = QWidget()
        files_layout = VBoxLayout(
            self.files_widget,
            spacing=constants.GAP_TINY,
        )
        self.files_label = QLabel("Files in the generated directory")
        files_layout.addWidget(self.files_label)
        self.folder_structure = QFileSystemModel()
        self.folder_widget = QTreeView()
        self.folder_widget.setObjectName("folder_widget")
        self.folder_widget.doubleClicked.connect(self._on_double_click)
        files_layout.addWidget(self.folder_widget)

        self.no_files_label = QLabel("The output directory does not exist anymore.", alignment=Qt.AlignmentFlag.AlignCenter)
        self.no_files_label.setObjectName("no_files_label")
        self.no_files_label.hide()
        layout.addWidget(self.no_files_label, 1)

        layout.addWidget(self.files_widget, 1)

        # Parameter widget
        try:
            parameters_header = QLabel("Parameters used")
            parameter_form = ParameterForm(self._run_record, editable=False)
            parameters_collapsible = Collapsible(parameters_header, parameter_form)
            layout.addWidget(parameters_collapsible)

    def show_results(self) -> None:
        """
        Updates the ResultWidget with results in the RunRecord.
        """
        # Set folder widget to right folder
        path = app_settings.workspace_path.filePath(self._run_record.run_id)
        if not QDir(path).exists():
            self.files_widget.hide()
            self.no_files_label.show()
        else:
            self.files_label.setText(f"Files in the output directory '{app_settings.workspace_path.dirName()}/{self._run_record.run_id}':")
            self.folder_structure.setRootPath(path)
            self.folder_widget.setModel(self.folder_structure)
            self.folder_widget.setRootIndex(self.folder_structure.index(path))
            self.folder_widget.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.files_widget.show()
            self.no_files_label.hide()

    @Slot(int)
    def _on_double_click(self, index) -> None:
        if not self.folder_structure.isDir(index):
            path = self.folder_structure.filePath(index)
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
