from typing import List, Optional

from spb_onprem.base_model import CustomBaseModel, Field


class CaptionTarget(CustomBaseModel):
    """
    캡션 대상

    이미지를 가르는 축(target)과 그 축에서 쓸 용어(terms)입니다.
    """
    target: str = Field(..., description="이미지를 가르는 축 (예: vehicle type)")
    terms: List[str] = Field(default_factory=list, description="이 축에서 쓸 용어 (예: truck, bus)")


class DatasetCaptionSettings(CustomBaseModel):
    """
    데이터셋 캡션 설정

    캡션 생성 프롬프트를 만들 때 쓰는 데이터셋 설정입니다.
    ``DatasetService.get_dataset_caption_settings`` 로 읽습니다 (3.0.0).
    """
    dataset_id: Optional[str] = Field(None, alias="datasetId", description="데이터셋 ID")
    data_definition: Optional[str] = Field(
        None,
        alias="dataDefinition",
        description="데이터를 한 문장으로 정의 (최대 100자)",
    )
    caption_targets: Optional[List[CaptionTarget]] = Field(
        None,
        alias="captionTargets",
        description="캡션 대상 목록 (target, terms)",
    )
    excluded_terms: Optional[List[str]] = Field(
        None,
        alias="excludedTerms",
        description="거의 모든 이미지에 공통이라 캡션에서 빼는 요소",
    )
