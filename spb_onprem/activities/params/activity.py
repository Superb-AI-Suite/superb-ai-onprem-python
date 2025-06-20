from typing import Union, Optional

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError


def get_activity_params(
    activity_id: Optional[str] = None,
    activity_name: Optional[str] = None,
    dataset_id: Union[
        UndefinedType,
        str
    ] = Undefined,
):
    """Create parameters for getting an activity.
    
    Args:
        activity_id (str): The ID of the activity to get.
        dataset_id (Optional[str]): The ID of the dataset to get the activity for.
        
    Returns:
        dict: Parameters for getting an activity
        
    Raises:
        BadParameterError: If activity_id is missing
    """
    if activity_id is None and activity_name is None:
        raise BadParameterError("Activity ID or name is required")

    params = {
    }

    if activity_id is not None:
        params["id"] = activity_id

    if activity_name is not None:
        params["name"] = activity_name

    if dataset_id is not Undefined:
        params["datasetId"] = dataset_id

    return params
