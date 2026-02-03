from enum import Enum


class DiagnosisStatus(str, Enum):
    """Diagnosis 상태 (모델과 동일하되 PREPARING 제외)"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
