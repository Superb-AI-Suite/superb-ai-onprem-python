from typing import Union, Any
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType


def create_analytics_report_item_params(
    dataset_id: str,
    report_id: str,
    type: AnalyticsReportItemType,
    title: Union[str, UndefinedType] = Undefined,
    description: Union[str, UndefinedType] = Undefined,
    content_id: Union[str, UndefinedType] = Undefined,
    meta: Union[Any, UndefinedType] = Undefined,
):
    """Get parameters for creating an analytics report item.
    
    Args:
        dataset_id: The dataset ID
        report_id: The report ID
        type: The type of report item (PIE, HORIZONTAL_BAR, etc.)
        title: Optional item title
        description: Optional item description
        content_id: Optional content ID
        meta: Optional metadata
        
    Returns:
        dict: Parameters for creating an analytics report item
    """
    params = {
        "datasetId": dataset_id,
        "reportId": report_id,
        "type": type.value if isinstance(type, AnalyticsReportItemType) else type,
    }
    
    if not isinstance(title, UndefinedType):
        params["title"] = title
    
    if not isinstance(description, UndefinedType):
        params["description"] = description
    
    if not isinstance(content_id, UndefinedType):
        params["contentId"] = content_id
    
    if not isinstance(meta, UndefinedType):
        params["meta"] = meta
    
    return params
