from typing import Optional

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType


class DiagnosisReportItem(CustomBaseModel):
    """Diagnosis 리포트 아이템 엔티티"""
    id: Optional[str] = Field(None, description="리포트 아이템 ID")
    diagnosis_id: Optional[str] = Field(None, alias="diagnosisId", description="Diagnosis ID")
    name: Optional[str] = Field(None, description="이름")
    type: Optional[AnalyticsReportItemType] = Field(None, description="타입")
    content_id: Optional[str] = Field(None, alias="contentId", description="컨텐츠 ID")
    description: Optional[str] = Field(None, description="설명")
    discriminator_value: Optional[str] = Field(None, alias="discriminatorValue", description="Discriminator 값 (e.g., '0.5')")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
