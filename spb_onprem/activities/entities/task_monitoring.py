from enum import Enum
from typing import Any, List, Optional

from spb_onprem.base_model import CustomBaseModel, Field


class TaskMonitoringRunType(str, Enum):
    BASE = "BASE"
    SUB = "SUB"


class MonitoringRunAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    NOT_FOUND = "NOT_FOUND"
    EXPIRED = "EXPIRED"
    UNAVAILABLE = "UNAVAILABLE"


class MonitoringDataAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"


class TaskState(str, Enum):
    NONE = "NONE"
    DEFERRED = "DEFERRED"
    SCHEDULED = "SCHEDULED"
    UP_FOR_RESCHEDULE = "UP_FOR_RESCHEDULE"
    REMOVED = "REMOVED"
    QUEUED = "QUEUED"
    UP_FOR_RETRY = "UP_FOR_RETRY"
    SHUTDOWN = "SHUTDOWN"
    RUNNING = "RUNNING"
    RESTARTING = "RESTARTING"
    FAILED = "FAILED"
    UPSTREAM_FAILED = "UPSTREAM_FAILED"
    SUCCESS = "SUCCESS"
    SKIPPED = "SKIPPED"
    UNKNOWN = "UNKNOWN"


class TaskKind(str, Enum):
    TASK = "TASK"
    DAG_RUN = "DAG_RUN"
    SENSOR = "SENSOR"
    UNKNOWN = "UNKNOWN"


class TaskDataAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    NOT_FOUND = "NOT_FOUND"
    EXPIRED = "EXPIRED"
    UNAVAILABLE = "UNAVAILABLE"


class RenderedTemplateValueType(str, Enum):
    JSON = "JSON"
    TEXT = "TEXT"
    LIST = "LIST"
    UNKNOWN = "UNKNOWN"


class TaskMonitoringDataAvailability(CustomBaseModel):
    run: MonitoringRunAvailability = Field(alias="run")
    graph: MonitoringDataAvailability = Field(alias="graph")
    tasks: MonitoringDataAvailability = Field(alias="tasks")


class TaskMonitoringLinkedRun(CustomBaseModel):
    run_type: TaskMonitoringRunType = Field(alias="runType")
    run_id: str = Field(alias="runId")


class TaskNode(CustomBaseModel):
    id: str = Field(alias="id")
    task_id: str = Field(alias="taskId")
    label: str = Field(alias="label")
    kind: TaskKind = Field(alias="kind")
    state: TaskState = Field(alias="state")
    raw_state: Optional[str] = Field(None, alias="rawState")
    duration_seconds: Optional[float] = Field(None, alias="durationSeconds")
    started_at: Optional[str] = Field(None, alias="startedAt")
    ended_at: Optional[str] = Field(None, alias="endedAt")
    attempt: Optional[int] = Field(None, alias="attempt")
    task_run_index: Optional[int] = Field(None, alias="taskRunIndex")


class TaskEdge(CustomBaseModel):
    id: str = Field(alias="id")
    source: str = Field(alias="source")
    target: str = Field(alias="target")


class TaskMonitoring(CustomBaseModel):
    run_type: TaskMonitoringRunType = Field(alias="runType")
    run_id: str = Field(alias="runId")
    run_state: Optional[str] = Field(None, alias="runState")
    data_availability: TaskMonitoringDataAvailability = Field(
        alias="dataAvailability"
    )
    linked_run: Optional[TaskMonitoringLinkedRun] = Field(None, alias="linkedRun")
    nodes: List[TaskNode] = Field(default_factory=list, alias="nodes")
    edges: List[TaskEdge] = Field(default_factory=list, alias="edges")


class TaskKubernetesRuntime(CustomBaseModel):
    pod_name: Optional[str] = Field(None, alias="podName")
    namespace: Optional[str] = Field(None, alias="namespace")
    image: Optional[str] = Field(None, alias="image")
    container_name: Optional[str] = Field(None, alias="containerName")
    node_name: Optional[str] = Field(None, alias="nodeName")
    pod_phase: Optional[str] = Field(None, alias="podPhase")


