from .ui_mr_main_window import Ui_MrMainWindow
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT
from .sequence import Sequence


class MrMainWindow(QMainWindow):
    def __init__(self, ds_mr_signal, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__lines = []

        self.__ds_mr_signal = ds_mr_signal
        self.__settings = QSettings()

        self.__ui = Ui_MrMainWindow()
        self.__ui.setupUi(self)

        self.__ru = self.__settings.value("ru_mnemonics", type=dict)

        self.__colors = self.__settings.value("colors", type=dict)

        figure = Figure(figsize=(5, 3))
        self.__canvas = FigureCanvas(figure)
        self.__ax = self.__canvas.figure.subplots()
        self.__ax.grid()
        self.__ax.set_xlabel(str(self.__ds_mr_signal.cols.etalon_pq))
        self.__ax.set_ylabel(str(self.__ds_mr_signal.cols.dut))

        layout = QVBoxLayout(self.__ui.centralwidget)
        layout.addWidget(self.__canvas)

        toolbar = NavigationToolbar2QT(self.__canvas, self)
        self.addToolBar(toolbar)
        toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)

        sequence = Sequence(self.__settings.value("sequence", type=int))

        if self.__settings.value("grid/on", type=bool):
            sequence = Sequence(self.__settings.value("sequence", type=int))
            margin = self.__settings.value("grid/margin", type=float)
            grid = [float(item)
                    for item in self.__settings.value("grid/data", type=list)]
            self.__ds_mr_signal.add_mr_calculated_handler(
                self.__mr_calculated_handler)
            self.__ds_mr_signal.calculate_parts_and_segments_by_grid(
                sequence, margin, grid)
        else:
            self.__ds_mr_signal.add_parts_calculated_handler(
                self.__parts_calculated_handler)
            self.__ds_mr_signal.calculate_parts_by_extremum(sequence)

    def __parts_calculated_handler(self):
        self.__clear_lines()

        for part in self.__ds_mr_signal.parts:
            if part.type == "up":
                label = "подъем"
            elif part.type == "down":
                label = "спуск"
            line, = self.__ax.plot(part[str(self.__ds_mr_signal.cols.etalon_pq)],
                                   part[str(self.__ds_mr_signal.cols.dut)],
                                   label=label, color=self.__colors[part.type])
            self.__lines.append(line)

        self.__ax.legend()

    def __clear_lines(self):
        for line in self.__lines:
            self.__ax.lines.remove(line)
        self.__lines.clear()

    def __mr_calculated_handler(self):
        self.__clear_lines()

        if (inds := self.__ds_mr_signal.get_up_mr_inds()) is not None:
            line, = self.__ax.plot(self.__ds_mr_signal.df.loc[inds, str(
                self.__ds_mr_signal.cols.etalon_pq)],
                self.__ds_mr_signal.df.loc[inds, str(
                    self.__ds_mr_signal.cols.dut)],
                label=self.__ru["up"], color=self.__colors["up"],
                marker=".")
            self.__lines.append(line)

        if (inds := self.__ds_mr_signal.get_down_mr_inds()) is not None:
            line, = self.__ax.plot(self.__ds_mr_signal.df.loc[inds, str(
                self.__ds_mr_signal.cols.etalon_pq)],
                self.__ds_mr_signal.df.loc[inds, str(
                    self.__ds_mr_signal.cols.dut)],
                label=self.__ru["down"], color=self.__colors["down"],
                marker=".")
            self.__lines.append(line)

        self.__ax.legend()

        self.__canvas.draw_idle()

    def closeEvent(self, a0):
        self.__ds_mr_signal.remove_parts_calculated_handler(
            self.__parts_calculated_handler)
        self.__ds_mr_signal.remove_mr_calculated_handler(
            self.__mr_calculated_handler)
        super().closeEvent(a0)
