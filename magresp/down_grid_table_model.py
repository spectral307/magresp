from PyQt6.QtCore import Qt, QAbstractTableModel


class DownGridTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            print(self._data)
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
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
        self._data[row][col] = value
        return True
