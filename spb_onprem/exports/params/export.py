from spb_onprem.exceptions import BadParameterError


def get_export_params(
    dataset_id: str,
    export_id: str,
):
    """Create parameters for getting an export.
    
    Args:
        export_id (str): The ID of the export to get.
        dataset_id (Optional[str]): The ID of the dataset to get the export for.
        slice_id (Optional[str]): The ID of the slice to get the export for.
        
    Returns:
        dict: Parameters for getting an export
        
    Raises:
        BadParameterError: If export_id is missing
    """
    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")

    if export_id is None:
        raise BadParameterError("Export ID is required")

    return {
        "dataset_id": dataset_id,
        "export_id": export_id
    } 