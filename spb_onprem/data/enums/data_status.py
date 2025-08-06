from enum import Enum

class DataStatus(str, Enum):
    """
    데이터의 상태를 나타내는 열거형
    """
    PENDING = "PENDING"
    REQUEST_LABELING = "REQUEST_LABELING"
    LABELING = "LABELING"
    REVIEWING = "REVIEWING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED" 