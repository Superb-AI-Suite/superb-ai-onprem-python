from typing import Optional, Union

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError


def start_activity_params(
    dataset_id: str,
    activity_id: Optional[str] = None,
    activity_type: Optional[str] = None,
    parameters: Union[
        UndefinedType,
        dict
    ] = Undefined,
    progress: Union[
        UndefinedType,
        dict
    ] = Undefined,
    meta: Union[
        UndefinedType,
        dict
    ] = Undefined,
) -> dict:
    """Create parameters for starting an activity.
    
    Args:
        dataset_id (str): The ID of the dataset to start the activity for.
        activity_id (Optional[str]): The ID of the activity to start.
        activity_type (Optional[str]): The type of the activity to start.
        parameters (Optional[dict]): The parameters to start the activity with.
        progress (Optional[dict]): The progress to start the activity with.
        meta (Optional[dict]): The meta information to start the activity with.
        
    Returns:
        dict: Parameters for starting an activity
        
    Raises:
        BadParameterError: If neither activity_id nor activity_type is provided
    """
    if activity_id is None and activity_type is None:
        raise BadParameterError("Either activity_id or activity_type must be provided")

    params = {
        "datasetId": dataset_id,
    }

    if activity_id is not None:
        params["id"] = activity_id
    else:
        params["jobType"] = activity_type

    if parameters is not Undefined:
        params["parameters"] = parameters
    if progress is not Undefined:
        params["progress"] = progress
    if meta is not Undefined:
        params["meta"] = meta

    return params
