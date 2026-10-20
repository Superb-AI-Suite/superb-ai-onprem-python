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