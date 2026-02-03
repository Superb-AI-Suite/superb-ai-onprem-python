from typing import Optional, List

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.exceptions import BadParameterError

from ..enums import DiagnosisStatus, DiagnosisOrderField, OrderDirection


class DiagnosisOrderBy(CustomBaseModel):
    """Diagnosis 정렬 옵션"""
    field: DiagnosisOrderField
    direction: OrderDirection


class DiagnosisFilterOptions(CustomBaseModel):
    """Diagnosis 필터 옵션"""
    id_in: Optional[List[str]] = Field(None, alias="idIn")
    name_contains: Optional[str] = Field(None, alias="nameContains")
    status_in: Optional[List[DiagnosisStatus]] = Field(None, alias="statusIn")
    created_by_in: Optional[List[str]] = Field(None, alias="createdByIn")
    score_key_in: Optional[List[str]] = Field(None, alias="scoreKeyIn")


class DiagnosisFilter(CustomBaseModel):
    """Diagnosis 필터"""
    must: Optional[DiagnosisFilterOptions] = Field(None, alias="must")
    not_filter: Optional[DiagnosisFilterOptions] = Field(None, alias="not")


def get_diagnoses_params(
    dataset_id: str,
    filter: Optional[DiagnosisFilter] = None,
    order_by: Optional[DiagnosisOrderBy] = None,
    cursor: Optional[str] = None,
    length: int = 10,
):
    if length < 1 or length > 50:
        raise BadParameterError("length must be between 1 and 50.")

    filter_dump = None
    if filter:
        filter_dump = filter.model_dump(by_alias=True, exclude_none=True)

    order_by_dump = None
    if order_by:
        order_by_dump = order_by.model_dump(by_alias=False)

    return {
        "dataset_id": dataset_id,
        "filter": filter_dump,
        "order_by": order_by_dump,
        "cursor": cursor,
        "length": length,
    }
