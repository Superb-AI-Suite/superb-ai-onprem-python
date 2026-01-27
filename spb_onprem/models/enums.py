from enum import Enum


class ModelStatus(str, Enum):
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ModelTaskType(str, Enum):
    OBJECT_DETECTION = "OBJECT_DETECTION"
    INSTANCE_SEGMENTATION = "INSTANCE_SEGMENTATION"
    OCR = "OCR"


class ModelOrderField(str, Enum):
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    COMPLETED_AT = "completedAt"
    NAME = "name"
    SCORE_VALUE = "scoreValue"


class OrderDirection(str, Enum):
    ASC = "ASC"
    DESC = "DESC"
