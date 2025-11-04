from typing import Optional, List
from spb_onprem.base_model import CustomBaseModel, Field
from .model import Model


class ModelPageInfo(CustomBaseModel):
    """
    모델 페이지 정보 엔터티
    
    모델 목록 조회 시 페이지네이션 정보를 포함합니다.
    """
    models: Optional[List[Model]] = Field(None, description="쿼리와 일치하는 모델 목록")
    next: Optional[str] = Field(None, description="페이지네이션에 사용할 커서")
    total_count: Optional[int] = Field(None, alias="totalCount", description="쿼리와 일치하는 모델의 총 개수")
