from typing import Optional, Union
from enum import Enum

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.base_types import Undefined, UndefinedType


class AnalyticsReportListOrderFields(str, Enum):
    """분석 리포트 정렬 필드"""
    UPDATED_AT = "updatedAt"
    CREATED_AT = "createdAt"
    TITLE = "title"


class AnalyticsReportsFilterOptions(CustomBaseModel):
    """Options for filtering analytics reports.
    
    Attributes:
        title_contains: Filter reports by title containing this string
    """
    title_contains: Optional[str] = Field(None, alias="titleContains")


class AnalyticsReportsFilter(CustomBaseModel):
    """Filter criteria for analytics report queries.
    
    Attributes:
        must_filter: Conditions that must be met
        not_filter: Conditions that must not be met
    """
    must_filter: Optional[AnalyticsReportsFilterOptions] = Field(None, alias="must")
    not_filter: Optional[AnalyticsReportsFilterOptions] = Field(None, alias="not")


class AnalyticsReportsOrderBy(CustomBaseModel):
    """Order by options for analytics reports.
    
    Attributes:
        field: The field to order by
        direction: The direction to order (ASC or DESC)
    """
    field: Optional[AnalyticsReportListOrderFields] = Field(None, description="정렬 필드")
    direction: Optional[str] = Field(None, description="정렬 방향 (ASC or DESC)")


def analytics_reports_params(
    dataset_id: str,
    analytics_reports_filter: Union[
        AnalyticsReportsFilter,
        UndefinedType
    ] = Undefined,
    cursor: Optional[str] = None,
    length: Optional[int] = 10,
    order_by: Union[
        AnalyticsReportsOrderBy,
        UndefinedType
    ] = Undefined,
):
    """Get parameters for listing analytics reports.
    
    Args:
        dataset_id: Required dataset ID
        analytics_reports_filter: Optional filter criteria for reports
        cursor: Optional cursor for pagination
        length: Optional number of items per page (default: 10)
        order_by: Optional order by options
        
    Returns:
        dict: Parameters for listing analytics reports
    """
    params = {
        "datasetId": dataset_id,
        "cursor": cursor,
        "length": length,
    }
    
    if analytics_reports_filter and not isinstance(analytics_reports_filter, UndefinedType):
        params["filter"] = analytics_reports_filter.model_dump(
            by_alias=True, exclude_unset=True
        )
    
    if order_by and not isinstance(order_by, UndefinedType):
        params["orderBy"] = order_by.model_dump(
            by_alias=True, exclude_unset=True
        )
    
    return params
