# Superb AI On-premise SDK

Python SDK for Superb AI's On-premise solution. This SDK provides a simple interface to interact with your on-premise Superb AI installation.

## Installation

```bash
pip install superb-ai-onprem
```

## Quick Start

```python
from spb_onprem import DatasetService, DataService
from spb_onprem.data.enums import DataType

# Initialize services
dataset_service = DatasetService()
data_service = DataService()

# Create a dataset
dataset = dataset_service.create_dataset(
    name="my-dataset",
    description="My first dataset"
)

# Upload an image with annotation
with open("image.jpg", "rb") as f:
    image_data = BytesIO(f.read())

data = data_service.create_image_data(
    dataset_id=dataset.id,
    key="image_1",
    image_content=image_data,
    annotation={
        "labels": ["car", "person"],
        "boxes": [
            {"x": 100, "y": 100, "width": 200, "height": 200}
        ]
    }
)
```

## Features

- Dataset Management
  - Create, update, and delete datasets
  - List and filter datasets
- Data Management
  - Upload images with annotations
  - Update annotations
  - Add/remove data from slices
  - Manage metadata
- Slice Management
  - Create and manage data slices
  - Filter and organize your data

## Usage Examples

### Dataset Operations

```python
from spb_onprem import DatasetService
from spb_onprem import DatasetsFilter, DatasetsFilterOptions

# Initialize service
dataset_service = DatasetService()

# Create a dataset
dataset = dataset_service.create_dataset(
    name="my-dataset",
    description="Dataset description"
)

# List datasets with filtering
filter = DatasetsFilter(
    must_filter=DatasetsFilterOptions(
        name_contains="test"
    )
)
datasets = dataset_service.get_datasets(filter=filter)
```

### Data Operations

```python
from spb_onprem import DataService
from spb_onprem import DataListFilter, DataFilterOptions

# Initialize service
data_service = DataService()

# List data with filtering
filter = DataListFilter(
    must_filter=DataFilterOptions(
        key_contains="image_",
        annotation_exists=True
    )
)
data_list = data_service.get_data_list(
    dataset_id="your-dataset-id",
    filter=filter
)

# Update annotation
data_service.update_annotation(
    dataset_id="your-dataset-id",
    data_id="your-data-id",
    annotation={
        "labels": ["updated_label"],
        "boxes": [...]
    }
)
```

### Slice Operations

```python
from spb_onprem import SliceService

# Initialize service
slice_service = SliceService()

# Create a slice
slice = slice_service.create_slice(
    dataset_id="your-dataset-id",
    name="validation-set",
    description="Validation data slice"
)

# Add data to slice
data_service.add_data_to_slice(
    dataset_id="your-dataset-id",
    data_id="your-data-id",
    slice_id=slice.id
)
```

## Error Handling

The SDK provides specific error types for different scenarios:

```python
from spb_onprem.exceptions import (
    BadParameterError,
    NotFoundError,
    UnknownError
)

try:
    dataset = dataset_service.get_dataset(dataset_id="non-existent-id")
except NotFoundError:
    print("Dataset not found")
except BadParameterError as e:
    print(f"Invalid parameter: {e}")
except UnknownError as e:
    print(f"An unexpected error occurred: {e}")
```

## Configuration

The SDK supports two authentication methods:

### 1. Config File Authentication (Default)

Create a config file at `~/.spb/onprem-config`:

```ini
[default]
host=https://your-onprem-host
access_key=your-access-key
access_key_secret=your-access-key-secret
```

This is the default authentication method when `SUPERB_SYSTEM_SDK=false` or not set.

### 2. Environment Variables (for Airflow DAGs)

When running in an Airflow DAG or other system environments, you can use environment variables for authentication. This method is activated by setting `SUPERB_SYSTEM_SDK=true`.

Required environment variables:
```bash
# Enable system SDK mode
export SUPERB_SYSTEM_SDK=true

# Set the host URL (either one is required)
export SUPERB_SYSTEM_SDK_HOST=https://your-superb-ai-host
# or
export SUNRISE_SERVER_URL=https://your-superb-ai-host

# Set the user email
export SUPERB_SYSTEM_SDK_USER_EMAIL=user@example.com
```

You can set these environment variables:
- Directly in your shell
- In your Airflow DAG configuration
- Through your deployment environment
- Using a `.env` file with your preferred method of loading environment variables

Note: 
- When `SUPERB_SYSTEM_SDK=true`, the SDK will ignore the config file (`~/.spb/onprem-config`) and use environment variables exclusively.
- When `SUPERB_SYSTEM_SDK=false` or not set, the SDK will look for authentication credentials in `~/.spb/onprem-config`.

## Requirements

- Python >= 3.7
- requests >= 2.22.0
- urllib3 >= 1.21.1
- pydantic >= 1.8.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support or feature requests, please contact the Superb AI team or create an issue in this repository.

