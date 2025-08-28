from spb_onprem.exceptions import BadParameterError


def delete_slice_params(
    dataset_id: str,
    slice_id: str,
):
    """Create parameters for slice deletion.
    
    Args:
        dataset_id (str): The dataset ID the slice belongs to.
        slice_id (str): The ID of the slice to delete.
        
    Returns:
        dict: Parameters for slice deletion
    """
    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")
    if slice_id is None:
        raise BadParameterError("Slice ID is required")

    return {
        "dataset_id": dataset_id,
        "id": slice_id,
    }
