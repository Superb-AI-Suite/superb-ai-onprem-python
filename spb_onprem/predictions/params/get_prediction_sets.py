def get_prediction_sets_params(
    dataset_id: str,
    filter: dict = None,
    cursor: str = None,
    length: int = 50
):
    """Generate variables for get prediction sets GraphQL query.
    
    Args:
        dataset_id (str): The ID of the dataset.
        filter (dict, optional): Filter for prediction sets.
        cursor (str, optional): Cursor for pagination.
        length (int): Number of items to retrieve per page.
        
    Returns:
        dict: Variables dictionary for the GraphQL query.
    """
    params = {
        "dataset_id": dataset_id,
        "length": length
    }
    
    if filter is not None:
        params["filter"] = filter
        
    if cursor is not None:
        params["cursor"] = cursor
        
    return params