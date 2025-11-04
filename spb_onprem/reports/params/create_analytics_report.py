from typing import Union, Any
from spb_onprem.base_types import Undefined, UndefinedType


def create_analytics_report_params(
    dataset_id: str,
    title: Union[str, UndefinedType] = Undefined,
    description: Union[str, UndefinedType] = Undefined,
    meta: Union[Any, UndefinedType] = Undefined,
):
    """Get parameters for creating an analytics report.
    
    Args:
        dataset_id: The dataset ID
        title: Optional report title
        description: Optional report description
        meta: Optional metadata
        
    Returns:
        dict: Parameters for creating an analytics report
    """
    params = {
        "datasetId": dataset_id,
    }
    
    if not isinstance(title, UndefinedType):
        params["title"] = title
    
    if not isinstance(description, UndefinedType):
        params["description"] = description
    
    if not isinstance(meta, UndefinedType):
        params["meta"] = meta
    
    return params
