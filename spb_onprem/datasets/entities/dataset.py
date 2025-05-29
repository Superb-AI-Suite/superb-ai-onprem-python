from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.entities.data import Data


class Dataset(CustomBaseModel):
    id: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)

    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
