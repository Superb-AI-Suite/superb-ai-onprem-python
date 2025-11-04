from typing import Optional, List, Any
from spb_onprem.base_model import CustomBaseModel, Field
from .analytics_report_item import AnalyticsReportItem


class AnalyticsReport(CustomBaseModel):
    """
    분석 리포트 엔터티
    
    데이터셋의 분석 리포트를 나타냅니다.
    여러 개의 리포트 아이템(차트, 그래프 등)으로 구성됩니다.
    """
    id: Optional[str] = Field(None, description="리포트 고유 식별자")
    dataset_id: Optional[str] = Field(None, alias="datasetId", description="이 리포트가 속한 데이터셋 ID")
    title: Optional[str] = Field(None, description="리포트 제목")
    description: Optional[str] = Field(None, description="리포트 설명")
    meta: Optional[dict] = Field(None, description="추가 메타데이터 (JSONObject)")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
    items: Optional[List[AnalyticsReportItem]] = Field(None, description="리포트 아이템 목록")
