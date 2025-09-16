from typing import Optional, List, Union, Literal
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.enums import DataType, DataStatus
from spb_onprem.exceptions import BadParameterError

# === 기본 필터 ===
class DateTimeRangeFilterOption(CustomBaseModel):
    datetime_from: Optional[str] = Field(None, alias="from")
    to: Optional[str] = None
    equals: Optional[str] = None

class UserFilterOption(CustomBaseModel):
    equals: Optional[str] = None
    contains: Optional[str] = None
    user_in: Optional[List[str]] = Field(None, alias="in")
    exists: Optional[bool] = None

class NumericRangeFilter(CustomBaseModel):
    gt: Optional[float] = None
    gte: Optional[float] = None
    lt: Optional[float] = None
    lte: Optional[float] = None
    equals: Optional[float] = None

class GeoLocationFilter(CustomBaseModel):
    latitude: float
    longitude: float
    radius_in_meters: float = Field(..., alias="radiusInMeters")

# === Meta 필터 ===
class NumberMetaFilter(CustomBaseModel):
    key: str
    range: Optional[NumericRangeFilter] = None

class KeywordMetaFilter(CustomBaseModel):
    key: str
    equals: Optional[str] = None
    contains: Optional[str] = None
    keyword_in: Optional[List[str]] = Field(None, alias="in")

class DateMetaFilter(CustomBaseModel):
    key: str
    range: Optional[DateTimeRangeFilterOption] = None

class MiscMetaFilter(CustomBaseModel):
    key: str
    equals: str

class MetaFilter(CustomBaseModel):
    num: Optional[List[NumberMetaFilter]] = None
    keyword: Optional[List[KeywordMetaFilter]] = None
    date: Optional[List[DateMetaFilter]] = None
    misc: Optional[List[MiscMetaFilter]] = None

# === Count 필터 ===
class CountFilter(CustomBaseModel):
    key: str
    range: Optional[NumericRangeFilter] = None

class DistanceCountFilter(CustomBaseModel):
    key: str
    distance_range: NumericRangeFilter = Field(..., alias="distanceRange")
    count_range: NumericRangeFilter = Field(..., alias="countRange")

class FrameCountsFilter(CustomBaseModel):
    annotation_class: Optional[List[CountFilter]] = Field(None, alias="class")
    group: Optional[List[CountFilter]] = None
    sub_class: Optional[List[CountFilter]] = Field(None, alias="subClass")
    distance: Optional[List[DistanceCountFilter]] = None

# === Frame 필터 ===
class FrameFilterOptions(CustomBaseModel):
    index: Optional[NumericRangeFilter] = None
    version_contains: Optional[str] = Field(None, alias="versionContains")
    channels_in: Optional[List[str]] = Field(None, alias="channelsIn")
    timestamp: Optional[DateTimeRangeFilterOption] = None
    location: Optional[GeoLocationFilter] = None
    meta: Optional[MetaFilter] = None
    counts: Optional[FrameCountsFilter] = None

# === Data 필터 ===
class DataFilterOptions(CustomBaseModel):
    id_in: Optional[List[str]] = Field(None, alias="idIn")
    slice_id_in: Optional[List[str]] = Field(None, alias="sliceIdIn")
    key_contains: Optional[str] = Field(None, alias="keyContains")
    key_matches: Optional[str] = Field(None, alias="keyMatches")
    sub_type_contains: Optional[str] = Field(None, alias="subTypeContains")
    sub_type_matches: Optional[str] = Field(None, alias="subTypeMatches")
    type_in: Optional[List[str]] = Field(None, alias="typeIn")
    created_at: Optional[DateTimeRangeFilterOption] = Field(None, alias="createdAt")
    updated_at: Optional[DateTimeRangeFilterOption] = Field(None, alias="updatedAt")
    created_by: Optional[UserFilterOption] = Field(None, alias="createdBy")
    updated_by: Optional[UserFilterOption] = Field(None, alias="updatedBy")
    meta: Optional[MetaFilter] = None
    assigned_to_user: Optional[str] = Field(None, alias="assignedToUser")

class DataSliceStatusFilterOption(CustomBaseModel):
    status_in: Optional[List[str]] = Field(None, alias="in")
    equals: Optional[str] = None
    status_not_in: Optional[List[str]] = Field(None, alias="notIn")

class DataSliceUserFilterOption(CustomBaseModel):
    equals: Optional[str] = None
    user_in: Optional[List[str]] = Field(None, alias="in")
    exists: Optional[bool] = None

