def delete_prediction_set_params(dataset_id: str, prediction_set_id: str):
    """Generate variables for delete prediction set GraphQL mutation.
    
    Args:
        dataset_id (str): The ID of the dataset.
        prediction_set_id (str): The ID of the prediction set to delete.
        
    Returns:
        dict: Variables dictionary for the GraphQL mutation.
    """
    return {
        "dataset_id": dataset_id,
        "id": prediction_set_id
    }