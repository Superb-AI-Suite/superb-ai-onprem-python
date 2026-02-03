from typing import Optional, List

from spb_onprem.base_model import CustomBaseModel, Field

from .diagnosis import Diagnosis


class DiagnosisPageInfo(CustomBaseModel):
    """Diagnosis 목록 조회 결과 (페이징)"""
    diagnoses: Optional[List[Diagnosis]] = Field(None, description="Diagnosis 목록")
    next: Optional[str] = Field(None, description="다음 페이지 커서")
    total_count: Optional[int] = Field(None, alias="totalCount", description="전체 개수")
