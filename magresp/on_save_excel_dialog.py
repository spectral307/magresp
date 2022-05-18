from PyQt6.QtCore import QSettings, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QDialog
from .ui_on_save_excel_dialog import Ui_OnSaveExcelDialog


class OnSaveExcelDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ui = Ui_OnSaveExcelDialog()
        self.__ui.setupUi(self)

        self.setFixedSize(self.size())

        self.__settings = QSettings()

        self.__ui.append_check_box.setChecked(
            self.__settings.value("output/excel/append", type=bool))

        self.__ui.direction_combo_box.addItem(
            self.__settings.value("ru_mnemonics")["vertical"])
        self.__ui.direction_combo_box.addItem(
            self.__settings.value("ru_mnemonics")["horizontal"])

        if self.__settings.value("output/excel/direction") == "vertical":
            self.__ui.direction_combo_box.setCurrentIndex(0)
        if self.__settings.value("output/excel/direction") == "horizontal":
            self.__ui.direction_combo_box.setCurrentIndex(1)

        excel_cell_reg_exp = QRegularExpression("^[a-zA-Z]\d{1,2}$")
        excel_cell_validator = QRegularExpressionValidator(excel_cell_reg_exp)
        self.__ui.start_cell_line_edit.setValidator(excel_cell_validator)

        self.__ui.start_cell_line_edit.setText(
            self.__settings.value("output/excel/start_cell"))

    def accept(self):
        append = self.__ui.append_check_box.isChecked()
        self.__settings.setValue("output/excel/append", append)

        if self.__ui.direction_combo_box.currentIndex() == 0:
            self.__settings.setValue("output/excel/direction", "vertical")
        elif self.__ui.direction_combo_box.currentIndex() == 1:
            self.__settings.setValue("output/excel/direction", "horizontal")

        self.__settings.setValue(
            "output/excel/start_cell", self.__ui.start_cell_line_edit.text().strip())

        return super().accept()
