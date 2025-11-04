from typing import Optional, List, Union, Literal
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.enums import DataType, DataStatus
from spb_onprem.exceptions import BadParameterError

# === 기본 필터 ===

class DateTimeRangeFilterOption(CustomBaseModel):
    """
    날짜/시간 범위 필터 옵션
    
    사용 예시:
        # 범위 필터
        {"from": "2025-01-01T00:00:00Z", "to": "2025-12-31T23:59:59Z"}
        
        # 정확한 날짜
        {"equals": "2025-09-17T10:00:00Z"}
        
        # 시작 날짜만
        {"from": "2025-01-01T00:00:00Z"}
    """
    datetime_from: Optional[str] = Field(None, alias="from", description="시작 날짜/시간 (ISO 8601 형식)")
    to: Optional[str] = Field(None, description="종료 날짜/시간 (ISO 8601 형식)")
    equals: Optional[str] = Field(None, description="정확한 날짜/시간 (ISO 8601 형식)")


class UserFilterOption(CustomBaseModel):
    """
    사용자 필터 옵션 (생성자, 수정자 등)
    
    사용 예시:
        # 정확한 사용자
        {"equals": "user@example.com"}
        
        # 부분 일치
        {"contains": "admin"}
        
        # 여러 사용자 중 하나
        {"in": ["user1@example.com", "user2@example.com"]}
        
        # 사용자 존재 여부
        {"exists": True}
    """
    equals: Optional[str] = Field(None, description="정확한 사용자 이메일")
    contains: Optional[str] = Field(None, description="사용자 이메일에 포함된 문자열")
    user_in: Optional[List[str]] = Field(None, alias="in", description="사용자 이메일 목록 중 하나")
    exists: Optional[bool] = Field(None, description="사용자 정보 존재 여부")


class NumericRangeFilter(CustomBaseModel):
    """
    숫자 범위 필터
    
    사용 예시:
        # 범위 필터
        {"gte": 0.8, "lt": 1.0}  # 0.8 이상 1.0 미만
        
        # 정확한 값
        {"equals": 5}
        
        # 단일 조건
        {"gt": 10}  # 10보다 큰 값
    """
    gt: Optional[float] = Field(None, description="초과 (greater than)")
    gte: Optional[float] = Field(None, description="이상 (greater than or equal)")
    lt: Optional[float] = Field(None, description="미만 (less than)")
    lte: Optional[float] = Field(None, description="이하 (less than or equal)")
    equals: Optional[float] = Field(None, description="정확한 값")


class GeoLocationFilter(CustomBaseModel):
    """
    지리적 위치 필터 (위도, 경도, 반경)
    
    사용 예시:
        {
            "latitude": 37.5665,
            "longitude": 126.9780,
            "radiusInMeters": 1000
        }
    """
    latitude: float = Field(..., description="위도 (-90 ~ 90)")
    longitude: float = Field(..., description="경도 (-180 ~ 180)")
    radius_in_meters: float = Field(..., alias="radiusInMeters", description="반경 (미터 단위)")

# === Meta 필터 ===

class NumberMetaFilter(CustomBaseModel):
    """
    숫자형 메타데이터 필터
    
    사용 예시:
        {
            "key": "confidence_score",
            "range": {"gte": 0.8, "lt": 1.0}
        }
    """
    key: str = Field(..., description="메타데이터 키 이름")
    range: Optional[NumericRangeFilter] = Field(None, description="숫자 범위 조건")

class KeywordMetaFilter(CustomBaseModel):
    """
    키워드/텍스트형 메타데이터 필터
    
    사용 예시:
        # 정확한 일치
        {"key": "category", "equals": "vehicle"}
        
        # 부분 일치
        {"key": "tags", "contains": "outdoor"}
        
        # 여러 값 중 하나
        {"key": "status", "in": ["active", "pending"]}
    """
    key: str = Field(..., description="메타데이터 키 이름")
    equals: Optional[str] = Field(None, description="정확한 값")
    contains: Optional[str] = Field(None, description="포함된 문자열")
    keyword_in: Optional[List[str]] = Field(None, alias="in", description="값 목록 중 하나")


