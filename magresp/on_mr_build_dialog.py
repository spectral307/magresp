from PyQt6.QtWidgets import QDialog, QPushButton
from PyQt6.QtCore import QSettings, QModelIndex
from .ui_on_mr_build_dialog import Ui_OnMrBuildDialog
from .sequence import Sequence
from .grid_table_model import GridTableModel, GridItemDelegate
from .down_grid_table_model import DownGridTableModel
import numpy as np


class OnMrBuildDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ui = Ui_OnMrBuildDialog()
        self.__ui.setupUi(self)

        self.__settings = QSettings()

        grid = self.__settings.value("grid")
        down_grid = self.__settings.value("down_grid")

        self.__grid_table_model = GridTableModel(grid)
        self.__ui.grid_table_view.setModel(self.__grid_table_model)

        self.__ui.grid_table_view.setItemDelegate(
            GridItemDelegate(self.__ui.grid_table_view))

        self.__ui.grid_table_view.setColumnWidth(0, 120)
        self.__ui.grid_table_view.setColumnWidth(1, 25)
        self.__ui.grid_table_view.setColumnWidth(2, 25)

        for i in range(self.__grid_table_model.rowCount(QModelIndex())):
            self.__add_buttons_to_grid_table_view(i)

        for el in Sequence:
            self.__ui.sequence_combo_box.addItem(self.__get_ru_mnemonics(el))

        self.__ui.sequence_combo_box.setCurrentIndex(
            self.__settings.value("sequence"))

        self.__ui.sequence_combo_box.currentIndexChanged.connect(
            self.__on_current_index_changed)

        self.__ui.grid_group_box.setChecked(
            self.__settings.value("grid_on", type=bool))
        self.__ui.down_grid_group_box.setChecked(
            self.__settings.value("down_grid_on", type=bool))

        self.__ui.grid_group_box.toggled.connect(
            self.__on_grid_group_box_toggled)
        self.__ui.down_grid_group_box.toggled.connect(
            self.__on_down_grid_group_box_toggled)

    def __add_buttons_to_grid_table_view(self, row):
        ind1 = self.__grid_table_model.createIndex(row, 1)
        ind2 = self.__grid_table_model.createIndex(row, 2)
        self.__ui.grid_table_view.setIndexWidget(
            ind1, QPushButton("+", self.__ui.grid_table_view))
        self.__ui.grid_table_view.setIndexWidget(
            ind2, QPushButton("-", self.__ui.grid_table_view))

    def __add_buttons_to_down_grid_table_view(self, row):
        ind1 = self.__down_grid_table_model.createIndex(row, 1)
        ind2 = self.__down_grid_table_model.createIndex(row, 2)
        self.__ui.grid_table_view.setIndexWidget(
            ind1, QPushButton("+", self.__ui.down_grid_table_view))
        self.__ui.grid_table_view.setIndexWidget(
            ind2, QPushButton("-", self.__ui.down_grid_table_view))

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

    def __on_grid_group_box_toggled(self, checked):
        self.__settings.setValue("grid_on", checked)

    def __on_down_grid_group_box_toggled(self, checked):
        self.__settings.setValue("down_grid_on", checked)
