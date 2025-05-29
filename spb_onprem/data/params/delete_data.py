

def delete_data_params(
    dataset_id: str,
    data_id: str,
):
    """Delete the data from dataset.

    Args:
        dataset_id (str): the dataset id which the data belongs to.
        data_id (str): the data id to delete.
    """
    
    return {
        "dataset_id": dataset_id,
        "id": data_id,
    }
