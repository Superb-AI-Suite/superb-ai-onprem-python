# 🔪 Slices Module

Comprehensive guide for data organization and filtering in Superb AI On-premise SDK.

## 🎯 Overview

The Slices module provides powerful tools for creating filtered views of your dataset. Slices allow you to organize data by criteria like project phases, quality levels, work assignments, or any custom logic without duplicating the underlying data.

## ⚡ Quick Start

```python
from spb_onprem.slices import SliceService
from spb_onprem.slices.entities import Slice

# Initialize service
service = SliceService()

# Create a new slice
slice_obj = service.create_slice(
    dataset_id="dataset_123",
    name="High Quality Images",
    description="Images with quality score > 0.9"
)

# Add data to slice
service.add_data_to_slice(
    dataset_id="dataset_123",
    slice_id=slice_obj.id,
    data_ids=["data_1", "data_2", "data_3"]
)

# Get slice with its data
slice_with_data = service.get_slice(
    dataset_id="dataset_123", 
    slice_id=slice_obj.id
)
```

## 🏗️ Core Operations

### Slice Creation
```python
# Create slice for specific project phase
training_slice = service.create_slice(
    dataset_id="dataset_123",
    name="Training Set v2.1",
    description="Curated training data for model v2.1",
    is_pinned=True  # Pin important slices
)

# Create slice for team assignment
review_slice = service.create_slice(
    dataset_id="dataset_123", 
    name="Review Queue - Team Alpha",
    description="Items assigned to Team Alpha for review"
)
```

### Data Management
```python
# Add multiple data items to slice
service.add_data_to_slice(
    dataset_id="dataset_123",
    slice_id="slice_456", 
    data_ids=["data_001", "data_002", "data_003"]
)

# Remove data from slice
service.remove_data_from_slice(
    dataset_id="dataset_123",
    slice_id="slice_456",
    data_ids=["data_001"]
)

# Get slice data with filtering
slice_data = service.get_slice_data(
    dataset_id="dataset_123",
    slice_id="slice_456",
    filter_options={"status": "LABELED"}
)
```

### Slice Management
```python
# Update slice information
updated_slice = service.update_slice(
    dataset_id="dataset_123",
    slice_id="slice_456",
    name="Updated Training Set v2.2",
    description="Enhanced with additional validation data",
    is_pinned=False
)

# List all slices in dataset
all_slices = service.get_slice_list(dataset_id="dataset_123")

# Delete slice (data remains in dataset)
service.delete_slice(
    dataset_id="dataset_123",
    slice_id="slice_456"
)
```

## 📋 Key Slice Entity

For detailed entity documentation with comprehensive field descriptions, see the entity file:

### Core Entity
- **[🔪 Slice](entities/slice.py)** - Data organization container with detailed field descriptions

The entity file contains:
- **Comprehensive class documentation**
- **Detailed field descriptions with `description` parameter**
- **Field aliases for API compatibility** 
- **Usage examples and constraints**

### Quick Entity Overview

```python
from spb_onprem.slices.entities import Slice

# Entity relationship example
slice_obj = Slice(
    name="Production Ready Dataset",
    description="Final validated data ready for production deployment", 
    is_pinned=True,  # Keep visible in UI
    # Timestamps and user info auto-populated by API
)

# Access field descriptions
field_info = Slice.model_fields
print(f"Name field: {field_info['name'].description}")
print(f"Pinned field: {field_info['is_pinned'].description}")
```

## 🔗 Related Services

- **[📊 Data Service](../data/README.md)** - Manage individual data items within slices
- **[📁 Dataset Service](../datasets/README.md)** - Organize datasets that contain slices
- **[⚡ Activity Service](../activities/README.md)** - Execute workflows on slice data
- **[📤 Export Service](../exports/README.md)** - Export data from specific slices

## 📚 Best Practices

### 1. **Meaningful Slice Organization**
```python
# Use descriptive names that indicate purpose
slices = [
    service.create_slice(name="Training_80pct_HighQuality", description="80% split, quality > 0.95"),
    service.create_slice(name="Validation_20pct_Diverse", description="20% split, diverse scenarios"),
    service.create_slice(name="Edge_Cases_Manual_Review", description="Challenging cases needing human review")
]
```

### 2. **Pin Important Slices**
```python
# Pin frequently used or critical slices
critical_slice = service.create_slice(
    dataset_id="dataset_123",
    name="Production Baseline v1.0", 
    description="Baseline dataset for production model comparison",
    is_pinned=True  # Always visible in UI
)
```

### 3. **Lifecycle Management**
```python
# Clean up temporary slices
temp_slices = service.get_slice_list(dataset_id="dataset_123")
for slice_obj in temp_slices:
    if "temp_" in slice_obj.name and not slice_obj.is_pinned:
        service.delete_slice(dataset_id="dataset_123", slice_id=slice_obj.id)
```

## 🎯 Common Use Cases

### 1. **ML Pipeline Organization**
- **Training/Validation/Test splits**: Separate data for model development
- **Quality-based filtering**: Group by annotation quality or confidence scores
- **Temporal slicing**: Organize by collection date or model version

### 2. **Team Collaboration**
- **Work assignment**: Assign specific data subsets to team members
- **Progress tracking**: Monitor completion status by slice
- **Review workflows**: Create review queues for quality assurance

### 3. **Data Curation**
- **Domain-specific subsets**: Medical scans, outdoor scenes, indoor objects
- **Difficulty levels**: Easy, medium, hard examples for training
- **Error analysis**: Group problematic cases for investigation

## 🚀 Advanced Slice Patterns

### Hierarchical Organization
```python
# Create nested slice structure
parent_slice = service.create_slice(name="Automotive_Dataset_2024", ...)
child_slices = [
    service.create_slice(name="Automotive_Urban_Scenarios", ...),
    service.create_slice(name="Automotive_Highway_Scenarios", ...),
    service.create_slice(name="Automotive_Weather_Variations", ...)
]
```

### Dynamic Slice Management
```python
# Programmatically manage slices based on data properties
def organize_by_quality(dataset_id, quality_threshold=0.9):
    high_quality = service.create_slice(
        dataset_id=dataset_id,
        name=f"High_Quality_gt_{quality_threshold}",
        description=f"Data items with quality > {quality_threshold}"
    )
    
    # Add logic to populate slice based on data analysis
    # ...
```

---

💡 **Next Steps**: Explore [Data Management](../data/README.md) to understand how to work with individual data items, or check [Activities](../activities/README.md) to learn about processing slice data with workflows.