from PySide6.QtCore import (
    Qt,
    Slot,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QScrollArea,
    QPushButton,
    QLabel,
)

from gui.model.parameter_group_list import ParameterGroupList
from gui.execution.command_executor import CommandExecutor
from gui.windows.run_widget import RunWidget
from gui.windows.history_widget import HistoryWidget
from gui.windows.settings_widget import SettingsWidget

 
class MainWindow(QMainWindow):
    """
    The main window of the RAiSD-AI GUI application.
    """
    def __init__(self, parameter_group_list: ParameterGroupList):
        """
        Initialize the main window.

        :param parameter_group_list: the parameters to be filled in by
        the user
        :type parameter_group_list: ParameterGroupList
        """
        super().__init__()
        self._parameter_group_list = parameter_group_list
        self.command_executor = CommandExecutor()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("RAiSD-AI-GUI")
        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Left sidebar
        left_sidebar = QWidget()
        left_sidebar_layout = QVBoxLayout(left_sidebar)
        central_layout.addWidget(left_sidebar)
        self._setup_left_sidebar(left_sidebar_layout)

        # Main stacked widget
        main_widget = QWidget()
        self.main_widget_layout = QStackedLayout(main_widget)
        central_layout.addWidget(main_widget)
        self._setup_main_widget(self.main_widget_layout)

    def _setup_left_sidebar(self, layout:QVBoxLayout):
        logo_widget = QWidget()
        logo_widget.setFixedSize(40, 40)
        logo_widget.setStyleSheet("background-color: lightgray;")
        layout.addWidget(logo_widget)

        # Run Button
        run_button = QPushButton()
        run_button.clicked.connect(self._run_button_clicked)
        run_button.setStyleSheet("background-color: lightblue;")
        run_button.setFixedSize(40, 40)
        layout.addWidget(run_button)

        # History Button
        history_button = QPushButton()
        history_button.clicked.connect(self._history_button_clicked)
        history_button.setStyleSheet("background-color: lightgreen;")
        history_button.setFixedSize(40, 40)
        layout.addWidget(history_button)

        # Settings Button
        settings_button = QPushButton()
        settings_button.clicked.connect(self._settings_button_clicked)
        settings_button.setStyleSheet("background-color: lightyellow;")
        settings_button.setFixedSize(40, 40)
        layout.addWidget(settings_button)

        layout.addStretch()

    def _setup_main_widget(self, layout:QStackedLayout):
        self.run_widget = RunWidget(self._parameter_group_list, self.command_executor)
        self.history_widget = HistoryWidget()
        self.settings_widget = SettingsWidget()

        layout.addWidget(self.run_widget)
        layout.addWidget(self.history_widget)
        layout.addWidget(self.settings_widget)

    @Slot()
    def _run_button_clicked(self) -> None:
        self.main_widget_layout.setCurrentWidget(self.run_widget)

    @Slot()
    def _history_button_clicked(self) -> None:
        self.main_widget_layout.setCurrentWidget(self.history_widget)

    @Slot()
    def _settings_button_clicked(self) -> None:
        self.main_widget_layout.setCurrentWidget(self.settings_widget)

    

    