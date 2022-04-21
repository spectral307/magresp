import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QDir
from .main_window import MainWindow
from .sequence import Sequence


def load_settings(reset=False):
    settings = QSettings()

    if reset:
        settings.clear()

    if settings.value("default_dir") is None:
        path = QDir.cleanPath(QDir.home().absolutePath() +
                              QDir.separator() + "Documents" +
                              QDir.separator() + "gtlab")
        settings.setValue("default_dir", path)

    if settings.value("show_raw_signals") is None:
        settings.setValue("show_raw_signals", False)

    if settings.value("ds_interval") is None:
        settings.setValue("ds_interval", 0.5)

    if "etalon" not in settings.childGroups():
        settings.beginGroup("etalon")
        settings.setValue("u0", "0.0")
        settings.setValue("k", "1.0")
        settings.setValue("unit", "В")
        settings.endGroup()

    if "channels" not in settings.childGroups():
        settings.beginGroup("channels/etalon")
        settings.setValue("name", "Эталон")
        settings.setValue("use_gtl_name", False)
        settings.setValue("ordinal", 0)
        settings.endGroup()

        settings.beginGroup("channels/dut")
        settings.setValue("name", "Прибор")
        settings.setValue("use_gtl_name", False)
        settings.setValue("ordinal", 1)
        settings.endGroup()

    if settings.value("sequence") is None:
        settings.setValue("sequence", int(Sequence.UP_DOWN))

    if "grid" not in settings.childGroups():
        settings.setValue("grid/on", False)
        settings.setValue("down_grid/on", False)
        settings.setValue("grid/data", [0., 100.])
        settings.setValue("down_grid/data", [0., 100.])


def remove_mr_settings():
    settings = QSettings()
    settings.remove("sequence")
    settings.remove("grid")


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("magresp")
    app.setOrganizationName("GTLab")
    app.setOrganizationDomain("gtlab.pro")

    # remove_mr_settings()
    load_settings(reset=False)

    main = MainWindow()
    main.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
