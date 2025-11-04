from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field


class ModelTrainClass(CustomBaseModel):
    """
    모델 학습 클래스 엔터티
    
    모델 학습에 사용되는 클래스별 정보와 성능 지표를 포함합니다.
    """
    class_name: Optional[str] = Field(None, alias="class", description="모델 학습 클래스 이름")
    annotation_type: Optional[str] = Field(None, alias="annotationType", description="어노테이션 타입")
    ap: Optional[float] = Field(None, description="AP (Average Precision) 점수")
    training_annotations_count: Optional[int] = Field(None, alias="trainingAnnotationsCount", description="학습용 어노테이션 수")
    validation_annotations_count: Optional[int] = Field(None, alias="validationAnnotationsCount", description="검증용 어노테이션 수")
