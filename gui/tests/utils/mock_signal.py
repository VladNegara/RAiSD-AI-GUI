from typing import Callable, overload

from PySide6.QtCore import Signal, SignalInstance, QObject


class MockSignal:
    def __init__(self, values: tuple) -> None:
        self.values: tuple = values
        self.slots: list = []


    def connect(self, slot: SignalInstance | Callable) -> None:
        self.slots.append(slot)

    def emit(self) -> None:
        for slot in self.slots:
            if isinstance(slot, SignalInstance):
                slot.emit(True)
            elif isinstance(slot, Callable):
                slot(*self.values)
        self.slots.clear()

# testing:
# Should output:
# True
# True

# class mcok(QObject):
#     signa = Signal(bool)
#     def __init__(self):
#         super().__init__()
#         self.signa.connect(lambda x: print(x))


# sig = MockSignal(tuple([True]))
# mco = mcok()

# sig.connect(lambda x: print(x))
# sig.connect(mco.signa)

# sig.emit()