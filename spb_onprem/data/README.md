# 📊 Data Service Guide

Complete guide for DataService - Upload, annotate, and manage your data entries.

## 🌟 Overview
DataService is the core service for managing individual data items within datasets. It provides comprehensive CRUD operations, advanced filtering, annotation management, and slice operations.

## 🚀 Quick Start
[간단한 예제 코드]

## 📚 Core Operations

### 1. 🔍 Data Retrieval
- **get_data()** - Retrieve a single data entry by ID
- **get_data_by_key()** - Retrieve a single data entry by key
- **get_data_list()** - Get paginated list of data entries with full details
- **get_data_id_list()** - Get paginated list of data IDs only (lightweight)

### 2. ✏️ Data Management
- **create_data()** - Create a new data entry in the dataset
- **update_data()** - Update data entry key or metadata
- **delete_data()** - Permanently delete a data entry

### 3. 🔧 Slice Operations
#### 3.1 Data-Slice Membership
- **add_data_to_slice()** - Add data entry to a specific slice
- **remove_data_from_slice()** - Remove data entry from a specific slice

#### 3.2 Slice Data Management
- **update_data_slice()** - Update data entry metadata within a slice

#### 3.3 Slice Annotation Management
- **update_slice_annotation()** - Update annotation for data in a specific slice
- **insert_slice_annotation_version()** - Create new annotation version for slice
- **update_slice_annotation_version()** - Update existing slice annotation version
- **delete_slice_annotation_version()** - Delete specific slice annotation version

#### 3.4 Slice Workflow Management
- **change_data_status()** - Change workflow status of data in slice
- **change_data_labeler()** - Assign/change labeler for data in slice
- **change_data_reviewer()** - Assign/change reviewer for data in slice

### 4. 🏷️ Annotation Management
- **update_annotation()** - Update main annotation for data entry
- **insert_annotation_version()** - Create new annotation version
- **delete_annotation_version()** - Delete specific annotation version

## 🎯 Advanced Filtering

Advanced filtering is available for data retrieval operations using `DataListFilter`:
- **get_data_list()** - Filter data entries with full details
- **get_data_id_list()** - Filter data entries (IDs only)

### DataListFilter Usage

#### 1. Basic Usage
```python
from spb_onprem.data.params import DataListFilter, DataFilterOptions

# Simple filter
filter = DataListFilter(
    must_filter=DataFilterOptions(
        type_in=["IMAGE"],
        key_contains="sample_"
    )
)

# Use with data retrieval
data_list, cursor, total = data_service.get_data_list(
    dataset_id="dataset-123",
    data_filter=filter
)
```

#### 2. Common Filter Patterns
```python
# Filter by data type and date range
filter = DataListFilter(
    must_filter=DataFilterOptions(
        type_in=["IMAGE", "VIDEO"],
        created_at={
            "from": "2025-01-01T00:00:00Z",
            "to": "2025-12-31T23:59:59Z"
        }
    )
)

# Filter with metadata
filter = DataListFilter(
    must_filter=DataFilterOptions(
        meta={
            "keyword": [{"key": "category", "equals": "vehicle"}],
            "num": [{"key": "confidence", "range": {"gte": 0.8}}]
        }
    )
)

# Filter by slice status
filter = DataListFilter(
    slice={
        "id": "slice-123",
        "must": {
            "status": {"in": ["LABELED", "REVIEWED"]}
        }
    }
)
```

#### 3. Creating Filters from Dictionary

You can create DataListFilter from dictionary data:

