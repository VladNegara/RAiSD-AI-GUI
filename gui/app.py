import sys
import sass
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QApplication,
    QSplashScreen,
)
from PySide6.QtGui import (
    QPixmap,
)

from gui.window import MainWindow


def main():
    app = QApplication(sys.argv)

    # Set styling
    with open("gui/style/variables.scss", "r") as f:
        variables = f.read()

    with open("gui/style/style.qss", "r") as f:
        stylesheet = f.read()

    final_stylesheet = variables + stylesheet
    final_stylesheet = sass.compile(string=final_stylesheet)

    app.setStyleSheet(final_stylesheet)

    splash_screen_pixmap = QPixmap("gui/style/resources/Raisd_ai_splash_screen.png")
    splash_screen = QSplashScreen(splash_screen_pixmap)
    splash_screen.setWindowFlags(splash_screen.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
    splash_screen.show()
    app.processEvents()

    # Set main window
    window = MainWindow()

    window.resize(1200,800)
    window.show()

    splash_screen.finish(window)

    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
