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
)

from .run_page_tab import RunPageTab
from gui.model.run_record import RunRecord
from gui.widgets import (
    VBoxLayout,
)
from gui.components.results import ResultsWidget
from gui.components.navigation_buttons_holder import NavigationButtonsHolder
from gui.style import constants


class ResultsTab(RunPageTab):
    """
    A tab to display the results of a run, and to allow the user
    to start a new run or edit the current run.
    """
    navigate_back = Signal()
    new_run = Signal()
    edit_run = Signal()
    
    def __init__(self, run_record: RunRecord):
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("run_results_widget")
        layout = VBoxLayout(
            widget,
            spacing=constants.GAP_MEDIUM,
        )

        self.title_label = QLabel("Run Results")
        self.title_label.setProperty("title", "true")
        layout.addWidget(self.title_label)

        self.results_widget = ResultsWidget(self._run_record)

        results_scroll = QScrollArea()
        results_scroll.setObjectName("results_scroll")
        results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        results_scroll.setWidgetResizable(True)
        results_scroll.setWidget(self.results_widget )
        layout.addWidget(results_scroll, 1)
        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        self.back_to_view_button = QPushButton("Back to Run")
        self.back_to_view_button.clicked.connect(self.navigate_back.emit)
        self.new_run_button = QPushButton("New Run")
        self.new_run_button.clicked.connect(self.new_run.emit)
        self.edit_run_button = QPushButton("Edit Run")
        self.edit_run_button.clicked.connect(self.edit_run.emit)

        return NavigationButtonsHolder(left_button=self.back_to_view_button, right_button=self.new_run_button, middle_button=self.edit_run_button)

    def refresh(self) -> None:
        pass

    def reset(self) -> None:
        pass

    @Slot(bool)
    def run_ended(self, run_successful: bool) -> None:
        if (run_successful):
            self.title_label.setText("Run Results (Successful)")
        else:  
            self.title_label.setText("Run Results (FAILED - Not saved in History)")
        self.results_widget.show_results()
