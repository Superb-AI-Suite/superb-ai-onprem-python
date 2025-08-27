from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field


class GeoLocation(CustomBaseModel):
    lat: float
    lon: float


class Frame(CustomBaseModel):
    """
    The frame of the data.
    Frame is the representation of a single frame in a sequence of data, such as a video or time series.
    """
    id: str
    index: Optional[int] = None
    captured_at: Optional[str] = Field(None, alias="capturedAt")
    geo_location: Optional[GeoLocation] = Field(None, alias="geoLocation")
    meta: Optional[dict] = None
