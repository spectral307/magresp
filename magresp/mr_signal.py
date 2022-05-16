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
        self.__current_sequence = None
        self.parts = []
        self.segments = {"up": [], "down": [], "top": [], "bottom": []}
        self.mr_values = {"up": [], "down": [], "top": [], "bottom": []}
        self.__up_mr_lims = None
        self.__down_mr_lims = None
        self.__mr = []
        self.__parts_calculated_handlers = []
        self.__segments_calculated_handlers = []
        self.__mr_values_calculated_handlers = []
        self.__mr_calculated_handlers = []

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

    def get_by_function(self, fs, block_duration):
        def by_function(i):
            return int(i / fs // block_duration)
        return by_function

    def downsample_by_block_averaging(self, block_duration: float, drop_last=True):
        signal_duration = self.df.iloc[-1, self.df.columns.get_loc(str(
            self.cols.time))] - self.df.iloc[0, self.df.columns.get_loc(str(self.cols.time))]
        if block_duration > signal_duration:
            raise ValueError("Block duration is larger than signal duration")

        agg_arg = {
            str(self.cols.time): self.__get_avg_time_block_function(block_duration)}
        for col in self.df.columns:
            if col != str(self.cols.time):
                agg_arg[col] = "mean"

        ds_df = self.df.groupby(by=self.get_by_function(
            self.fs, block_duration)).agg(agg_arg)

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

    def calculate_parts_by_extremum(self, sequence):
        self.__clear_parts()
        self.__clear_segments()
        self.__clear_mr_values()
        self.__clear_mr()
        self.__current_sequence = None

        if sequence == Sequence.UP:
            self.parts.append(self.df)
            self.parts[0].type = "up"
        elif sequence == Sequence.DOWN:
            self.parts.append(self.df)
            self.parts[0].type = "down"
        elif sequence == Sequence.UP_DOWN:
            maxi, _ = self.__get_max()
            self.parts.append(self.df.loc[:maxi])
            self.parts.append(self.df.loc[maxi:])
            self.parts[0].type = "up"
            self.parts[1].type = "down"
        elif sequence == Sequence.DOWN_UP:
            mini, _ = self.__get_min()
            self.parts.append(self.df.loc[:mini])
            self.parts.append(self.df.loc[mini:])
            self.parts[0].type = "down"
            self.parts[1].type = "up"
        else:
            raise ValueError("sequence")

        for handler in self.__parts_calculated_handlers:
            handler()

    def add_parts_calculated_handler(self, handler):
        if handler in self.__parts_calculated_handlers:
            return
        self.__parts_calculated_handlers.append(handler)

    def remove_parts_calculated_handler(self, handler):
        if handler not in self.__parts_calculated_handlers:
            return
        self.__parts_calculated_handlers.remove(handler)

    def add_segments_calculated_handler(self, handler):
        if handler in self.__segments_calculated_handlers:
            return
        self.__segments_calculated_handlers.append(handler)

    def remove_segments_calculated_handler(self, handler):
        if handler not in self.__segments_calculated_handlers:
            return
        self.__segments_calculated_handlers.remove(handler)

    def add_mr_values_calculated_handler(self, handler):
        if handler in self.__mr_values_calculated_handlers:
            return
        self.__mr_values_calculated_handlers.append(handler)

    def remove_mr_values_calculated_handler(self, handler):
        if handler not in self.__mr_values_calculated_handlers:
            return
        self.__mr_values_calculated_handlers.remove(handler)

    def add_mr_calculated_handler(self, handler):
        if handler in self.__mr_calculated_handlers:
            return
        self.__mr_calculated_handlers.append(handler)

    def remove_mr_calculated_handler(self, handler):
        if handler not in self.__mr_calculated_handlers:
            return
        self.__mr_calculated_handlers.remove(handler)

    def calculate_parts_and_segments_by_grid(self, sequence, margin, grid, down_grid=None):
        self.__clear_parts()
        self.__clear_segments()
        self.__clear_mr_values()
        self.__clear_mr()

        self.__current_sequence = sequence

        down_grid_on = True
        if down_grid is None:
            down_grid = grid
            down_grid_on = False

        if sequence == Sequence.UP:
            maxi, maxv = self.__get_max()
            if maxv >= (grid[-1] - margin) and maxv <= (grid[-1] + margin):
                pass
            elif maxv > (grid[-1] + margin):
                pass
        elif sequence == Sequence.DOWN:
            mini, minv = self.__get_min()
            if minv >= (grid[0] - margin) and minv <= (grid[0] + margin):
                pass
            elif minv < (grid[0] - margin):
                pass
        elif sequence == Sequence.UP_DOWN:
            maxi, maxv = self.__get_max()
            if grid[-1] == down_grid[-1]:
                if maxv >= (grid[-1] - margin) and maxv <= (grid[-1] + margin):
                    top_segment = self.__get_segment(
                        self.df, grid[-1] - margin, grid[-1] + margin)
                    top_segment_start = top_segment.iloc[[0]].index[0]
                    top_segment_end = top_segment.iloc[[-1]].index[0]
                    self.parts.append(self.df.loc[:top_segment_start])
                    self.parts.append(
                        self.df.loc[top_segment_start:top_segment_end])
                    self.parts.append(self.df.loc[top_segment_end:])
                    self.parts[0].type = "up"
                    self.parts[1].type = "top"
                    self.parts[2].type = "down"
                    self.segments["top"].append(top_segment)
                    self.__calculate_up_segments(margin, grid[:-1])
                    self.__calculate_down_segments(margin, grid[:-1])
                elif maxv > (grid[-1] + margin):
                    self.parts.append(self.df.loc[:maxi])
                    self.parts.append(self.df.loc[maxi:])
                    self.parts[0].type = "up"
                    self.parts[1].type = "down"
                    self.__calculate_up_segments(margin, grid)
                    self.__calculate_down_segments(margin, grid)
                else:
                    raise BaseException()
            else:
                if maxv >= (grid[-1] - margin) and maxv <= (grid[-1] + margin):
                    top_segment = self.__get_segment(
                        self.df, grid[-1] - margin, grid[-1] + margin)
                    top_segment_start = top_segment.iloc[[0]].index[0]
                    top_segment_end = top_segment.iloc[[-1]].index[0]
                    self.parts.append(self.df.loc[:top_segment_end])
                    self.parts[0].type = "up"
                elif maxv > (grid[-1] + margin):
                    self.parts.append(self.df.loc[:maxi])
                    self.parts[0].type = "up"
                else:
                    raise BaseException()
                self.__calculate_up_segments(margin, grid)
                if maxv >= (down_grid[-1] - margin) and maxv <= (down_grid[-1] + margin):
                    top_segment = self.__get_segment(
                        self.df, down_grid[-1] - margin, down_grid[-1] + margin)
                    top_segment_start = top_segment.iloc[[0]].index[0]
                    top_segment_end = top_segment.iloc[[-1]].index[0]
                    self.parts.append(self.df.loc[top_segment_start:])
                    self.parts[0].type = "down"
                elif maxv > (down_grid[-1] + margin):
                    self.parts.append(self.df.loc[maxi:])
                    self.parts[0].type = "down"
                else:
                    raise BaseException()
                self.__calculate_down_segments(margin, grid)
        elif sequence == Sequence.DOWN_UP:
            mini, minv = self.__get_min()
            if minv >= (grid[0] - margin) and minv <= (grid[0] + margin):
                bottom_segment = self.__get_segment(
                    self.df, grid[0] - margin, grid[0] + margin)
                bottom_segment_start = bottom_segment.iloc[[0]].index[0]
                bottom_segment_end = bottom_segment.iloc[[-1]].index[0]
                self.parts.append(self.df.loc[:bottom_segment_start])
                self.parts.append(
                    self.df.loc[bottom_segment_start:bottom_segment_end])
                self.parts.append(self.df.loc[bottom_segment_end:])
                self.parts[0].type = "down"
                self.parts[1].type = "bottom"
                self.parts[2].type = "up"
            elif minv < (grid[0] - margin):
                self.parts.append(self.df.loc[:mini])
                self.parts.append(self.df.loc[mini:])
                self.parts[0].type = "down"
                self.parts[1].type = "up"
            else:
                raise BaseException()
        else:
            raise ValueError("sequence")

        for handler in self.__parts_calculated_handlers:
            handler()

        for handler in self.__segments_calculated_handlers:
            handler()

        self.__pick_mr_values(sequence)

    def __pick_mr_values(self, sequence):
        self.__clear_mr()

        for part in self.parts:
            for segment in self.segments[part.type]:
                picked_value = segment.iloc[[-26]]
                self.mr_values[part.type].append(picked_value)
            self.mr_values[part.type].sort(key=lambda item: item.index[0])

        if sequence == Sequence.UP_DOWN:
            self.__mr.extend(self.mr_values["up"])
            up_mr_left_lim = 0
            up_mr_right_lim = len(self.mr_values["up"])
            down_mr_left_lim = len(self.mr_values["up"])
            down_mr_right_lim = len(
                self.mr_values["up"]) + len(self.mr_values["down"])
            if len(self.mr_values["top"]) > 0:
                self.__mr.append(self.mr_values["top"][0])
                up_mr_right_lim += 1
                down_mr_right_lim += 1
            self.__mr.extend(self.mr_values["down"])
            self.__up_mr_lims = (up_mr_left_lim, up_mr_right_lim)
            self.__down_mr_lims = (down_mr_left_lim, down_mr_right_lim)
        elif sequence == Sequence.DOWN_UP:
            raise NotImplementedError()
        elif sequence == Sequence.UP:
            raise NotImplementedError()
        elif sequence == Sequence.DOWN:
            raise NotImplementedError()
        else:
            raise ValueError("sequence")

        for handler in self.__mr_values_calculated_handlers:
            handler()

        for handler in self.__mr_calculated_handlers:
            handler()

    def set_mr_value(self, mr_value_ind, new_xdata_ind):
        print("===> set_mr_value:")
        print("mr_value_ind:", mr_value_ind)
        print("new_xdata_ind:", new_xdata_ind)
        if len(self.__mr) == 0:
            raise BaseException()

        self.__mr[mr_value_ind] = self.df.loc[[new_xdata_ind]]

        print("MR:", self.__mr)
        for item in self.__mr:
            print(type(item))

        print(self.get_up_mr())
        print(self.get_down_mr())
        print(self.get_up_mr_inds())
        print(self.get_down_mr_inds())

        for handler in self.__mr_calculated_handlers:
            handler()

    def get_up_mr(self):
        if self.__up_mr_lims is None:
            return None
        return self.__mr[self.__up_mr_lims[0]:self.__up_mr_lims[1]]

    def get_up_mr_inds(self):
        if self.__up_mr_lims is None:
            return None
        return [item.index[0] for item in self.get_up_mr()]

    def get_down_mr(self):
        if self.__down_mr_lims is None:
            return None
        return self.__mr[self.__down_mr_lims[0]:self.__down_mr_lims[1]]

    def get_down_mr_inds(self):
        if self.__down_mr_lims is None:
            return None
        return [item.index[0] for item in self.get_down_mr()]

    def __get_max(self):
        m = self.df[str(self.cols.etalon_pq)].idxmax()
        return m, self.df.loc[m, str(self.cols.etalon_pq)]

    def __get_min(self):
        m = self.df[str(self.cols.etalon_pq)].idxmin()
        return m, self.df.loc[m, str(self.cols.etalon_pq)]

    def __get_segment(self, signal: pd.DataFrame, lower_limit: float, upper_limit: float):
        slice = signal.loc[(signal[str(self.cols.etalon_pq)] >= lower_limit) &
                           (signal[str(self.cols.etalon_pq)] <= upper_limit)]
        start = slice.index[0]
        end = slice.index[-1]
        ret = self.df.loc[start: end]
        return ret

    def __calculate_up_segments(self, margin, grid):
        up_part = None
        for part in self.parts:
            if part.type == "up":
                up_part = part
        if up_part is None:
            raise BaseException("Up part not found")
        for value in grid:
            self.segments["up"].append(self.__get_segment(
                up_part, value - margin, value + margin))

    def __calculate_down_segments(self, margin, grid):
        down_part = None
        for part in self.parts:
            if part.type == "down":
                down_part = part
        if down_part is None:
            raise BaseException("Down part not found")
        for value in grid:
            self.segments["down"].append(self.__get_segment(
                down_part, value - margin, value + margin))

    def __clear_parts(self):
        self.parts.clear()

    def __clear_segments(self):
        self.segments["top"].clear()
        self.segments["bottom"].clear()
        self.segments["up"].clear()
        self.segments["down"].clear()

    def __clear_mr_values(self):
        self.mr_values["top"].clear()
        self.mr_values["bottom"].clear()
        self.mr_values["up"].clear()
        self.mr_values["down"].clear()

    def __clear_mr(self):
        self.__mr.clear()
        self.__up_mr_lims = None
        self.__down_mr_lims = None
