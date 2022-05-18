from PyQt6.QtWidgets import QMainWindow, QFileDialog, QApplication
from PyQt6.QtCore import QSettings
from .ui_main_window import Ui_MainWindow
from os.path import dirname, basename
from gtrfile import GtrFile
from .mr_signal import MRSignal
from .on_open_file_dialog import OnOpenFileDialog
from .osc_main_window import OscMainWindow
from .mr_main_window import MrMainWindow


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__ui = Ui_MainWindow()
        self.__ui.setupUi(self)

        self.__ui.open_file_action.triggered.connect(self.open_file)
        self.__ui.exit_action.triggered.connect(self.exit)

        self.__filename = None
        self.__osc_win = None
        self.__mr_win = None

    def exit(self):
        QApplication.quit()

    def open_file(self):
        settings = QSettings()

        gtr_dir = settings.value("gtr_dir")
        file = QFileDialog.getOpenFileName(
            self, "Открыть файл", gtr_dir, "Файлы gtr (*.gtr)")
        record_path = file[0]
        if not record_path:
            return

        record_dir = dirname(record_path)
        self.__filename = basename(record_path)
        if record_dir != settings.value("gtr_dir"):
            settings.setValue("gtr_dir", record_dir)
        if settings.value("use_same_gtr_and_reports_dir", type=bool):
            if record_dir != settings.value("reports_dir"):
                settings.setValue("reports_dir", record_dir)

        res = OnOpenFileDialog().exec()

        if res == 1:
            if self.__mr_win is not None:
                self.__mr_win.close()
                self.__mr_win = None
            if self.__osc_win is not None:
                self.__osc_win.close()
                self.__osc_win = None

            gtr = GtrFile(record_path)

            etalon_ch_number = settings.value("channels/etalon/ordinal")
            dut_ch_number = settings.value("channels/dut/ordinal")

            etalon_ch_name = None
            if not settings.value("channels/etalon/use_gtl_name", type=bool):
                etalon_ch_name = settings.value("channels/etalon/name")

            dut_ch_name = None
            if not settings.value("channels/dut/use_gtl_name", type=bool):
                dut_ch_name = settings.value("channels/dut/name")

            self.__mr_signal = MRSignal.create_from_gtrfile(
                gtr, etalon_ch_number, dut_ch_number, etalon_ch_name, dut_ch_name)

            block_duration = float(settings.value(
                "ds_interval").replace(",", "."))
            self.__ds_mr_signal = self.__mr_signal.downsample_by_block_averaging(
                block_duration)

            self.__osc_win = OscMainWindow(
                self.__mr_signal, self.__ds_mr_signal, self)
            self.__osc_win.mr_settings_accepted.connect(
                self.on_mr_settings_accepted)
            self.__osc_win.move(self.pos().x() + 25, self.pos().y() + 25)
            self.__osc_win.setWindowTitle(f"Осциллограмма: {self.__filename}")
            self.__osc_win.show()

            self.__ui.statusbar.showMessage(f"Открыт: {record_path}")

    def on_mr_settings_accepted(self):
        if self.__mr_win is not None:
            self.__mr_win.close()
            self.__mr_win = None
        self.__mr_win = MrMainWindow(self.__ds_mr_signal, self)
        self.__mr_win.move(self.pos().x() + 50, self.pos().y() + 50)
        self.__mr_win.setWindowTitle(f"АХ: {self.__filename}")
        self.__mr_win.show()
