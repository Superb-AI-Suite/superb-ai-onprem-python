from typing import Optional, Any
from enum import Enum
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.contents.entities.base_content import BaseContent


class AnalyticsReportItemType(str, Enum):
    """분석 리포트 아이템 타입"""
    PIE = "PIE"
    HORIZONTAL_BAR = "HORIZONTAL_BAR"
    VERTICAL_BAR = "VERTICAL_BAR"
    HEATMAP = "HEATMAP"


class AnalyticsReportItem(CustomBaseModel):
    """
    분석 리포트 아이템 엔터티
    
    리포트 내의 개별 차트나 시각화 아이템을 나타냅니다.
    """
    id: Optional[str] = Field(None, description="리포트 아이템 고유 식별자")
    type: Optional[AnalyticsReportItemType] = Field(None, description="리포트 아이템 타입 (PIE, BAR, HEATMAP 등)")
    title: Optional[str] = Field(None, description="리포트 아이템 제목")
    description: Optional[str] = Field(None, description="리포트 아이템 설명")
    content: Optional[BaseContent] = Field(None, description="리포트 아이템 컨텐츠")
    meta: Optional[Any] = Field(None, description="추가 메타데이터 (JSONObject)")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
