from typing import Optional, List

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.contents.entities import BaseContent
from .comment import Comment


class AnnotationVersion(CustomBaseModel):
    """
    어노테이션 버전 엔터티
    
    어노테이션의 특정 버전을 나타내며, 실제 어노테이션 파일 내용과 
    버전별 메타데이터를 포함합니다.
    """
    id: Optional[str] = Field(None, description="버전 고유 식별자")
    channels: Optional[List[str]] = Field(None, description="데이터 채널 목록 (rgb, depth 등)")
    version: Optional[str] = Field(None, description="버전 문자열 (v1.0, v2.1 등)")
    content: Optional[BaseContent] = Field(None, description="어노테이션 파일 컨텐츠")
    meta: Optional[dict] = Field(None, description="버전별 메타데이터")


class Annotation(CustomBaseModel):
    """
    어노테이션 엔터티
    
    데이터의 어노테이션 정보를 관리하며, 여러 버전의 어노테이션과
    댓글 기반 피드백 시스템을 포함할 수 있습니다.
    """
    versions: Optional[List[AnnotationVersion]] = Field(None, description="어노테이션 버전 목록")
    comments: Optional[List[Comment]] = Field(None, description="어노테이션에 대한 댓글 및 피드백")
    meta: Optional[dict] = Field(None, description="메인 어노테이션 메타데이터")

