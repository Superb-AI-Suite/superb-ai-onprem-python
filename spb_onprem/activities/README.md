# ⚡ Activities Module

Comprehensive guide for workflow management in Superb AI On-premise SDK.

## 🎯 Overview

The Activities module provides powerful tools for defining and executing data processing workflows. Activities represent automated or semi-automated tasks like labeling, review, validation, and quality assurance.

## ⚡ Quick Start

```python
from spb_onprem.activities import ActivityService
from spb_onprem.activities.entities import Activity, ActivityHistory

# Initialize service
service = ActivityService()

# Create a new activity
activity = service.create_activity(
    dataset_id="dataset_123",
    name="Image Labeling Workflow",
    description="Semi-automated object detection labeling",
    activity_type="labeling"
)

# Start activity execution
history = service.start_activity(
    dataset_id="dataset_123",
    activity_id=activity.id,
    parameters={"batch_size": 100, "auto_save": True}
)

# Check execution status
status = service.get_activity_history(
    dataset_id="dataset_123",
    activity_id=activity.id,
    history_id=history.id
)
```

## 🏗️ Core Operations

### Activity Definition
```python
# Create labeling activity with custom schema
activity = service.create_activity(
    dataset_id="dataset_123",
    name="Quality Control Review",
    description="Human review of auto-generated annotations",
    activity_type="review",
    progress_schema=[
        {
            "key": "reviewed_count",
            "schema_type": "Number", 
            "required": True,
            "default": 0
        }
    ],
    parameter_schema=[
        {
            "key": "reviewer_name",
            "schema_type": "String",
            "required": True
        }
    ]
)
```

### Activity Execution
```python
# Start activity with parameters
execution = service.start_activity(
    dataset_id="dataset_123", 
    activity_id="activity_456",
    parameters={
        "reviewer_name": "Alice Smith",
        "quality_threshold": 0.95,
        "batch_size": 50
    }
)

# Monitor execution progress  
progress = service.get_activity_history(
    dataset_id="dataset_123",
    activity_id="activity_456", 
    history_id=execution.id
)

print(f"Status: {progress.status}")
print(f"Progress: {progress.progress}")
```

## 📋 Key Activity Entities

For detailed entity documentation with comprehensive field descriptions, see the entity files:

### Core Entities
- **[⚡ Activity](entities/activity.py)** - Workflow definition with schema and settings
- **[📊 ActivityHistory](entities/activity_history.py)** - Execution records and progress tracking

Each entity file contains:
- **Comprehensive class documentation**
- **Detailed field descriptions with `description` parameter** 
- **Schema validation and type safety**
- **Field aliases for API compatibility**

### Quick Entity Overview

```python
from spb_onprem.activities.entities import Activity, ActivityHistory, ActivityStatus

# Activity definition example
activity = Activity(
    name="Autonomous Annotation Review",
    description="Review AI-generated annotations for accuracy",
    activity_type="review",
    progress_schema=[{"key": "completion_rate", "schema_type": "Number"}],
    parameter_schema=[{"key": "reviewer_id", "schema_type": "String"}]
)

# Execution tracking example  
history = ActivityHistory(
    activity_id="activity_123",
    status=ActivityStatus.RUNNING,
    parameters={"reviewer_id": "user_456"},
    progress={"completion_rate": 0.45, "items_processed": 450}
)
```

## 🗑️ Deletion Activities (2.0.0)

The delete functions start an activity instead of deleting rows at once, so the
files in storage are deleted too (`remove_data_from_slice` deletes no files; it only
takes data out of a slice). Each returns the started `ActivityHistory`.

| Function | Activity type | Parameters sent |
| --- | --- | --- |
| `ModelService.delete_models` | `DELETE_MODEL` | `dataset_id`, `model_filter` |
| `DiagnosisService.delete_diagnoses` | `DELETE_DIAGNOSIS` | `dataset_id`, `diagnosis_filter` |
| `ReportService.delete_analytics_reports` | `DELETE_ANALYTICS_REPORT` | `dataset_id`, `analytics_report_filter` |
| `SliceService.delete_slices` | `DELETE_SLICE` | `dataset_id`, `slice_filter` |
| `DataService.delete_data` | `DELETE_DATA` | `dataset_id`, `data_filter` |
| `DataService.remove_data_from_slice` | `REMOVE_DATA_FROM_SLICE` | `dataset_id`, `slice_id`, `data_filter` |
| `DatasetService.delete_dataset` | `DELETE_DATASET` | `dataset_id` |
| `ModelDeploymentService.delete_model_deployments` | `DELETE_MODEL_DEPLOYMENT` | `dataset_id`, `deployment_filter` |

