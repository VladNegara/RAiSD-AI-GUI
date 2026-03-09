import queue

from PySide6.QtCore import (
        QObject, 
        QProcess, 
        Signal, 
        Slot,
)

class CommandExecutor(QObject):
    """
    A class that manages the execution of shell commands in QProcesses.
        
    Use `start_execution` to start the execution.
    Use `stop_execution` to stop the execution.
    """

    output = Signal(str)                    # line of stdout output
    execution_started = Signal(int)         # number of processes to run
    execution_finished = Signal()   
    execution_stopped = Signal()
    execution_failed = Signal(int)          # exit_code
    process_started = Signal(int)           # process_index
    process_finished = Signal(int)          # process_index
    sub_step_finished = Signal(int, int)    # process_index, step_number

    def __init__(self):
        """
        Initialize a `CommandExecutor` object.
        """
        super().__init__()
        self._process = QProcess()

        self._process.started.connect(self._process_started)
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.readyReadStandardError.connect(self._read_error)
        self._process.finished.connect(self._process_finished)
        
        self._commands = []
        self._command_queue = queue.Queue()

        self._error_message = ""

    @Slot(list)
    def start_execution(self, commands:list[str]=[]) -> None:
        """
        Starts exectution of a list of commands. Puts all the commands
        in the command queue and starts the first process.

        :param commands: the list of commands to be executed
        :type command: list[str]
        """
        if len(commands) is 0:
            raise Exception("Give at least 1 command")
        if self._process.state() is (QProcess.ProcessState.Starting or QProcess.ProcessState.Running):
            raise Exception("Execution is still running")
        
        self.execution_started.emit(len(commands))
        self._commands = commands
        for command in self._commands:
            self._command_queue.put(command)
        self._next_process()   

    @Slot()
    def stop_execution(self) -> None:
        """
        Stops the execution of the current process.
        """
        self._stop_process()

    @Slot()
    def _next_process(self) -> None:
        """
        Starts the next process with the next command from the queue.

        If the queue is empty then the `execution_finished` signal is emitted.
        """
        try:
            command = self._command_queue.get(block=False)
            self._start_process(command)
        except queue.Empty:
            self.execution_finished.emit()

    @Slot()
    def _start_process(self, command:str) -> None:
        """
        Starts a process with the given command.

        :param command: the command to be executed in the process
        :type command: str
        """
        self._process.start("bash", ["-c", command])

    @Slot()
    def _stop_process(self) -> None:
        """
        Stops the current running process.
        """
        if self._process.state() == QProcess.ProcessState.Running:
            self._process.terminate()
            if not self._process.waitForFinished(500):
                self._process.kill()

    @Slot()
    def _process_started(self) -> None:
        """
        Emits `process_started` with the process_index.
        """
        self.process_started.emit(self.get_process_index())

    @Slot()
    def _process_finished(self, exit_code:int, exit_status:QProcess.ExitStatus) -> None:
        """
        Starts the next process and signals the completion of the previous process
        or signals the end of the execution.

        If the process finished with exit code 9 or 15, `execution_stopped` is emitted.
        Otherwise `execution_failed` is emitted with the exit code of the process.
        """
        if exit_status is QProcess.ExitStatus.NormalExit and exit_code == 0:
            self.process_finished.emit(self.get_process_index())
            self._next_process()
        else:
            if exit_code == 9 or exit_code == 15:
                self.execution_stopped.emit()
            else:
                self.execution_failed.emit(exit_code) 

    @Slot()
    def _read_output(self) -> None:
        """
        Reads the stdout of the process and emits the data.
        """
        data = self._process.readAllStandardOutput().data().decode()
        self.output.emit(data.strip())
        # TODO: filter output for substeps (self.sub_step_finished)

    @Slot()
    def _read_error(self) -> None:
        """
        Reads the stderr of the process and compiles the error message.
        """
        data = self._process.readAllStandardError().data().decode()
        self._error_message += data.strip()

    def get_error_message(self) -> str:
        """
        The compiled error message.
        """
        error_message = self._error_message
        self._error_message = ""
        return error_message

    def get_process_index(self) -> int:
        """
        The index of the current process.
        """
        process_index = len(self._commands) - self._command_queue.qsize() - 1
        return process_index
