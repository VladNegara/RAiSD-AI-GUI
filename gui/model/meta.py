from abc import ABC

from PySide6.QtCore import QObject


class AbstractQObjectMeta(type(ABC), type(QObject)):
    """
    Metaclass for an abstract base QObject class.
    """

    pass
