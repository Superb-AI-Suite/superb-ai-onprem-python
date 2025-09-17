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
    액티비티 실행 히스토리 엔터티
    
    액티비티의 개별 실행 기록을 관리합니다.
    작업 진행 상태, 파라미터, 결과를 추적하는 데 사용됩니다.
    """
    id: Optional[str] = Field(None, alias="id", description="액티비티 히스토리 고유 식별자")
    dataset_id: Optional[str] = Field(None, alias="datasetId", description="상위 데이터셋 ID")
    activity_id: Optional[str] = Field(None, alias="jobId", description="실행된 액티비티 ID")
    status: Optional[ActivityStatus] = Field(None, alias="status", description="실행 상태 (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)")
    
    parameters: Optional[dict] = Field(None, alias="parameters", description="실행 파라미터")
    progress: Optional[dict] = Field(None, alias="progress", description="진행 상황 정보")
    
    meta: Optional[dict] = Field(None, alias="meta", description="실행 메타데이터")
    
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시 (ISO 8601)")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시 (ISO 8601)")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")
