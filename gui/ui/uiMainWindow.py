# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'uiMainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCommandLinkButton, QDial,
    QDialogButtonBox, QDoubleSpinBox, QFrame, QKeySequenceEdit,
    QMainWindow, QMenuBar, QRadioButton, QScrollBar,
    QSizePolicy, QSlider, QSpinBox, QStatusBar,
    QTabWidget, QTimeEdit, QToolButton, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(761, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(70, 0, 621, 541))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.frame = QFrame(self.tab)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(30, 60, 521, 381))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalSlider = QSlider(self.frame)
        self.verticalSlider.setObjectName(u"verticalSlider")
        self.verticalSlider.setGeometry(QRect(120, 110, 16, 160))
        self.verticalSlider.setOrientation(Qt.Orientation.Vertical)
        self.dial = QDial(self.frame)
        self.dial.setObjectName(u"dial")
        self.dial.setGeometry(QRect(340, 150, 50, 64))
        self.toolButton = QToolButton(self.frame)
        self.toolButton.setObjectName(u"toolButton")
        self.toolButton.setGeometry(QRect(190, 60, 21, 22))
        self.radioButton = QRadioButton(self.frame)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(200, 110, 98, 24))
        self.commandLinkButton = QCommandLinkButton(self.frame)
        self.commandLinkButton.setObjectName(u"commandLinkButton")
        self.commandLinkButton.setGeometry(QRect(190, 290, 172, 41))
        self.buttonBox = QDialogButtonBox(self.frame)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 320, 168, 26))
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.spinBox = QSpinBox(self.frame)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setGeometry(QRect(20, 260, 78, 26))
        self.doubleSpinBox = QDoubleSpinBox(self.frame)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setGeometry(QRect(20, 200, 94, 26))
        self.timeEdit = QTimeEdit(self.frame)
        self.timeEdit.setObjectName(u"timeEdit")
        self.timeEdit.setGeometry(QRect(360, 330, 118, 26))
        self.horizontalScrollBar = QScrollBar(self.frame)
        self.horizontalScrollBar.setObjectName(u"horizontalScrollBar")
        self.horizontalScrollBar.setGeometry(QRect(290, 40, 160, 16))
        self.horizontalScrollBar.setOrientation(Qt.Orientation.Horizontal)
        self.keySequenceEdit = QKeySequenceEdit(self.frame)
        self.keySequenceEdit.setObjectName(u"keySequenceEdit")
        self.keySequenceEdit.setGeometry(QRect(340, 90, 113, 26))
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.widget = QWidget(self.tab_2)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(100, 90, 100, 86))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.radioButton_1 = QRadioButton(self.widget)
        self.radioButton_1.setObjectName(u"radioButton_1")

        self.verticalLayout.addWidget(self.radioButton_1)

        self.radioButton_2 = QRadioButton(self.widget)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.verticalLayout.addWidget(self.radioButton_2)

        self.radioButton_3 = QRadioButton(self.widget)
        self.radioButton_3.setObjectName(u"radioButton_3")

        self.verticalLayout.addWidget(self.radioButton_3)

        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 761, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.toolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.commandLinkButton.setText(QCoreApplication.translate("MainWindow", u"CommandLinkButton", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.radioButton_1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.radioButton_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Tab 2", None))
    # retranslateUi

