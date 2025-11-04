from typing import Optional, List, Any
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.contents.entities.base_content import BaseContent
from spb_onprem.slices.entities.slice import Slice
from .model_train_class import ModelTrainClass


class Model(CustomBaseModel):
    """
    모델 엔터티
    
    머신러닝 모델의 정보와 학습 상태, 성능 지표를 포함합니다.
    """
    id: Optional[str] = Field(None, description="모델 고유 식별자")
    dataset_id: Optional[str] = Field(None, alias="datasetId", description="이 모델이 속한 데이터셋 ID")
    baseline_model: Optional[str] = Field(None, alias="baselineModel", description="사용된 베이스라인 모델")
    name: Optional[str] = Field(None, description="모델 이름")
    description: Optional[str] = Field(None, description="모델 설명")
    training_classes: Optional[List[ModelTrainClass]] = Field(None, alias="trainingClasses", description="모델의 학습 클래스")
    training_data_count: Optional[int] = Field(None, alias="trainingDataCount", description="학습용 데이터 수")
    validation_data_count: Optional[int] = Field(None, alias="validationDataCount", description="검증용 데이터 수")
    is_pinned: Optional[bool] = Field(None, alias="isPinned", description="모델 즐겨찾기 고정 여부")
    is_trained: Optional[bool] = Field(None, alias="isTrained", description="모델 학습 완료 여부")
    trained_at: Optional[str] = Field(None, alias="trainedAt", description="모델 학습 완료 일시 (ISO 8601)")
    model_content: Optional[BaseContent] = Field(None, alias="modelContent", description="모델 컨텐츠 베이스")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    meta: Optional[Any] = Field(None, description="추가 메타데이터 (JSONObject)")
    training_slices: Optional[List[Slice]] = Field(None, alias="trainingSlices", description="모델의 학습용 슬라이스")
    validation_slices: Optional[List[Slice]] = Field(None, alias="validationSlices", description="모델의 검증용 슬라이스")
