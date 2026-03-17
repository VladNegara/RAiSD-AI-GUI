import datetime as dt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSplitter,
)
from PySide6.QtCore import Slot, Qt

from gui.widgets.operation_record_widget import OperationRecord
from gui.widgets.operation_record_list_widget import HistoryList


class HistoryWidget(QWidget):
    """
    The history page, showing a list of completed runs on the left
    and the details of the selected run on the right.
    """

    def __init__(self):
        super().__init__()
        self._history_list: HistoryList = HistoryList()
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self._history_list.run_selected.connect(self._on_run_selected)

        dummy_records = [
            OperationRecord(
                name="Run 1",
                operations={"IMG-GEN"},
                input_files=["datasets/train/msneutral1.vcf", "datasets/train/msneutral2.vcf","datasets/train/msneutral3.vcf", "datasets/train/msneutral4.vcf"],
                output_folder="PycharmProjects/outputs/cokcokcokcokcoooooooooooooooooooooooookuzunfiledirectory",
                date=dt.datetime.now() - dt.timedelta(minutes=5),
            ),
            OperationRecord(
                name="Run 2",
                operations={"MDL-GEN", "IMG-GEN"},
                input_files=["datasets/train/msneutral3.fasta"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(hours=3),
            ),
            OperationRecord(
                name="Run 3",
                operations={"SWP-SCN"},
                input_files=["datasets/test/sweep1.vcf"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=2),
            ),
            OperationRecord(
                name="Run 4",
                operations={"RSD-DEF"},
                input_files=["datasets/test/neutral1.vcf", "datasets/test/neutral2.vcf"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(weeks=2),
            ),
            OperationRecord(
                name="Run 5",
                operations={"MDL-TST"},
                input_files=["datasets/test/model_test.fasta"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=60),
            ),
            OperationRecord(
                name="Run 6",
                operations={"RSD-DEF"},
                input_files=["datasets/test/neutral1.vcf", "datasets/test/neutral2.vcf"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=70),
            ),
            OperationRecord(
                name="Run 7",
                operations={"MDL-TST"},
                input_files=["datasets/test/model_test.fasta"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=80),
            ),
            OperationRecord(
                name="Run 8",
                operations={"RSD-DEF"},
                input_files=["datasets/test/neutral1.vcf", "datasets/test/neutral2.vcf"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=90),
            ),
            OperationRecord(
                name="Run 9",
                operations={"MDL-TST"},
                input_files=["datasets/test/model_test.fasta"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=100),
            ),
            OperationRecord(
                name="Run 10",
                operations={"RSD-DEF"},
                input_files=["datasets/test/neutral1.vcf", "datasets/test/neutral2.vcf"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=110),
            ),
            OperationRecord(
                name="Run 11",
                operations={"MDL-TST"},
                input_files=["datasets/test/model_test.fasta"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=120),
            ),
            OperationRecord(
                name="Run 12",
                operations={"RSD-DEF"},
                input_files=["datasets/test/neutral1.vcf", "datasets/test/neutral2.vcf"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=130),
            ),
            OperationRecord(
                name="Run 13",
                operations={"SWP-SCN"},
                input_files=["datasets/test/sweep1.vcf"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=300),
            ),
            OperationRecord(
                name="Run 14",
                operations={"MDL-GEN", "IMG-GEN"},
                input_files=["datasets/train/msneutral3.fasta"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days=500),
            ),
            OperationRecord(
                name="Run 15",
                operations={"IMG-GEN"},
                input_files=["datasets/train/msneutral1.vcf", "datasets/train/msneutral2.vcf"],
                output_folder="PycharmProjects/outputs",
                date=dt.datetime.now() - dt.timedelta(days = 759),
            ),
        ]
        for op_rec in reversed(dummy_records):
            self._history_list.add_record(op_rec)

        splitter.addWidget(self._history_list)

        # Right panel: detail view. This will be changed with results view after it is implemented.
        self._detail_panel = QWidget()
        detail_layout = QVBoxLayout(self._detail_panel)
        self._detail_label = QLabel("Select a run to see details.")
        self._detail_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._detail_label.setWordWrap(True)
        detail_layout.addWidget(self._detail_label)
        detail_layout.addStretch()
        splitter.addWidget(self._detail_panel)

        # Give the list 1/3 and the detail panel 2/3 of the width
        splitter.setSizes([200, 400])

    def add_completed_run(self, op_rec: OperationRecord) -> None:
        """
        Add a completed run to the history list.

        :param op_rec: the completed operation record to add
        :type op_rec: OperationRecord
        """
        self._history_list.add_record(op_rec)

    @Slot(OperationRecord)
    def _on_run_selected(self, op_rec: OperationRecord) -> None:
        """
        Update the detail panel when a record is selected from the list.
        """
        self._detail_label.setText(
            f"Name: {op_rec.name}\n"
            f"Date: {op_rec.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Operations: {', '.join(op_rec.operations)}\n"
            f"Input files:\n" + "\n".join(f"  - {f}" for f in op_rec.input_files) + "\n"
            f"Output folder: {op_rec.output_folder}"
        )