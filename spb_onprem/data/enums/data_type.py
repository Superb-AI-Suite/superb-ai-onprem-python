from enum import Enum


class DataType(str, Enum):
    """
    The type of the data.
    This is used to determine the type of the data.
    """
    SUPERB_IMAGE = "SUPERB_IMAGE"
    SUPERB_VIDEO = "SUPERB_VIDEO"
    MCAP = "MCAP"
    SUPERB_3D = "SUPERB_3D"
