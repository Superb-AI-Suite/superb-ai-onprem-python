from typing import (
    Optional,
    List,
    Union,
    Any
)
from enum import Enum
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.enums import DataType, DataStatus
from spb_onprem.exceptions import BadParameterError


class CommentStatus(str, Enum):
    """댓글 상태를 나타내는 열거형"""
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class AnnotationFilter(CustomBaseModel):
    type: Optional[str] = None
    name: Optional[str] = None


class AnnotationRangeFilter(CustomBaseModel):
    annotation_type: Optional[str] = Field(None, alias="annotationType")
    class_name: Optional[str] = Field(None, alias="className")
    class_count_equals: Optional[int] = Field(None, alias="classCountEquals")
    class_count_in: Optional[List[int]] = Field(None, alias="classCountIn")
    class_count_max: Optional[int] = Field(None, alias="classCountMax")
    class_count_min: Optional[int] = Field(None, alias="classCountMin")


class DateTimeRangeFilter(CustomBaseModel):
    """날짜/시간 범위 필터"""
    from_date: Optional[str] = Field(None, alias="from")
    to_date: Optional[str] = Field(None, alias="to")
    equals: Optional[str] = None


class UserFilter(CustomBaseModel):
    """사용자 필터 옵션"""
    equals: Optional[str] = None
    contains: Optional[str] = None
    in_list: Optional[List[str]] = Field(None, alias="in")
    exists: Optional[bool] = None


class StringMetaFilter(CustomBaseModel):
    """문자열 메타 데이터 필터"""
    key: str
    contains: Optional[str] = None
    equals: Optional[str] = None
    in_list: Optional[List[str]] = Field(None, alias="in")


class NumberMetaFilter(CustomBaseModel):
    """숫자 메타 데이터 필터"""
    key: str
    min_value: Optional[float] = Field(None, alias="min")
    max_value: Optional[float] = Field(None, alias="max")
    equals: Optional[float] = None
    in_list: Optional[List[float]] = Field(None, alias="in")


class DateTimeMetaFilter(CustomBaseModel):
    """날짜/시간 메타 데이터 필터"""
    key: str
    from_date: Optional[str] = Field(None, alias="from")
    to_date: Optional[str] = Field(None, alias="to")
    equals: Optional[str] = None


class MetaFilterOptions(CustomBaseModel):
    """메타 데이터 필터 옵션들"""
    string_meta: Optional[List[StringMetaFilter]] = Field(None, alias="stringMeta")
    number_meta: Optional[List[NumberMetaFilter]] = Field(None, alias="numberMeta")
    date_time_meta: Optional[List[DateTimeMetaFilter]] = Field(None, alias="dateTimeMeta")


class DataSliceStatusFilter(CustomBaseModel):
    """데이터 슬라이스 상태 필터"""
    in_list: Optional[List[DataStatus]] = Field(None, alias="in")
    equals: Optional[DataStatus] = None
    not_in: Optional[List[DataStatus]] = Field(None, alias="notIn")


class DataSliceUserFilter(CustomBaseModel):
    """데이터 슬라이스 사용자 필터 (labeler, reviewer용)"""
    equals: Optional[str] = None
    in_list: Optional[List[str]] = Field(None, alias="in")
    exists: Optional[bool] = None


class DataSliceTagsFilter(CustomBaseModel):
    """데이터 슬라이스 태그 필터"""
    contains: Optional[str] = None
    has_any: Optional[List[str]] = Field(None, alias="hasAny")
    has_all: Optional[List[str]] = Field(None, alias="hasAll")
    exists: Optional[bool] = None


class DataSliceCommentFilter(CustomBaseModel):
    """데이터 슬라이스 댓글 필터"""
    comment_contains: Optional[str] = Field(None, alias="commentContains")
    category: Optional[str] = None
    status: Optional[CommentStatus] = None
    created_by: Optional[UserFilter] = Field(None, alias="createdBy")
    created_at: Optional[DateTimeRangeFilter] = Field(None, alias="createdAt")
    exists: Optional[bool] = None


class DataSlicePropertiesFilter(CustomBaseModel):
    """슬라이스 속성 필터 (ID 제외)"""
    status: Optional[DataSliceStatusFilter] = None
    labeler: Optional[DataSliceUserFilter] = None
    reviewer: Optional[DataSliceUserFilter] = None
    tags: Optional[DataSliceTagsFilter] = None
    status_changed_at: Optional[DateTimeRangeFilter] = Field(None, alias="statusChangedAt")
    comments: Optional[DataSliceCommentFilter] = None
    meta: Optional[MetaFilterOptions] = None


class DataSliceFilter(CustomBaseModel):
    """슬라이스 필터 (ID + must/not 구조)"""
    id: str  # 검색할 슬라이스 ID (필수)
    must: Optional[DataSlicePropertiesFilter] = None  # 만족해야 하는 조건
    not_filter: Optional[DataSlicePropertiesFilter] = Field(None, alias="not")  # 만족하지 않아야 하는 조건


class DataFilterOptions(CustomBaseModel):
    id_in: Optional[List[str]] = Field(None, alias="idIn")
    slice_id: Optional[str] = Field(None, alias="sliceId")
    slice_id_in: Optional[List[str]] = Field(None, alias="sliceIdIn")
    slice_id_any: Optional[List[str]] = Field(None, alias="sliceIdAny")  # 추가된 필드
    slice_id_exists: Optional[bool] = Field(None, alias="sliceIdExists")  # 추가된 필드
    key_contains: Optional[str] = Field(None, alias="keyContains")
    key_matches: Optional[str] = Field(None, alias="keyMatches")
    sub_type_contains: Optional[str] = Field(None, alias="subTypeContains")  # 추가된 필드
    sub_type_matches: Optional[str] = Field(None, alias="subTypeMatches")  # 추가된 필드
    type_in: Optional[List[DataType]] = Field(None, alias="typeIn")
    annotation_any: Optional[List[AnnotationFilter]] = Field(None, alias="annotationAny")
    annotation_in: Optional[List[AnnotationFilter]] = Field(None, alias="annotationIn")
    annotation_exists: Optional[bool] = Field(None, alias="annotationExists")
    annotation_range: Optional[List[AnnotationRangeFilter]] = Field(None, alias="annotationRange")
    prediction_set_id_in: Optional[List[str]] = Field(None, alias="predictionSetIdIn")
    prediction_set_id_exists: Optional[bool] = Field(None, alias="predictionSetIdExists")
    
    # 추가된 필드들 (GraphQL과 매칭)
    created_at: Optional[DateTimeRangeFilter] = Field(None, alias="createdAt")
    updated_at: Optional[DateTimeRangeFilter] = Field(None, alias="updatedAt")
    created_by: Optional[UserFilter] = Field(None, alias="createdBy")
    updated_by: Optional[UserFilter] = Field(None, alias="updatedBy")
    meta: Optional[MetaFilterOptions] = None


class DataListFilter(CustomBaseModel):
    must_filter: Optional[DataFilterOptions] = Field(None, alias="must")
    not_filter: Optional[DataFilterOptions] = Field(None, alias="not")
    slice: Optional[DataSliceFilter] = Field(None, alias="slice")


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
        "filter": data_filter.model_dump(
            by_alias=True, exclude_unset=True
        ) if data_filter else None,
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
        "filter": data_filter.model_dump(
            by_alias=True, exclude_unset=True
        ) if data_filter else None,
        "cursor": cursor,
        "length": length
    }
