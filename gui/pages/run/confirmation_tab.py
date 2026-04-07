from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
)
from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QPushButton,
    QLabel,
    QListWidget,
    QAbstractItemView,
)
from PySide6.QtGui import (
    QGuiApplication,
)

from .run_page_tab import RunPageTab
from gui.model.settings import app_settings
from gui.model.run_record import RunRecord
from gui.widgets import (
    HBoxLayout,
    VBoxLayout,
)
from gui.components.parameter import ParameterForm
from gui.components.dialog import ErrorDialog
from gui.style import constants
from gui.components.navigation_buttons_holder import NavigationButtonsHolder


class ConfirmationTab(RunPageTab):
    """
    A tab to confirm the parameters and operations 
    selected by the user, and to start the run.
    """
    navigate_back = Signal()
    start_run = Signal()

    def __init__(self, run_record: RunRecord):
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        """
        Set up a ConfirmationTab, including a header,
        a section for the commands to be run, and the ParameterForm,
        in locked form.
        """
        widget = QWidget()
        widget.setObjectName("parameter_confirmation_widget")
        layout = VBoxLayout(
            widget,
            spacing=constants.GAP_MEDIUM,
        )

        # Header
        title_label = QLabel("Parameter Confirmation")
        title_label.setProperty("title", "true")
        layout.addWidget(title_label)

        # Commands
        commands_widget = QWidget()
        commands_layout = VBoxLayout(
            commands_widget,
            spacing=constants.GAP_TINY,
        )

        commands_header = QWidget()
        commands_header_layout = HBoxLayout(commands_header)

        commands_label = QLabel("Commands generated from the input:")
        commands_header_layout.addWidget(commands_label, 1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_all)
        commands_header_layout.addWidget(copy_button)
        commands_layout.addWidget(commands_header)

        self.commands_view = QListWidget()
        self.commands_view.setObjectName("commands_view")
        self.commands_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.commands_view.clicked.connect(self._copy_command)
        commands_layout.addWidget(self.commands_view)
        layout.addWidget(commands_widget)

        # Parameters
        parameter_form = ParameterForm(self._run_record, editable=False)
        parameter_form.setObjectName("parameter_form")

        parameter_form_scroll = QScrollArea()
        parameter_form_scroll.setObjectName("parameter_form_scroll")
        parameter_form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        parameter_form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        parameter_form_scroll.setWidgetResizable(True)
        parameter_form_scroll.setWidget(parameter_form)
        layout.addWidget(parameter_form_scroll, 1)

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.navigate_back.emit)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._run_button_clicked)

        return NavigationButtonsHolder(left_button=self.edit_button, right_button=self.run_button)

    def refresh(self) -> None:
        self.update_commands()

    def reset(self) -> None:
        self.update_commands()

    def update_commands(self) -> None:
        """
        Updates the ParameterConfirmationWidget with the commands from
        the RunResult.
        """
        self.commands_view.clear()
        if self._run_record.to_cli():
            self.commands_view.addItems([app_settings.executable_file_path.absoluteFilePath() + " " + command for command in self._run_record.to_cli()])
            self.commands_view.setMaximumHeight(self.commands_view.sizeHintForRow(0)*(self.commands_view.count()+1))

    @Slot(int)
    def _copy_command(self, index) -> None:
        """
        Copies a singular command from the QTreeWidget to the clipboard.
        """
        command = self.commands_view.itemFromIndex(index).text()
        cb = QGuiApplication.clipboard()
        cb.setText(command)

    @Slot()
    def _copy_all(self) -> None:
        """
        Copies all commands from the run result to the clipboard.
        """
        if self._run_record.to_cli():
            string = '; '.join(self._run_record.to_cli())
            cb = QGuiApplication.clipboard()
            cb.setText(string)

    @Slot()
    def _run_button_clicked(self) -> None:
        if self._run_record.valid:
            self.start_run.emit()
        else:
            dialog = ErrorDialog(self, "Invalid input", "Input parameters are invalid")
            dialog.exec()
        pass

    @Slot()
    def run_started(self) -> None:
        self.run_button.setEnabled(False)
        self.run_button.setText("Running")

    @Slot()
    def run_ended(self) -> None:
        self.run_button.setEnabled(True)
        self.run_button.setText("Run")

