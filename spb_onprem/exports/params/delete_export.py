from spb_onprem.exceptions import BadParameterError


def delete_export_params(
    dataset_id: str,
    export_id: str,
):
    """Create parameters for export deletion.
    
    Args:
        export_id (str): The ID of the export to delete.
        
    Returns:
        dict: Parameters for export deletion
        
    Raises:
        BadParameterError: If export_id is missing
    """
    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")

    if export_id is None:
        raise BadParameterError("Export ID is required")

    params = {
        "dataset_id": dataset_id,
        "export_id": export_id,
    }

    return params