from typing import Optional
from sdk.base_model import CustomBaseModel, Field
from sdk.data.entities.data import Data


class Dataset(CustomBaseModel):
    id: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)

    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
