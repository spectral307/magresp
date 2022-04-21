import pandas as pd
from typing import NamedTuple
from .sequence import Sequence


class column(NamedTuple):
    name: str
    unit: str

    def __str__(self):
        return f"{self.name}{f', {self.unit}' if self.unit else ''}"


class columns:
    def __init__(self, time: column, etalon: column, dut: column, etalon_pq: column = None):
        self.__time = time
        self.__etalon = etalon
        self.__dut = dut
        self.etalon_pq = etalon_pq

    @property
    def time(self):
        return self.__time

    @property
    def etalon(self):
        return self.__etalon

    @property
    def dut(self):
        return self.__dut


class MRSignal:
    @property
    def cols(self):
        return self.__cols

    # не использовать __init__ напрямую, использовать фабричные методы
    def __init__(self, fs: float, df: pd.DataFrame, time_col: column, etalon_col: column, dut_col: column):
        self.__cols = columns(time_col, etalon_col, dut_col)
        self.df = df
        self.fs = fs
        self.k = None
        self.u0 = None
        self.parts = []

    @classmethod
    def _create_from_vectors(cls, fs, time_vector, etalon_vector, dut_vector,
                             time_col_name, time_col_unit, etalon_col_name, etalon_col_unit, dut_col_name, dut_col_unit):
        time_col = column(time_col_name, time_col_unit)
        etalon_col = column(etalon_col_name, etalon_col_unit)
        dut_col = column(dut_col_name, dut_col_unit)
        df = pd.DataFrame({str(time_col): time_vector,
                           str(etalon_col): etalon_vector,
                           str(dut_col): dut_vector})
        return MRSignal(fs, df, time_col, etalon_col, dut_col)

    @classmethod
    def create_from_gtrfile(cls, gtrfile, etalon_ch_number, dut_ch_number, etalon_ch_name=None, dut_ch_name=None):
        items = gtrfile.read_items(-1, until_eof=True)
        gtl_etalon_ch_name = gtrfile.header["inputs"][etalon_ch_number]["name"]
        gtl_dut_ch_name = gtrfile.header["inputs"][dut_ch_number]["name"]
        if etalon_ch_name is None:
            etalon_ch_name = gtl_etalon_ch_name
        if dut_ch_name is None:
            dut_ch_name = gtl_dut_ch_name
        # etalon_ch_unit = gtrfile.header["inputs"][etalon_ch_number]["unit"]
        # dut_ch_unit = gtrfile.header["inputs"][dut_ch_number]["unit"]
        etalon_ch_unit = "В"
        dut_ch_unit = "В"
        return cls._create_from_vectors(gtrfile.header["rate"], items["t"],
                                        items["s"][gtl_etalon_ch_name], items["s"][gtl_dut_ch_name], "время", "с",
                                        etalon_ch_name, etalon_ch_unit, dut_ch_name, dut_ch_unit)

    def __get_avg_time_block_function(self, block_duration):
        def avg_time_block(group):
            block_ordinal = group.index[0] / self.fs // block_duration
            return block_ordinal * block_duration + block_duration / 2
        return avg_time_block

    def downsample_by_block_averaging(self, block_duration: float, drop_last=True):
        agg_arg = {
            str(self.cols.time): self.__get_avg_time_block_function(block_duration)}
        for col in self.df.columns:
            if col != str(self.cols.time):
                agg_arg[col] = "mean"
        ds_df = self.df.groupby(by=lambda i:
                                i / self.fs // block_duration).agg(agg_arg)
        if drop_last:
            ds_df.drop(ds_df.index[-1], inplace=True)
        return MRSignal(1 / block_duration, ds_df,
                        self.cols.time, self.cols.etalon, self.cols.dut)

    def calculate_etalon_pq_col(self, unit, k, u0):
        self.k = k
        self.u0 = u0
        self.cols.etalon_pq = column(self.cols.etalon.name, unit)
        self.df[str(self.cols.etalon_pq)] = (
            self.df[str(self.cols.etalon)] - u0) / k

    def separate_into_parts(self, sequence):
        self.parts = []
        if sequence == Sequence.UP:
            self.parts.append(self.df)
            self.parts[0].is_up_part = True
            self.parts[0].is_down_part = False
        elif sequence == Sequence.DOWN:
            self.parts.append(self.df)
            self.parts[0].is_up_part = False
            self.parts[0].is_down_part = True
        elif sequence == Sequence.UP_DOWN:
            borderpoint = self.df[str(self.cols.etalon)].idxmax()
            self.parts.append(self.df.loc[:borderpoint])
            self.parts.append(self.df.loc[borderpoint:])
            self.parts[0].is_up_part = True
            self.parts[0].is_down_part = False
            self.parts[1].is_up_part = False
            self.parts[1].is_down_part = True
        elif sequence == Sequence.DOWN_UP:
            borderpoint = self.df[str(self.cols.etalon)].idxmin()
            self.parts.append(self.df.loc[:borderpoint])
            self.parts.append(self.df.loc[borderpoint:])
            self.parts[0].is_up_part = False
            self.parts[0].is_down_part = True
            self.parts[1].is_up_part = True
            self.parts[1].is_down_part = False
        else:
            raise ValueError("sequence")
