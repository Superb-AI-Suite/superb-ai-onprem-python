from enum import Enum


class SceneType(str, Enum):
    """
    The scene type of the data.
    This is used to determine the type of the file.
    """
    IMAGE = "IMAGE"
    MCAP = "MCAP"
    ETC = "ETC"