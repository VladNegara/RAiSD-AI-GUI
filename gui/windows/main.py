from PySide6.QtCore import (
    Slot,
    QDir
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QScrollArea,
    QPushButton,
)

from PySide6.QtGui import (
    QCursor, Qt,
)

from gui.model.settings import app_settings
from gui.model.run_record import RunRecord
from gui.execution.command_executor import CommandExecutor
from gui.windows.run_widget import RunWidget
from gui.windows.history_widget import HistoryWidget
from gui.windows.settings_widget import SettingsWidget
 
class MainWindow(QMainWindow):
    """
    The main window of the RAiSD-AI GUI application.
    """
    def __init__(self):
        """
        Initialize the main window.
        """
        super().__init__()
        app_settings.settings_changed.connect(self._init_main_window)
        self._init_main_window()

    def _init_main_window(self) -> None:
        run_record = RunRecord.from_yaml(app_settings.config_path.absoluteFilePath())
        self._run_record = run_record
        self.command_executor = CommandExecutor(run_record)
        self._setup_ui()

    def _setup_ui(self):
        app_settings.workspace_path_changed.connect(self._set_workspace_path_title)
        self._set_workspace_path_title(app_settings.workspace_path)

        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        central_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Left sidebar
        left_sidebar = QWidget()
        left_sidebar.setObjectName("left_sidebar")
        left_sidebar_layout = QVBoxLayout(left_sidebar)
        central_layout.addWidget(left_sidebar)
        self._setup_left_sidebar(left_sidebar_layout)

        # Main stacked widget
        main_widget = QWidget()
        self.main_widget_layout = QStackedLayout(main_widget)
        central_layout.addWidget(main_widget)
        self._setup_main_widget(self.main_widget_layout)

        for button in self.findChildren(QPushButton):
            button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))


    def _setup_left_sidebar(self, layout: QVBoxLayout):
        layout.setContentsMargins(0,20,0,0)

        logo_widget = QWidget()
        logo_widget.setFixedSize(40, 40)
        logo_widget.setObjectName("logo_widget")
        layout.addWidget(logo_widget)

        # Run Button
        run_button = QPushButton()
        run_button.clicked.connect(self._run_button_clicked)
        run_button.setObjectName("run_button")
        run_button.setProperty("state", "active")
        run_button.setFixedSize(40, 40)
        layout.addWidget(run_button)

        # History Button
        history_button = QPushButton()
        history_button.clicked.connect(self._history_button_clicked)
        history_button.setObjectName("history_button")
        history_button.setFixedSize(40, 40)
        layout.addWidget(history_button)

        # Settings Button
        settings_button = QPushButton()
        settings_button.clicked.connect(self._settings_button_clicked)
        settings_button.setObjectName("settings_button")
        settings_button.setFixedSize(40, 40)
        layout.addWidget(settings_button)

        self._buttons = [
            run_button,
            history_button,
            settings_button
        ]

        layout.addStretch()

    def _set_active_view(self, active_index: int) -> None:
        for i, button in enumerate(self._buttons):
            if i == active_index:
                state = "active"
            else:
                state = "default"
            button.setProperty("state", state)
            button.style().unpolish(button)  # Required to apply styling dynamically
            button.style().polish(button)

    def _setup_main_widget(self, layout: QStackedLayout):
        self.run_widget = RunWidget(self._run_record, self.command_executor)
        self.history_widget = HistoryWidget()
        self.settings_widget = SettingsWidget()
        self.run_widget.run_saved.connect(self.history_widget.add_completed_run)

        layout.addWidget(self.run_widget)
        layout.addWidget(self.history_widget)
        layout.addWidget(self.settings_widget)

    @Slot()
    def _run_button_clicked(self) -> None:
        self.main_widget_layout.setCurrentWidget(self.run_widget)
        self._set_active_view(0)

    @Slot()
    def _history_button_clicked(self) -> None:
        self.history_widget.update_history_time()
        self.main_widget_layout.setCurrentWidget(self.history_widget)
        self._set_active_view(1)

    @Slot()
    def _settings_button_clicked(self) -> None:
        self.main_widget_layout.setCurrentWidget(self.settings_widget)
        self._set_active_view(2)

    def _set_workspace_path_title(self, new_workspace: QDir, max_len: int = 30) -> None:
        """
        Update the window title to reflect the new workspace path.

        Shortens the path if it exceeds a certain length.
        
        :param new_workspace: the new workspace path
        :type new_workspace: QDir

        :param max_len: the maximum length of the path to display
        :type max_len: int
        """
        new_workspace_path = new_workspace.absolutePath()
        if len(new_workspace_path) > max_len:
            self.setWindowTitle(f"RAiSD-AI-GUI - '..{new_workspace_path[-max_len + 2:]}'")
        else:
            self.setWindowTitle(f"RAiSD-AI-GUI - '{new_workspace_path}'")

    