class DataSliceTagsFilterOption(CustomBaseModel):
    contains: Optional[str] = None
    has_any: Optional[List[str]] = Field(None, alias="hasAny")
    has_all: Optional[List[str]] = Field(None, alias="hasAll")
    exists: Optional[bool] = None

class DataSliceCommentFilterOption(CustomBaseModel):
    comment_contains: Optional[str] = Field(None, alias="commentContains")
    category: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[UserFilterOption] = Field(None, alias="createdBy")
    created_at: Optional[DateTimeRangeFilterOption] = Field(None, alias="createdAt")
    exists: Optional[bool] = None

class DataSlicePropertiesFilter(CustomBaseModel):
    status: Optional[DataSliceStatusFilterOption] = None
    labeler: Optional[DataSliceUserFilterOption] = None
    reviewer: Optional[DataSliceUserFilterOption] = None
    tags: Optional[DataSliceTagsFilterOption] = None
    status_changed_at: Optional[DateTimeRangeFilterOption] = Field(None, alias="statusChangedAt")
    comments: Optional[DataSliceCommentFilterOption] = None
    meta: Optional[MetaFilter] = None
    assigned_to_user: Optional[str] = Field(None, alias="assignedToUser")

class DataSliceFilter(CustomBaseModel):
    id: str
    must_filter: Optional[DataSlicePropertiesFilter] = Field(None, alias="must")
    not_filter: Optional[DataSlicePropertiesFilter] = Field(None, alias="not")


class FrameFilter(CustomBaseModel):
    conditions: Optional[FrameFilterOptions] = None
    mode: Optional[Union[str, Literal["INDIVIDUAL_FRAMES", "DATA_SUMMARY"]]] = "INDIVIDUAL_FRAMES"
    matching_frame_count: Optional[NumericRangeFilter] = Field(None, alias="matchingFrameCount")


class DataFilter(CustomBaseModel):
    must_filter: Optional[DataFilterOptions] = Field(None, alias="must")
    not_filter: Optional[DataFilterOptions] = Field(None, alias="not")
    frames: Optional[List[FrameFilter]] = None
    slice: Optional[DataSliceFilter] = None


class DataListFilter(CustomBaseModel):
    must_filter: Optional[DataFilterOptions] = Field(None, alias="must")
    not_filter: Optional[DataFilterOptions] = Field(None, alias="not")
    slice: Optional[DataSliceFilter] = Field(None, alias="slice")
    frames: Optional[List[FrameFilter]] = Field(None, alias="frames")


def get_data_id_list_params(
    dataset_id: str,
    data_filter: Optional[DataListFilter] = None,
    cursor: Optional[str] = None,
    length: Optional[int] = 50,
):
    """Make the variables for the dataIdList query.

    Args:
        dataset_id (str): The dataset id.
        data_filter (Optional[DataListFilter], optional): The filter for the data list. Defaults to None.
        cursor (Optional[str], optional): The cursor for the data list. Defaults to None.
        length (Optional[int], optional): The length of the data list. Defaults to 50.

    Raises:
        BadParameterError: The maximum length is 200.

    Returns:
        dict: The variables for the dataIdList query.
    """
    if length > 200:
        raise BadParameterError("The maximum length is 200.")
    return {
        "dataset_id": dataset_id,
        "filter": data_filter.model_dump(by_alias=True, exclude_unset=True) if data_filter else None,
        "cursor": cursor,
        "length": length
    }


def get_data_list_params(
    dataset_id: str,
    data_filter: Optional[DataListFilter] = None,
    cursor: Optional[str] = None,
    length: Optional[int] = 10,
):
    """Make the variables for the dataList query.

    Args:
        dataset_id (str): The dataset id.
        data_filter (Optional[DataListFilter], optional): The filter for the data list. Defaults to None.
        cursor (Optional[str], optional): The cursor for the data list. Defaults to None.
        length (Optional[int], optional): The length of the data list. Defaults to 10.

    Raises:
        BadParameterError: The maximum length is 50.

    Returns:
        dict: The variables for the dataList query.
    """

    if length > 50:
        raise BadParameterError("The maximum length is 50.")
    return {
        "dataset_id": dataset_id,
        "filter": data_filter.model_dump(by_alias=True, exclude_unset=True) if data_filter else None,
        "cursor": cursor,
        "length": length
    }
