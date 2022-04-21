from PyQt6.QtWidgets import QMainWindow, QFileDialog, QApplication
from PyQt6.QtCore import QSettings
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

            etalon_ch_number = settings.value("channels/etalon/ordinal")
            dut_ch_number = settings.value("channels/dut/ordinal")

            etalon_ch_name = None
            if not settings.value("channels/etalon/use_gtl_name", type=bool):
                etalon_ch_name = settings.value("channels/etalon/name")

            dut_ch_name = None
            if not settings.value("channels/dut/use_gtl_name", type=bool):
                dut_ch_name = settings.value("channels/dut/name")

            mr_signal = MRSignal.create_from_gtrfile(
                gtr, etalon_ch_number, dut_ch_number, etalon_ch_name, dut_ch_name)

            block_duration = float(settings.value(
                "ds_interval").replace(",", "."))
            ds_mr_signal = mr_signal.downsample_by_block_averaging(
                block_duration)

            osc_win = OscMainWindow(mr_signal, ds_mr_signal, self)
            osc_win.move(self.pos().x() + 25, self.pos().y() + 25)
            osc_win.show()
