from typing import List, Optional, Any
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.enums.data_status import DataStatus
from .comment import Comment
from .annotation import Annotation
from .data_annotation_stats import DataAnnotationStat

class DataSlice(CustomBaseModel):
    """
    데이터 슬라이스 멤버십 엔터티
    
    특정 슬라이스 내에서의 데이터 상태와 워크플로 정보를 나타냅니다.
    라벨링, 리뷰 등의 작업 진행 상황을 추적합니다.
    """
    id: Optional[str] = Field(None, description="슬라이스 고유 식별자")
    status: Optional[DataStatus] = Field(DataStatus.PENDING, description="워크플로 상태 (UNLABELED, LABELED, REVIEWED 등)")
    labeler: Optional[str] = Field(None, description="할당된 라벨러")
    reviewer: Optional[str] = Field(None, description="할당된 리뷰어")
    tags: Optional[List[str]] = Field(None, description="슬라이스 태그 목록")
    status_changed_at: Optional[str] = Field(None, alias="statusChangedAt", description="상태 변경일시")
    annotation: Optional[Annotation] = Field(None, description="슬라이스별 어노테이션")
    annotation_stats: Optional[List[DataAnnotationStat]] = Field(None, alias="annotationStats", description="슬라이스 어노테이션 통계")
    comments: Optional[List[Comment]] = Field(None, description="슬라이스에 대한 댓글 및 피드백")
    meta: Optional[dict] = Field(None, description="슬라이스별 메타데이터") 