class DateMetaFilter(CustomBaseModel):
    """
    날짜형 메타데이터 필터
    
    사용 예시:
        {
            "key": "capture_date",
            "range": {
                "from": "2025-01-01T00:00:00Z",
                "to": "2025-06-30T23:59:59Z"
            }
        }
    """
    key: str = Field(..., description="메타데이터 키 이름")
    range: Optional[DateTimeRangeFilterOption] = Field(None, description="날짜 범위 조건")


class MiscMetaFilter(CustomBaseModel):
    """
    기타 메타데이터 필터 (정확한 일치만 지원)
    
    사용 예시:
        {"key": "custom_field", "equals": "specific_value"}
    """
    key: str = Field(..., description="메타데이터 키 이름")
    equals: str = Field(..., description="정확한 값")


class MetaFilter(CustomBaseModel):
    """
    메타데이터 필터 컨테이너
    
    사용 예시:
        {
            "num": [{"key": "confidence", "range": {"gte": 0.8}}],
            "keyword": [{"key": "category", "equals": "vehicle"}],
            "date": [{"key": "capture_date", "range": {"from": "2025-01-01T00:00:00Z"}}],
            "misc": [{"key": "custom", "equals": "value"}]
        }
    """
    num: Optional[List[NumberMetaFilter]] = Field(None, description="숫자형 메타데이터 필터 목록")
    keyword: Optional[List[KeywordMetaFilter]] = Field(None, description="키워드형 메타데이터 필터 목록")
    date: Optional[List[DateMetaFilter]] = Field(None, description="날짜형 메타데이터 필터 목록")
    misc: Optional[List[MiscMetaFilter]] = Field(None, description="기타 메타데이터 필터 목록")

# === Count 필터 ===
class CountFilter(CustomBaseModel):
    key: str
    range: Optional[NumericRangeFilter] = None

class DistanceCountFilter(CustomBaseModel):
    key: str
    distance_range: NumericRangeFilter = Field(..., alias="distanceRange")
    count_range: NumericRangeFilter = Field(..., alias="countRange")


class AnnotationCountsFilter(CustomBaseModel):
    annotation_class: Optional[List[CountFilter]] = Field(None, alias="class")
    group: Optional[List[CountFilter]] = None
    sub_class: Optional[List[CountFilter]] = Field(None, alias="subClass")


class FrameCountsFilter(AnnotationCountsFilter):
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
    """
    데이터 필터링 옵션 (기본 데이터 속성 필터)
    
    사용 예시:
        DataFilterOptions(
            type_in=["IMAGE", "VIDEO"],
            key_contains="sample_",
            created_at={"from": "2025-01-01T00:00:00Z"},
            meta={"keyword": [{"key": "category", "equals": "vehicle"}]}
        )
    """
    # ID 및 키 필터
    id_in: Optional[List[str]] = Field(None, alias="idIn", description="특정 데이터 ID 목록 중 하나")
    slice_id_in: Optional[List[str]] = Field(None, alias="sliceIdIn", description="특정 슬라이스 ID 목록에 속한 데이터")
    
    # 키 패턴 필터
    key_contains: Optional[str] = Field(None, alias="keyContains", description="키에 포함된 문자열")
    key_matches: Optional[str] = Field(None, alias="keyMatches", description="키와 매칭되는 정규식 패턴")
    
    # 타입 필터
    sub_type_contains: Optional[str] = Field(None, alias="subTypeContains", description="서브타입에 포함된 문자열")
    sub_type_matches: Optional[str] = Field(None, alias="subTypeMatches", description="서브타입과 매칭되는 정규식 패턴")
    type_in: Optional[List[str]] = Field(None, alias="typeIn", description="데이터 타입 목록 중 하나 (IMAGE, VIDEO 등)")
    
    # 날짜 필터
    created_at: Optional[DateTimeRangeFilterOption] = Field(None, alias="createdAt", description="생성일 범위")
    updated_at: Optional[DateTimeRangeFilterOption] = Field(None, alias="updatedAt", description="수정일 범위")
    
    # 사용자 필터
    created_by: Optional[UserFilterOption] = Field(None, alias="createdBy", description="생성자 필터")
    updated_by: Optional[UserFilterOption] = Field(None, alias="updatedBy", description="수정자 필터")
    
    # 메타데이터 및 기타
    meta: Optional[MetaFilter] = Field(None, description="커스텀 메타데이터 필터")
    assigned_to_user: Optional[str] = Field(None, alias="assignedToUser", description="할당된 사용자")
    annotation_counts: Optional[AnnotationCountsFilter] = Field(None, alias="annotationCounts", description="어노테이션 개수 필터")

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
    annotation_counts: Optional[AnnotationCountsFilter] = Field(None, alias="annotationCounts")

