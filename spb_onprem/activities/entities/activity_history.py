from typing import Optional, Any
from enum import Enum
from spb_onprem.base_model import CustomBaseModel, Field


class ActivityStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ActivityHistory(CustomBaseModel):
    """
    The activity history.
    """
    id: Optional[str] = Field(None, alias="id")
    dataset_id: Optional[str] = Field(None, alias="datasetId")
    activity_id: Optional[str] = Field(None, alias="jobId")
    status: Optional[ActivityStatus] = Field(None, alias="status")
    
    parameters: Optional[dict] = Field(None, alias="parameters")
    progress: Optional[dict] = Field(None, alias="progress")
    
    meta: Optional[dict] = Field(None, alias="meta")
    
    created_at: Optional[str] = Field(None, alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
