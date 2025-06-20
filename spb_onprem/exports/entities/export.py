from typing import Optional, Any
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.params import DataListFilter


class Export(CustomBaseModel):
    """
    The export entity.
    """
    id: str = Field(..., alias="id")
    dataset_id: str = Field(..., alias="datasetId")
    
    name: Optional[str] = Field(None, alias="name")
    data_filter: Optional[DataListFilter] = Field(None, alias="dataFilter")
    location: Optional[str] = Field(None, alias="location")
    
    data_count: Optional[int] = Field(None, alias="dataCount")
    annotation_count: Optional[int] = Field(None, alias="annotationCount")
    frame_count: Optional[int] = Field(None, alias="frameCount")
    
    meta: Optional[dict] = Field(None, alias="meta")
    
    created_at: Optional[str] = Field(None, alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
    completed_at: Optional[str] = Field(None, alias="completedAt") 