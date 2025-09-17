# 📤 Exports Module

Comprehensive guide for data and annotation export in Superb AI On-premise SDK.

## 🎯 Overview

The Exports module provides powerful tools for exporting your annotated datasets to various formats. Whether you need COCO, YOLO, Pascal VOC, or custom formats, the export system handles format conversion, filtering, and packaging for external systems.

## ⚡ Quick Start

```python
from spb_onprem.exports import ExportService
from spb_onprem.exports.entities import Export
from spb_onprem.data.params import DataListFilter

# Initialize service
service = ExportService()

# Create a simple export
export = service.create_export(
    dataset_id="dataset_123",
    name="COCO Format Export v1.0",
    export_format="COCO",
    data_filter=DataListFilter(
        slice_ids=["slice_456"],
        annotation_status=["REVIEWED"]
    )
)

# Monitor export progress
status = service.get_export(
    dataset_id="dataset_123", 
    export_id=export.id
)
print(f"Export status: {status.status}")
```

## 🏗️ Core Operations

### Export Creation
```python
# Export with advanced filtering
filtered_export = service.create_export(
    dataset_id="dataset_123",
    name="High Quality Training Data",
    export_format="YOLO",
    data_filter=DataListFilter(
        annotation_status=["REVIEWED", "APPROVED"],
        data_types=["IMAGE"],
        created_at_gte="2024-01-01T00:00:00Z"
    ),
    options={
        "include_images": True,
        "include_annotations": True,
        "compression": "zip",
        "split_ratio": {"train": 0.8, "val": 0.2}
    }
)

# Custom format export
custom_export = service.create_export(
    dataset_id="dataset_123", 
    name="Medical AI Format",
    export_format="CUSTOM",
    template_config={
        "annotation_format": "medical_dicom",
        "metadata_fields": ["patient_id", "scan_date"],
        "anonymization": True
    }
)
```

### Export Management
```python
# List all exports for dataset
exports = service.get_export_list(dataset_id="dataset_123")

# Filter exports by status
active_exports = [e for e in exports if e.status == "PROCESSING"]
completed_exports = [e for e in exports if e.status == "COMPLETED"]

# Get export details with file location
export_detail = service.get_export(
    dataset_id="dataset_123",
    export_id="export_789"
)

print(f"Export location: {export_detail.location}")
print(f"Data count: {export_detail.data_count}")
print(f"Annotation count: {export_detail.annotation_count}")
```

### Export Download
```python
# Download completed export
if export_detail.status == "COMPLETED":
    download_url = service.get_export_download_url(
        dataset_id="dataset_123",
        export_id="export_789"
    )
    
    # Use download_url to retrieve the export file
    print(f"Download from: {download_url}")
```

## 📋 Key Export Entity

For detailed entity documentation with comprehensive field descriptions, see the entity file:

### Core Entity
- **[📤 Export](entities/export.py)** - Export job configuration and status with detailed field descriptions

The entity file contains:
- **Comprehensive class documentation**
- **Detailed field descriptions with `description` parameter**
- **Export format specifications**
- **Field aliases for API compatibility**

### Quick Entity Overview

```python
from spb_onprem.exports.entities import Export
from spb_onprem.data.params import DataListFilter

# Entity relationship example
export = Export(
    name="Production Model Training Set",
    data_filter=DataListFilter(slice_ids=["high_quality_slice"]),
    location="s3://exports/coco_format_20241201.zip",
    data_count=15000,
    annotation_count=45000,
    meta={
        "format": "COCO",
        "version": "1.0", 
        "split_config": {"train": 0.8, "val": 0.15, "test": 0.05}
    }
)

# Access field descriptions
field_info = Export.model_fields
print(f"Location field: {field_info['location'].description}")
print(f"Data filter: {field_info['data_filter'].description}")
```

## 🔗 Related Services

- **[📊 Data Service](../data/README.md)** - Source data for exports
- **[📁 Dataset Service](../datasets/README.md)** - Export entire datasets or subsets
- **[🔪 Slice Service](../slices/README.md)** - Export specific data slices
- **[⚡ Activity Service](../activities/README.md)** - Automate export workflows

## 📚 Supported Export Formats

