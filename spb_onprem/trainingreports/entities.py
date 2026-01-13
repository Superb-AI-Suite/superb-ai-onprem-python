from typing import Optional

from spb_onprem.base_model import CustomBaseModel, Field


class TrainingReport(CustomBaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    model_id: Optional[str] = Field(None, alias="modelId")
    content_id: Optional[str] = Field(None, alias="contentId")
    description: Optional[str] = None

    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
