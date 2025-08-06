from typing import List, Optional, Any
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.enums.data_status import DataStatus
from .annotation import Annotation

class DataSlice(CustomBaseModel):
    """
    데이터 슬라이스 정보를 담는 클래스
    """
    id: Optional[str] = None
    status: Optional[DataStatus] = DataStatus.PENDING
    labeler: Optional[str] = None
    reviewer: Optional[str] = None
    tags: Optional[List[str]] = None
    status_changed_at: Optional[str] = Field(None, alias="statusChangedAt")
    annotation: Optional[Annotation] = None
    meta: Optional[Any] = None 