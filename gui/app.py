import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from windows.main import MainWindow

def main():
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("windowsvista"))

    window = MainWindow()  
    window.show()
    app.exec()
    print("App closed")

if __name__ == "__main__":
    main()