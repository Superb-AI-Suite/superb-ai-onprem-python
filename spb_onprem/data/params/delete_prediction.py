

def delete_prediction_params (
    dataset_id: str,
    data_id: str,
    set_id: str,
):
    """Delete prediction from selected data.

    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be deleted
        set_id (str): set id to be deleted
        
    Returns:
        dict: the params for graphql query
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "set_id": set_id,
    }
