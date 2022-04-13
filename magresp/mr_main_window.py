from .ui_mr_main_window import Ui_MrMainWindow
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT


class MrMainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ui = Ui_MrMainWindow()
        self.__ui.setupUi(self)

        figure = Figure(figsize=(5, 3))
        canvas = FigureCanvas(figure)
        self.ax = canvas.figure.subplots()
        self.ax.grid()
        self.ax.grid()

        layout = QVBoxLayout(self.__ui.centralwidget)
        layout.addWidget(canvas)

        toolbar = NavigationToolbar2QT(canvas, self)
        self.addToolBar(toolbar)
        toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)
