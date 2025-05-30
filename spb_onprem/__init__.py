try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.1.0"

# Services
from .datasets.service import DatasetService
from .data.service import DataService
from .slices.service import SliceService

# Core Entities and Enums
from .entities import (
    # Core Entities
    Data,
    Scene,
    Annotation,
    AnnotationVersion,
    Prediction,
    DataMeta,
    Dataset,
    Slice,
    
    # Enums
    DataType,
    SceneType,
    DataMetaTypes,
    DataMetaValue,
)

# Filters
from .searches import (
    AnnotationFilter,
    DataListFilter,
    DataFilterOptions,
    DatasetsFilter,
    DatasetsFilterOptions,
    SlicesFilter,
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
    "SlicesFilter",
    "SlicesFilterOptions",
)
