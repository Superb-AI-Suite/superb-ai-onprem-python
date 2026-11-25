from spb_onprem.exceptions import BadParameterError


def dataset_caption_settings_params(dataset_id: str):
    """Get parameters for the datasetCaptionSettings query.

    Args:
        dataset_id: ID of the dataset

    Returns:
        dict: Parameters for the query

    Raises:
        BadParameterError: If dataset_id is missing
    """
    if not dataset_id:
        raise BadParameterError("dataset_id is required.")
    return {"datasetId": dataset_id}
