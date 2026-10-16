# 📁 Dataset Module

Comprehensive guide for dataset management in Superb AI On-premise SDK.

## 🎯 Overview

The Dataset module provides powerful tools for organizing and managing your data collections. Datasets serve as containers that group related data for specific projects or domains.

## ⚡ Quick Start

```python
from spb_onprem.datasets import DatasetService
from spb_onprem.datasets.entities import Dataset

# Initialize service
service = DatasetService()

# Create a new dataset
dataset = service.create_dataset(
    name="My Computer Vision Dataset",
    description="Dataset for object detection training"
)

# Get existing dataset
dataset = service.get_dataset(dataset_id="dataset_123")

# List all datasets with pagination
datasets, cursor, total = service.get_datasets(length=10)
```

## 🏗️ Core Operations

### Dataset Creation
```python
# Create with basic info
dataset = service.create_dataset(
    name="Production Dataset v2.0",
    description="High-quality annotated images for production model"
)

# Dataset will include auto-generated metadata
print(f"Created: {dataset.created_at}")
print(f"ID: {dataset.id}")
```

### Dataset Type
```python
from spb_onprem.datasets import DatasetType

# Create a Vision-Language (VLM) dataset.
# Omit `type` (or pass None) for a Computer Vision dataset.
# The type is set only on creation and cannot be changed later.
vlm_dataset = service.create_dataset(
    name="VLM Fine-tuning Dataset",
    type=DatasetType.VLM,
)

print(vlm_dataset.type)  # DatasetType.VLM (None for a Computer Vision dataset)
```

### Dataset Management
```python
# Update dataset information
updated = service.update_dataset(
    dataset_id="dataset_123",
    name="Updated Dataset Name",
    description="New description with more details"
)

# Delete dataset (use with caution)
service.delete_dataset(dataset_id="dataset_123")
```

### Dataset Listing
```python
# Get all datasets with pagination
datasets, cursor, total = service.get_datasets(length=10)

# Iterate through datasets
for dataset in datasets:
    print(f"{dataset.name}: {dataset.id}")
    
# Get next page if available
if cursor:
    next_datasets, next_cursor, total = service.get_datasets(
        cursor=cursor,
        length=10
    )
```

## 📋 Key Dataset Entity

For detailed entity documentation with comprehensive field descriptions, see the entity file:

### Core Entity
- **[📁 Dataset](entities/dataset.py)** - Main dataset container with detailed field descriptions

The entity file contains:
- **Comprehensive class documentation**
- **Detailed field descriptions with `description` parameter**
- **Field aliases for API compatibility**
- **Usage examples and constraints**

### Quick Entity Overview

```python
from spb_onprem.datasets.entities import Dataset

# Entity relationship example
dataset = Dataset(
    name="Medical Images Dataset",
    description="Annotated medical scans for diagnostic AI training",
    # Timestamps and user info auto-populated by API
)

# Access field descriptions
field_info = Dataset.model_fields
print(f"Name field: {field_info['name'].description}")
print(f"Description field: {field_info['description'].description}")
```

## 🔗 Related Services

- **[📊 Data Service](../data/README.md)** - Manage individual data items within datasets
- **[🔪 Slice Service](../slices/README.md)** - Create filtered views of dataset data  
- **[⚡ Activity Service](../activities/README.md)** - Process dataset workflows
- **[🤖 Models Service](../models/README.md)** - Track ML models and training configurations
- **[📈 Reports Service](../reports/README.md)** - Generate analytics and visualizations

## 📚 Best Practices

### 1. **Dataset Organization**
```python
# Use descriptive names and detailed descriptions
dataset = service.create_dataset(
    name="Autonomous_Driving_Urban_Scenarios_v3.1",
    description="Urban driving scenarios with weather variations, collected Q2 2024"
)
```

### 2. **Lifecycle Management**
```python
# Always check dataset existence before operations
try:
    dataset = service.get_dataset(dataset_id="dataset_123")
    print("Dataset found and accessible")
except Exception as e:
    print(f"Dataset not accessible: {e}")
```

### 3. **Metadata Utilization**
```python
# Use creation metadata for audit trails
dataset = service.get_dataset(dataset_id="dataset_123")
print(f"Dataset created by: {dataset.created_by}")
print(f"Last updated: {dataset.updated_at}")
```

## 🎯 Use Cases

- **🏢 Project Organization**: Group data by project, client, or domain
- **🔄 Version Control**: Maintain different versions of training data
- **👥 Team Collaboration**: Share structured data collections across teams
- **📊 Quality Management**: Organize data by quality levels or validation status
- **🚀 Model Training**: Create focused datasets for specific ML models

---

💡 **Next Steps**: Explore [Data Management](../data/README.md) to learn how to add and manage individual data items within your datasets.