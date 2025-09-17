from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.contents.entities import BaseContent


class Prediction(CustomBaseModel):
    """
    ML 모델 예측 결과 엔터티
    
    기계학습 모델이 생성한 예측 결과를 나타냅니다.
    어노테이션과 비교하여 모델 성능을 평가하는 데 사용됩니다.
    """
    set_id: Optional[str] = Field(None, alias="setId", description="예측 세트 식별자 - 같은 모델/버전의 예측들을 그룹화")
    content: Optional[BaseContent] = Field(None, description="예측 결과 파일 (JSON, XML 등)")
    meta: Optional[dict] = Field(None, description="예측 관련 메타데이터 (모델 버전, 신뢰도 점수 등)")
