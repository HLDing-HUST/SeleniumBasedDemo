from PyQt5.QtWidgets import QMainWindow
from .example import Ui_MainWindow as example_ui
import os

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = example_ui()
        self.ui.setupUi(self)
