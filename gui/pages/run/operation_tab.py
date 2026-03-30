from PySide6.QtCore import (
    Qt,
    Slot,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QRadioButton,
    QPushButton,
    QLabel,
)

from .run_page_tab import RunPageTab, NavigationButtonsHolder
from gui.model.run_record import RunRecord
from gui.widgets.operation import OperationTreeWidget
from gui.widgets.resizable_stacked_widget import ResizableStackedWidget
from gui.widgets.parameter import ParameterWidget


class OperationTab(RunPageTab):
    """
    A tab that allows the user to choose a run id and
    to select operations to be run.
    """

    def __init__(self, run_record: RunRecord):
        
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("operation_selection_widget")
        layout = QVBoxLayout(widget)

        operation_selection_label = QLabel("Operation Selection")
        operation_selection_label.setObjectName("operation_selection_label")
        layout.addWidget(operation_selection_label)

        run_id_parameter_widget = ParameterWidget.from_parameter(
            self._run_record.run_id_parameter,
            editable=True,
        )
        run_id_widget = run_id_parameter_widget.build_form_row()
        layout.addWidget(run_id_widget)

        self.operation_selector = self.__class__.OperationSelector(
            self._run_record
        )
        layout.addWidget(self.operation_selector, stretch=1000)

        layout.addStretch(1)

        # Show operation selector only if run ID is valid
        self.operation_selector.setVisible(
            self._run_record.run_id_valid,
        )
        self._run_record.run_id_valid_changed.connect(
            self._run_id_valid_changed,
        )

        return widget
    
    def reset(self) -> None:
        self.operation_selector.reset()

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("next_button")
        self._update_next_button_state()
        self._run_record.run_id_valid_changed.connect(
            self._update_next_button_state,
        )
        self._run_record.operations_valid_changed.connect(
            self._update_next_button_state,
        )
        return NavigationButtonsHolder(right_button=self.next_button)

    
    class OperationSelector(QWidget):
        def __init__(self, run_record: RunRecord):
            super().__init__()

            self._run_record = run_record

            layout = QHBoxLayout(self)

            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)

            tree_scroll = QScrollArea()
            tree_scroll.setObjectName("tree_scroll")
            tree_scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            tree_scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            tree_scroll.setWidgetResizable(True)

            self.tree_stacked_widget = ResizableStackedWidget()
            self.tree_stacked_widget.setObjectName("tree_stacked_widget")
            
            self.tree_selectors : list[tuple[QRadioButton, OperationTreeWidget]]= []
            for i, tree in enumerate(
                    self._run_record.operation_trees
            ):
                self.button = QRadioButton(tree.root.name)
                self.button.setChecked(
                    i
                    == self._run_record.selected_operation_tree_index
                )
                button_layout.addWidget(self.button)

                widget = OperationTreeWidget(tree)
                self.tree_stacked_widget.addWidget(widget)

                self.button.clicked.connect(lambda _, i=i: self._button_clicked(i))
                self.tree_selectors.append((self.button, widget))
            tree_scroll.setWidget(self.tree_stacked_widget)

            button_layout.addStretch()

            layout.addWidget(button_widget)
            layout.addWidget(tree_scroll)

        def _button_clicked(self, i: int) -> None:
            self._run_record.selected_operation_tree_index = i
            self.tree_stacked_widget.current_index = i

        def reset(self) -> None:
            self.tree_stacked_widget.current_index = 0
            for i, (button, widget) in enumerate(self.tree_selectors):
                button.setChecked(i == self._run_record.selected_operation_tree_index) 
                widget.reset()

    @Slot()
    def _run_id_valid_changed(self, new_valid) -> None:
        self.operation_selector.setVisible(new_valid)

    @Slot()
    def _update_next_button_state(self) -> None:
        valid = (
            self._run_record.run_id_valid
            and self._run_record.operations_valid
        )
        self.next_button.setEnabled(valid)
        if valid:
            self.next_button.setProperty("highlight", "true")
        else:
            self.next_button.setProperty("highlight", "false")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)