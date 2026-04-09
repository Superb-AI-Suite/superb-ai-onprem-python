from enum import Enum
from typing import Any, Dict, List, Optional

from spb_onprem.base_model import CustomBaseModel, Field


class WorkflowDefinitionStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"


class WorkflowRunStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class WorkflowNodeExecutionStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class WorkflowNodeType(str, Enum):
    AUTO_LABEL = "AUTO_LABEL"
    TRAIN = "TRAIN"
    DIAGNOSE = "DIAGNOSE"


class WorkflowBindingSourceType(str, Enum):
    TRIGGER = "trigger"
    NODE_OUTPUT = "node_output"
    LITERAL = "literal"


class WorkflowBindingConfig(CustomBaseModel):
    type: WorkflowBindingSourceType = Field(..., description="바인딩 소스 타입")
    path: Optional[str] = Field(None, description="trigger 또는 node output에서 읽을 경로")
    node_key: Optional[str] = Field(None, alias="nodeKey", description="node_output일 때 참조할 node key")
    value: Optional[Any] = Field(None, description="literal 바인딩일 때 사용할 값")


class WorkflowNodeDefinition(CustomBaseModel):
    key: str = Field(..., description="노드 key")
    node_type: WorkflowNodeType = Field(..., alias="nodeType", description="노드 타입")
    job_type: str = Field(..., alias="jobType", description="child job 조회용 job type")
    bindings: Optional[Dict[str, WorkflowBindingConfig]] = Field(
        None,
        description="trigger/node_output/literal 바인딩 규칙",
    )
    required_outputs: Optional[List[str]] = Field(
        None,
        alias="requiredOutputs",
        description="완료 시 필수 output key 목록",
    )
    next_node_key: Optional[str] = Field(
        None,
        alias="nextNodeKey",
        description="다음 node key",
    )


class WorkflowDefinition(CustomBaseModel):
    id: Optional[str] = Field(None, description="Workflow definition ID")
    key: Optional[str] = Field(None, description="Workflow logical key")
    name: Optional[str] = Field(None, description="Workflow 이름")
    description: Optional[str] = Field(None, description="Workflow 설명")
    version: Optional[int] = Field(None, description="Definition 버전")
    status: Optional[WorkflowDefinitionStatus] = Field(None, description="Definition 상태")
    start_node_key: Optional[str] = Field(None, alias="startNodeKey", description="시작 node key")
    trigger_schema: Optional[Dict[str, Any]] = Field(
        None,
        alias="triggerSchema",
        description="수동 시작 입력 검증용 JSON schema",
    )
    nodes: Optional[List[WorkflowNodeDefinition]] = Field(
        None,
        description="Workflow node 목록",
    )
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시")
    created_by: Optional[str] = Field(None, alias="createdBy", description="생성자")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시")
    updated_by: Optional[str] = Field(None, alias="updatedBy", description="수정자")


class WorkflowNodeExecution(CustomBaseModel):
    id: Optional[str] = Field(None, description="Workflow node execution ID")
    workflow_run_id: Optional[str] = Field(None, alias="workflowRunId", description="Workflow run ID")
    node_key: Optional[str] = Field(None, alias="nodeKey", description="실행된 node key")
    node_type: Optional[WorkflowNodeType] = Field(None, alias="nodeType", description="실행된 node 타입")
    job_type: Optional[str] = Field(None, alias="jobType", description="연결된 child job type")
    sequence_no: Optional[int] = Field(None, alias="sequenceNo", description="실행 순번")
    status: Optional[WorkflowNodeExecutionStatus] = Field(None, description="Node 실행 상태")
    job_history_id: Optional[str] = Field(None, alias="jobHistoryId", description="연결된 child job history ID")
    input_snapshot: Optional[Dict[str, Any]] = Field(None, alias="inputSnapshot", description="실행 입력 스냅샷")
    output_snapshot: Optional[Dict[str, Any]] = Field(None, alias="outputSnapshot", description="실행 output 스냅샷")
    error_reason: Optional[str] = Field(None, alias="errorReason", description="실패 사유")
    started_at: Optional[str] = Field(None, alias="startedAt", description="시작 시각")
    completed_at: Optional[str] = Field(None, alias="completedAt", description="종료 시각")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시")


class WorkflowRun(CustomBaseModel):
    id: Optional[str] = Field(None, description="Workflow run ID")
    workflow_definition_id: Optional[str] = Field(
        None,
        alias="workflowDefinitionId",
        description="실행에 사용한 workflow definition ID",
    )
    workflow_key: Optional[str] = Field(None, alias="workflowKey", description="Workflow logical key")
    workflow_version: Optional[str] = Field(None, alias="workflowVersion", description="실행에 사용한 workflow version")
    status: Optional[WorkflowRunStatus] = Field(None, description="Workflow run 상태")
    trigger_input: Optional[Dict[str, Any]] = Field(None, alias="triggerInput", description="수동 시작 trigger input")
    dataset_id: Optional[str] = Field(None, alias="datasetId", description="실행 대상 dataset ID")
    started_by: Optional[str] = Field(None, alias="startedBy", description="시작 사용자")
    current_node_key: Optional[str] = Field(None, alias="currentNodeKey", description="현재 또는 마지막 node key")
    last_node_execution_id: Optional[str] = Field(
        None,
        alias="lastNodeExecutionId",
        description="마지막 node execution ID",
    )
    stop_reason: Optional[str] = Field(None, alias="stopReason", description="중단/실패 사유")
    node_executions: Optional[List[WorkflowNodeExecution]] = Field(
        None,
        alias="nodeExecutions",
        description="Run에 속한 node execution 목록",
    )
    started_at: Optional[str] = Field(None, alias="startedAt", description="시작 시각")
    completed_at: Optional[str] = Field(None, alias="completedAt", description="종료 시각")
    created_at: Optional[str] = Field(None, alias="createdAt", description="생성일시")
    updated_at: Optional[str] = Field(None, alias="updatedAt", description="수정일시")


class WorkflowDefinitionPageInfo(CustomBaseModel):
    items: Optional[List[WorkflowDefinition]] = Field(None, description="Workflow definition 목록")
    next: Optional[str] = Field(None, description="다음 페이지 cursor")
    total_count: Optional[int] = Field(None, alias="totalCount", description="전체 개수")


class WorkflowRunPageInfo(CustomBaseModel):
    items: Optional[List[WorkflowRun]] = Field(None, description="Workflow run 목록")
    next: Optional[str] = Field(None, description="다음 페이지 cursor")
    total_count: Optional[int] = Field(None, alias="totalCount", description="전체 개수")
