def model_params(
    dataset_id: str,
    model_id: str,
):
    """Get parameters for retrieving a single model.
    
    Args:
        dataset_id: The dataset ID
        model_id: The model ID
        
    Returns:
        dict: Parameters for retrieving a model
    """
    return {
        "datasetId": dataset_id,
        "modelId": model_id,
    }
