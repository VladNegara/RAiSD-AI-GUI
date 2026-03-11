from PySide6.QtWidgets import (
    QWidget,
    QDialog, 
    QMessageBox,
    QDialogButtonBox, 
    QLabel, 
    QVBoxLayout,
)

class ConfirmDialog(QMessageBox):
    """
    A simple confirmation dialog that asks the user to confirm an action.
    """
    def __init__(self, parent: QWidget, title: str, action: str):
        """
        Initialize a `ConfirmDialog` object.

        The `action` should be in the imperative mood.
        
        :param parent: the parent of the dialog
        :type parent: QWidget

        :param title: the title of the dialog
        :type title: str

        :param action: the action of the dialog
        :type action: str
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setText(f"You are about to {action}. Are you sure?")
        self.setIcon(QMessageBox.Icon.Warning)
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        self.setDefaultButton(QMessageBox.StandardButton.Cancel)

class ErrorDialog(QMessageBox):
    """
    A simple dialog that gives the user information about an error.
    """
    def __init__(self, parent:QWidget, title:str, error:str):
        """
        Initialize an `ErrorDialog` object.

        :param parent: the parent of the dialog
        :type parent: QWidget

        :param title: the title of the dialog
        :type title: str

        :param error: the error
        :type error: str
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setText(error)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.setDefaultButton(QMessageBox.StandardButton.Ok)