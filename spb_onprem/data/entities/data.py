from typing import List, Optional
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.enums import DataType
from .scene import Scene
from .annotation import Annotation
from .data_meta import DataMeta
from .data_slice import DataSlice
from .frame import Frame
from spb_onprem.contents.entities import BaseContent
from .data_annotation_stats import DataAnnotationStat

class Data(CustomBaseModel):
    """
    메인 데이터 엔터티 - 데이터셋 내의 개별 데이터 항목
    
    데이터는 이미지, 비디오, 텍스트 등 다양한 형태의 컨텐츠를 나타내며,
    어노테이션, 메타데이터, 슬라이스 정보 등을 포함합니다.
    """
    # 식별자
    id: Optional[str] = Field(None, description="데이터 고유 식별자")
    dataset_id: Optional[str] = Field(None, alias="datasetId", description="상위 데이터셋 ID")
    key: Optional[str] = Field(None, description="사용자 정의 고유 키")
    
    # 데이터 타입 및 내용
    type: Optional[DataType] = Field(None, description="데이터 타입 (IMAGE, VIDEO 등)")
    scene: Optional[List[Scene]] = Field(None, description="컨텐츠/파일 정보")
    frames: Optional[List[Frame]] = Field(None, description="프레임 정보 (비디오 데이터용)")
    thumbnail: Optional[BaseContent] = Field(None, description="썸네일 이미지")
    
    # 어노테이션 및 예측
    annotation: Optional[Annotation] = Field(None, description="어노테이션 데이터")
    annotation_stats: Optional[List[DataAnnotationStat]] = Field(None, alias="annotationStats", description="어노테이션 통계 정보")

    # 메타데이터
    meta: Optional[List[DataMeta]] = Field(None, description="커스텀 메타데이터 목록")
    
    # 시간 정보
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
    
    # 슬라이스 정보
    slices: Optional[List[DataSlice]] = Field(None, description="슬라이스 멤버십 정보")
