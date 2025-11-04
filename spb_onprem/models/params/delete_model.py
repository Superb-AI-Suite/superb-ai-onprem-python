def delete_model_params(
    dataset_id: str,
    model_id: str,
):
    """Get parameters for deleting a model.
    
    Args:
        dataset_id: The dataset ID
        model_id: The model ID
        
    Returns:
        dict: Parameters for deleting a model
    """
    return {
        "datasetId": dataset_id,
        "id": model_id,
    }
