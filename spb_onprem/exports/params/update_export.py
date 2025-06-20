from typing import Union
from datetime import datetime

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from spb_onprem.data.params import DataListFilter


def update_export_params(
    dataset_id: str,
    export_id: str,
    location: Union[
        UndefinedType,
        str
    ] = Undefined,
    name: Union[
        UndefinedType,
        str
    ] = Undefined,
    data_filter: Union[
        UndefinedType,
        DataListFilter,
        dict
    ] = Undefined,
    data_count: Union[
        UndefinedType,
        int
    ] = Undefined,
    frame_count: Union[
        UndefinedType,
        int
    ] = Undefined,
    annotation_count: Union[
        UndefinedType,
        int
    ] = Undefined,
    meta: Union[
        UndefinedType,
        dict
    ] = Undefined,
    completed_at: Union[
        UndefinedType,
        datetime
    ] = Undefined,
):
    """Create parameters for export update.
    
    Args:
        dataset_id (str): The ID of the dataset to update the export for.
        export_id (str): The ID of the export to update.
        location (Optional[str]): The location where the export will be stored.
        name (Optional[str]): The name of the export.
        data_filter (Optional[DataListFilter | dict]): The search filter of the data.
        data_count (Optional[int]): The number of data items to export.
        frame_count (Optional[int]): The number of frames to export.
        annotation_count (Optional[int]): The number of annotations to export.
        meta (Optional[dict]): The meta information for the export.
        completed_at (Optional[datetime]): The completed time of the export.
        
    Returns:
        dict: Parameters for export update
        
    Raises:
        BadParameterError: If required parameters are missing
    """
    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")
    if export_id is None:
        raise BadParameterError("Export ID is required")

    params = {
        "dataset_id": dataset_id,
        "export_id": export_id,
    }

    if location is not Undefined:
        params["location"] = location
    if name is not Undefined:
        params["name"] = name
    if data_filter is not Undefined and data_filter is not None:
        # Handle both DataListFilter objects and plain dicts
        if isinstance(data_filter, DataListFilter):
            params["data_filter"] = data_filter.model_dump(by_alias=True, exclude_unset=True)
        else:
            # Assume it's a dict and use it directly
            params["data_filter"] = data_filter
    if data_count is not Undefined:
        params["data_count"] = data_count
    if frame_count is not Undefined:
        params["frame_count"] = frame_count
    if annotation_count is not Undefined:
        params["annotation_count"] = annotation_count
    if meta is not Undefined:
        params["meta"] = meta
    if completed_at is not Undefined:
        params["completed_at"] = completed_at

    return params 