from PySide6.QtWidgets import (
    QWidget,
)

class Page(QWidget):
    """
    An abstract base class for the main pages of the application.
    Each page should inherit from this class and 
    implement the _setup_ui and update_ui methods.
    """
    def __init__(self) -> None:
        """
        Initialize the page.
        """
        super().__init__()

    def _setup_ui(self) -> None:
        """
        Set up the UI elements of the page.

        This method should be implemented by each page subclass.
        """
        raise NotImplementedError()