class TaskRuntimeDetail(CustomBaseModel):
    executor: Optional[str] = Field(None, alias="executor")
    queue: Optional[str] = Field(None, alias="queue")
    pool: Optional[str] = Field(None, alias="pool")
    pool_slots: Optional[float] = Field(None, alias="poolSlots")
    hostname: Optional[str] = Field(None, alias="hostname")
    unixname: Optional[str] = Field(None, alias="unixname")
    pid: Optional[int] = Field(None, alias="pid")
    priority_weight: Optional[float] = Field(None, alias="priorityWeight")
    queued_at: Optional[str] = Field(None, alias="queuedAt")
    scheduled_at: Optional[str] = Field(None, alias="scheduledAt")
    external_executor_id: Optional[str] = Field(None, alias="externalExecutorId")
    kubernetes: Optional[TaskKubernetesRuntime] = Field(None, alias="kubernetes")


class TaskDetail(CustomBaseModel):
    availability: TaskDataAvailability = Field(alias="availability")
    task_id: str = Field(alias="taskId")
    task_run_index: Optional[int] = Field(None, alias="taskRunIndex")
    label: Optional[str] = Field(None, alias="label")
    state: TaskState = Field(alias="state")
    raw_state: Optional[str] = Field(None, alias="rawState")
    operator: Optional[str] = Field(None, alias="operator")
    trigger_rule: Optional[str] = Field(None, alias="triggerRule")
    started_at: Optional[str] = Field(None, alias="startedAt")
    ended_at: Optional[str] = Field(None, alias="endedAt")
    duration_seconds: Optional[float] = Field(None, alias="durationSeconds")
    attempt: Optional[int] = Field(None, alias="attempt")
    max_attempts: Optional[int] = Field(None, alias="maxAttempts")
    runtime: Optional[TaskRuntimeDetail] = Field(None, alias="runtime")


class TaskRenderedTemplateSection(CustomBaseModel):
    key: str = Field(alias="key")
    value: Optional[Any] = Field(None, alias="value")
    value_type: RenderedTemplateValueType = Field(alias="valueType")


class TaskRenderedTemplates(CustomBaseModel):
    availability: TaskDataAvailability = Field(alias="availability")
    task_id: str = Field(alias="taskId")
    task_run_index: Optional[int] = Field(None, alias="taskRunIndex")
    sections: List[TaskRenderedTemplateSection] = Field(
        default_factory=list,
        alias="sections",
    )


class TaskLogMetadata(CustomBaseModel):
    line_count: Optional[int] = Field(None, alias="lineCount")
    size_bytes: Optional[int] = Field(None, alias="sizeBytes")
    started_at: Optional[str] = Field(None, alias="startedAt")
    ended_at: Optional[str] = Field(None, alias="endedAt")


class TaskLogChunk(CustomBaseModel):
    availability: TaskDataAvailability = Field(alias="availability")
    task_id: str = Field(alias="taskId")
    task_run_index: Optional[int] = Field(None, alias="taskRunIndex")
    attempt: Optional[int] = Field(None, alias="attempt")
    content: Optional[str] = Field(None, alias="content")
    next_cursor: Optional[str] = Field(None, alias="nextCursor")
    has_more: bool = Field(alias="hasMore")
    is_complete: bool = Field(alias="isComplete")
    metadata: Optional[TaskLogMetadata] = Field(None, alias="metadata")


class TaskLogDownload(CustomBaseModel):
    availability: TaskDataAvailability = Field(alias="availability")
    task_id: str = Field(alias="taskId")
    task_run_index: Optional[int] = Field(None, alias="taskRunIndex")
    attempt: Optional[int] = Field(None, alias="attempt")
    content: Optional[str] = Field(None, alias="content")
    download_filename: Optional[str] = Field(None, alias="downloadFilename")
    line_count: Optional[int] = Field(None, alias="lineCount")
    is_tail: bool = Field(alias="isTail")
