from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QSettings
from .ui_on_mr_build_dialog import Ui_OnMrBuildDialog
from .sequence import Sequence


class OnMrBuildDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ui = Ui_OnMrBuildDialog()
        self.__ui.setupUi(self)

        self.__settings = QSettings()

        for el in Sequence:
            self.__ui.sequence_combo_box.addItem(self.__get_ru_mnemonics(el))

        self.__ui.sequence_combo_box.setCurrentIndex(
            self.__settings.value("sequence"))

        self.__ui.sequence_combo_box.currentIndexChanged.connect(
            self.__on_current_index_changed)

    def __get_ru_mnemonics(self, value):
        if value == Sequence.UP:
            return "подъем"
        elif value == Sequence.DOWN:
            return "спуск"
        elif value == Sequence.UP_DOWN:
            return "подъем, спуск"
        elif value == Sequence.DOWN_UP:
            return "спуск, подъем"
        else:
            raise ValueError("value")

    def __on_current_index_changed(self, i):
        self.__settings.setValue("sequence", i)