```python
# Method 1: Direct dictionary conversion
filter_dict = {
    "must": {
        "typeIn": ["IMAGE"],
        "keyContains": "sample_",
        "createdAt": {
            "from": "2025-01-01T00:00:00Z",
            "to": "2025-12-31T23:59:59Z"
        }
    }
}

filter = DataListFilter.model_validate(filter_dict)

# Method 2: Build from configuration
config = {
    "data_types": ["IMAGE", "VIDEO"],
    "key_pattern": "sample_",
    "date_from": "2025-01-01T00:00:00Z"
}

filter = DataListFilter(
    must_filter=DataFilterOptions(
        type_in=config["data_types"],
        key_contains=config["key_pattern"],
        created_at={
            "from": config["date_from"]
        }
    )
)

# Important: Use field aliases in dictionary
# Python field names (snake_case) vs API field names (camelCase)
filter_dict = {
    "must": {
        "typeIn": ["IMAGE"],           # Use "typeIn", not "type_in"
        "keyContains": "sample_",      # Use "keyContains", not "key_contains"
        "createdAt": {                 # Use "createdAt", not "created_at"
            "from": "2025-01-01T00:00:00Z"
        }
    }
}

filter = DataListFilter.model_validate(filter_dict)
```

#### 4. Advanced Filter Configuration

For comprehensive filter documentation with detailed examples and field descriptions, see:
**[📂 Filter Parameter Documentation](params/data_list.py)**

The `data_list.py` file contains extensive inline documentation covering:
- **All filter classes and their purposes**
- **Detailed field descriptions and constraints**
- **Practical usage examples for each filter type**
- **API field aliases (camelCase vs snake_case)**
- **Complex filtering scenarios**

Quick reference:
- **`must_filter`**: AND conditions (all must match)
- **`not_filter`**: NOT conditions (none should match)  
- **`slice`**: Slice-specific filtering with slice ID
- **`frames`**: Frame-level filtering for video data

#### 5. Performance Tips

- **Use `get_data_id_list()`** for lightweight queries when you only need IDs
- **Limit length parameter**: Max 50 for both `get_data_list()` and `get_data_id_list()`
- **Use specific filters** rather than broad queries for better performance
- **Combine `id_in` with other filters** to refine large result sets
- **Use `slice_id_in`** to query specific slices efficiently

## 💡 Best Practices

## ⚠️ Error Handling

## � Key Data Entities

For detailed entity documentation with comprehensive field descriptions, see the entity files:

### Core Entities
- **[📄 Data](entities/data.py)** - Main data entity with detailed field descriptions
- **[📝 Annotation & AnnotationVersion](entities/annotation.py)** - Annotation management entities
- **[� Comment & Reply](entities/comment.py)** - Feedback and discussion system for annotations
- **[�🔧 DataSlice](entities/data_slice.py)** - Slice membership and workflow information
- **[🎬 Frame](entities/frame.py)** - Video frame entities with timestamp/geo data
- **[🎭 Scene](entities/scene.py)** - File content representation (images, videos, text)
- **[🏷️ DataMeta](entities/data_meta.py)** - Structured custom metadata entities

Each entity file contains:
- **Comprehensive class documentation**
- **Detailed field descriptions with `description` parameter**
- **Usage examples and constraints**
- **Field aliases for API compatibility**

### Quick Entity Overview

```python
from spb_onprem.data.entities import (
    Data,           # Main data container with metadata, annotations, predictions
    Annotation,     # Annotation management with version control and comments
    Comment,        # Feedback and discussion on annotations
    Reply,          # Threaded replies to comments
    DataSlice,      # Slice membership with workflow status (labeling, review)
    Frame,          # Video frame data with timestamps and geo-location
    Scene,          # File content representation (images, videos, documents)  
    DataMeta,       # Structured custom metadata with type validation
)

# Entity relationship example with comment system
data = Data(
    key="image_001.jpg",
    type=DataType.IMAGE,
    scene=[Scene(type=SceneType.IMAGE, content=image_content)],
    annotation=Annotation(
        meta={"quality": "high"},
        comments=[
            Comment(
                category="질문",
                comment="이 바운딩 박스가 정확한가요?",
                status="열림",
                replies=[
                    Reply(comment="네, 검증 완료했습니다.", created_by="reviewer_01")
                ]
            )
        ]
    ),
    meta=[DataMeta(key="camera_model", value="Canon EOS", type=DataMetaTypes.STRING)]
)
```

## �🔗 Related Services