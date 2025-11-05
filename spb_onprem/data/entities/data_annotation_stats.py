from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field

class DataAnnotationStat(CustomBaseModel):
    type: Optional[str] = Field(None, description="어노테이션 타입")
    group: Optional[str] = Field(None, description="어노테이션 그룹")
    annotation_class: Optional[str] = Field(None, alias="annotationClass", description="어노테이션 클래스")
    sub_class: Optional[str] = Field(None, alias="subClass", description="어노테이션 서브 클래스")
    count: Optional[int] = Field(None, description="어노테이션 개수")