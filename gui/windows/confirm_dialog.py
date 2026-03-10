from PySide6.QtWidgets import (
    QWidget,
    QDialog, 
    QDialogButtonBox, 
    QLabel, 
    QVBoxLayout,
)

class ConfirmDialog(QDialog):
    """
    A simple confirmation dialog that asks the user to confirm an action.
    """
    def __init__(self, parent:QWidget, title:str, function:str):
        """
        Initializes the ConfirmDialog.

        Write function like a git commit
        
        :param parent: the parent of the dialog
        :type parent: Qwidget

        :param title: the title of the dialog
        :type title: str

        :param function: the function of the dialog
        :type function: str
        """
        super().__init__(parent)

        self.setWindowTitle(title)

        QBtn = (
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(f"You are about to {function}. Are you sure?")
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)