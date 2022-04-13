from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6.QtCore import Qt
from .ui_osc_main_window import Ui_OscMainWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT
from .mr_main_window import MrMainWindow


class OscMainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ui = Ui_OscMainWindow()
        self.__ui.setupUi(self)

        figure = Figure(figsize=(5, 3))
        canvas = FigureCanvas(figure)
        self.ax1, self.ax2 = canvas.figure.subplots(2, 1, sharex=True)
        self.ax1.grid()
        self.ax2.grid()

        layout = QVBoxLayout(self.__ui.centralwidget)
        layout.addWidget(canvas)

        toolbar = NavigationToolbar2QT(canvas, self)
        self.addToolBar(toolbar)
        toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)

        self.__ui.mr_action.triggered.connect(self.__build_mr)
        self.__ui.exit_action.triggered.connect(self.__exit)

    def __exit(self):
        self.close()

    def __build_mr(self):
        mr_win = MrMainWindow(self)
        mr_win.move(self.pos().x() + 25, self.pos().y() + 25)
        mr_win.show()
