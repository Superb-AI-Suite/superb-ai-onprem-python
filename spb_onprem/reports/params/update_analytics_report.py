from typing import Union, Any, Optional
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.reports.entities.analytics_report import AnalyticsReportStatus


def update_analytics_report_params(
    dataset_id: str,
    report_id: str,
    title: Union[str, UndefinedType] = Undefined,
    description: Union[str, UndefinedType] = Undefined,
    status: Union[Optional[AnalyticsReportStatus], UndefinedType] = Undefined,
    meta: Union[Any, UndefinedType] = Undefined,
):
    """Get parameters for updating an analytics report.
    
    Args:
        dataset_id: The dataset ID
        report_id: The report ID
        title: Optional new title
        description: Optional new description
        status: Optional new status (PENDING/IN_PROGRESS/COMPLETED/FAILED)
        meta: Optional new metadata
        
    Returns:
        dict: Parameters for updating an analytics report
    """
    params = {
        "datasetId": dataset_id,
        "reportId": report_id,
    }
    
    if not isinstance(title, UndefinedType):
        params["title"] = title
    
    if not isinstance(description, UndefinedType):
        params["description"] = description
    
    if not isinstance(status, UndefinedType):
        params["status"] = status
    
    if not isinstance(meta, UndefinedType):
        params["meta"] = meta
    
    return params
