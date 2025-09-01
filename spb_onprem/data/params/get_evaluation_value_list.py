def get_evaluation_value_list_params(
    dataset_id: str,
    prediction_set_id: str,
    filter: dict = None,
    length: int = 50,
    cursor: str = None
):
    """Generate variables for get evaluation value list GraphQL query.
    
    Args:
        dataset_id (str): The ID of the dataset.
        prediction_set_id (str): The ID of the prediction set.
        filter (dict, optional): Diagnosis filter for evaluation values.
        length (int): Number of items to retrieve per page.
        cursor (str, optional): Cursor for pagination.
        
    Returns:
        dict: Variables dictionary for the GraphQL query.
    """
    params = {
        "datasetId": dataset_id,
        "predictionSetId": prediction_set_id,
        "length": length
    }
    
    if filter is not None:
        params["filter"] = filter
        
    if cursor is not None:
        params["cursor"] = cursor
        
    return params