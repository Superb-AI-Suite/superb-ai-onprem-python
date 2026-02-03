from .service import DiagnosisService
from .entities import (
    Diagnosis,
    DiagnosisReportItem,
    DiagnosisReportItemType,
    DiagnosisPageInfo,
    DiagnosisStatus,
    DiagnosisOrderField,
    OrderDirection,
)
from .params import (
    DiagnosisFilter,
    DiagnosisFilterOptions,
    DiagnosisOrderBy,
)

# spb_onprem __init__.py 호환용 별칭
DiagnosesFilter = DiagnosisFilter
DiagnosesFilterOptions = DiagnosisFilterOptions

__all__ = (
    "DiagnosisService",
    "Diagnosis",
    "DiagnosisReportItem",
    "DiagnosisReportItemType",
    "DiagnosisPageInfo",
    "DiagnosisStatus",
    "DiagnosisOrderField",
    "OrderDirection",
    "DiagnosisFilter",
    "DiagnosisFilterOptions",
    "DiagnosisOrderBy",
    "DiagnosesFilter",
    "DiagnosesFilterOptions",
)
