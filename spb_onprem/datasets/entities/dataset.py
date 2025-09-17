from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.entities.data import Data


class Dataset(CustomBaseModel):
    """
    데이터셋 엔터티
    
    데이터를 그룹화하고 관리하는 컨테이너입니다.
    프로젝트별, 도메인별로 데이터를 조직화하는 데 사용됩니다.
    """
    id: Optional[str] = Field(None, description="데이터셋 고유 식별자")
    name: Optional[str] = Field(None, description="데이터셋 이름")
    description: Optional[str] = Field(None, description="데이터셋 설명")

    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
