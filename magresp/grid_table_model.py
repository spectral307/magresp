from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtWidgets import QDoubleSpinBox, QStyledItemDelegate
from math import inf
import numpy as np


class GridItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(5)
        editor.setMinimum(-inf)
        editor.setMaximum(inf)
        return editor


class GridTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = np.zeros((len(data), 3), dtype=np.float64)
        self._data[:, 0] = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return float(self._data[index.row(), index.column()])

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

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
        self._data[row, col] = value
        return True

    def getGrid(self):
        return self._data[:, 0]
