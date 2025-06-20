from spb_onprem.exceptions import BadParameterError

def delete_activity_params(
    activity_id: str,
):
    """Create parameters for activity deletion.
    
    Args:
        activity_id (str): The ID of the activity to delete.
        
    Returns:
        dict: Parameters for activity deletion
        
    Raises:
        BadParameterError: If activity_id is None
    """
    if activity_id is None:
        raise BadParameterError("Activity ID is required")

    params = {
        "id": activity_id,
    }
    return params
