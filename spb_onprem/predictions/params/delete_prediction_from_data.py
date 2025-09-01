def delete_prediction_from_data_params(
    dataset_id: str, 
    data_id: str, 
    prediction_set_id: str
):
    """Generate variables for delete prediction from data GraphQL mutation.
    
    Args:
        dataset_id (str): The ID of the dataset.
        data_id (str): The ID of the data.
        prediction_set_id (str): The ID of the prediction set.
        
    Returns:
        dict: Variables dictionary for the GraphQL mutation.
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "prediction_set_id": prediction_set_id
    }