from PyQt6.QtWidgets import QDialog, QPushButton, QTableView, QMessageBox
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from .ui_on_mr_build_dialog import Ui_OnMrBuildDialog
from .sequence import Sequence
from .grid_table_model import GridTableModel, GridItemDelegate
import importlib.resources


class OnMrBuildDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ui = Ui_OnMrBuildDialog()
        self.__ui.setupUi(self)

        self.setFixedSize(self.size())

        self.__settings = QSettings()

        self.__ui.margin_unit_label.setText(
            self.__settings.value("etalon/unit"))
        self.__ui.margin_unit_label.adjustSize()

        self.__ui.margin_double_spin_box.setValue(
            self.__settings.value("grid/margin", type=float))

        with importlib.resources.path(f"{__package__}.images", "plus.png") as p:
            plus_path = p
        with importlib.resources.path(f"{__package__}.images", "minus.png") as p:
            minus_path = p
        self.__plus_icon = QIcon(str(plus_path))
        self.__minus_icon = QIcon(str(minus_path))

        grid = self.__settings.value("grid/data")
        down_grid = self.__settings.value("down_grid/data")

        self.__grid_table_model = GridTableModel(
            grid, self.__settings.value("etalon/unit"))

        self.__init_table_view(self.__ui.grid_table_view,
                               self.__grid_table_model)

        self.__down_grid_table_model = GridTableModel(
            down_grid, self.__settings.value("etalon/unit"))

        self.__init_table_view(self.__ui.down_grid_table_view,
                               self.__down_grid_table_model)

        self.__ui.append_grid_item_push_button.setIcon(self.__plus_icon)
        self.__ui.append_down_grid_item_push_button.setIcon(self.__plus_icon)
        self.__ui.append_grid_item_push_button.clicked.connect(
            lambda: self.__append_item_to_table_view(self.__ui.grid_table_view, self.__grid_table_model))
        self.__ui.append_down_grid_item_push_button.clicked.connect(
            lambda: self.__append_item_to_table_view(self.__ui.down_grid_table_view, self.__down_grid_table_model))

        for el in Sequence:
            self.__ui.sequence_combo_box.addItem(self.__get_ru_mnemonics(el))

        self.__ui.sequence_combo_box.setCurrentIndex(
            self.__settings.value("sequence"))

        self.__ui.sequence_combo_box.currentIndexChanged.connect(
            self.__on_current_index_changed)

        self.__ui.grid_group_box.setChecked(
            self.__settings.value("grid/on", type=bool))
        self.__ui.down_grid_group_box.setChecked(
            self.__settings.value("down_grid/on", type=bool))

        self.__ui.grid_group_box.toggled.connect(
            self.__on_grid_group_box_toggled)
        self.__ui.down_grid_group_box.toggled.connect(
            self.__on_down_grid_group_box_toggled)

    def __init_table_view(self, table_view: QTableView, table_model: GridTableModel):
        table_view.setModel(table_model)
        table_view.setItemDelegate(
            GridItemDelegate(table_view))

        table_view.setColumnWidth(0, 120)
        table_view.setColumnWidth(1, 25)
        table_view.setColumnWidth(2, 25)

        for i in range(table_model.rowCount()):
            self.__add_buttons_to_table_view_item(i, table_view, table_model)

    def __add_buttons_to_table_view_item(self, index, table_view: QTableView, table_model: GridTableModel):
        plus_button_index = table_model.createIndex(index, 1)
        minus_button_index = table_model.createIndex(index, 2)

        row = table_model.getRow(index)

        plus_button = QPushButton(table_view)
        plus_button.setIcon(self.__plus_icon)
        table_view.setIndexWidget(plus_button_index, plus_button)
        plus_button.clicked.connect(
            lambda: self.__insert_item_into_table_view(row, table_view, table_model))

        minus_button = QPushButton(table_view)
        minus_button.setIcon(self.__minus_icon)
        table_view.setIndexWidget(minus_button_index, minus_button)
        minus_button.clicked.connect(
            lambda: self.__remove_item_from_table_view(row, table_model))

    def __insert_item_into_table_view(self, row, table_view: QTableView, table_model: GridTableModel):
        index = table_model.getRowIndex(row)
        table_model.insertRow(index)
        self.__add_buttons_to_table_view_item(index, table_view, table_model)

    def __remove_item_from_table_view(self, row, table_model: GridTableModel):
        index = table_model.getRowIndex(row)
        table_model.removeRow(index)

    def __append_item_to_table_view(self, table_view: QTableView, table_model: GridTableModel):
        row_count = table_model.rowCount()
        table_model.insertRow(row_count)
        self.__add_buttons_to_table_view_item(
            row_count, table_view, table_model)

    def __get_ru_mnemonics(self, value):
        ru = self.__settings.value("ru_mnemonics", type=dict)
        return ru[value]

    def __on_current_index_changed(self, i):
        self.__settings.setValue("sequence", i)

    def __on_grid_group_box_toggled(self, checked):
        self.__settings.setValue("grid/on", checked)

    def __on_down_grid_group_box_toggled(self, checked):
        self.__settings.setValue("down_grid/on", checked)

    def __is_strictly_increasing(self, grid):
        return all(x < y for x, y in zip(grid, grid[1:]))

    def accept(self):
        grid = self.__grid_table_model.getGrid()
        grid_on = self.__ui.grid_group_box.isChecked()
        if grid_on:
            if len(grid) == 0:
                QMessageBox().critical(None, "Ошибка", "Сетка пуста")
                return
            if not self.__is_strictly_increasing(grid):
                QMessageBox().critical(None, "Ошибка", "Сетка должна быть строго возрастающей")
                return
            margin = self.__ui.margin_double_spin_box.value()
            if margin == 0:
                QMessageBox().critical(None, "Ошибка", "Ворота должны быть больше нуля")
                return
            self.__settings.setValue("grid/margin", margin)

        down_grid = self.__down_grid_table_model.getGrid()
        down_grid_on = self.__ui.down_grid_group_box.isChecked()
        if down_grid_on:
            if len(down_grid) == 0:
                QMessageBox().critical(None, "Ошибка", "Сетка спуска пуста")
                return
            if down_grid_on and not self.__is_strictly_increasing(down_grid):
                QMessageBox().critical(None, "Ошибка", "Сетка спуска должна быть строго возрастающей")
                return

        self.__settings.setValue("grid/on", grid_on)
        self.__settings.setValue("grid/data", grid)

        self.__settings.setValue("donw_grid/on", down_grid_on)
        self.__settings.setValue("down_grid/data", down_grid)

        return super().accept()
