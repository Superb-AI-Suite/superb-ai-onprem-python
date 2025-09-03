def get_prediction_set_params(dataset_id: str, prediction_set_id: str):
    """Generate variables for get prediction set GraphQL query.
    
    Args:
        dataset_id (str): The ID of the dataset.
        prediction_set_id (str): The ID of the prediction set.
        
    Returns:
        dict: Variables dictionary for the GraphQL query.
    """
    return {
        "dataset_id": dataset_id,
        "id": prediction_set_id
    }