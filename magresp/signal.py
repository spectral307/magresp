import pandas as pd
from typing import NamedTuple


class Signal:
    class col(NamedTuple):
        name: str
        unit: str

    # не использовать __init__ напрямую, использовать фабричные методы
    def __init__(self, fs, data, time, etalon, dut):
        self.data = data
        self.fs = fs
        self.time = time
        self.etalon = etalon
        self.dut = dut

    @classmethod
    def create_from_vectors(cls, fs, time_vector, etalon_vector, dut_vector,
                            time_name, time_unit, etalon_name, etalon_unit, dut_name, dut_unit):
        time = Signal.col(time_name, time_unit)
        etalon = Signal.col(etalon_name, etalon_unit)
        dut = Signal.col(dut_name, dut_unit)
        data = pd.DataFrame({time.name: time_vector,
                             etalon.name: etalon_vector,
                             dut.name: dut_vector})
        return Signal(fs, data, time, etalon, dut)

    @classmethod
    def create_from_gtrfile(cls, gtrfile, etalon_ch_number, dut_ch_number):
        items = gtrfile.read_items(-1, until_eof=True)
        etalon_ch_name = gtrfile.header["inputs"][etalon_ch_number]["name"]
        dut_ch_name = gtrfile.header["inputs"][dut_ch_number]["name"]
        etalon_ch_unit = gtrfile.header["inputs"][etalon_ch_number]["unit"]
        dut_ch_unit = gtrfile.header["inputs"][dut_ch_number]["unit"]
        return cls.create_from_vectors(gtrfile.header["rate"], items["t"],
                                       items["s"][etalon_ch_name], items["s"][dut_ch_name], "time", "s",
                                       etalon_ch_name, etalon_ch_unit, dut_ch_name, dut_ch_unit)

    def agg_time(self, block_duration):
        def ret(group):
            block_ordinal = group.index[0] / self.fs // block_duration
            return block_ordinal * block_duration + block_duration / 2
        return ret

    def downsample_by_block_averaging(self, block_duration: float, drop_last=True):
        agg_arg = {self.time.name: self.agg_time(block_duration)}
        for col in self.data.columns:
            if col != self.time.name:
                agg_arg[col] = "mean"
        ds_data = self.data.groupby(by=lambda i:
                                    i / self.fs // block_duration).agg(agg_arg)
        if drop_last:
            ds_data.drop(ds_data.index[-1], inplace=True)
        return Signal(1 / block_duration, ds_data,
                      self.time, self.etalon, self.dut)
