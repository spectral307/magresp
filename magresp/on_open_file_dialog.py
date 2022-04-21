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

        self.__ui.etalon_ch_name_line_edit.setText(
            self.__settings.value("channels/etalon/name"))
        self.__ui.use_gtl_etalon_ch_name_check_box.stateChanged.connect(
            self.__on_use_gtl_etalon_ch_name_changed)
        self.__ui.use_gtl_etalon_ch_name_check_box.setChecked(
            self.__settings.value("channels/etalon/use_gtl_name", type=bool))
        self.__ui.etalon_ch_ordinal_spin_box.setValue(
            self.__settings.value("channels/etalon/ordinal", type=int))
        self.__ui.etalon_ch_ordinal_spin_box.valueChanged.connect(
            self.__on_etalon_ch_ordinal_changed)

        self.__ui.dut_ch_name_line_edit.setText(
            self.__settings.value("channels/dut/name"))
        self.__ui.use_gtl_dut_ch_name_check_box.stateChanged.connect(
            self.__on_use_gtl_dut_ch_name_changed)
        self.__ui.use_gtl_dut_ch_name_check_box.setChecked(
            self.__settings.value("channels/dut/use_gtl_name", type=bool))
        self.__ui.dut_ch_ordinal_spin_box.setValue(
            self.__settings.value("channels/dut/ordinal", type=int))
        self.__ui.dut_ch_ordinal_spin_box.valueChanged.connect(
            self.__on_dut_ch_ordinal_changed)

        self.__ui.show_raw_signals_check_box.setChecked(
            self.__settings.value("show_raw_signals", type=bool))

    def __on_use_gtl_dut_ch_name_changed(self, state):
        if state == 0:
            self.__ui.dut_ch_name_line_edit.setDisabled(False)
        elif state == 2:
            self.__ui.dut_ch_name_line_edit.setDisabled(True)

    def __on_use_gtl_etalon_ch_name_changed(self, state):
        if state == 0:
            self.__ui.etalon_ch_name_line_edit.setDisabled(False)
        elif state == 2:
            self.__ui.etalon_ch_name_line_edit.setDisabled(True)

    def accept(self):
        ds_interval = self.__ui.ds_line_edit.text().strip()
        try:
            float(ds_interval.replace(",", "."))
        except ValueError:
            QMessageBox().critical(None, "Ошибка", "Неверное значение интервала усреднения")
            return

        k = self.__ui.k_line_edit.text().strip()
        try:
            float(k.replace(",", "."))
        except ValueError:
            QMessageBox().critical(None, "Ошибка", "Неверное значение K")
            return

        u0 = self.__ui.u0_line_edit.text().strip()
        try:
            float(u0.replace(",", "."))
        except ValueError:
            QMessageBox().critical(None, "Ошибка", "Неверное значение U0")
            return

        etalon_ch_name = self.__ui.etalon_ch_name_line_edit.text().strip()
        if etalon_ch_name == "" and not self.__ui.use_gtl_etalon_ch_name_check_box.isChecked():
            QMessageBox().critical(None, "Ошибка", "Название канала эталона не задано")
            return

        dut_ch_name = self.__ui.dut_ch_name_line_edit.text().strip()
        if dut_ch_name == "" and not self.__ui.use_gtl_dut_ch_name_check_box.isChecked():
            QMessageBox().critical(None, "Ошибка", "Название канала измеряемого прибора не задано")
            return

        if ds_interval != self.__settings.value("ds_interval"):
            self.__settings.setValue("ds_interval", ds_interval)

        if k != self.__settings.value("etalon/k"):
            self.__settings.setValue("etalon/k", k)

        if u0 != self.__settings.value("etalon/u0"):
            self.__settings.setValue("etalon/u0", u0)

        unit = self.__ui.unit_line_edit.text().strip()
        if unit != self.__settings.value("etalon/unit"):
            self.__settings.setValue("etalon/unit", unit)

        if etalon_ch_name != self.__settings.value("channels/etalon/name"):
            self.__settings.setValue("channels/etalon/name", etalon_ch_name)

        use_gtl_etalon_ch_name = self.__ui.use_gtl_etalon_ch_name_check_box.isChecked()
        if use_gtl_etalon_ch_name != self.__settings.value("channels/etalon/use_gtl_name", type=bool):
            self.__settings.setValue(
                "channels/etalon/use_gtl_name", use_gtl_etalon_ch_name)

        etalon_ch_ordinal = self.__ui.etalon_ch_ordinal_spin_box.value()
        if etalon_ch_ordinal != self.__settings.value("channels/etalon/ordinal", type=int):
            self.__settings.setValue(
                "channels/etalon/ordinal", etalon_ch_ordinal)

        if dut_ch_name != self.__settings.value("channels/dut/name"):
            self.__settings.setValue("channels/dut/name", dut_ch_name)

        use_gtl_dut_ch_name = self.__ui.use_gtl_dut_ch_name_check_box.isChecked()
        if use_gtl_dut_ch_name != self.__settings.value("channels/dut/use_gtl_name", type=bool):
            self.__settings.setValue(
                "channels/dut/use_gtl_name", use_gtl_dut_ch_name)

        dut_ch_ordinal = self.__ui.dut_ch_ordinal_spin_box.value()
        if dut_ch_ordinal != self.__settings.value("channels/dut/ordinal", type=int):
            self.__settings.setValue("channels/dut/ordinal", dut_ch_ordinal)

        show_raw_signals = self.__ui.show_raw_signals_check_box.isChecked()
        self.__settings.setValue("show_raw_signals", show_raw_signals)

        return super().accept()

    def __on_etalon_ch_ordinal_changed(self, i):
        if i == 0:
            self.__ui.dut_ch_ordinal_spin_box.setValue(1)
        elif i == 1:
            self.__ui.dut_ch_ordinal_spin_box.setValue(0)
        else:
            raise ValueError("i")

    def __on_dut_ch_ordinal_changed(self, i):
        if i == 0:
            self.__ui.etalon_ch_ordinal_spin_box.setValue(1)
        elif i == 1:
            self.__ui.etalon_ch_ordinal_spin_box.setValue(0)
        else:
            raise ValueError("i")
