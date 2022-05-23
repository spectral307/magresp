from PyQt6.QtWidgets import QTableView
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt


class GridTableView(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if (e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter):
            if (self.hasFocus() or self.isPersistentEditorOpen(self.currentIndex())):
                cur_row = self.currentIndex().row()
                self.setCurrentIndex(self.model().index(cur_row + 1, 0))
                if not (cur_row + 1 == self.model().rowCount()):
                    return
        return super().keyPressEvent(e)