class DataSliceFilter(CustomBaseModel):
    id: str
    must_filter: Optional[DataSlicePropertiesFilter] = Field(None, alias="must")
    not_filter: Optional[DataSlicePropertiesFilter] = Field(None, alias="not")


class FrameFilter(CustomBaseModel):
    conditions: Optional[FrameFilterOptions] = None
    matching_frame_count: Optional[NumericRangeFilter] = Field(None, alias="matchingFrameCount")


class DataFilter(CustomBaseModel):
    must_filter: Optional[DataFilterOptions] = Field(None, alias="must")
    not_filter: Optional[DataFilterOptions] = Field(None, alias="not")
    frames: Optional[List[FrameFilter]] = None
    slice: Optional[DataSliceFilter] = None


class DataListFilter(CustomBaseModel):
    """
    데이터 리스트 필터 - 메인 필터 클래스
    
    논리 연산자를 사용한 복합 필터링을 지원합니다:
    - must_filter: AND 조건 (모든 조건이 참이어야 함)
    - not_filter: NOT 조건 (모든 조건이 거짓이어야 함)
    - slice: 특정 슬라이스 내에서 필터링
    - frames: 프레임 레벨 필터링 (비디오 데이터용)
    
    사용 예시:
        # 기본 필터
        DataListFilter(
            must_filter=DataFilterOptions(
                type_in=["IMAGE"],
                key_contains="sample_"
            )
        )
        
        # 복합 필터 (AND + NOT)
        DataListFilter(
            must_filter=DataFilterOptions(type_in=["IMAGE"]),
            not_filter=DataFilterOptions(key_contains="test_")
        )
        
        # 슬라이스 특정 필터
        DataListFilter(
            slice={
                "id": "slice-123",
                "must": {"status": {"in": ["LABELED"]}}
            }
        )
        
        # Dictionary에서 생성 (alias 사용 필수)
        filter_dict = {
            "must": {
                "typeIn": ["IMAGE"],
                "keyContains": "sample_"
            }
        }
        filter = DataListFilter.model_validate(filter_dict)
    """
    must_filter: Optional[DataFilterOptions] = Field(
        None, 
        alias="must", 
        description="AND 조건 - 모든 조건이 참이어야 함"
    )
    not_filter: Optional[DataFilterOptions] = Field(
        None, 
        alias="not", 
        description="NOT 조건 - 모든 조건이 거짓이어야 함"
    )
    slice: Optional[DataSliceFilter] = Field(
        None, 
        alias="slice", 
        description="슬라이스별 필터링"
    )
    frames: Optional[List[FrameFilter]] = Field(
        None, 
        alias="frames", 
        description="프레임 레벨 필터 목록 (비디오 데이터용)"
    )


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
        BadParameterError: The maximum length is 50.

    Returns:
        dict: The variables for the dataIdList query.
    """
    if length > 50:
        raise BadParameterError("The maximum length is 50.")
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
