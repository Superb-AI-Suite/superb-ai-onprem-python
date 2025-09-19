from enum import Enum
from typing import Optional, List
from spb_onprem.base_model import CustomBaseModel, Field


class CommentStatus(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    RESOLVED = "RESOLVED"


class Reply(CustomBaseModel):
    """
    댓글 답글 엔터티
    
    댓글에 대한 답글을 나타냅니다.
    중첩된 토론과 협업을 지원하는 데 사용됩니다.
    """
    id: Optional[str] = Field(None, description="답글 고유 식별자")
    comment: Optional[str] = Field(None, description="답글 내용")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")


class Comment(CustomBaseModel):
    """
    댓글 엔터티
    
    어노테이션에 대한 댓글과 피드백을 관리합니다.
    리뷰 프로세스와 품질 관리에 사용됩니다.
    """
    id: Optional[str] = Field(None, description="댓글 고유 식별자")
    category: Optional[str] = Field(None, description="댓글 카테고리 (질문, 제안, 오류 등)")
    comment: Optional[str] = Field(None, description="댓글 내용")
    status: Optional[CommentStatus] = Field(None, description="댓글 상태 (열림, 해결됨, 닫힘 등)")
    replies: Optional[List[Reply]] = Field(None, description="댓글에 대한 답글 목록")
    meta: Optional[dict] = Field(None, description="댓글 메타데이터")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
    