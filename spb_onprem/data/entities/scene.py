from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.enums import SceneType
from spb_onprem.contents.entities import BaseContent

class Scene(CustomBaseModel):
    """
    데이터의 씬(Scene) 엔터티
    
    데이터의 실제 파일 표현을 나타냅니다.
    이미지, 비디오, 텍스트 파일 등의 컨텐츠 정보를 포함합니다.
    """
    id: Optional[str] = Field(None, description="씬 고유 식별자")
    type: Optional[SceneType] = Field(None, description="씬 타입 (IMAGE, VIDEO, TEXT 등)")
    content: Optional[BaseContent] = Field(None, description="실제 파일 컨텐츠 정보")
    meta: Optional[dict] = Field(None, description="씬별 메타데이터")
