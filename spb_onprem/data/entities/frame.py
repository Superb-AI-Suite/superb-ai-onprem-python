from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field


class GeoLocation(CustomBaseModel):
    """지리적 위치 정보"""
    lat: float = Field(description="위도")
    lon: float = Field(description="경도")


class Frame(CustomBaseModel):
    """
    비디오/시계열 데이터의 프레임 엔터티
    
    비디오나 시계열 데이터의 개별 프레임을 나타냅니다.
    타임스탬프, 지리적 위치, 메타데이터를 포함합니다.
    """
    id: Optional[str] = Field(None, description="프레임 고유 식별자")
    index: Optional[int] = Field(None, description="프레임 인덱스 (시퀀스 내 순서)")
    captured_at: Optional[str] = Field(None, alias="capturedAt", description="촬영/캡처 시간 (ISO 8601)")
    geo_location: Optional[GeoLocation] = Field(None, alias="geoLocation", description="촬영 위치 정보")
    meta: Optional[dict] = Field(None, description="프레임별 메타데이터")
