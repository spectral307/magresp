from .ui_on_open_file_dialog import Ui_OnOpenFileDialog
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import QSettings, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator


class OnOpenFileDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ui = Ui_OnOpenFileDialog()
        self.__ui.setupUi(self)

        self.setFixedSize(self.size())

        positive_double_reg_exp = QRegularExpression(
            "^[0-9]*\,?[0-9]+(e[-+]?[0-9]+)?$")
        positive_double_validator = QRegularExpressionValidator(
            positive_double_reg_exp)

        self.__ui.ds_line_edit.setValidator(positive_double_validator)
        self.__ui.k_line_edit.setValidator(positive_double_validator)
        self.__ui.u0_line_edit.setValidator(positive_double_validator)

        self.__settings = QSettings()

        ds_interval = self.__settings.value("ds_interval")
        self.__ui.ds_line_edit.setText(ds_interval.replace(".", ","))

        self.__settings.beginGroup("etalon")

        k = self.__settings.value("k")
        self.__ui.k_line_edit.setText(k.replace(".", ","))

        u0 = self.__settings.value("u0")
        self.__ui.u0_line_edit.setText(u0.replace(".", ","))

        self.__ui.unit_line_edit.setText(self.__settings.value("unit"))

        self.__settings.endGroup()

        self.__ui.show_raw_signals_check_box.setChecked(
            self.__settings.value("show_raw_signals", type=bool))

    def accept(self):
        ds_interval = self.__ui.ds_line_edit.text()
        try:
            float(ds_interval.replace(",", "."))
        except ValueError:
            QMessageBox().critical(None, "Ошибка", "Неверное значение интервала усреднения")
            return
        if ds_interval != self.__settings.value("ds_interval"):
            self.__settings.setValue("ds_interval", ds_interval)

        k = self.__ui.k_line_edit.text()
        try:
            float(k.replace(",", "."))
        except ValueError:
            QMessageBox().critical(None, "Ошибка", "Неверное значение K")
            return
        if k != self.__settings.value("etalon/k"):
            self.__settings.setValue("etalon/k", k)

        u0 = self.__ui.u0_line_edit.text()
        try:
            float(u0.replace(",", "."))
        except ValueError:
            QMessageBox().critical(None, "Ошибка", "Неверное значение U0")
            return
        if u0 != self.__settings.value("etalon/u0"):
            self.__settings.setValue("etalon/u0", u0)

        unit = self.__ui.unit_line_edit.text()
        if unit != self.__settings.value("etalon/unit"):
            self.__settings.setValue("etalon/unit", unit)

        show_raw_signals = self.__ui.show_raw_signals_check_box.isChecked()
        self.__settings.setValue("show_raw_signals", show_raw_signals)

        return super().accept()
