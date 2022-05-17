from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtWidgets import QDoubleSpinBox, QStyledItemDelegate
from math import inf


class GridItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(3)
        editor.setMinimum(-inf)
        editor.setMaximum(inf)
        return editor


class GridTableModel(QAbstractTableModel):
    def __init__(self, data, unit):
        super().__init__()
        self._data = []
        for i, el in enumerate(data):
            self._data.append([float(el), 0, 0])
        self.__header_labels = [unit, "+", "-"]

    def data(self, index, role):
        row = index.row()
        col = index.column()
        if col >= 1:
            return
        if role == Qt.ItemDataRole.EditRole:
            return self._data[row][col]
        if role == Qt.ItemDataRole.DisplayRole:
            return "{:.3f}".format(self._data[row][col]).replace(".", ",")

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        if len(self._data) == 0:
            return 0
        return len(self._data[0])

    def flags(self, index):
        flags = super().flags(index)

        flags |= Qt.ItemFlag.ItemIsEditable
        flags |= Qt.ItemFlag.ItemIsSelectable
        flags |= Qt.ItemFlag.ItemIsEnabled
        flags |= Qt.ItemFlag.ItemIsDragEnabled
        flags |= Qt.ItemFlag.ItemIsDropEnabled

        return flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        row = index.row()
        col = index.column()
        if col >= 1:
            return False
        self._data[row][col] = value
        return True

    def insertRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertRows(parent, row, row+count-1)
        for i in range(count):
            self._data.insert(row, [0, 0, 0])
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveRows(parent, row, row+count-1)
        for i in range(count):
            self._data.pop(row)
        self.endRemoveRows()
        return True

    def clear(self):
        self.removeRows(0, self.rowCount())

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.__header_labels[section]
        return super().headerData(section, orientation, role)

    def getGrid(self):
        return [el[0] for el in self._data]

    def getRow(self, row):
        return self._data[row]

    def getRowIndex(self, row):
        return self._data.index(row)
