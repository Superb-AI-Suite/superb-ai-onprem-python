from typing import Optional, Any
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.params import DataListFilter


class Export(CustomBaseModel):
    """
    익스포트 엔터티
    
    데이터와 어노테이션을 외부 시스템에서 사용할 수 있는 형태로 
    내보내기 작업을 정의합니다. 다양한 포맷(COCO, YOLO, Custom)을 지원합니다.
    """
    id: str = Field(..., alias="id", description="익스포트 고유 식별자")
    dataset_id: str = Field(..., alias="datasetId", description="상위 데이터셋 ID")
    
    name: Optional[str] = Field(None, alias="name", description="익스포트 작업 이름")
    data_filter: Optional[DataListFilter] = Field(None, alias="dataFilter", description="내보낼 데이터 필터 조건")
    location: Optional[str] = Field(None, alias="location", description="익스포트 파일 저장 위치")
    
    data_count: Optional[int] = Field(None, alias="dataCount", description="내보낸 데이터 개수")
    annotation_count: Optional[int] = Field(None, alias="annotationCount", description="내보낸 어노테이션 개수")
    frame_count: Optional[int] = Field(None, alias="frameCount", description="내보낸 프레임 개수")
    
    meta: Optional[dict] = Field(None, alias="meta", description="익스포트 메타데이터 (포맷, 옵션 등)")
    
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
    completed_at: Optional[str] = Field(None, alias="completedAt", description="완료일시 (ISO 8601)") 