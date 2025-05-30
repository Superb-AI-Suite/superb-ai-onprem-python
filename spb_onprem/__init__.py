try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0.dev0"

# Services
from .datasets.service import DatasetService
from .data.service import DataService
from .slices.service import SliceService

# Core Entities
from .data.entities import (
    Data,
    Scene,
    Annotation,
    AnnotationVersion,
    Prediction,
    DataMeta,
)
from .datasets.entities import Dataset
from .slices.entities import Slice

# Enums
from .data.enums import (
    DataType,
    SceneType,
    DataMetaTypes,
    DataMetaValue,
)

# Filters
from .data.params.data_list import (
    AnnotationFilter,
    DataListFilter,
    DataFilterOptions,
)
from .datasets.params.datasets import (
    DatasetsFilter,
    DatasetsFilterOptions,
)
from .slices.params.slices import (
    SlicesFilterOptions,
)

__all__ = (
    # Services
    "DatasetService",
    "DataService",
    "SliceService",
    
    # Core Entities
    "Data",
    "Scene",
    "Annotation",
    "AnnotationVersion",
    "Prediction",
    "DataMeta",
    "Dataset",
    "Slice",
    
    # Enums
    "DataType",
    "SceneType",
    "DataMetaTypes",
    "DataMetaValue",
    
    # Filters
    "AnnotationFilter",
    "DataListFilter",
    "DataFilterOptions",
    "DatasetsFilter",
    "DatasetsFilterOptions",
    "SlicesFilterOptions",
)
