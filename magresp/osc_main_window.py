from configparser import SafeConfigParser
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from .ui_osc_main_window import Ui_OscMainWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT
from .on_mr_build_dialog import OnMrBuildDialog
from matplotlib.lines import Line2D
from snap_cursor_stack import SnapCursorStack


class OscMainWindow(QMainWindow):
    mr_settings_accepted = pyqtSignal()

    def __init__(self, mr_signal, ds_mr_signal, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__mr_signal = mr_signal
        self.__ds_mr_signal = ds_mr_signal
        self.__settings = QSettings()

        self.__ru = self.__settings.value("ru_mnemonics", type=dict)

        self.__ui = Ui_OscMainWindow()
        self.__ui.setupUi(self)

        self.__colors = self.__settings.value("colors", type=dict)

        figure = Figure(figsize=(5, 3))
        self.__canvas = FigureCanvas(figure)
        self.__ax1, self.__ax2 = self.__canvas.figure.subplots(
            2, 1, sharex=True)
        self.__ax1.grid()
        self.__ax2.grid()

        layout = QVBoxLayout(self.__ui.centralwidget)
        layout.addWidget(self.__canvas)

        toolbar = NavigationToolbar2QT(self.__canvas, self)
        self.addToolBar(toolbar)
        toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)

        self.__ui.build_mr_action.triggered.connect(self.__build_mr)
        self.__ui.exit_action.triggered.connect(self.__exit)

        ds_mr_signal.calculate_etalon_pq_col(
            self.__settings.value("etalon/unit"),
            float(self.__settings.value("etalon/k").replace(",", ".")),
            float(self.__settings.value("etalon/u0").replace(",", ".")))

        line1, = self.__ax1.plot(ds_mr_signal.df[str(ds_mr_signal.cols.time)],
                                 ds_mr_signal.df[str(
                                     ds_mr_signal.cols.etalon_pq)], color=self.__colors["ds"],
                                 label=self.__ru["ds"], zorder=1, marker=".")
        line2, = self.__ax2.plot(ds_mr_signal.df[str(ds_mr_signal.cols.time)],
                                 ds_mr_signal.df[str(
                                     ds_mr_signal.cols.dut)], color=self.__colors["ds"],
                                 label=self.__ru["ds"], zorder=1, marker=".")

        self.__ax1_lines = []
        self.__ax2_lines = []
        self.__ax1_lines.append(line1)
        self.__ax2_lines.append(line2)

        self.__snap_cursor_stack = None

        if self.__settings.value("show_raw_signals", type=bool):
            mr_signal.calculate_etalon_pq_col(
                self.__settings.value("etalon/unit"),
                float(self.__settings.value("etalon/k").replace(",", ".")),
                float(self.__settings.value("etalon/u0").replace(",", ".")))

            self.__ax1.plot(mr_signal.df[str(mr_signal.cols.time)], mr_signal.df[str(mr_signal.cols.etalon_pq)],
                            label=self.__ru["raw"], zorder=0)
            self.__ax2.plot(mr_signal.df[str(mr_signal.cols.time)], mr_signal.df[str(mr_signal.cols.dut)],
                            label=self.__ru["raw"], zorder=0)

        self.__ax1.set_xlabel(str(ds_mr_signal.cols.time))
        self.__ax1.set_ylabel(str(ds_mr_signal.cols.etalon_pq))
        self.__ax1.autoscale(enable=True, axis="x", tight=True)
        self.__ax2.set_xlabel(str(ds_mr_signal.cols.time))
        self.__ax2.set_ylabel(str(ds_mr_signal.cols.dut))
        self.__ax2.autoscale(enable=True, axis="x", tight=True)

    def __exit(self):
        self.close()

    def __build_mr(self):
        res = OnMrBuildDialog().exec()

        if res == 1:
            if self.__settings.value("grid/on", type=bool):
                self.__ds_mr_signal.add_segments_calculated_handler(
                    self.__segments_calculated_handler)
                self.__ds_mr_signal.add_mr_values_calculated_handler(
                    self.__mr_values_calculated_handler)
            else:
                self.__ds_mr_signal.add_parts_calculated_handler(
                    self.__parts_calculated_handler)
            self.mr_settings_accepted.emit()

    def __remove_lines(self):
        for line in self.__ax1_lines:
            self.__ax1.lines.remove(line)
        for line in self.__ax2_lines:
            self.__ax2.lines.remove(line)

        self.__ax1_lines.clear()
        self.__ax2_lines.clear()

    def __segments_calculated_handler(self):
        self.__remove_lines()
        if self.__snap_cursor_stack is not None:
            self.__snap_cursor_stack.clear()
            self.__snap_cursor_stack = None

        legend_lines = []
        legend_labels = []

        for part_type in self.__ds_mr_signal.segments:
            for segment in self.__ds_mr_signal.segments[part_type]:
                line1, = self.__ax1.plot(segment[str(self.__ds_mr_signal.cols.time)],
                                         segment[str(
                                             self.__ds_mr_signal.cols.etalon_pq)],
                                         c=self.__colors[part_type], marker=".")
                line2, = self.__ax2.plot(segment[str(self.__ds_mr_signal.cols.time)],
                                         segment[str(
                                             self.__ds_mr_signal.cols.dut)],
                                         c=self.__colors[part_type], marker=".")
                self.__ax1_lines.append(line1)
                self.__ax2_lines.append(line2)
            if len(self.__ds_mr_signal.segments[part_type]) > 0:
                legend_lines.append(
                    Line2D([0], [0], c=self.__colors[part_type], marker="."))
                legend_labels.append(self.__ru[part_type])

        self.__ax1.legend(legend_lines, legend_labels, loc="upper right")
        self.__ax2.legend(legend_lines, legend_labels, loc="upper right")

        self.__canvas.draw_idle()

    def __mr_values_calculated_handler(self):
        if self.__snap_cursor_stack is not None:
            self.__snap_cursor_stack.clear()

        self.__snap_cursor_stack = SnapCursorStack(
            [self.__ax1, self.__ax2],
            self.__ds_mr_signal.df[str(self.__ds_mr_signal.cols.time)],
            [self.__ds_mr_signal.df[str(self.__ds_mr_signal.cols.etalon_pq)],
             self.__ds_mr_signal.df[str(self.__ds_mr_signal.cols.dut)]])

        self.__snap_cursor_stack.add_cursors_moved_handler(
            self.__cursors_moved_handler)

        for part_type in self.__ds_mr_signal.mr_values:
            for mr_value in self.__ds_mr_signal.mr_values[part_type]:
                self.__snap_cursor_stack.add_cursor(
                    mr_value.index[0], color=self.__colors[part_type])

        self.__canvas.draw_idle()

    def __cursors_moved_handler(self, i, v):
        print(i, v)
        print(self.__snap_cursor_stack.get_cursor_xdata())
        print(self.__snap_cursor_stack.get_cursor_xdata_inds())
        self.__ds_mr_signal.set_mr_value(i, v)

    def __parts_calculated_handler(self):
        self.__remove_lines()
        if self.__snap_cursor_stack is not None:
            self.__snap_cursor_stack.clear()
            self.__snap_cursor_stack = None

        legend_lines = []
        legend_labels = []

        for part in self.__ds_mr_signal.parts:
            line1, = self.__ax1.plot(part[str(self.__ds_mr_signal.cols.time)],
                                     part[str(self.__ds_mr_signal.cols.etalon_pq)],
                                     c=self.__colors[part.type],
                                     marker=".", label=self.__ru[part.type])
            line2, = self.__ax2.plot(part[str(self.__ds_mr_signal.cols.time)],
                                     part[str(self.__ds_mr_signal.cols.dut)],
                                     c=self.__colors[part.type],
                                     marker=".", label=self.__ru[part.type])
            self.__ax1_lines.append(line1)
            self.__ax2_lines.append(line2)
            legend_lines.append(
                Line2D([0], [0], c=self.__colors[part.type], marker="."))
            legend_labels.append(self.__ru[part.type])

        self.__ax1.legend(legend_lines, legend_labels, loc="upper right")
        self.__ax2.legend(legend_lines, legend_labels, loc="upper right")

        self.__canvas.draw_idle()

    def closeEvent(self, a0):
        self.__ds_mr_signal.remove_parts_calculated_handler(
            self.__parts_calculated_handler)
        self.__ds_mr_signal.remove_segments_calculated_handler(
            self.__segments_calculated_handler)
        self.__ds_mr_signal.remove_mr_values_calculated_handler(
            self.__mr_values_calculated_handler)
        if self.__snap_cursor_stack is not None:
            self.__snap_cursor_stack.clear()
        return super().closeEvent(a0)
