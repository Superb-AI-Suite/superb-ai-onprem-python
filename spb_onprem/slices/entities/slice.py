from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field


class Slice(CustomBaseModel):
    """
    THE SLICE.
    """
    id: Optional[str] = None
    dataset_id: Optional[str] = Field(None, alias="datasetId")
    name: Optional[str] = None
    description: Optional[str] = None
    is_pinned: Optional[bool] = Field(None, alias="isPinned")
    created_at: Optional[str] = Field(None, alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
