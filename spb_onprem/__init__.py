try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.1.0"

# Services
from .datasets.service import DatasetService
from .data.service import DataService
from .slices.service import SliceService
from .activities.service import ActivityService
from .exports.service import ExportService

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
    Export,

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
    ExportFilter,
    ExportFilterOptions,
)

__all__ = (
    # Services
    "DatasetService",
    "DataService",
    "SliceService",
    "ActivityService",
    "ExportService",

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
    "Export",
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
    "ExportFilter",
    "ExportFilterOptions",
)
