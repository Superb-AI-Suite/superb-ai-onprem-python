def get_data_detail_params(dataset_id: str, data_id: str):
    """Generate variables for get data detail GraphQL query.
    
    Args:
        dataset_id (str): The ID of the dataset.
        data_id (str): The ID of the data.
        
    Returns:
        dict: Variables dictionary for the GraphQL query.
    """
    return {
        "datasetId": dataset_id,
        "id": data_id
    }