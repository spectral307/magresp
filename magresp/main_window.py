from PyQt6.QtWidgets import QMainWindow, QFileDialog, QApplication
from PyQt6.QtCore import QSettings, QDir
from .ui_main_window import Ui_MainWindow
from os.path import dirname
from gtrfile import GtrFile
import matplotlib.pyplot as plt
from .signal import Signal
from rich import print as rich_print
from json import load as json_load
import importlib.resources


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__ui = Ui_MainWindow()
        self.__ui.setupUi(self)
        self.__ui.open_file_action.triggered.connect(self.open_file)
        self.__ui.exit_action.triggered.connect(self.exit)

    def get_config(self):
        with importlib.resources.open_text(__package__, "config.json") as file:
            return json_load(file)

    def exit(self):
        QApplication.q__uit()

    def open_file(self):
        settings = QSettings()
        default_dir = settings.value("default_dir")
        home_dir = QDir.home().absolutePath()
        if not default_dir:
            default_dir = home_dir

        file = QFileDialog.getOpenFileName(
            self, "Открыть файл", default_dir, "Файлы gtr (*.gtr)")

        if not file[0]:
            return

        record_path = file[0]

        dir = QDir()
        settings.setValue("default_dir", dirname(
            dir.absoluteFilePath(record_path)))
        self.__ui.statusbar.showMessage(record_path)

        config = self.get_config()

        gtr = GtrFile(record_path)

        rich_print(gtr.header)

        sequence = config["sequence"]

        etalon_ch_number = config["channels"]["etalon"]
        dut_ch_number = config["channels"]["dut"]

        etalon_ch_name = gtr.header["inputs"][etalon_ch_number]["name"]
        dut_ch_name = gtr.header["inputs"][dut_ch_number]["name"]

        etalon_ch_unit = gtr.header["inputs"][etalon_ch_number]["unit"]
        dut_ch_unit = gtr.header["inputs"][dut_ch_number]["unit"]

        record = Signal.create_from_gtrfile(
            gtr, etalon_ch_number, dut_ch_number)

        ds_record = record.downsample_by_block_averaging(.5)

        plot_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        fig, ax = plt.subplots(2, 1, sharex=True)
        ax[0].plot(record.data[record.time.name], record.data[record.etalon.name],
                   label=etalon_ch_name, zorder=0)
        ax[1].plot(record.data[record.time.name], record.data[record.dut.name],
                   label=dut_ch_name, zorder=0)
        ax[0].scatter(ds_record.data[ds_record.time.name],
                      ds_record.data[ds_record.etalon.name], color=plot_colors[1], label=etalon_ch_name, zorder=1)
        ax[1].scatter(ds_record.data[ds_record.time.name],
                      ds_record.data[ds_record.dut.name], color=plot_colors[1], label=dut_ch_name, zorder=1)
        ax[0].grid()
        ax[0].set_xlabel("t, s")
        ax[0].set_ylabel(
            f"{etalon_ch_name}{f' ,{etalon_ch_unit}' if etalon_ch_unit else ''}")
        ax[0].autoscale(enable=True, axis="x", tight=True)
        ax[1].grid()
        ax[1].set_xlabel("t, s")
        ax[1].set_ylabel(
            f"{dut_ch_name}{f' ,{dut_ch_unit}' if dut_ch_unit else ''}")
        ax[1].autoscale(enable=True, axis="x", tight=True)
        # plt.get_current_fig_manager().window.showMaximized()
        plt.show()

        fig, ax = plt.subplots()
        ax.plot(ds_record.data[ds_record.etalon.name],
                ds_record.data[ds_record.dut.name])
        ax.set_xlabel(
            f"{etalon_ch_name}{f' ,{etalon_ch_unit}' if etalon_ch_unit else ''}")
        ax.set_ylabel(
            f"{dut_ch_name}{f' ,{dut_ch_unit}' if dut_ch_unit else ''}")
        # ax.autoscale(enable=True, axis="x", tight=True)
        ax.grid()
        # plt.get_current_fig_manager().window.showMaximized()
        plt.show()
