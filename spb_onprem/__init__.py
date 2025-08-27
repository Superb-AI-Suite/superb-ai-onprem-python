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
from .contents.service import ContentService

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
    DataSlice,
    Activity,
    ActivityHistory,
    Export,
    Content,
    Frame,

    # Enums
    DataType,
    SceneType,
    DataMetaTypes,
    DataMetaValue,
    DataStatus,
    ActivityStatus,
    ActivitySchema,
    SchemaType,
)

# Filters
from .searches import (
    AnnotationFilter,
    DataListFilter,
    DataFilterOptions,
    AnnotationRangeFilter,
    DateTimeRangeFilter,
    UserFilter,
    StringMetaFilter,
    NumberMetaFilter,
    DateTimeMetaFilter,
    MetaFilterOptions,
    DataSliceStatusFilter,
    DataSliceUserFilter,
    DataSliceTagsFilter,
    DataSliceCommentFilter,
    DataSlicePropertiesFilter,
    DataSliceFilter,
    CommentStatus,
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
    "ContentService",

    # Core Entities
    "Data",
    "Scene",
    "Annotation",
    "AnnotationVersion",
    "Prediction",
    "DataMeta",
    "Dataset",
    "Slice",
    "DataSlice",
    "Activity",
    "ActivityHistory",
    "Export",
    "Content",
    "Frame",
    
    # Enums
    "DataType",
    "SceneType",
    "DataMetaTypes",
    "DataMetaValue",
    "DataStatus",
    "ActivityStatus",
    "ActivitySchema",
    "SchemaType",
    "CommentStatus",
    
    # Filters
    "AnnotationFilter",
    "DataListFilter",
    "DataFilterOptions",
    "AnnotationRangeFilter",
    "DateTimeRangeFilter",
    "UserFilter",
    "StringMetaFilter",
    "NumberMetaFilter",
    "DateTimeMetaFilter",
    "MetaFilterOptions",
    "DataSliceStatusFilter",
    "DataSliceUserFilter",
    "DataSliceTagsFilter",
    "DataSliceCommentFilter",
    "DataSlicePropertiesFilter",
    "DataSliceFilter",
    "DatasetsFilter",
    "DatasetsFilterOptions",
    "SlicesFilter",
    "SlicesFilterOptions",
    "ActivitiesFilter",
    "ActivitiesFilterOptions",
    "ExportFilter",
    "ExportFilterOptions",
)
