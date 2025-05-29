from enum import Enum
from typing import Union
from datetime import datetime


class DataMetaTypes(str, Enum):
    """The data meta types."""
    STRING = "String"
    NUMBER = "Number"
    BOOLEAN = "Boolean"
    DATETIME = "DateTime"
    ANNOTATION = "Annotation"


DataMetaValue = Union[str, int, float, bool, datetime, dict, list]
