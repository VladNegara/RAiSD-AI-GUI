import datetime as dt
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout

from gui.model.settings import app_settings
from gui.model.run_result import RunResult

class HistoryRecordWidget(QWidget):
    """
    A widget for single operation record to be put in the history_list
    """
    def __init__(self, run_result: RunResult):
        super().__init__()
        self._run_result = run_result

        layout = QGridLayout(self)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)

        # top left: the name of the operation record
        name_label = QLabel(self._run_result.name)
        layout.addWidget(name_label, 0, 0, Qt.AlignmentFlag.AlignLeft)

        # top right: indication of the completion time/date
        time_label = QLabel(self._format_time_ago(self._run_result.time_completed))
        layout.addWidget(time_label, 0, 1, Qt.AlignmentFlag.AlignRight)

        # # middle (from left to right): input files with commas in between with elided text functionality
        # files_label = QLabel(", ".join(run_result.input_files))
        # files_label.setMaximumWidth(400)
        # files_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        # files_label.setToolTip("\n".join(run_result.input_files))
        # files_label.setText(files_label.fontMetrics().elidedText(
        #     ", ".join(run_result.input_files), Qt.TextElideMode.ElideRight, 400
        # ))
        # layout.addWidget(files_label, 1, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)

        # # bottom left: output folder with elided text functionality
        # output_label = QLabel()
        # output_label.setMaximumWidth(250)
        # output_label.setToolTip(str(run_result.output_folder))
        # output_label.setText(output_label.fontMetrics().elidedText(
        #     str(run_result.output_folder), Qt.TextElideMode.ElideRight, 250
        # ))
        # layout.addWidget(output_label, 2, 0, Qt.AlignmentFlag.AlignLeft)

        # bottom right: logic to add operation icons, not yet visible
        # operations_widget = QWidget()
        # operations_layout = QHBoxLayout(operations_widget)
        # operations_layout.setContentsMargins(0, 0, 0, 0)
        # operations_layout.setSpacing(0)
        # for operation in run_result.operations:
        #     icon_widget = QWidget()
        #     icon_widget.setFixedSize(28, 28)
        #     icon_widget.setToolTip(operation)
        #     icon_widget.setObjectName("operation_icon")
        #     icon_widget.setProperty("operation", operation)
        #     operations_layout.addWidget(icon_widget)
        # operations_layout.addStretch()
        # layout.addWidget(operations_widget, 2, 1, Qt.AlignmentFlag.AlignRight)

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