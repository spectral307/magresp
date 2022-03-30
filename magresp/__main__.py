from json import load as json_load
from rich import print as rich_print
import importlib.resources
import pandas as pd
from gtrfile import GtrFile
from os.path import join
import matplotlib.pyplot as plt
import numpy as np
import warnings


def get_config():
    with importlib.resources.open_text(__package__, "config.json") as file:
        return json_load(file)


def agg_time(fs, block_duration):
    def ret(group):
        block_ordinal = group.index[0] / fs // block_duration
        return block_ordinal * block_duration + block_duration / 2
    return ret


def downsample_by_block_averaging(record: pd.DataFrame, fs: float, block_duration: float, drop_last=True):
    ret = record.groupby(by=lambda i:
                         i / fs // block_duration).agg({"t": agg_time(fs, block_duration), "6V": "mean", "МИДА": "mean"})
    if drop_last:
        ret.drop(ret.index[-1], inplace=True)
    return ret


def main():
    config = get_config()

    record_path = join(config["input"]["dir"], config["input"]["file"])

    gtr = GtrFile(record_path)

    rich_print(gtr.header)

    sequence = config["sequence"]
    print(sequence)

    etalon_ch_number = config["channels"]["etalon"]
    dut_ch_number = config["channels"]["dut"]

    etalon_ch_name = gtr.header["inputs"][etalon_ch_number]["name"]
    dut_ch_name = gtr.header["inputs"][dut_ch_number]["name"]

    etalon_ch_unit = gtr.header["inputs"][etalon_ch_number]["unit"]
    dut_ch_unit = gtr.header["inputs"][dut_ch_number]["unit"]

    print(etalon_ch_name)
    print(dut_ch_name)

    res = gtr.read_items(-1, until_eof=True)
    record = pd.DataFrame(
        data={"t": res["t"],
              etalon_ch_name: res["s"][etalon_ch_name],
              dut_ch_name: res["s"][dut_ch_name]})

    downsampled_record = downsample_by_block_averaging(
        record, gtr.header["rate"], .5)

    plot_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    fig, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(record["t"], record[etalon_ch_name],
               label=etalon_ch_name, zorder=0)
    ax[1].plot(record["t"], record[dut_ch_name], label=dut_ch_name, zorder=0)
    ax[0].scatter(downsampled_record["t"],
                  downsampled_record[etalon_ch_name], color=plot_colors[1], label=etalon_ch_name, zorder=1)
    ax[1].scatter(downsampled_record["t"],
                  downsampled_record[dut_ch_name], color=plot_colors[1], label=dut_ch_name, zorder=1)
    ax[0].grid()
    ax[0].set_xlabel("t, s")
    ax[0].set_ylabel(
        f"{etalon_ch_name}{' ,' if etalon_ch_unit else ''}{etalon_ch_unit}")
    ax[0].autoscale(enable=True, axis="x", tight=True)
    ax[1].grid()
    ax[1].set_xlabel("t, s")
    ax[1].set_ylabel(
        f"{dut_ch_name}{' ,' if dut_ch_unit else ''}{dut_ch_unit}")
    ax[1].autoscale(enable=True, axis="x", tight=True)
    plt.get_current_fig_manager().window.showMaximized()
    plt.show()

    fig, ax = plt.subplots()
    ax.plot(downsampled_record[etalon_ch_name],
            downsampled_record[dut_ch_name])
    ax.grid()
    plt.show()


if __name__ == "__main__":
    main()