### 1. **Computer Vision Formats**
```python
# COCO format (object detection, segmentation)
coco_export = service.create_export(
    dataset_id="dataset_123",
    name="COCO Detection Export",
    export_format="COCO",
    options={
        "annotation_types": ["bbox", "segmentation"],
        "category_mapping": "auto"
    }
)

# YOLO format (object detection)
yolo_export = service.create_export(
    dataset_id="dataset_123",
    name="YOLO Training Set", 
    export_format="YOLO",
    options={
        "class_names_file": True,
        "image_format": "jpg"
    }
)

# Pascal VOC format
voc_export = service.create_export(
    dataset_id="dataset_123",
    name="Pascal VOC Export",
    export_format="PASCAL_VOC"
)
```

### 2. **Custom Formats**
```python
# Define custom export template
custom_template = {
    "format_name": "medical_annotations",
    "file_structure": {
        "images/": "original_images", 
        "annotations/": "json_annotations",
        "metadata/": "patient_metadata"
    },
    "annotation_schema": {
        "bbox_format": "xyxy",
        "coordinate_system": "image_relative",
        "required_fields": ["diagnosis", "confidence"]
    }
}

medical_export = service.create_export(
    dataset_id="medical_dataset",
    name="Medical AI Training Data",
    export_format="CUSTOM", 
    template_config=custom_template
)
```

## 📚 Best Practices

### 1. **Strategic Export Planning**
```python
# Plan exports by use case
exports = {
    "training": service.create_export(
        name="ML_Training_Set_v2.1",
        data_filter=DataListFilter(slice_ids=["training_slice"]),
        options={"split_ratio": {"train": 0.8, "val": 0.2}}
    ),
    "production": service.create_export(
        name="Production_Baseline_Set", 
        data_filter=DataListFilter(annotation_status=["APPROVED"]),
        options={"include_metadata": True, "quality_threshold": 0.95}
    )
}
```

### 2. **Quality Control**
```python
# Export only high-quality, reviewed data
quality_filter = DataListFilter(
    annotation_status=["REVIEWED", "APPROVED"],
    quality_score_gte=0.9,
    has_annotations=True
)

quality_export = service.create_export(
    dataset_id="dataset_123",
    name="High_Quality_Production_Set",
    data_filter=quality_filter,
    options={"validate_annotations": True}
)
```

### 3. **Export Monitoring**
```python
def monitor_export(dataset_id, export_id):
    """Monitor export progress until completion"""
    while True:
        export = service.get_export(dataset_id, export_id)
        
        if export.status == "COMPLETED":
            print(f"✅ Export completed: {export.location}")
            break
        elif export.status == "FAILED": 
            print(f"❌ Export failed: {export.meta.get('error')}")
            break
        else:
            print(f"⏳ Export in progress... Status: {export.status}")
            time.sleep(30)
```

## 🎯 Common Use Cases

### 1. **ML Pipeline Integration**
- **Training data preparation**: Export annotated datasets for model training
- **Validation sets**: Create consistent validation datasets across experiments
- **Model benchmarking**: Export standardized test sets

### 2. **External System Integration**
- **Third-party tools**: Export to AutoML platforms, annotation tools
- **Data sharing**: Share datasets with partners or research collaborators
- **Backup and archival**: Create point-in-time snapshots of datasets

### 3. **Format Migration**
- **Legacy system support**: Export to older annotation formats
- **Multi-format delivery**: Provide same dataset in multiple formats
- **Custom integration**: Export to proprietary internal formats

## 🚀 Advanced Export Features

### Batch Export Operations
```python
# Export multiple slices simultaneously
batch_exports = []
for slice_id in ["slice_1", "slice_2", "slice_3"]:
    export = service.create_export(
        dataset_id="dataset_123",
        name=f"Batch_Export_{slice_id}",
        data_filter=DataListFilter(slice_ids=[slice_id]),
        export_format="COCO"
    )
    batch_exports.append(export)
```

### Incremental Exports
```python
# Export only newly annotated data
incremental_filter = DataListFilter(
    updated_at_gte="2024-01-01T00:00:00Z",
    annotation_status=["COMPLETED"]
)

incremental_export = service.create_export(
    dataset_id="dataset_123",
    name="Incremental_Update_Jan2024",
    data_filter=incremental_filter
)
```

---

💡 **Next Steps**: Explore [Data Management](../data/README.md) to understand the source data for exports, or check [Activities](../activities/README.md) to automate export workflows as part of your data pipeline.