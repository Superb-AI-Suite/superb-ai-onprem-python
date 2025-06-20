from typing import Union

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from spb_onprem.activities.entities import ActivityStatus


def update_activity_history_params(
    activity_history_id: str,
    status: Union[
        UndefinedType,
        ActivityStatus
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
    """Create parameters for updating an activity history.
    
    Args:
        activity_history_id (str): The ID of the activity history to update.
        status (Optional[ActivityStatus]): The status to update the activity to.
        progress (Optional[dict]): The progress to update the activity with.
        meta (Optional[dict]): The meta information to update with.
        
    Returns:
        dict: Parameters for updating activity history
        
    Raises:
        BadParameterError: If activity_history_id is not provided or if neither status nor progress is provided
    """
    if activity_history_id is None:
        raise BadParameterError("Activity history ID is required")
    
    if status is Undefined and progress is Undefined:
        raise BadParameterError("Either status or progress must be provided")

    params = {
        "id": activity_history_id,
    }
    
    if status is not Undefined:
        params["status"] = status
    if progress is not Undefined:
        params["progress"] = progress
    if meta is not Undefined:
        params["meta"] = meta

    return params
