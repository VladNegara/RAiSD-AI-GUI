from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFileSystemModel,
    QTreeView
)

from PySide6.QtCore import (
    QDir
)

from gui.model.parameter_group_list import ParameterGroupList

class ResultsWidget(QWidget):
    """
    The results of a completed execution shown.
    """
    def __init__(self, parameter_group_list: ParameterGroupList):
        """
        Initialize a `ResultsWidget` object.

        :param parameter_group_list: the parameters filled out by 
        the user
        :type parameter_group_list: ParameterGroupList
        """
        super().__init__()
        self._parameter_group_list = parameter_group_list
        layout = QVBoxLayout(self)

        # Summary widget
        results_summary_body = QWidget()
        results_summary_layout = QVBoxLayout(results_summary_body)
        results_summary_layout.addWidget(QLabel("This run was succesfull!"))
        layout.addWidget(results_summary_body)

        # Folder widget
        folder_structure = QFileSystemModel()
        folder_structure.setRootPath(QDir.currentPath())
        folder_widget = QTreeView()
        folder_widget.setModel(folder_structure)
        folder_widget.setRootIndex(folder_structure.index(QDir.currentPath()))
        layout.addWidget(folder_widget)