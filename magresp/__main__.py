import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QDir
from .main_window import MainWindow
from .sequence import Sequence
import matplotlib.pyplot as plt
import os.path


def get_default_path():
    path = QDir.cleanPath(QDir.home().absolutePath() +
                          QDir.separator() + "Documents" +
                          QDir.separator() + "gtlab")
    if not os.path.exists(path):
        path = QDir.home().absolutePath()
    return path


def load_settings(reset=False):
    settings = QSettings()

    if reset:
        settings.clear()

    if settings.value("colors") is None:
        default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        colors = {
            "raw": default_colors[0],
            "ds": default_colors[1],
            "up": default_colors[1],
            "down": default_colors[2],
            "top": default_colors[3],
            "bottom": default_colors[3]
        }
        settings.setValue("colors", colors)

    if settings.value("ru_mnemonics") is None:
        ru_mnemonics = {
            Sequence.UP: "подъем",
            Sequence.DOWN: "спуск",
            Sequence.UP_DOWN: "подъем, спуск",
            Sequence.DOWN_UP: "спуск, подъем",
            "up": "подъем",
            "down": "спуск",
            "top": "общий верх",
            "bottom": "общий низ",
            "raw": "исходный",
            "ds": "усредненный",
            "horizontal": "горизонтальное",
            "vertical": "вертикальное"
        }
        settings.setValue("ru_mnemonics", ru_mnemonics)

    if settings.value("gtr_dir") is None:
        settings.setValue("gtr_dir", get_default_path())

    if settings.value("settings_dir") is None:
        settings.setValue("settings_dir", get_default_path())

    if settings.value("reports_dir") is None:
        settings.setValue("reports_dir", get_default_path())

    if settings.value("use_same_gtr_and_reports_dir") is None:
        settings.setValue("use_same_gtr_and_reports_dir", True)

    if settings.value("show_raw_signals") is None:
        settings.setValue("show_raw_signals", False)

    if settings.value("show_raw_magnitude_response") is None:
        settings.setValue("show_raw_magnitude_response", True)

    if settings.value("ds_interval") is None:
        settings.setValue("ds_interval", "0,5")

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
        settings.setValue("grid/margin", 10.)
        settings.setValue("grid/interpolate", True)
        settings.setValue("grid/detector_type", "static")
        settings.setValue("grid/detector_value", -6)

    settings.beginGroup("output")
    if "excel" not in settings.childGroups():
        settings.setValue("excel/append", True)
        settings.setValue("excel/direction", "hor")
        settings.setValue("excel/start_cell", "A1")
    settings.endGroup()


def clear_mr_settings():
    settings = QSettings()
    settings.clear()


def remove_settings(key):
    settings = QSettings()
    settings.remove(key)


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("magresp")
    app.setOrganizationName("GTLab")
    app.setOrganizationDomain("gtlab.pro")

    load_settings(reset=False)

    main = MainWindow()
    main.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
