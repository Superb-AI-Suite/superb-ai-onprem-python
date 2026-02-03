from typing import Optional, List, Any

from spb_onprem.base_model import CustomBaseModel, Field

from .diagnosis_report_item import DiagnosisReportItem
from ..enums import DiagnosisStatus


class Diagnosis(CustomBaseModel):
    """Diagnosis 엔티티"""
    dataset_id: Optional[str] = Field(None, alias="datasetId", description="Dataset ID")
    id: Optional[str] = Field(None, description="Diagnosis ID")
    name: Optional[str] = Field(None, description="이름")
    description: Optional[str] = Field(None, description="설명")
    status: Optional[DiagnosisStatus] = Field(None, description="상태")
    score_key: Optional[str] = Field(None, alias="scoreKey", description="Score 키")
    score_value: Optional[float] = Field(None, alias="scoreValue", description="Score 값")
    score_unit: Optional[str] = Field(None, alias="scoreUnit", description="Score 단위")
    diagnosis_parameters: Optional[Any] = Field(None, alias="diagnosisParameters", description="파라미터 (JSON)")
    diagnosis_report_items: Optional[List[DiagnosisReportItem]] = Field(
        None, alias="diagnosisReportItems", description="리포트 아이템 목록"
    )
    completed_at: Optional[str] = Field(None, alias="completedAt", description="완료일시")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
