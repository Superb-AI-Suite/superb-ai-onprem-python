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
    """액티비티 스키마 정의"""
    key: Optional[str] = Field(None, description="스키마 키")
    schema_type: Optional[SchemaType] = Field(None, description="데이터 타입 (String, Number, Boolean 등)")
    required: Optional[bool] = Field(None, description="필수 필드 여부")
    default: Optional[Any] = Field(None, description="기본값")


class Activity(CustomBaseModel):
    """
    액티비티 엔터티
    
    데이터 처리 작업의 워크플로우를 정의합니다.
    라벨링, 리뷰, 검증 등의 작업 프로세스를 관리합니다.
    """
    id: Optional[str] = Field(None, alias="id", description="액티비티 고유 식별자")
    dataset_id: Optional[str] = Field(None, alias="datasetId", description="상위 데이터셋 ID")
    
    name: Optional[str] = Field(None, alias="name", description="액티비티 이름")
    description: Optional[str] = Field(None, alias="description", description="액티비티 설명")
    activity_type: Optional[str] = Field(None, alias="type", description="액티비티 타입 (labeling, review 등)")
    
    progress_schema: Optional[List[ActivitySchema]] = Field(None, alias="progressSchema", description="진행상태 스키마 정의")
    parameter_schema: Optional[List[ActivitySchema]] = Field(None, alias="parameterSchema", description="파라미터 스키마 정의")
    
    settings: Optional[dict] = Field(None, alias="settings", description="액티비티 설정 정보")
    
    meta: Optional[dict] = Field(None, alias="meta", description="액티비티 메타데이터")
    
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
