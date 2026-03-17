import datetime as dt
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout


class OperationRecord:
    """
    A record of one single operation with all the necessary attributes
    """
    def __init__(
            self,
            name: str,
            operations: set[str],
            input_files: list[str],
            output_folder: str,
            date: dt.datetime,
            # TODO: parameters
    ) -> None:
        self.name = name
        self.operations = operations
        self.input_files = input_files
        self.output_folder = output_folder
        self.date = date


class HistoryListWidget(QWidget):
    """
    A widget for single operation record to be put in the history_list
    """
    def __init__(self, op_rec: OperationRecord):
        super().__init__()

        layout = QGridLayout(self)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)

        name_label = QLabel(op_rec.name)
        layout.addWidget(name_label, 0, 0, Qt.AlignmentFlag.AlignLeft)

        time_label = QLabel(self._format_time_ago(op_rec.date))
        layout.addWidget(time_label, 0, 1, Qt.AlignmentFlag.AlignRight)

        files_label = QLabel(", ".join(op_rec.input_files))
        files_label.setMaximumWidth(300)
        files_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        files_label.setToolTip("\n".join(op_rec.input_files))
        files_label.setText(files_label.fontMetrics().elidedText(
            ", ".join(op_rec.input_files), Qt.TextElideMode.ElideRight, 300
        ))
        layout.addWidget(files_label, 1, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)

        output_label = QLabel()
        output_label.setMaximumWidth(300)
        output_label.setToolTip(str(op_rec.output_folder))
        output_label.setText(output_label.fontMetrics().elidedText(
            str(op_rec.output_folder), Qt.TextElideMode.ElideRight, 300
        ))
        layout.addWidget(output_label, 2, 0, Qt.AlignmentFlag.AlignLeft)

        operations_widget = QWidget()
        operations_layout = QHBoxLayout(operations_widget)
        operations_layout.setContentsMargins(0, 0, 0, 0)
        operations_layout.setSpacing(0)

        for operation in op_rec.operations:
            icon_widget = QWidget()
            icon_widget.setFixedSize(28, 28)
            icon_widget.setToolTip(operation)
            icon_widget.setObjectName("operation_icon")
            icon_widget.setProperty("operation", operation)
            operations_layout.addWidget(icon_widget)

        operations_layout.addStretch()
        layout.addWidget(operations_widget, 2, 1, Qt.AlignmentFlag.AlignRight)

    @staticmethod
    def _format_time_ago(date: dt.datetime) -> str:

        delta = dt.datetime.now() - date
        total_seconds = int(delta.total_seconds())
        minutes = total_seconds // 60
        hours = minutes // 60
        days = delta.days
        weeks = days // 7
        months = days // 30
        years = days // 365

        if minutes < 60:
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
        elif hours < 24:
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
        elif days < 7:
            return f"{days} {'day' if days == 1 else 'days'} ago"
        elif days < 30:
            return f"{weeks} {'week' if weeks == 1 else 'weeks'} ago"
        elif days < 365:
            return f"{months} {'month' if months == 1 else 'months'} ago"
        else:
            return f"{years} {'year' if years == 1 else 'years'} ago"