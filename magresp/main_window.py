from PyQt6.QtWidgets import QMainWindow, QFileDialog, QApplication
from PyQt6.QtCore import QSettings, Qt
from .ui_main_window import Ui_MainWindow
from os.path import dirname
from gtrfile import GtrFile
import matplotlib.pyplot as plt
from .mr_signal import MRSignal
from .on_open_file_dialog import OnOpenFileDialog
from .osc_main_window import OscMainWindow


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__ui = Ui_MainWindow()
        self.__ui.setupUi(self)

        self.__ui.open_file_action.triggered.connect(self.open_file)
        self.__ui.exit_action.triggered.connect(self.exit)

    def exit(self):
        QApplication.quit()

    def open_file(self):
        settings = QSettings()

        default_dir = settings.value("default_dir")
        file = QFileDialog.getOpenFileName(
            self, "Открыть файл", default_dir, "Файлы gtr (*.gtr)")
        record_path = file[0]
        if not record_path:
            return

        record_dir = dirname(record_path)
        if record_dir != settings.value("default_dir"):
            settings.setValue("default_dir", record_dir)

        res = OnOpenFileDialog().exec()

        if res == 1:
            gtr = GtrFile(record_path)

            etalon_ch_number = settings.value("channels/etalon")
            dut_ch_number = settings.value("channels/dut")

            mr_signal = MRSignal.create_from_gtrfile(
                gtr, etalon_ch_number, dut_ch_number)

            block_duration = float(settings.value(
                "ds_interval").replace(",", "."))
            ds_mr_signal = mr_signal.downsample_by_block_averaging(
                block_duration)

            plot_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

            osc_win = OscMainWindow(self)
            osc_win.move(self.pos().x() + 25, self.pos().y() + 25)
            osc_win.show()

            osc_win.ax1.set_xlabel(str(ds_mr_signal.cols.time))
            osc_win.ax1.set_ylabel(str(ds_mr_signal.cols.etalon_pq))
            osc_win.ax1.autoscale(enable=True, axis="x", tight=True)
            osc_win.ax2.set_xlabel(str(ds_mr_signal.cols.time))
            osc_win.ax2.set_ylabel(str(ds_mr_signal.cols.dut))
            osc_win.ax2.autoscale(enable=True, axis="x", tight=True)

            ds_mr_signal.calculate_etalon_pq_col(
                settings.value("etalon/unit"),
                float(settings.value("etalon/k").replace(",", ".")),
                float(settings.value("etalon/u0").replace(",", ".")))

            osc_win.ax1.plot(ds_mr_signal.df[str(ds_mr_signal.cols.time)],
                             ds_mr_signal.df[str(
                                 ds_mr_signal.cols.etalon_pq)], color=plot_colors[1],
                             label=str(ds_mr_signal.cols.etalon_pq), zorder=1, marker=".")
            osc_win.ax2.plot(ds_mr_signal.df[str(ds_mr_signal.cols.time)],
                             ds_mr_signal.df[str(
                                 ds_mr_signal.cols.dut)], color=plot_colors[1],
                             label=str(ds_mr_signal.cols.dut), zorder=1, marker=".")

            if settings.value("show_raw_signals", type=bool):
                mr_signal.calculate_etalon_pq_col(
                    settings.value("etalon/unit"),
                    float(settings.value("etalon/k").replace(",", ".")),
                    float(settings.value("etalon/u0").replace(",", ".")))

                osc_win.ax1.plot(mr_signal.df[str(mr_signal.cols.time)], mr_signal.df[str(mr_signal.cols.etalon_pq)],
                                 label=str(mr_signal.cols.etalon_pq), zorder=0)
                osc_win.ax2.plot(mr_signal.df[str(mr_signal.cols.time)], mr_signal.df[str(mr_signal.cols.dut)],
                                 label=str(mr_signal.cols.dut), zorder=0)
