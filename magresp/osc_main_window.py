from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6.QtCore import Qt, QSettings
from .ui_osc_main_window import Ui_OscMainWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT
from .mr_main_window import MrMainWindow
from .on_mr_build_dialog import OnMrBuildDialog
from .sequence import Sequence
import matplotlib.pyplot as plt


class OscMainWindow(QMainWindow):
    def __init__(self, mr_signal, ds_mr_signal, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__mr_signal = mr_signal
        self.__ds_mr_signal = ds_mr_signal
        self.__settings = QSettings()

        self.__ui = Ui_OscMainWindow()
        self.__ui.setupUi(self)

        figure = Figure(figsize=(5, 3))
        canvas = FigureCanvas(figure)
        self.__ax1, self.__ax2 = canvas.figure.subplots(2, 1, sharex=True)
        self.__ax1.grid()
        self.__ax2.grid()

        layout = QVBoxLayout(self.__ui.centralwidget)
        layout.addWidget(canvas)

        toolbar = NavigationToolbar2QT(canvas, self)
        self.addToolBar(toolbar)
        toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)

        self.__ui.build_mr_action.triggered.connect(self.__build_mr)
        self.__ui.exit_action.triggered.connect(self.__exit)

        self.__ax1.set_xlabel(str(ds_mr_signal.cols.time))
        self.__ax1.set_ylabel(str(ds_mr_signal.cols.etalon_pq))
        self.__ax1.autoscale(enable=True, axis="x", tight=True)
        self.__ax2.set_xlabel(str(ds_mr_signal.cols.time))
        self.__ax2.set_ylabel(str(ds_mr_signal.cols.dut))
        self.__ax2.autoscale(enable=True, axis="x", tight=True)

        ds_mr_signal.calculate_etalon_pq_col(
            self.__settings.value("etalon/unit"),
            float(self.__settings.value("etalon/k").replace(",", ".")),
            float(self.__settings.value("etalon/u0").replace(",", ".")))

        plot_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        self.__ax1.plot(ds_mr_signal.df[str(ds_mr_signal.cols.time)],
                        ds_mr_signal.df[str(
                            ds_mr_signal.cols.etalon_pq)], color=plot_colors[1],
                        label=str(ds_mr_signal.cols.etalon_pq), zorder=1, marker=".")
        self.__ax2.plot(ds_mr_signal.df[str(ds_mr_signal.cols.time)],
                        ds_mr_signal.df[str(
                            ds_mr_signal.cols.dut)], color=plot_colors[1],
                        label=str(ds_mr_signal.cols.dut), zorder=1, marker=".")

        if self.__settings.value("show_raw_signals", type=bool):
            mr_signal.calculate_etalon_pq_col(
                self.__settings.value("etalon/unit"),
                float(self.__settings.value("etalon/k").replace(",", ".")),
                float(self.__settings.value("etalon/u0").replace(",", ".")))

            self.__ax1.plot(mr_signal.df[str(mr_signal.cols.time)], mr_signal.df[str(mr_signal.cols.etalon_pq)],
                            label=str(mr_signal.cols.etalon_pq), zorder=0)
            self.__ax2.plot(mr_signal.df[str(mr_signal.cols.time)], mr_signal.df[str(mr_signal.cols.dut)],
                            label=str(mr_signal.cols.dut), zorder=0)

    def __exit(self):
        self.close()

    def __build_mr(self):
        res = OnMrBuildDialog().exec()

        if res == 1:
            mr_win = MrMainWindow(self.__ds_mr_signal, self)
            mr_win.move(self.pos().x() + 25, self.pos().y() + 25)
            mr_win.show()
