class SegmentError(BaseException):
    def __init__(self, type, grid_value,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type
        self.grid_value = grid_value


class EmptySegmentError(SegmentError):
    pass


class ShortSegmentError(SegmentError):
    pass
