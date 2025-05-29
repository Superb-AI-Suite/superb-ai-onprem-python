

def remove_data_from_slice_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
):
    """Insert data to selected slice.

    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be removed
        slice_id (str): slice id to be removed

    Returns:
        dict: the params for graphql query
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "slice_id": slice_id,
    }
