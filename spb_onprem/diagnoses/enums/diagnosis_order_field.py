from enum import Enum


class DiagnosisOrderField(str, Enum):
    """Diagnosis 목록 정렬 필드"""
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    COMPLETED_AT = "completedAt"
    NAME = "name"
    SCORE_VALUE = "scoreValue"
