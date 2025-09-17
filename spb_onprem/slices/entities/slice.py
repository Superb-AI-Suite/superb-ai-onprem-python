from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field


class Slice(CustomBaseModel):
    """
    슬라이스 엔터티
    
    데이터셋 내에서 특정 조건으로 필터링된 데이터 그룹입니다.
    프로젝트 단계별, 작업자별, 품질별로 데이터를 분류하고 관리하는 데 사용됩니다.
    """
    id: Optional[str] = Field(None, description="슬라이스 고유 식별자")
    dataset_id: Optional[str] = Field(None, alias="datasetId", description="상위 데이터셋 ID")
    name: Optional[str] = Field(None, description="슬라이스 이름")
    description: Optional[str] = Field(None, description="슬라이스 설명")
    is_pinned: Optional[bool] = Field(None, alias="isPinned", description="즐겨찾기 고정 여부")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
