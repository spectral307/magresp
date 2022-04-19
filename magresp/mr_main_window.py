from .ui_mr_main_window import Ui_MrMainWindow
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT
from .sequence import Sequence


class MrMainWindow(QMainWindow):
    def __init__(self, ds_mr_signal, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ds_mr_signal = ds_mr_signal
        self.mr_build_requested = pyqtSignal()
        self.__settings = QSettings()

        self.__ui = Ui_MrMainWindow()
        self.__ui.setupUi(self)

        figure = Figure(figsize=(5, 3))
        canvas = FigureCanvas(figure)
        self.__ax = canvas.figure.subplots()
        self.__ax.grid()
        self.__ax.set_xlabel(str(self.__ds_mr_signal.cols.etalon_pq))
        self.__ax.set_ylabel(str(self.__ds_mr_signal.cols.dut))

        layout = QVBoxLayout(self.__ui.centralwidget)
        layout.addWidget(canvas)

        toolbar = NavigationToolbar2QT(canvas, self)
        self.addToolBar(toolbar)
        toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)

        sequence = Sequence(self.__settings.value("sequence", type=int))

        self.__ds_mr_signal.separate_into_parts(sequence)

        for part in self.__ds_mr_signal.parts:
            if part.is_up_part:
                label = "подъем"
            elif part.is_down_part:
                label = "спуск"
            self.__ax.plot(part[str(self.__ds_mr_signal.cols.etalon_pq)],
                           part[str(self.__ds_mr_signal.cols.dut)],
                           label=label)
        self.__ax.legend()
