# 🤖 Models Module

Manage machine learning models, training configurations, and performance metrics in your Superb AI datasets.

## 📋 Table of Contents
- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Key Concepts](#-key-concepts)
- [Key Model Entities](#-key-model-entities)
- [Common Use Cases](#-common-use-cases)
- [Advanced Usage](#-advanced-usage)
- [Best Practices](#-best-practices)

## 🎯 Overview

The Models module provides comprehensive model lifecycle management capabilities:
- **📊 Model Registration**: Create and track ML models with training metadata
- **🎓 Training Configuration**: Define training and validation datasets using slices
- **📈 Performance Tracking**: Store class-level metrics (AP scores, annotation counts)
- **🔖 Version Management**: Pin important models and track training history
- **🔄 Model Updates**: Update model metadata, content, and training status

## 🚀 Quick Start

### Initialize the Service

```python
from spb_onprem import ModelService

# Create service instance
model_service = ModelService()
```

### Basic Model Operations

```python
# 1. List models in a dataset
models, next_cursor, total_count = model_service.get_models(
    dataset_id="dataset_123",
    length=10
)

print(f"Found {total_count} models")
for model in models:
    print(f"- {model.name} (Baseline: {model.baseline_model})")
    print(f"  Trained: {model.is_trained}, Pinned: {model.is_pinned}")

# 2. Get a specific model
model = model_service.get_model(
    dataset_id="dataset_123",
    model_id="model_456"
)

print(f"Model: {model.name}")
print(f"Training data: {model.training_data_count}")
print(f"Validation data: {model.validation_data_count}")

# 3. Create a new model
from spb_onprem.models.entities import ModelTrainClass

new_model = model_service.create_model(
    dataset_id="dataset_123",
    name="YOLOv8 Detection Model v1",
    baseline_model="yolov8n",
    description="Object detection model for vehicle detection",
    training_slice_ids=["slice_train_001"],
    validation_slice_ids=["slice_val_001"],
    training_classes=[
        ModelTrainClass(
            class_name="car",
            annotation_type="box",
            ap=0.85,
            training_annotations_count=1500,
            validation_annotations_count=300
        ),
        ModelTrainClass(
            class_name="truck",
            annotation_type="box",
            ap=0.78,
            training_annotations_count=800,
            validation_annotations_count=200
        )
    ]
)

print(f"✅ Created model: {new_model.id}")
```

## 🔑 Key Concepts

### Model Entity Structure

```python
Model:
  - id: Unique identifier
  - dataset_id: Parent dataset
  - name: Model name
  - baseline_model: Base architecture (e.g., "yolov8n", "resnet50")
  - training_classes: Per-class performance metrics
  - training_slices: Slices used for training
  - validation_slices: Slices used for validation
  - model_content: Trained model file reference
  - is_trained: Training completion status
  - is_pinned: Favorite/important model flag
```

### Training Classes

Each model can track per-class metrics:

```python
ModelTrainClass:
  - class: Class name (e.g., "car", "person")
  - annotation_type: Type of annotation (e.g., "box", "polygon")
  - ap: Average Precision score (0.0 - 1.0)
  - training_annotations_count: Number of training annotations
  - validation_annotations_count: Number of validation annotations
```

## 📋 Key Model Entities

For detailed entity documentation with comprehensive field descriptions, see the entity files:

### Core Entities
- **[🤖 Model](entities/model.py)** - Main model entity with training configuration and metrics
- **[📊 ModelTrainClass](entities/model_train_class.py)** - Class-level performance metrics
- **[📄 ModelPageInfo](entities/model_page_info.py)** - Pagination information for model lists

Each entity file contains:
- **Comprehensive class documentation**
- **Detailed field descriptions with `description` parameter**
- **Usage examples and constraints**
- **Field aliases for API compatibility**

### Quick Entity Overview

```python
from spb_onprem.models.entities import Model, ModelTrainClass

# Entity relationship example
model = Model(
    name="YOLOv8 Vehicle Detector",
    baseline_model="yolov8n",
    description="Real-time vehicle detection",
    training_classes=[
        ModelTrainClass(
            class_name="car",
            annotation_type="box",
            ap=0.85
        )
    ]
)

# Access field descriptions
field_info = Model.model_fields
print(f"Name field: {field_info['name'].description}")
print(f"Baseline model field: {field_info['baseline_model'].description}")
```

## 💼 Common Use Cases

### 1. Track Model Training Progress

```python
# Create model before training
model = model_service.create_model(
    dataset_id="dataset_123",
    name="Detection Model v1",
    baseline_model="yolov8n",
    training_slice_ids=["slice_train"],
    validation_slice_ids=["slice_val"],
    is_trained=False  # Not trained yet
)

# ... training happens externally ...

# Update after training completes
from datetime import datetime

updated_model = model_service.update_model(
    dataset_id="dataset_123",
    model_id=model.id,
    is_trained=True,
    trained_at=datetime.now().isoformat(),
    training_classes=[
        ModelTrainClass(
            class_name="vehicle",
            annotation_type="box",
            ap=0.87,
            training_annotations_count=2000,
            validation_annotations_count=500
        )
    ],
    model_content_id="content_trained_weights_001"
)

print(f"✅ Training completed at {updated_model.trained_at}")
```

### 2. Compare Model Performance

```python
from spb_onprem.models.params import ModelsFilter, ModelsFilterOptions

# Get all trained models
models_filter = ModelsFilter(
    must_filter=ModelsFilterOptions(
        is_trained=True
    )
)

models, _, total = model_service.get_models(
    dataset_id="dataset_123",
    models_filter=models_filter,
    length=50
)

# Compare performance
for model in sorted(models, key=lambda m: m.trained_at or "", reverse=True):
    print(f"\n{model.name} ({model.baseline_model})")
    print(f"  Trained: {model.trained_at}")
    print(f"  Training data: {model.training_data_count}")
    
    if model.training_classes:
        avg_ap = sum(tc.ap or 0 for tc in model.training_classes) / len(model.training_classes)
        print(f"  Average AP: {avg_ap:.3f}")
        
        for tc in model.training_classes:
            print(f"    - {tc.class_name}: AP={tc.ap:.3f}")
```

### 3. Pin Best Performing Models

```python
# Pin a production-ready model
pinned_model = model_service.pin_model(
    dataset_id="dataset_123",
    model_id="model_best_v5"
)

print(f"✅ Pinned model: {pinned_model.name}")

# Filter to show only pinned models
pinned_filter = ModelsFilter(
    must_filter=ModelsFilterOptions(
        is_pinned=True
    )
)

pinned_models, _, _ = model_service.get_models(
    dataset_id="dataset_123",
    models_filter=pinned_filter
)

print(f"\n📌 Pinned models ({len(pinned_models)}):")
for model in pinned_models:
    print(f"  - {model.name}")
```

### 4. Experiment Tracking

```python
# Track multiple training experiments
experiments = [
    {
        "name": "YOLOv8n - Baseline",
        "baseline": "yolov8n",
        "description": "Baseline with default hyperparameters"
    },
    {
        "name": "YOLOv8n - Augmented",
        "baseline": "yolov8n",
        "description": "With heavy augmentation"
    },
    {
        "name": "YOLOv8s - Large",
        "baseline": "yolov8s",
        "description": "Larger model variant"
    }
]

created_models = []
for exp in experiments:
    model = model_service.create_model(
        dataset_id="dataset_123",
        name=exp["name"],
        baseline_model=exp["baseline"],
        description=exp["description"],
        training_slice_ids=["slice_train"],
        validation_slice_ids=["slice_val"],
        meta={
            "experiment_group": "yolo_comparison",
            "created_at": datetime.now().isoformat()
        }
    )
    created_models.append(model)
    print(f"✅ Created experiment: {model.name}")
```

## 🔧 Advanced Usage

### Filtering Models

```python
from spb_onprem.models.params import (
    ModelsFilter,
    ModelsFilterOptions
)

# Complex filtering
models_filter = ModelsFilter(
    must_filter=ModelsFilterOptions(
        name_contains="yolo",
        is_trained=True,
        is_pinned=False
    ),
    not_filter=ModelsFilterOptions(
        name_contains="deprecated"
    )
)

models, next_cursor, total = model_service.get_models(
    dataset_id="dataset_123",
    models_filter=models_filter,
    length=20
)
```

### Pagination

```python
all_models = []
cursor = None

while True:
    models, cursor, total = model_service.get_models(
        dataset_id="dataset_123",
        cursor=cursor,
        length=50
    )
    
    all_models.extend(models)
    print(f"Loaded {len(all_models)}/{total} models")
    
    if not cursor:
        break

print(f"✅ Loaded all {len(all_models)} models")
```

### Bulk Operations

```python
# Archive old experimental models
from spb_onprem.models.params import ModelsFilterOptions

# Get unpinned, untrained models
old_filter = ModelsFilter(
    must_filter=ModelsFilterOptions(
        is_trained=False,
        is_pinned=False,
        name_contains="experiment"
    )
)

old_models, _, _ = model_service.get_models(
    dataset_id="dataset_123",
    models_filter=old_filter,
    length=50
)

print(f"Found {len(old_models)} old experimental models")

# Delete them
for model in old_models:
    model_service.delete_model(
        dataset_id="dataset_123",
        model_id=model.id
    )
    print(f"🗑️  Deleted: {model.name}")
```

## 🎯 Best Practices

### 1. **Consistent Naming Convention**

```python
# Good: Clear, versioned naming
name = f"{baseline_model}_{dataset_name}_v{version}"
# Example: "yolov8n_vehicles_v3"

# Better: Include training date and key metrics
from datetime import datetime
name = f"{baseline_model}_{purpose}_{datetime.now().strftime('%Y%m%d')}"
# Example: "yolov8n_detection_20250104"
```

### 2. **Track Training Metadata**

```python
model = model_service.create_model(
    dataset_id=dataset_id,
    name="Detection Model v5",
    baseline_model="yolov8n",
    training_slice_ids=training_slices,
    validation_slice_ids=val_slices,
    meta={
        "training_config": {
            "epochs": 100,
            "batch_size": 16,
            "learning_rate": 0.001,
            "optimizer": "Adam"
        },
        "hardware": {
            "gpu": "NVIDIA A100",
            "training_time_hours": 3.5
        },
        "dataset_version": "v2.1",
        "notes": "Improved performance on small objects"
    }
)
```

### 3. **Version Control Integration**

```python
# Link to model weights and code versions
model = model_service.update_model(
    dataset_id=dataset_id,
    model_id=model_id,
    meta={
        "git_commit": "abc123def456",
        "model_weights_s3": "s3://models/yolov8n_v5.pt",
        "training_script_version": "v1.2.0",
        "framework_versions": {
            "pytorch": "2.0.0",
            "ultralytics": "8.0.100"
        }
    }
)
```

### 4. **Pin Production Models**

```python
# Mark production-ready models
production_model = model_service.pin_model(
    dataset_id=dataset_id,
    model_id=best_model_id
)

# Add production metadata
model_service.update_model(
    dataset_id=dataset_id,
    model_id=best_model_id,
    meta={
        "status": "production",
        "deployed_at": datetime.now().isoformat(),
        "deployment_endpoint": "https://api.example.com/detect",
        "approved_by": "ml_team"
    }
)
```

### 5. **Regular Performance Audits**

```python
# Audit model performance
models, _, _ = model_service.get_models(
    dataset_id=dataset_id,
    models_filter=ModelsFilter(
        must_filter=ModelsFilterOptions(is_trained=True)
    ),
    length=100
)

# Generate performance report
for model in models:
    if model.training_classes:
        avg_ap = sum(tc.ap or 0 for tc in model.training_classes) / len(model.training_classes)
        
        if avg_ap < 0.7:
            print(f"⚠️  Low performance: {model.name} (AP: {avg_ap:.3f})")
        elif avg_ap > 0.9:
            print(f"✅ High performance: {model.name} (AP: {avg_ap:.3f})")
```

## 🔗 Related Modules

- **[📁 Datasets](../datasets/README.md)** - Parent container for models
- **[🔪 Slices](../slices/README.md)** - Define training/validation data splits
- **[📊 Data](../data/README.md)** - Access training data and annotations
- **[📈 Reports](../reports/README.md)** - Visualize model performance metrics

## ⚠️ Important Notes

- **Slice Requirements**: Models must reference valid training and validation slices
- **Training Status**: Set `is_trained=True` only after training completes
- **Performance Metrics**: AP scores should be between 0.0 and 1.0
- **Model Content**: Store actual model weights separately, reference via `model_content_id`
- **Deletion**: Deleting a model does not delete referenced slices or model files

## 🆘 Common Issues

**Issue: Model creation fails with missing slices**
```python
# Solution: Verify slices exist first
from spb_onprem import SliceService

slice_service = SliceService()
slice = slice_service.get_slice(dataset_id=dataset_id, slice_id=slice_id)
```

**Issue: Training classes not displaying correctly**
```python
# Solution: Ensure proper ModelTrainClass objects
from spb_onprem.models.entities import ModelTrainClass

training_classes = [
    ModelTrainClass(
        class_name="car",  # Use 'class_name', not 'class'
        annotation_type="box",
        ap=0.85
    )
]
```

---

**📚 Need more help?** Check the [main README](../../README.md) or explore related modules!
