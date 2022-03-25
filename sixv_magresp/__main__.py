from json import load as json_load
from rich import print as rich_print
import importlib.resources
import pandas as pd
from gtrfile import GtrFile
from os.path import join
import matplotlib.pyplot as plt


def get_config():
    with importlib.resources.open_text(__package__, "config.json") as file:
        return json_load(file)


def main():
    config = get_config()

    record_path = join(config["input"]["dir"], config["input"]["file"])

    gtr = GtrFile(record_path)

    rich_print(gtr.header)

    etalon_ch_number = config["channels"]["etalon"]
    dut_ch_number = config["channels"]["dut"]

    etalon_ch_name = gtr.header["inputs"][etalon_ch_number]["name"]
    dut_ch_name = gtr.header["inputs"][dut_ch_number]["name"]

    print(etalon_ch_name)
    print(dut_ch_name)

    res = gtr.read_items(-1, until_eof=True)
    record = pd.DataFrame(
        data={"t": res["t"],
              etalon_ch_name: res["s"][etalon_ch_name],
              dut_ch_name: res["s"][dut_ch_name]})

    ax = plt.subplot()
    ax.plot(record["t"], record[etalon_ch_name], label=etalon_ch_name)
    ax.plot(record["t"], record[dut_ch_name], label=dut_ch_name)
    ax.grid()
    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
