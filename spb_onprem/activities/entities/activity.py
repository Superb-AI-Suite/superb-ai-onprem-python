from typing import Optional, List, Any
from enum import Enum
from spb_onprem.base_model import CustomBaseModel, Field


class SchemaType(str, Enum):
    STRING = "String"
    NUMBER = "Number"
    BOOLEAN = "Boolean"
    JSON_OBJECT = "JSONObject"
    DATETIME = "DateTime"


class ActivitySchema(CustomBaseModel):
    key: Optional[str] = None
    schema_type: Optional[SchemaType] = None
    required: Optional[bool] = None
    default: Optional[Any] = None


class Activity(CustomBaseModel):
    id: Optional[str] = Field(None, alias="id")
    dataset_id: Optional[str] = Field(None, alias="datasetId")
    
    name: Optional[str] = Field(None, alias="name")
    description: Optional[str] = Field(None, alias="description")
    activity_type: Optional[str] = Field(None, alias="type")
    
    progress_schema: Optional[List[ActivitySchema]] = Field(None, alias="progressSchema")
    parameter_schema: Optional[List[ActivitySchema]] = Field(None, alias="parameterSchema")
    
    settings: Optional[dict] = Field(None, alias="settings")
    
    meta: Optional[dict] = Field(None, alias="meta")
    
    created_at: Optional[str] = Field(None, alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
