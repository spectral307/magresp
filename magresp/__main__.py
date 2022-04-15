import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QDir
from .main_window import MainWindow
from .sequence import Sequence


def load_settings():
    settings = QSettings()

    if not settings.value("default_dir"):
        path = QDir.cleanPath(QDir.home().absolutePath() +
                              QDir.separator() + "Documents" +
                              QDir.separator() + "gtlab")
        settings.setValue("default_dir", path)

    if not settings.value("show_raw_signals"):
        settings.setValue("show_raw_signals", False)

    if not settings.value("ds_interval"):
        settings.setValue("ds_interval", 0.5)

    if "etalon" not in settings.childGroups():
        settings.beginGroup("etalon")
        settings.setValue("u0", 0.0)
        settings.setValue("k", 1.0)
        settings.setValue("unit", "В")
        settings.endGroup()

    if "channels" not in settings.childGroups():
        settings.beginGroup("channels")
        settings.setValue("etalon", 0)
        settings.setValue("dut", 1)
        settings.endGroup()

    if not settings.value("sequence"):
        settings.setValue("sequence", 0)


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("magresp")
    app.setOrganizationName("GTLab")
    app.setOrganizationDomain("gtlab.pro")

    load_settings()

    main = MainWindow()
    main.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