IDs are sent as the filter `{"must": {"idIn": [...]}}`. A filter model is sent with
its camelCase aliases (`{"must": {...}, "not": {...}}`). The deprecated singular
functions (`delete_model`, `delete_diagnosis`, `delete_analytics_report`,
`delete_slice`) call the plural one with one ID.

An admin of the dataset (Owner, WorkspaceAdmin or DATASET-ADMIN) starts it at
once; another user submits it as `AWAITING_APPROVAL`. `ContentService.delete_content`
is not an activity (a content is a file, not an entity); it raises when storage fails.

```python
from spb_onprem import ActivityService, ActivityStatus, DataService

history = DataService().delete_data(dataset_id="dataset_123", data_ids=["data_1", "data_2"])

# Optional: block until it ends (SUCCESS, FAILED, CANCELED or REJECTED).
# AWAITING_APPROVAL is not an end; TimeoutError reports the last status.
done = ActivityService().wait_for_activity(history.id, dataset_id="dataset_123", timeout=600, poll_interval=5)
if done.status != ActivityStatus.SUCCESS:
    print(done.status, done.meta)
```

## 📜 Listing Runs (2.3.0)

`get_activity_histories` returns one page of the runs (activity histories) of a dataset,
newest first by `createdAt`, as `(runs, next_cursor, total)`. Each run is the same
`ActivityHistory` that `get_activity_history` returns.

```python
from spb_onprem import ActivityService, ActivityStatus

service = ActivityService()

# The newest 10 runs of a dataset
runs, next_cursor, total = service.get_activity_histories("dataset_123")
for run in runs:
    print(run.created_at, run.status, run.activity_id, run.id)

# Filters: one value or a list (any of them matches); filters combine with AND
failed, _, failed_total = service.get_activity_histories(
    "dataset_123",
    activity_id="activity_456",                         # Activity.id (= run.activity_id)
    status=[ActivityStatus.FAILED, ActivityStatus.CANCELED],
    requester="user@example.com",                       # who started it (= run.created_by)
    slice_id="slice_789",                               # started with start_activity(slice_id=...)
    length=50,                                          # 1 to 50, default 10
)

# Every run, oldest first (stable while new runs start)
cursor = None
while True:
    runs, cursor, _ = service.get_activity_histories("dataset_123", cursor=cursor, length=50, oldest_first=True)
    ...
    if cursor is None:
        break
```

| Argument | Platform filter | Notes |
| --- | --- | --- |
| `dataset_id` (required) | `datasetId`, `must.datasetId` | |
| `activity_id` | `must.jobIdIn` | |
| `status` | `must.statusIn` | `ActivityStatus` or its name; `"CANCELLED"` reads as `CANCELED` |
| `requester` | `must.requestedByIn` | email |
| `slice_id` | `must.sliceIdIn` | only runs started with a slice; a slice inside `parameters` does not count |
| `oldest_first` | `orderBy: {field: createdAt, direction: ASC}` | default `DESC` (newest first) |

- The platform has no time-range filter and sorts by `createdAt` only here.
- A user who is not an admin of the dataset (Owner, WorkspaceAdmin, DATASET-ADMIN)
  sees only their own runs; the platform replaces `requester` with that user.
- Every run must belong to `dataset_id`. If the platform returns a run of another
  dataset, nothing is returned and `BadResponseError` is raised.
- An empty list (`status=[]`) is refused with `BadParameterError`: the platform would
  read it as no condition.
- The cursor is an offset. Newest first, a run started while you page pushes the others
  down, so a run can show up twice; page with `oldest_first=True` to see each once. When
  the number of runs is a multiple of `length`, the last page is empty.

## 🔗 Related Services

- **[📊 Data Service](../data/README.md)** - Manage data items processed by activities
- **[📁 Dataset Service](../datasets/README.md)** - Organize datasets for activity execution
- **[🔪 Slice Service](../slices/README.md)** - Target specific data subsets for processing
- **[📈 Reports Service](../reports/README.md)** - Track activity progress and results

## 🎯 Common Activity Types

### 1. **Labeling Activities**
- Manual annotation workflows
- Semi-automated labeling with human review
- Batch labeling operations

### 2. **Quality Assurance**  
- Annotation quality review
- Inter-annotator agreement validation
- Automated quality checks

### 3. **Data Processing**
- Image preprocessing pipelines
- Data augmentation workflows
- Format conversion tasks

---

💡 **Next Steps**: Explore [Data Management](../data/README.md) to understand how activities process individual data items, or check [Slice Management](../slices/README.md) to learn about targeting specific data subsets.