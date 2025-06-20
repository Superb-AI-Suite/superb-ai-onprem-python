try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.1.0"

# Services
from .datasets.service import DatasetService
from .data.service import DataService
from .slices.service import SliceService
from .activities.service import ActivityService

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
    Activity,
    ActivityHistory,

    # Enums
    DataType,
    SceneType,
    DataMetaTypes,
    DataMetaValue,
    ActivityStatus,
    ActivitySchema,
    SchemaType,
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
    ActivitiesFilter,
    ActivitiesFilterOptions,
)

__all__ = (
    # Services
    "DatasetService",
    "DataService",
    "SliceService",
    "ActivityService",

    # Core Entities
    "Data",
    "Scene",
    "Annotation",
    "AnnotationVersion",
    "Prediction",
    "DataMeta",
    "Dataset",
    "Slice",
    "Activity",
    "ActivityHistory",
    
    # Enums
    "DataType",
    "SceneType",
    "DataMetaTypes",
    "DataMetaValue",
    "ActivityStatus",
    "ActivitySchema",
    "SchemaType",
    
    # Filters
    "AnnotationFilter",
    "DataListFilter",
    "DataFilterOptions",
    "DatasetsFilter",
    "DatasetsFilterOptions",
    "SlicesFilter",
    "SlicesFilterOptions",
    "ActivitiesFilter",
    "ActivitiesFilterOptions",
)
