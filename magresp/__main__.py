import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QDir
from .main_window import MainWindow
from .sequence import Sequence
import matplotlib.pyplot as plt


def load_settings(reset=False):
    settings = QSettings()

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
            "top": "верх",
            "bottom": "низ",
            "raw": "исходный",
            "ds": "усредненный"
        }
        settings.setValue("ru_mnemonics", ru_mnemonics)

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
        settings.setValue("grid/margin", 10.)


def remove_mr_settings():
    settings = QSettings()
    # settings.clear()
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
