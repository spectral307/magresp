# Form implementation generated from reading ui file 'on_save_excel_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.3.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_OnSaveExcelDialog(object):
    def setupUi(self, OnSaveExcelDialog):
        OnSaveExcelDialog.setObjectName("OnSaveExcelDialog")
        OnSaveExcelDialog.resize(280, 180)
        self.buttonBox = QtWidgets.QDialogButtonBox(OnSaveExcelDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 120, 231, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.append_check_box = QtWidgets.QCheckBox(OnSaveExcelDialog)
        self.append_check_box.setGeometry(QtCore.QRect(20, 20, 121, 20))
        self.append_check_box.setObjectName("append_check_box")
        self.direction_combo_box = QtWidgets.QComboBox(OnSaveExcelDialog)
        self.direction_combo_box.setGeometry(QtCore.QRect(130, 50, 131, 22))
        self.direction_combo_box.setObjectName("direction_combo_box")
        self.start_cell_line_edit = QtWidgets.QLineEdit(OnSaveExcelDialog)
        self.start_cell_line_edit.setGeometry(QtCore.QRect(130, 80, 131, 22))
        self.start_cell_line_edit.setObjectName("start_cell_line_edit")
        self.direction_label = QtWidgets.QLabel(OnSaveExcelDialog)
        self.direction_label.setGeometry(QtCore.QRect(20, 50, 81, 16))
        self.direction_label.setObjectName("direction_label")
        self.start_cell_label = QtWidgets.QLabel(OnSaveExcelDialog)
        self.start_cell_label.setGeometry(QtCore.QRect(20, 80, 111, 16))
        self.start_cell_label.setObjectName("start_cell_label")

        self.retranslateUi(OnSaveExcelDialog)
        self.buttonBox.accepted.connect(OnSaveExcelDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(OnSaveExcelDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(OnSaveExcelDialog)

    def retranslateUi(self, OnSaveExcelDialog):
        _translate = QtCore.QCoreApplication.translate
        OnSaveExcelDialog.setWindowTitle(_translate("OnSaveExcelDialog", "Параметры сохранения"))
        self.append_check_box.setText(_translate("OnSaveExcelDialog", "Дописать в файл"))
        self.direction_label.setText(_translate("OnSaveExcelDialog", "Направление:"))
        self.start_cell_label.setText(_translate("OnSaveExcelDialog", "Начальная ячейка:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    OnSaveExcelDialog = QtWidgets.QDialog()
    ui = Ui_OnSaveExcelDialog()
    ui.setupUi(OnSaveExcelDialog)
    OnSaveExcelDialog.show()
    sys.exit(app.exec())
