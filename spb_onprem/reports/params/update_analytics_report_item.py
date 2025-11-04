from typing import Union, Any
from spb_onprem.base_types import Undefined, UndefinedType


def update_analytics_report_item_params(
    dataset_id: str,
    report_id: str,
    item_id: str,
    title: Union[str, UndefinedType] = Undefined,
    description: Union[str, UndefinedType] = Undefined,
    content_id: Union[str, UndefinedType] = Undefined,
    meta: Union[Any, UndefinedType] = Undefined,
):
    """Get parameters for updating an analytics report item.
    
    Args:
        dataset_id: The dataset ID
        report_id: The report ID
        item_id: The item ID
        title: Optional new title
        description: Optional new description
        content_id: Optional new content ID
        meta: Optional new metadata
        
    Returns:
        dict: Parameters for updating an analytics report item
    """
    params = {
        "datasetId": dataset_id,
        "reportId": report_id,
        "itemId": item_id,
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
