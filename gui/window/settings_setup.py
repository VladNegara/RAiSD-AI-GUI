from PySide6.QtCore import (
    QObject, 
    QDir,
    QFileInfo,
    Signal,
    Slot
)
from PySide6.QtWidgets import (
    QFileDialog,
    QDialog,
    QLabel,
    QPushButton,
    QDialogButtonBox,
    QComboBox,
    QLineEdit
)

from gui.style import constants
from gui.widgets import VBoxLayout
from gui.model.settings import app_settings


class SettingsSetup():
     
    class SetupDialog(QDialog):
            """
            A dialog for displaying and setting the application settings.
            """

            def __init__(
                    self, 
                    parent=None, 
                    ):
                super().__init__(parent)
                self.setWindowTitle("Complete setup")
                self.setModal(True)
                self.resize(400, 300)
                
                layout = VBoxLayout(self, spacing=constants.GAP_TINY)

                # workspace
                workspace_header = QLabel("Select workspace")
                layout.addWidget(workspace_header)

                self._file_browse = QPushButton('Browse')
                self._file_browse.clicked.connect(lambda _, i=self._file_browse: self._open_file_dialog_folder(i))
                layout.addWidget(self._file_browse)

                self.buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
                self.buttonbox.setCenterButtons(True)
                self.buttonbox.accepted.connect(self._close_clicked)
                layout.addWidget(self.buttonbox)

            @Slot()
            def _close_clicked(self) -> None:
                """
                Close the dialog if a valid workspace path has been selected. 
                """
                if app_settings._workspace_path:
                    self.close()
        
            @Slot(QPushButton)
            def _open_file_dialog_folder(self, button : QPushButton) -> None:
                """
                Helper function that opens the OS file picker. If `multiple`
                is `True`, it uses `getOpenFileNames` to allow for multiple
                file selection. Otherwise, it uses `getOpenFileName` to allow
                only a single file.
                """
                new_path = QFileDialog.getExistingDirectory(
                    None,
                    "Select Directory",
                    "",
                    QFileDialog.Option.ShowDirsOnly
                )
                if not new_path:  # Check for empty string (canceled)
                    return  
                try:
                    app_settings.workspace_path = QDir(new_path)
                    button.setText(new_path)
                except Exception as e:
                    print(f"Error setting workspace: {e}")

    @classmethod
    def initialize_settings(cls) -> None:
        """
        Initialize a settings object by filling it.
        """
        app_settings.from_yaml(app_settings.settings_file_path)
        if not app_settings._workspace_path:
            dialog = cls.SetupDialog()
            dialog.exec()
            
            if app_settings._workspace_path:
                print(f"Workspace path set to: {app_settings._workspace_path.absolutePath()}")
            else:
                app_settings.workspace_path = QDir("./")
                if app_settings._workspace_path:
                    print(f"No workspace path selected. Using default workspace path: {app_settings._workspace_path.absolutePath()}")
